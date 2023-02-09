"""
Definerer en klasse Prognoseresultater som kan brukes til å hente resultater fra Samkjøringsmodellen.

For å bruke Prognoseresultater-objektet som et bibliotek kan du putte denne filen inn i
prosjektet ditt og skrive from prognoseresultater import Prognoseresultater.

Se main-funksjonen for et eksempel på bruk av Prognoseresultater-objektet. Det er bare funksjonene som vises
frem i dette eksemplet som det er meningen at en bruker skal bruke.
Hvis man kjører denne filen som et frittstående script (altså ikke bruker det som et bibliotek slik som avsnittet over)
med kommandoen python prognoseresultater.py.

Laget av haen 3.11.2021
"""
import os
import pandas as pd
import struct

def main():
    """
    Hovedfunksjon som tester funksjonene i Prognoseresultater-objektet

    Fungerer også som et eksempel på hvordan man kan bruke funksjonaliteten.
    """
    # Lag Prognoseresultater-objekt
    r = Prognoseresultater()

    # Lag sti til modellmappe
    #modellmappe = r"X:\Prosjekter\2022_Magasinprognose\Prognoser\Uke_46\Simuleringer\Basis\emps"

    # Les data fra modellmappe inn til Prognoseresultater-objekt
    r.les_data(modellmappe)

    # Under kaller jeg på funksjoner som er definert for Prognoseresultater-objektet
    # De forskjellige funksjonene sammenstiller data fra modellen og returnerer det
    # som en dataframe, slik at brukeren enkelt kan jobbe videre med dataene


    df = r.utveksling()
    print(df.head(), "\n")

    # df.to_excel("utveksling.xlsx")

    return

    df = r.tilsig()
    print(df.head(), "\n")

    df = r.magasinfylling()
    print(df.head(), "\n")

    df = r.kraftpris()
    print(df.head(), "\n")



    df = r.forbruk()
    print(df.head(), "\n")

    df = r.produksjon()
    print(df.head(), "\n")

    df = r.industriforbruk()
    print(df.head(), "\n")

    df = r.termisk()
    print(df.head(), "\n")

    df = r.tidsoppløsning()
    print(df.head(), "\n")

