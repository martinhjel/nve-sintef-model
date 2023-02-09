import os
import pandas as pd

# dette skriptet lager en .SCRIPT fil som kan brukes til å opprette nye fastkon-kontrakter i EMPS/Samnett (med mengde 0 GWh)
# laget av A.Roos, EK
# Sist oppdatert: 18.05.2022
# datatype = forbruk/produksjon (det er ulik kommandorekkefølge for disse to)
# df til forbruk skal inneholde kolonner = [omrnavn, fastkon_nr, kontraktnavn, prisavh_eksp_beskrivelse, lastprofil_nr, effektprofil_nr, tempavhprofil_nr, temperaturserie, vektfaktor]

def skriv_lag_fastkon_script(output_filsti, output_filnavn, df, datatype):

    if datatype == 'forbruk':

        lines = []
        for omr in df['omrnavn'].unique():

            lines.append('INNDAT')
            lines.append(omr)
            lines.append('LESKOR')
            lines.append('FASTKON')

            for n, r in df[df['omrnavn'] == omr].iterrows():

                kontr_nr = int(r["fastkon_nr"])
                kontr_navn = r["kontraktnavn"]
                lastprofil = int(r["lastprofil_nr"])
                effektprofil = r["effektprofil_nr"]
                tempavhprofil = r["tempavhprofil_nr"]
                prisavh = r['prisavh_eksp_beskrivelse']
                tempserie1 = r["temperaturserie1"]
                vektfaktor1 = r["vektfaktor1"]
                tempserie2 = r["temperaturserie2"]
                vektfaktor2 = r["vektfaktor2"]
                # tempserie3 = r["temperaturserie3"]
                # vektfaktor3 = r["vektfaktor3"]
                # tempserie4 = r["temperaturserie4"]
                # vektfaktor4 = r["vektfaktor4"]

                # Lager kommandoer:
                lines.append(str(kontr_nr))
                lines.append("FORPL")
                lines.append(str(kontr_navn))
                lines.append("TOTAL")
                lines.append('1, 52, 0, 0')  # pris/mengde periode 1
                lines.append('53, 104, 0, 0')  # pris/mengde periode 2
                lines.append('105, 156, 0, 0')  # pris/mengde periode 3
                lines.append('JA')
                lines.append(str(lastprofil))
                lines.append(str(int(effektprofil)))

                # hvis temperaturavhengig forbruk - endring av temperaturavhengighet
                if pd.isnull(tempavhprofil) == False:
                    lines.append('TA')
                    lines.append(str(tempserie1))
                    lines.append('BEHOLD')
                    lines.append(str(vektfaktor1))
                    if pd.isnull(tempserie2) == False:
                        lines.append(str(tempserie2))
                        lines.append('BEHOLD')
                        lines.append(str(vektfaktor2))
                        # if pd.isnull(tempserie3) == False:
                        #     lines.append(str(tempserie3))
                        #     lines.append('BEHOLD')
                        #     lines.append(str(vektfaktor3))
                        #     if pd.isnull(tempserie4) == False:
                        #         lines.append(str(tempserie4))
                        #         lines.append('BEHOLD')
                        #         lines.append(str(vektfaktor4))
                    lines.append('S') #uthopp
                    lines.append(str(int(tempavhprofil)))
                    lines.append('') #uthopp

                # hvis prisavhengig forbruk - endring av prisavhengighet
                if pd.isnull(prisavh) == False:
                    lines.append('PA')
                    lines.append('EKSP') # eksponentiel beskrivelse
                    lines.append(str(prisavh))
                    lines.append('JA')

                lines.append("") # uthopp

            lines.append("")  # uthopp
            lines.append("")  # uthopp til meny for generering av markedsdata
            lines.append("FILGEN")  # lagre fil
            lines.append("")

        lines.append("EXIT")  # avslutt enmdat

        script = "\n".join(lines)

        with open(f'{output_filsti}/{output_filnavn}', "w") as f:
            f.write(script)


# denne brukes til testing av skriptet
if __name__ == '__main__':
    df = pd.read_excel(f'output/NVE_basis_TESTalro/EMPS_kontraktliste_EXEMPEL.xlsx')
    df = df.loc[df['empskategori'] != 'prefdat_enkeltkontrakt']
    output_filsti = os.path.join('', 'lag_fastkon_TEST.SCRIPT')
    skriv_lag_fastkon_script(output_filsti, df, datatype='forbruk')