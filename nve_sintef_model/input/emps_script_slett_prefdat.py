# dette skriptet lager en .SCRIPT fil som kan brukes til å slette prefdat i EMPS/Samnett
# laget av A.Roos & H.Endresen, EK
# Sist oppdatert: 16.05.2022

#TODO: dette skriptet bør på sikt flyttes til nve_modell. Dette er dupliserende skript til det som ligger i oppdatere_forbruk.

def skriv_slett_prefdat_script(output_filsti, output_filnavn, prefdat_dict):

    lines = []

    for k in prefdat_dict.keys():

        omrnavn = k

        lines.append('INNDAT')
        lines.append(omrnavn)
        lines.append('LESKOR')
        lines.append('PREFDAT')
        lines.append("SL")

        for n in prefdat_dict[k]:
            lines.append(str(n))

        lines.append("") # uthopp til pref-meny
        lines.append("") # uthopp til leskorr-meny
        lines.append("") # uthopp til hoved-meny

        lines.append("filgen") # lagre
        lines.append(omrnavn)

    lines.append("EXIT")

    script = "\n".join(lines)

    with open(f'{output_filsti}/{output_filnavn}', "w") as f:
        f.write(script)
        