class Prognoseresultater:
    """
    Klasse for å hente ut resultater fra en Samkjøringsmodellmappe.

    Fungerer bare for versjon 9.9 av Samkjøringsmodellen.

    Laget av haen 3.11.2021
    """

    # TODO: Bytt ut lister med np.array for mer effektive lesefunksjoner

    def les_data(self, modellmappe):
        """
        Leser diverse filer i modellmappen og lagrer dataene i objektet.

        Fungerer bare for versjon 9.9 av Samkjøringsmodellen.

        Legger beslag på mye minne hvis modellen er kjørt med fin tidsoppløsning.
        """
        samres = les_samres(os.path.join(modellmappe, "SAMRES.SAMK"))

        trinnliste = les_trinnliste(os.path.join(modellmappe, "trinnliste.txt"))

        omr = les_omr(os.path.join(modellmappe, "C20_OMRADE.EMPS"))

        # omr.to_excel("omr_98.xlsx")

        prefres_info = les_prefres_info(os.path.join(modellmappe, "SekvRes", "info.data"))

        prefres = []
        for scenarionr, aar in enumerate(samres["hist"], start=1):
            filsti = os.path.join(modellmappe, "SekvRes", "PrefRes_%03d.SAMK" % scenarionr)
            prefres.append(
                les_prefres_scenariofil(filsti, aar,
                                        samres["jstart"], samres["jslutt"], samres["npenm"],
                                        prefres_info["ntrinnsum"], prefres_info["irecl_prefres"]))
        prefres = pd.concat(prefres)
        prefres = prefres.reset_index(drop=True)

        ntrinn_per_omr = trinnliste.pivot_table(index="omrnr", values="typenr", aggfunc="count")
        ntrinn_per_omr = list(ntrinn_per_omr["typenr"])

        sapref28 = les_sapref28(os.path.join(modellmappe, "SAPREF28.SAMK"),
                                prefres_info["ntrinnsum"], ntrinn_per_omr,
                                samres["npenm"], samres["nuke"])

        utv = les_utveksling(os.path.join(modellmappe, "UTVEKSLING.SAMK"),
                             samres["nfor"], samres["hist"],
                             samres["jstart"], samres["jslutt"], samres["npenm"])

        prisavsnitt = les_prisavsnitt(os.path.join(modellmappe, "PRISAVSNITT.DATA"))

        maskenett = les_maskenett(os.path.join(modellmappe, "MASKENETT.DATA"),
                                  samres["nuke"], samres["npenm"])

        brensel = les_brensel(os.path.join(modellmappe, "BRENSEL.ARCH"))

        varmekraft_brensel = les_varmekraft_brensel(modellmappe, omr)

        minmax = les_minmax(os.path.join(modellmappe, "MINMAX.SAMK"),
                            samres["nverk"], samres["nuke"], samres["npenm"])

        self.samres = samres
        self.trinnliste = trinnliste
        self.omr = omr
        self.prefres = prefres
        self.sapref28 = sapref28
        self.utv = utv
        self.maskenett = maskenett
        self.prisavsnitt = prisavsnitt
        self.brensel = brensel
        self.varmekraft_brensel = varmekraft_brensel
        self.minmax = minmax

    def magasinfylling(self) -> pd.DataFrame:
        """
        Magasinfylling per område i Samkjøringsmodellen,
        og vannverdi tilhørende magasinfyllingen og magasingrenser.

        (Samme magasinfylling og vannverdi som mag og vv i kurvetegn-programmet)

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            aar - simulert værår
            uke - simulert uke
            magasinfylling - volum lagret i magasinet ved utgangen av uken i GWh
            minmag - nedre magasingrense for enmagasinmodellen i GWh
            maxmag - øvre magasingrense for enmagasinmodellen i GWh
            vannverdi - vannverdi tilhørende den aktuelle magasinfyllingen i øre/kWh
        """
        # hent magasinfylling
        df = self.samres["mag"].copy()
        df = df.melt(id_vars=["aar", "uke"], var_name="omrnr", value_name="magasinfylling")

        # koble på vannverdi
        v = self.samres["vv"].copy()
        v = v.melt(id_vars=["aar", "uke"], var_name="omrnr", value_name="vannverdi")
        df = df.merge(v, on=["omrnr", "aar", "uke"], how="left")
        df["vannverdi"] = df["vannverdi"].fillna(0)

        # koble på minimumsmagasin
        m = self.minmax["minmag"].copy()
        m = m.melt(id_vars=["uke"], var_name="omrnr", value_name="minmag")
        df = df.merge(m, on=["omrnr", "uke"])
        df["minmag"] = df["minmag"].fillna(0)

        # koble på maksimumsmagasin
        m = self.minmax["maxmag"].copy()
        m = m.melt(id_vars=["uke"], var_name="omrnr", value_name="maxmag")
        df = df.merge(m, on=["omrnr", "uke"])
        df["maxmag"] = df["maxmag"].fillna(0)

        # koble på områdenavn
        df = self.omr.merge(df, on="omrnr")

        # ordne rekkefølge på kolonner i dataframen
        kolonner = ["omrnr", "omrnavn", "aar", "uke",
                    "magasinfylling", "minmag", "maxmag", "vannverdi"]
        df = df[kolonner]

        return df

    def kraftpris(self) -> pd.DataFrame:
        """
        Kraftpriser fra Samkjøringsmodellen.
        (Samme kraftpris som krv i kurvetegn-programmet)

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            aar - simulert værår
            uke - simulert uke
            tsnitt - tidsperiode innad i uken (tidsavsnitt)
            tsnitt_timer - antall timer i det aktuelle tidsavsnittet
            kraftpris - kraftpris i øre/kWh
        """
        # hent kraftpriser
        df = self.samres["krv"].copy()
        df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="kraftpris")

        # koble på områdenavn
        df = self.omr.merge(df, on="omrnr")

        # koble på tsnitt_timer (så bruker kan aggregere prisene riktig)
        df["tsnitt_timer"] = df["tsnitt"].apply(lambda ts: self.samres["ntimen"][ts - 1])

        # ordne rekkefølge på kolonner i dataframen
        kolonner = ["omrnr", "omrnavn", "aar", "uke", "tsnitt", "tsnitt_timer", "kraftpris"]
        df = df[kolonner]

        return df

    def utveksling(self) -> pd.DataFrame:
        """
        Utveksling på linjer i Samkjøringsmodellen sammen med informasjon som beskriver linjene.
        (Samme utveksling som utv i kurvetegn-programmet)

        Returnerer pandas.DataFrame med kolonner
            linjenr - id på linje (definert av rekkefølge i filen MASKENETT.DATA)
            omrnr - id på område
            omrnavn - navn på område
            aar - simulert værår
            uke - simulert uke
            tsnitt - tidsperiode innad i uken (tidsavsnitt)
            tsnitt_timer - antall timer i det aktuelle tidsavsnittet
            kap_fra - installert kapasitet i retning omr_fra->omr_til i GWh/tsnitt (fra MASKENETT.DATA)
            kap_til - installert kapasitet i retning omr_til->omr_fra i GWh/tsnitt (fra MASKENETT.DATA)
                      (negativ verdi grunnet motsatt vei av flytretningen på linjen)
            tap - tap på linjen (fra MASKENETT.DATA)
            avgift_fra - handelsavgift i retning omr_fra->omr_til i øre/kWh (fra MASKENETT.DATA)
            avgift_til - handelsavgift i retning omr_til->omr_fra i øre/kWh (fra MASKENETT.DATA)
            utveksling - netto utveksling på linjen i retning omr_fra->omr_til i GWh/tsnitt
                         (negative verdier betyr utveksling i retning omr_til->omr_fra)
            tilgjengelig_fra - Tilgjengelig kapasitet omr_fra->omr_til i GWh/tsnitt
            tilgjengelig_til - Tilgjengelig kapasitet omr_til->omr_fra i GWh/tsnitt
                               (negativ verdi grunnet motsatt vei av flytretningen på linjen)
        """

        # hent utveksling
        df = self.utv.copy()
        df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="linjenr", value_name="utveksling")

        dfc=df[df["linjenr"]==5].copy()

        # koble på info om linjene (kapasitet, tapsfaktor, områder ol.)
        m = self.maskenett.copy()
        df = df.merge(m, on=["linjenr", "uke", "tsnitt"], how="left")

        # koble på omrnavn
        o = self.omr.copy()
        o = dict(zip(o["omrnr"].astype(int), o["omrnavn"]))
        print(o)
        df["omrnavn_fra"] = df["omrnr_fra"].apply(lambda n : o[n])
        df["omrnavn_til"] = df["omrnr_til"].apply(lambda n : o[n])

        # koble på tsnitt_timer (så bruker kan aggregere prisene riktig)
        df["tsnitt_timer"] = df["tsnitt"].apply(lambda ts: self.samres["ntimen"][ts - 1])

        # regn ut tilgjengelig kapasitet
        df["tilgjengelig_fra"] = df["kap_fra"] + df["avvik_fra"]
        df["tilgjengelig_til"] = df["kap_til"] + df["avvik_til"]

        # endre fortegn på kapasiteter i til-retningen
        df["kap_til"] *= -1.0
        df["tilgjengelig_til"] *= -1.0

        # konvertere fra MW til GWh/tsnitt
        for key in ['utveksling', 'avvik_fra', 'avvik_til', 'kap_fra',
                    'kap_til', 'tilgjengelig_fra', 'tilgjengelig_til']:
            df[key] = df[key] * df["tsnitt_timer"] / 1000.0

        # ordne rekkefølge på kolonner i dataframe
        kolonner = ["linjenr", "omrnr_fra", "omrnavn_fra", "omrnr_til", "omrnavn_til",
                    "aar", "uke", "tsnitt", "tsnitt_timer",
                    'kap_fra', 'kap_til','avvik_fra','avvik_til', 'tap', 'avgift_fra', 'avgift_til',
                    'utveksling', 'tilgjengelig_fra', 'tilgjengelig_til']
        df = df[kolonner]

        return df

    def produksjon(self) -> pd.DataFrame:
        """
        Diverse kilder til produksjon i Samkjøringsmodellen.

        For å få total produksjon kan man summere
            vannkraft, vind_sol og annen_produksjon

        uekte_produksjon er det samme som rasjonering. Da er det ikke nok ekte produksjon til å
        dekke forbruket, og modellen fyller da opp med uekte_produksjon for å sørge for at likningene går opp.

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            typenr - id på kontrakt
            navn - navn på kontrakt
            aar - simulert værår
            uke - simulert uke
            tsnitt - tidsperiode innad i uken (tidsavsnitt)
            tsnitt_timer - antall timer i det aktuelle tidsavsnittet
            vannkraft - vannkraftproduksjon i GWh/tsnitt
            vind_sol - Vind- og solkraftproduksjon i GWh/tsnitt
            annen_produksjon - Resterende produksjon som ikke er vann, vind eller sol.
                               (Dette utgjør primært termisk produksjon, men kan også inneholde import,
                               hvis dette er modellert som lokal produksjon.
                               NVE gjør normalt ikke dette, bortsett fra utvekslingen med Russland i FINNMARK)
            uekte_produksjon - mengden rasjonert forbruk i det aktuelle tidsavsnitett i GWh/tsnitt
        """
        # hent vannkraftproduksjon
        df = self.samres["egpr"].copy()
        df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="vannkraft")

        # koble på vind- og solkraftproduksjon
        v = self.samres["vind"].copy()
        v = v.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="vind_sol")
        df = df.merge(v, on=["omrnr", "aar", "uke", "tsnitt"])

        # legg til annen produksjon
        t = self.trinnliste.copy()
        t = t[t["katnr"].isin([1, 3, 4, 6, 8])] # Produksjonskategorier, men uten rasjonering

        p = self.prefres.copy()
        p = p.set_index(["aar", "uke", "tsnitt"])
        p = p[list(t["sumtrinn"])]
        p = p.reset_index()
        p = p.melt(id_vars=["aar", "uke", "tsnitt"], var_name="sumtrinn", value_name="annen_produksjon")

        p = t.merge(p, on="sumtrinn")

        p = p.pivot_table(index=["omrnr", "aar", "uke", "tsnitt"],
                          values="annen_produksjon", aggfunc="sum")
        p = p.reset_index()

        df = df.merge(p, on=["omrnr", "aar", "uke", "tsnitt"], how="left")
        df["annen_produksjon"] = df["annen_produksjon"].fillna(0.0)

        # legg til uekte_produksjon (rasjonering)
        t = self.trinnliste.copy()
        t = t[t["katnr"] == 40] # Rasjonering

        p = self.prefres.copy()
        p = p.set_index(["aar", "uke", "tsnitt"])
        p = p[list(t["sumtrinn"])]
        p = p.reset_index()
        p = p.melt(id_vars=["aar", "uke", "tsnitt"], var_name="sumtrinn", value_name="uekte_produksjon")

        p = t.merge(p, on="sumtrinn")

        p = p.pivot_table(index=["omrnr", "aar", "uke", "tsnitt"],
                          values="uekte_produksjon", aggfunc="sum")
        p = p.reset_index()

        df = df.merge(p, on=["omrnr", "aar", "uke", "tsnitt"], how="left")
        df["uekte_produksjon"] = df["uekte_produksjon"].fillna(0)

        # koble på omrnavn
        df = self.omr.merge(df, on="omrnr")

        # koble på tsnitt_timer (så bruker kan aggregere dataene)
        df["tsnitt_timer"] = df["tsnitt"].apply(lambda ts: self.samres["ntimen"][ts - 1])

        # ordne rekkefølge på kolonner i dataframe
        kolonner = ["omrnr", "omrnavn", "aar", "uke","tsnitt", "tsnitt_timer",
                    "vannkraft", "vind_sol", "annen_produksjon", "uekte_produksjon"]
        df = df[kolonner]

        return df


    def forbruk(self) -> pd.DataFrame:
        """
        Data for ulike typer forbruk i Samkjøringsmodellen.

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            aar - simulert værår
            uke - simulert uke
            tsnitt - tidsperiode innad i uken (tidsavsnitt)
            tsnitt_timer - antall timer i det aktuelle tidsavsnittet
                           (kan brukes til å regne fra GWh/tsnitt til MW)
            fast_forbruk - fast, potensielt temperaturavhengig, forbruk (fastkraft)
            utkoblbart_forbruk - den prisavhengige delen av forbruket
                                 (industriforbruk + forbruksendringer i fast forbruk pga. priselastisitet)
            uekte_forbruk - mengden overskuddsproduksjon i det aktuelle tidsavsnitett i GWh/tsnitt
                            (mengden "Flomkraft")

        Mer om uekte_forbruk: Oppstår når det er mer must-run produksjon enn forbruk+eksport
        for å sørge for balanse mellom produksjon og forbruk til enhver tid (for at likningene skal gå opp)
          -> uekte_forbruk måler tilbusdoverskudd med andre ord
          -> (kalles Flomkraft i Samkjøringsmodellen)
        """
        # hent fastkraft
        df = self.samres["fast"].copy()
        df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="fast_forbruk")

        # koble på utkoblbart forbruk
        t = self.trinnliste.copy()
        t = t[t["katnr"].isin([2, 5, 7, 9, 30])] # Forbrukskategorier, men uten flomkraft

        p = self.prefres.copy()
        p = p.set_index(["aar", "uke", "tsnitt"])
        p = p[list(t["sumtrinn"])]
        p = p.reset_index()
        p = p.melt(id_vars=["aar", "uke", "tsnitt"], var_name="sumtrinn", value_name="utkoblbart_forbruk")

        p = t.merge(p, on="sumtrinn")

        p = p.pivot_table(index=["omrnr", "aar", "uke", "tsnitt"],
                          values="utkoblbart_forbruk", aggfunc="sum")
        p = p.reset_index()

        df = df.merge(p, on=["omrnr", "aar", "uke", "tsnitt"], how="left")
        df["utkoblbart_forbruk"] = df["utkoblbart_forbruk"].fillna(0.0)
        df["utkoblbart_forbruk"] *= -1 # fordi forbruk lagres som negative tall i prefres

        # koble på uekte forbruk
        t = self.trinnliste.copy()
        t = t[t["katnr"] == 20] # Flomkraft

        p = self.prefres.copy()
        p = p.set_index(["aar", "uke", "tsnitt"])
        p = p[list(t["sumtrinn"])]
        p = p.reset_index()
        p = p.melt(id_vars=["aar", "uke", "tsnitt"], var_name="sumtrinn", value_name="uekte_forbruk")

        p = t.merge(p, on="sumtrinn")

        p = p.pivot_table(index=["omrnr", "aar", "uke", "tsnitt"],
                          values="uekte_forbruk", aggfunc="sum")
        p = p.reset_index()

        df = df.merge(p, on=["omrnr", "aar", "uke", "tsnitt"], how="left")
        df["uekte_forbruk"] = df["uekte_forbruk"].fillna(0.0).abs()

        # koble på områdenavn
        df = self.omr.merge(df, on="omrnr")

        # koble på tsnitt_timer (så bruker kan aggregere dataene)
        df["tsnitt_timer"] = df["tsnitt"].apply(lambda ts: self.samres["ntimen"][ts - 1])

        # ordne rekkefølge på kolonner i dataframe
        kolonner = ["omrnr", "omrnavn", "aar", "uke", "tsnitt", "tsnitt_timer",
                    "fast_forbruk", "utkoblbart_forbruk", "uekte_forbruk"]
        df = df[kolonner]

        return df

    def industriforbruk(self) -> pd.DataFrame:
        """
        Data for industriforbruk i Samkjøringsmodellen.
         -> Kontrakter som er modellert som "kategorinr 9 - Salg refert lastprofil"
         -> (Det er mulig å modellere forbruk på andre måter, men NVE bruker denne måten.
             Hvis NVE endrer modelleringen vil ikke denne funksjonen lenger
             gi oversikt over alt industriforbruk i modellen)

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            typenr - id på kontrakt
            navn - navn på kontrakt
            aar - simulert værår
            uke - simulert uke
            tsnitt - tidsperiode innad i uken (tidsavsnitt)
            tsnitt_timer - antall timer i det aktuelle tidsavsnittet
            utkoblingspris - hvis kraftprisen blir høyere kobles forbruket ut, enhet i øre/kWh
            kapasitet - potensialet for forbruk i det aktuelle tidsavsnittet i GWh/tsnitt
            forbruk - mengden forbruk i det aktuelle tidsavsnitett i GWh/tsnitt
        """
        # hent alle kontrakter med kategorinr 9
        t = self.trinnliste.copy()
        t = t[t["katnr"] == 9] # Salg refert lastprofil

        # hent forbruksverdier
        df = self.prefres.copy()

        # filtrer dataframen slik at den bare inneholder
        # kategori 9 kolonner
        # gjøres for at melt-operasjon lengre ned skal gå raskere og bruke mindre minne
        df = df.set_index(["aar", "uke", "tsnitt"])
        df = df[list(t["sumtrinn"])]
        df = df.reset_index()

        # stable om dataene slik at de lagres radvis
        # dette går ut over effektiviteten men blir enklere å jobbe med
        df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="sumtrinn", value_name="forbruk")
        # endre til positive verdier fordi forbruk i prefres-filen i Samkjøringsmodellen
        # lagrer forbruk med negative verdier, og vi ønsker positive verdier her
        df["forbruk"] = df["forbruk"].abs()

        # koble på info om kontraktene (navn, omr, osv)
        df = t.merge(df, on="sumtrinn")

        # koble på kapasitet og utkoblingspris
        p = self.sapref28.copy()
        p = p.rename(columns={"pris" : "utkoblingspris", "mengde" : "kapasitet"})
        p["kapasitet"] = p["kapasitet"].abs() # snu fortegn på kapasitet til positive verdier
        df = df.merge(p, on=["omrnr", "typenr", "uke", "tsnitt"])

        # koble på tsnitt_timer (så bruker kan aggregere dataene)
        df["tsnitt_timer"] = df["tsnitt"].apply(lambda ts : self.samres["ntimen"][ts - 1])

        # ordne rekkefølge på kolonner i dataframe
        kolonner = ["omrnr", "omrnavn", "typenr", "navn", "aar", "uke",
                    "tsnitt", "tsnitt_timer", "utkoblingspris", "kapasitet", "forbruk"]
        df = df[kolonner]

        return df

    def termisk(self) -> pd.DataFrame:
        """
        Data for termisk kraftproduksjon i Samkjøringsmodellen.

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            typenr - id på kontrakt
            navn - navn på kontrakt
            brenselnavn - navn på brensel
            aar - simulert værår
            uke - simulert uke
            tsnitt - tidsperiode innad i uken (tidsavsnitt)
            tsnitt_timer - antall timer i det aktuelle tidsavsnittet
            marginalkostnad - hvis kraftprisen blir lavere produseres det ikke, enhet i øre/kWh
                              blir enten satt direkte eller hvis brensel, regnes ut med formel
                                  marginalkostnad = brenselpris/virkningsgrad + co2faktor*co2pris/virkningsgrad + lokal_kostnad
            kapasitet - potensialet for produksjon i det aktuelle tidsavsnittet i GWh/tsnitt
            produksjon - mengden produksjon i det aktuelle tidsavsnitett i GWh/tsnitt
        """
        # hent kontakter (trinn) og filtrer ut de som gjelder varmekraft
        t = self.trinnliste.copy()
        t = t[t["katnavn"] == "Varmekraft"]

        # hent verdier for alle trinn
        df = self.prefres.copy()

        # filtrer bort alle kolonner som ikke er varmekraft
        # gjøres for at melt-operasjonen under skal gå raskere og bruke mindre minne
        df = df.set_index(["aar", "uke", "tsnitt"])
        df = df[list(t["sumtrinn"])]
        df = df.reset_index()

        df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="sumtrinn", value_name="produksjon")

        # koble info om kontraktene på verdiene (navn, omr osv)
        df = t.merge(df, on="sumtrinn")

        # koble på brensel for varmekontraktene
        # (slik at bruker kan aggergere produksjon per brensel)
        k = self.varmekraft_brensel.copy()
        df = df.merge(k, on=["omrnr", "typenr"], how="left")

        # koble på marginalkostnad og produksjonskapasitet
        p = self.sapref28.copy()
        p = p.rename(columns={"pris" : "marginalkostnad", "mengde" : "kapasitet"})
        df = df.merge(p, on=["omrnr", "typenr", "uke", "tsnitt"])

        # koble på tsnitt_timer (slik at bruker kan aggregere dataene)
        df["tsnitt_timer"] = df["tsnitt"].apply(lambda ts : self.samres["ntimen"][ts - 1])

        # ordne rekkefølge på kolonner i dataframe
        kolonner = ["omrnr", "omrnavn", "typenr", "navn", "brenselnavn", "aar", "uke",
                    "tsnitt", "tsnitt_timer", "marginalkostnad", "kapasitet", "produksjon"]
        df = df[kolonner]

        return df

    def tilsig(self) -> pd.DataFrame:
        '''
        Gir oversikt over bruttotilsig, (reg+ureg)

        Returnerer pandas.DataFrame med kolonner
            omrnr - id på område
            omrnavn - navn på område
            aar - simulert værår
            uke - simulert uke
            reg - regulert tilsig i løpet av uka i GWh
            ureg - uregulert tilsig i løpet av uka i GWh
            bruttotilsig - sum av regulert og uregulert tilsig i løpet av uka i GWh

        '''
        # hent reg + ureg
        dfr = self.samres["reg"].copy()
        dfu = self.samres["ureg"].copy()

        dfr = dfr.melt(id_vars=["aar", "uke","tsnitt"], var_name="omrnr", value_name="reg")
        dfr = dfr.pivot_table(index=["aar", "uke", "omrnr"], values="reg", aggfunc="sum").reset_index()

        dfu = dfu.melt(id_vars=["aar", "uke","tsnitt"], var_name="omrnr", value_name="ureg")
        dfu = dfu.pivot_table(index=["aar", "uke","omrnr"], values="ureg", aggfunc="sum").reset_index()

        df=dfr.merge(dfu, on=["aar","uke","omrnr"])
        df["bruttotilsig"]=df["reg"]+df["ureg"]

        return df


    def tidsoppløsning(self) -> pd.DataFrame:
        """
        Gir oversikt over tidsoppløsningen innad i uken i modellsimuleringen.

        Kan være nyttig hvis man konvertere dataene til timesoppløsning.

        Returnerer pandas.DataFrame med kolonner:
            uketime - time i uken (1, 2, 3, .., 167, 168)
            ukedag - hvilken ukedag uketimen tilhører (man = 1, tir = 2, ... , søn = 7)
            helg - True hvis ukedag in [6, 7], else False
            døgntime - Time i døgnet
            tsnitt - Hvilket tidsavsnitt uketimen tilhører
        """
        df = self.prisavsnitt.copy()
        return df


