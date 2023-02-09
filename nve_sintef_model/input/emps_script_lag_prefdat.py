import os
import pandas as pd

#TODO: dette skriptet bør på sikt flyttes til nve_modell. Dette er dupliserende skript til det som ligger i oppdatere_forbruk.

# dette skriptet lager en .SCRIPT fil som kan brukes til å opprette nye prefdat-kontrakter i EMPS/Samnett for forbruk eller termisk produksjon
# laget av A.Roos, EK
# Sist oppdatert: 18.05.2022
# datatype = forbruk/produksjon (det er ulik kommandorekkefølge for disse to)
# df til forbruk skal inneholde kolonner = [omrnavn, prefdat_nr, kontraktnavn, prefdat_pris, lastprofil_nr, effektprofil_nr]

def skriv_lag_prefdat_script(output_filsti, output_filnavn, df, datatype, kap_dict, antall_aar):

    # datatype = forbruk eller termisk

    if datatype == 'forbruk':

        lines = []
        for omr in df['omrnavn'].unique():

            lines.append('INNDAT')
            lines.append(omr)
            lines.append('LESKOR')
            lines.append('PREFDAT')

            for n, r in df[df['omrnavn'] == omr].iterrows():

                prefnavn     = r["kontraktnavn"]
                prefnr       = r["prefdat_nr"]
                pris         = r["prefdat_pris"]
                lastprofil   = r["lastprofil_nr"]
                effprofil    = r["effektprofil_nr"]

                lines.append(str(int(prefnr)))
                lines.append("REFER")
                lines.append("SALG")
                lines.append(str(prefnavn))
                lines.append("TOTAL")
                lines.append('-1') # ingen brensel
                lines.append('156') # sluttuke
                lines.append(str(pris))
                lines.append('156') # sluttuke
                lines.append('0') # mengde GWh
                lines.append(str(int(lastprofil))) # lastprofil
                lines.append("EP") # endring av effektprofil
                lines.append(str(int(effprofil)))
                lines.append('') # data ok.

            lines.append("") # uthopp til leskorr-meny
            lines.append("") # uthopp til hoveddata-meny

            lines.append("FILGEN") # lagre fil
            lines.append("")

        lines.append("EXIT") # avslutt enmdat

        script = "\n".join(lines)

        with open(f'{output_filsti}/{output_filnavn}', "w") as f:
            f.write(script)


    elif datatype == 'termisk':

        lines = []
        for omrnavn in df.omrnavn.unique():

            lines.append("I,%s,L,P" % omrnavn)

            for __, r in df[df.omrnavn == omrnavn].iterrows():

                prefnavn = r["prefnavn"]
                prefnr = r["prefnr"]
                brenselnr = r["brenselnr"]
                voc = r["voc"]
                eff = r["full_eff"]
                effektprofil = 1
                tilgjengelighet = 100

                eff *= 100
                assert eff >= 0 and eff <= 100

                lines.append(str(prefnr))
                lines.append("varme")
                lines.append(prefnavn)
                lines.append("total")
                lines.append(str(brenselnr))
                lines.append(str(voc))
                lines.append(str(eff))
                lines.append(str(effektprofil))
                lines.append("profil")

                sluttuke = 0
                for __ in range(antall_aar):
                    for uke in range(1, 53):
                        sluttuke += 1
                        kap = kap_dict[(omrnavn, prefnr)][uke]

                        lines.append("%d %4.2f" % (sluttuke, kap))

                lines.append(str(tilgjengelighet))
                lines.append("")  # uthopp til pref-meny

            lines.append("")  # uthopp til leskorr-meny
            lines.append("")  # uthopp til hoveddata-meny

            lines.append("filgen")  # lagre fil
            lines.append(str(omrnavn))  # lagre fil

        lines.append("exit")  # avslutt enmdat

        script = "\n".join(lines)

        with open(f'{output_filsti}/{output_filnavn}', "w") as f:
            f.write(script)

    else:
        print('Feil spesifikasjon av datatype for funksjon skriv_lag_prefdat_script.py. Skript stoppet.')
        exit()


# denne brukes til testing av skriptet
if __name__ == '__main__':
    antall_aar_data = ['2021', '2025', '2030', '2040']
    forb_df_sti = r'X:\Prosjekter\2022_HAVNETT\Modellinput\Oppdatering_forbruk\output\Basis_NVE22'
    forb_df_fil = 'mal_kontraktliste.xlsx'
    forb_df = pd.read_excel(os.path.join(forb_df_sti, forb_df_fil))
    output_filsti = os.path.join(forb_df_sti, 'lag_prefdat_forb.SCRIPT')
    skriv_lag_prefdat_script(output_filsti, forb_df, datatype = 'forbruk')