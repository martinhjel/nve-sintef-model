import os


# dette skriptet lager en .SCRIPT fil som kan brukes til å oppdatere forbuksdata for prefdat- og fastkon-kontrakter i EMPS/Samnett
# laget av H.Endresen & A.Roos, EK
# Sist oppdatert: 16.05.2022
# df skal inneholde kolonner = [empsområdenavn, emps_prefdat_kontraktnummer/emps_fastkon_kontraktsnummer, forbruk] (årsforbruk i gitt år)

def skriv_oppdater_forb_script(output_filsti, output_filnavn, df, typekon):
    '''
    Denne funksjonen lager .SCRIPT fil som kan brukes til å oppdatere forbuksdata for prefdat-, fastkon eller begge kntraktstyper i EMPS/Samnett.

    :param str output_filsti: stien der output fil skal ligge
    :param str output_filnavn: navn på output fil
    :param pandas.DataFrame df: dataframe med forbruk per år
    :param str typekon: {'begge', 'prefdat', 'fastkon'}
    :return: tekstlinjer og textfil som lagres i lokasjon definert av output sti

    **Kolonner i dataframe:**
        Name: empsområdenavn, dtype: str

        Name: kontraktnummer, dtype: int64

        Name: forbruk, dtype: float64
    '''

    lines = []

    if typekon == 'prefdat':

        for n, row in df.iterrows():
            omrade = str(row['empsområdenavn'])
            kontraktnummer = str(int(row['prefdat_kontraktnummer']))
            mengde_GWh = str(row['forbruk'])

            # Lager kommandoer:
            lines.append("INNDAT")
            lines.append(omrade)
            lines.append("LESKOR")
            lines.append("PREFDAT")
            lines.append(kontraktnummer)
            lines.append("KAP")  # endring av mengde i hver periode
            lines.append("52")  # periode 1
            lines.append(mengde_GWh)
            lines.append("104")  # periode 2
            lines.append(mengde_GWh)
            lines.append("156")  # periode 3
            lines.append(mengde_GWh)
            lines.append("")
            lines.append("")
            lines.append("")
            lines.append("FILGEN")
            lines.append("")

    elif typekon == 'fastkon':

        for n, row in df.iterrows():
            omrade = str(row['empsområdenavn'])
            kontraktnummer = str(int(row['fastkon_kontraktnummer']))
            mengde_GWh = str(row['forbruk'])
            pris = ""

            # Leager kommandoer:
            lines.append("INNDAT")
            lines.append(omrade)
            lines.append("LESKOR")
            lines.append("FASTKON")
            lines.append(kontraktnummer)
            lines.append("MP")  # endring av priser og mengder
            lines.append("1")  # periode 1
            lines.append("52")
            lines.append(mengde_GWh)
            lines.append(pris)
            lines.append("53")  # periode 2
            lines.append("104")
            lines.append(mengde_GWh)
            lines.append(pris)
            lines.append("105")  # periode 3
            lines.append("156")
            lines.append(mengde_GWh)
            lines.append(pris)  #
            lines.append("JA")  # er data o.k.?
            lines.append("")
            lines.append("")
            lines.append("")
            lines.append("FILGEN")
            lines.append("")

    lines_final = lines.copy()
    lines_final.append("EXIT")  # avslutt enmdat

    script = "\n".join(lines_final)
    with open(f'{output_filsti}/{output_filnavn}', "w") as f:
        f.write(script)

    return lines


# denne brukes til testing av skriptet
if __name__ == '__main__':
    import pandas as pd

    nettap = 'samnett'
    aar = 2030
    typekon = 'fastkon'
    df = pd.read_excel(
        r'X:\Prosjekter\2022_HAVNETT\Modellinput\Oppdatering_forbruk\output\TESTalro\EMPS_data_TESTalro.xlsx')