# ---------- Lesefunksjoner ---------------------------------

# Disse funksjonene leser resulatfiler i Samkjøringsmodellen

def les_samres(filsti):
    names = ["krv", "vv", "mag", "flom", "reg", "ureg", "fast", "egpr", "int", "vind"]

    d = {n: [] for n in names}

    with open(filsti, "rb") as f:

        nverk, jstart, jslutt = struct.unpack(3 * "i", f.read(3 * 4))
        serie = struct.unpack(1 * "i", f.read(1 * 4))[0] * -1
        nsim, nuke, staar = struct.unpack(3 * "i", f.read(3 * 4))
        runcode = struct.unpack(40 * "c", f.read(40 * 1))
        npenm, istbl, nfor = struct.unpack(3 * "i", f.read(3 * 4))

        blengde = max([10 * nverk * 4 * 1, (npenm + 2 * 1) * 4, 40 + 12 * 4])

        f.seek(2 * blengde)
        ntimen = struct.unpack(npenm * "i", f.read(npenm * 4))

        f.seek(4 * blengde)
        hist = struct.unpack(nsim * "i", f.read(nsim * 4))

        blokk = istbl

        for aar in hist:
            for uke in range(jstart, jslutt + 1):
                for tsnitt in range(1, npenm + 1):
                    f.seek(blokk * blengde)
                    row = {n: [aar, uke, tsnitt] for n in names}
                    for omrnr in range(1, nverk + 1):
                        values = struct.unpack(10 * "f", f.read(10 * 4))
                        for i, value in enumerate(values):
                            name = names[i]
                            row[name].append(value)
                    blokk += 1
                    for name in names:
                        d[name].append(row[name])

    runcode = b"".join(runcode).decode("utf-8")

    omrnr_liste = list(range(1, nverk + 1))
    for n in names:
        d[n] = pd.DataFrame(d[n], columns=["aar", "uke", "tsnitt"] + omrnr_liste)

    for n in ["mag", "flom"]:
        df = d[n]
        df = df.pivot_table(index=["aar", "uke"], values=omrnr_liste, aggfunc="sum")
        df = df.reset_index()
        d[n] = df

    df = d["vv"]
    df = df.pivot_table(index=["aar", "uke"], values=omrnr_liste, aggfunc="min")
    df = df.reset_index()
    d["vv"] = df

    d["nverk"] = nverk
    d["jstart"] = jstart
    d["jslutt"] = jslutt
    d["serie"] = serie
    d["nsim"] = nsim
    d["nuke"] = nuke
    d["staar"] = staar
    d["runcode"] = runcode
    d["npenm"] = npenm
    d["istbl"] = istbl
    d["nfor"] = nfor
    d["blengde"] = blengde
    d["ntimen"] = ntimen
    d["hist"] = hist

    return d

def les_trinnliste(filsti):
    rader = []

    sumtrinn = 0

    with open(filsti) as f:
        antall_omr = int(f.readline().split(",")[0])

        for omrnr in range(1, antall_omr + 1):
            omrnr, omrnavn = f.readline().split(",")[:2]

            omrnr = int(omrnr)
            omrnavn = omrnavn.replace("'", "").strip()

            antall_trinn = int(f.readline().split(",")[0])
            for i in range(antall_trinn):
                typenr, navn, katnr, katnavn = f.readline().split(",")[:4]

                typenr = int(typenr)
                katnr = int(katnr)
                navn = navn.replace("'", "").strip()
                katnavn = katnavn.replace("'", "").strip()

                sumtrinn += 1
                rader.append((sumtrinn, omrnr, omrnavn, typenr, navn, katnr, katnavn))

    kolonnenavn = ["sumtrinn", "omrnr", "omrnavn", "typenr", "navn", "katnr", "katnavn"]
    df = pd.DataFrame(rader, columns=kolonnenavn)

    return df


def les_omr(filsti):
    rader = []

    with open(filsti, "rb") as f:
        blengde, nverk = struct.unpack(2 * "i", f.read(2 * 4))
        f.seek(blengde)

        for omrnr in range(1, nverk + 1):
            omrnavn = struct.unpack(20 * "c", f.read(20 * 1))

            # dekode og rydde omrnavn
            omrnavn = b"".join(omrnavn)
            try:
                omrnavn = omrnavn.decode("cp865")
            except:
                omrnavn = omrnavn.decode("utf-8", "ignore")
            omrnavn = omrnavn.strip()

            rader.append([omrnr, omrnavn])

    df = pd.DataFrame(rader, columns=["omrnr", "omrnavn"])

    return df

def les_prefres_info(filsti):
    d = dict()
    with open(filsti, "rb") as f:
        d["iverprefres"], d["irecl_infofil"], d["irecl_prefres"] = struct.unpack("i"*3, f.read(4*3))
        d["irecl_peg_pkrv"], d["irecl_maske"], d["jstart"], d["jslutt"], d["jslutt_st"] = struct.unpack("i"*5, f.read(4*5))
        d["npenm_u"], d["npenm"], d["npref_m_start"], d["ntrinnsum"] = struct.unpack("i"*4, f.read(4*4))
        d["nfor"], d["nverk"], d["npre"] = struct.unpack("i"*3, f.read(4*3))
    return d

def les_prefres_scenariofil(filsti, aar, jstart, jslutt, npenm, ntrinnsum, blengde):
    rader = []

    with open(filsti, "rb") as f:
        for uke in range(jstart, jslutt + 1):
            for tsnitt in range(1, npenm + 1):
                blokk = (uke - jstart)*npenm + tsnitt - 1
                f.seek(blokk*blengde)
                values = list(struct.unpack("f"*ntrinnsum, f.read(4*ntrinnsum)))
                rader.append([aar, uke, tsnitt] + values)

    kolonnenavn = ["aar", "uke", "tsnitt"] + list(range(1, ntrinnsum + 1))
    df = pd.DataFrame(rader, columns=kolonnenavn)

    return df


def les_sapref28(filsti, num_sumtrinn, ntrinn_per_omr, npenm, nuke):
    """
    filsti         - sti til sapref28-fil
    num_sumtrinn   - totalt antall trinn i modellen
    ntrinn_per_omr - antall trinn per omr
    npenm          - antall tidsavsnitt
    nuke           - antall uker i dataperioden
    nverk          - antall delomraader
    """

    startplass = []
    s = 0
    for n in ntrinn_per_omr:
        startplass.append(s)
        s += n

    rader_pris = []
    rader_mengde = []

    blengde = num_sumtrinn * 4

    with open(filsti, "rb") as f:
        # NB! typenr i denne filen er ikke lik typenr i trinnliste.txt
        typenr = struct.unpack("i" * num_sumtrinn, f.read(4 * num_sumtrinn))

        for uke in range(1, nuke + 1):
            blokk = (uke - 1) * (npenm + 2) + 3
            f.seek(blokk * blengde)
            typek = struct.unpack("i" * num_sumtrinn, f.read(4 * num_sumtrinn))

            blokk = (uke - 1) * (npenm + 2) + 4
            f.seek(blokk * blengde)
            pris = struct.unpack("f" * num_sumtrinn, f.read(4 * num_sumtrinn))

            # finn riktig typenr tilhørende pris og mengde for denne uken
            # (pris og mengde er sortert ihht pris, og ritig plassering ligger i typek-listen)
            i = 0
            typenr_uke = []
            for omrnr, ntrinn_omr in enumerate(ntrinn_per_omr, start=1):
                for __ in range(ntrinn_omr):
                    itypek = typek[i]
                    itypenr = typenr[startplass[omrnr - 1] + itypek - 1]
                    typenr_uke.append(itypenr)
                    i += 1

            i = 0
            for omrnr, ntrinn_omr in enumerate(ntrinn_per_omr, start=1):
                for __ in range(ntrinn_omr):
                    rader_pris.append((uke, omrnr, typenr_uke[i], pris[i]))
                    i += 1

            for tsnitt in range(1, npenm + 1):
                blokk = (uke - 1) * (npenm + 2) + 5 + tsnitt - 1
                f.seek(blokk * blengde)
                mengde = struct.unpack("f" * num_sumtrinn, f.read(4 * num_sumtrinn))

                i = 0
                for omrnr, ntrinn_omr in enumerate(ntrinn_per_omr, start=1):
                    for __ in range(ntrinn_omr):
                        rader_mengde.append((uke, tsnitt, omrnr, typenr_uke[i], mengde[i]))
                        i += 1

    df_pris = pd.DataFrame(rader_pris, columns=["uke", "omrnr", "typenr", "pris"])
    df_mengde = pd.DataFrame(rader_mengde, columns=["uke", "tsnitt", "omrnr", "typenr", "mengde"])

    df = pd.merge(df_pris, df_mengde, on=["uke", "omrnr", "typenr"])

    return df

def les_utveksling(filsti, nfor, hist, jstart, jslutt, npenm):
    rader = []

    with open(filsti, "rb") as f:
        for aar in hist:
            for uke in range(jstart, jslutt + 1):
                for tsnitt in range(1, npenm + 1):
                    utv = struct.unpack(nfor*"f", f.read(nfor*4))
                    rader.append([aar, uke, tsnitt] + list(utv))

    df = pd.DataFrame(rader, columns=["aar", "uke", "tsnitt"] + list(range(1, nfor + 1)))

    return df

def les_prisavsnitt(filsti):
    data = []
    with open(filsti) as f:
        for line in f:

            line = line.replace("\n", "")
            line = line.replace("\r", "")

            strings = line.split(",")

            if len(strings) != 25:
                continue

            strings = [int(s) for s in strings[:-1]]

            data.append(strings)

    rader = []
    uketime = 0
    for ukedag, time_liste in enumerate(data, start=1):
        for dogntime, tsnitt in enumerate(time_liste, start=1):
            uketime += 1
            helg = ukedag in [6, 7]
            rader.append((uketime, ukedag, helg, dogntime, tsnitt))

    kolonner = ["uketime", "ukedag", "helg", "dogntime", "tsnitt"]
    df = pd.DataFrame(rader, columns=kolonner)

    return df

def les_maskenett(filsti, nuke, npenm):
    def clean(string):
        string = string.replace("\n", "")
        string = string.replace("\r", "")
        string = string.replace("'", "")
        string = string.strip()
        return string

    def is_number(string):
        try:
            float(string)
            return True
        except:
            return False

    def is_connection(strings):
        if len(strings) < 4:
            return False
        return (strings[0].isdigit()
                and not strings[1].isdigit()
                and strings[2].isdigit()
                and not strings[3].isdigit())

    def les_linjer_og_tap(tekstlinjer):
        rows = []
        connection_nr = 0

        for line in tekstlinjer:

            strings = line.split(",")
            strings = [clean(s) for s in strings]
            strings = [s for s in strings if s]

            if is_connection(strings):
                connection_nr += 1
                count = 0
                from_nr, from_name, to_nr, to_name = strings[:4]
                continue

            try:
                count += 1
            except:
                continue

            if count not in [1, 2]:
                continue

            elif count == 1:
                tap, from_avgift, to_avgift = strings[:3]
                continue

            if count == 2:
                from_cap, to_cap = strings[1:3]
                row = (connection_nr, from_nr, to_nr, from_cap, to_cap, tap, from_avgift, to_avgift)
                rows.append(row)
                continue

        cols = ["linjenr", "omrnr_fra", "omrnr_til", "kap_fra", "kap_til", "tap", "avgift_fra", "avgift_til"]
        df = pd.DataFrame(rows, columns=cols)

        return df

    def les_avvik(tekstlinjer):
        rows = []
        connection_nr = 0

        for line in tekstlinjer:
            strings = line.split(",")
            strings = [clean(s) for s in strings]
            strings = [s for s in strings if s]

            if len(strings) < 5:
                continue

            if is_connection(strings):
                connection_nr += 1
                from_nr, from_name, to_nr, to_name = strings[:4]
                continue

            if not all([is_number(s) for s in strings[:5]]):
                continue

            tsnitt, start, stop, from_cap, to_cap = strings[:5]

            for week in range(int(start), int(stop) + 1):
                row = (connection_nr, week, tsnitt, from_cap, to_cap)
                rows.append(row)

        cols = ["linjenr", "uke", "tsnitt", "avvik_fra", "avvik_til"]
        df = pd.DataFrame(rows, columns=cols)

        df["linjenr"] = df["linjenr"].astype(int)
        df["uke"] = df["uke"].astype(int)
        df["tsnitt"] = df["tsnitt"].astype(int)
        df["avvik_fra"] = df["avvik_fra"].astype(float)
        df["avvik_til"] = df["avvik_til"].astype(float)

        return df

    with open(filsti) as f:
        tekstlinjer = f.readlines()

    df = les_linjer_og_tap(tekstlinjer)

    avvik = les_avvik(tekstlinjer)

    uke_tsnitt = []
    for uke in range(1, nuke + 1):
        for tsnitt in range(1, npenm + 1):
            uke_tsnitt.append((uke, tsnitt))
    uke_tsnitt = pd.DataFrame(uke_tsnitt, columns=["uke", "tsnitt"])

    # cross join for å få uke, tsnitt inn i df
    # så vi kan koble på avvik
    df["merger"] = 1
    uke_tsnitt["merger"] = 1
    df = df.merge(uke_tsnitt, on="merger")
    del df["merger"]

    tr = []

    for n in range(1,npenm+1):
        tr.append([0,n])
        tr.append([n,n])
    tr = pd.DataFrame(tr, columns=['tsnitt', 'tsnitt_ny'])

    avvik = avvik.merge(tr, on="tsnitt")
    del avvik['tsnitt']
    avvik = avvik.rename(columns={'tsnitt_ny':'tsnitt'})

    df = df.merge(avvik, on=["linjenr", "uke", "tsnitt"], how="left")

    df["avvik_fra"] = df["avvik_fra"].fillna(0.0)
    df["avvik_til"] = df["avvik_til"].fillna(0.0)

    df["linjenr"] = df["linjenr"].astype(int)
    df["omrnr_fra"] = df["omrnr_fra"].astype(int)
    df["omrnr_til"] = df["omrnr_til"].astype(int)

    df["kap_fra"] = df["kap_fra"].astype(float)
    df["kap_til"] = df["kap_til"].astype(float)
    df["avvik_fra"] = df["avvik_fra"].astype(float)
    df["avvik_til"] = df["avvik_til"].astype(float)
    df["avgift_fra"] = df["avgift_fra"].astype(float)
    df["avgift_til"] = df["avgift_til"].astype(float)
    df["tap"] = df["tap"].astype(float)

    return df

def les_brensel(filsti):
    rows = []
    with open(filsti) as f:

        versionsnr, antall_brensler, sluttuke = [int(i) for i in f.readline().split(",")[:3]]

        for brenselnr in range(1, antall_brensler + 1):

            navn, utslipp, energi = f.readline().split(",")[:3]

            navn = navn.replace("'", "").strip()
            utslipp = float(utslipp)
            energi = float(energi)

            uke = 1
            last_uke = 0

            while uke < sluttuke:
                uke, brenselpris, brenselavgift, co2avgift = f.readline().split(",")[:4]

                brenselpris = float(brenselpris)
                brenselavgift = float(brenselavgift)
                co2avgift = float(co2avgift)
                uke = int(uke)
                u = last_uke + 1

                while u <= uke:
                    rows.append((brenselnr, navn, u, utslipp, energi, brenselpris, brenselavgift, co2avgift))
                    u += 1

                last_uke = uke

    cols = ["brenselnr", "brenselnavn", "uke", "utslipp", "energi",
            "brenselpris", "brenselavgift", "co2_avgift"]

    df = pd.DataFrame(rows, columns=cols)

    return df


def les_enmdfil_varmekraft_brensel(path):
    """
    leser enmd-fil og returnerer df med kolonner typenr, brenselnavn

    path - sti til enmd-fil
    """
    rows = []

    kontrakter = []
    brensler = []

    with open(path) as f:

        for line in f:
            if "Typenr, Kategori, Navn, Eget(T)" in line:
                kontrakter.append(line)

            if "Sluttuke, Brenselnavn" in line:
                brensler.append(line)

    varme = [s for s in kontrakter if s.split(",")[1].strip() == "3"]

    assert len(varme) == len(brensler), "lesing av %s gikk ikke som forventet" % path

    for v, b in zip(varme, brensler):
        prefnr = int(v.split(",")[0].strip())
        brensel = b.split(",")[1].replace("'", "").strip()

        rows.append((prefnr, brensel))

    df = pd.DataFrame(rows, columns=["typenr", "brenselnavn"])

    return df

def les_varmekraft_brensel(modellmappe, omr):
    dfs = []
    for __, r in omr.iterrows():
        filsti = os.path.join(modellmappe, "%s.ENMD" % r["omrnavn"])

        rows = []
        kontrakter = []
        brensler = []
        with open(filsti) as f:
            for line in f:
                if "Typenr, Kategori, Navn, Eget(T)" in line:
                    kontrakter.append(line)

                if "Sluttuke, Brenselnavn" in line:
                    brensler.append(line)

        varme = [s for s in kontrakter if s.split(",")[1].strip() == "3"]

        assert len(varme) == len(brensler), "lesing av %s gikk ikke som forventet" % path

        for v, b in zip(varme, brensler):
            prefnr = int(v.split(",")[0].strip())
            brensel = b.split(",")[1].replace("'", "").strip()

            rows.append((prefnr, brensel))

        df = pd.DataFrame(rows, columns=["typenr", "brenselnavn"])

        df["omrnr"] = int(r["omrnr"])

        dfs.append(df)

    df = pd.concat(dfs)

    df = df.reset_index(drop=True)
    df = df[["omrnr", "typenr", "brenselnavn"]]

    return df


def les_minmax(filsti, nverk, nuke, npenm):
    keys = ["maxmag", "minmag", "maxpro", "minpro"]
    out = {k: [] for k in keys}
    out["fastk"] = []

    with open(filsti, "rb") as f:

        for uke in range(1, nuke + 1):

            restr_rows = {k: [uke] for k in keys}
            fastk_rows = [[uke, tsnitt] for tsnitt in range(1, npenm + 1)]

            for omrnr in range(1, nverk + 1):

                values = list(struct.unpack("f" * 4, f.read(4 * 4)))
                for key, value in zip(keys, values):
                    restr_rows[key].append(value)

                values = struct.unpack("f" * npenm, f.read(npenm * 4))
                for idx, value in enumerate(values):
                    fastk_rows[idx].append(value)

            for key in keys:
                out[key].append(restr_rows[key])

            for row in fastk_rows:
                out["fastk"].append(row)

    for key in keys:
        out[key] = pd.DataFrame(out[key], columns=["uke"] + list(range(1, nverk + 1)))

    out["fastk"] = pd.DataFrame(out["fastk"], columns=["uke", "tsnitt"] + list(range(1, nverk + 1)))

    return out
