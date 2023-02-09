# dette skriptet lager en .SCRIPT fil som kan brukes til å slette fastkon i EMPS/Samnett
# laget av A.Roos, EK
# Sist oppdatert: 18.05.2022

def lag_slett_fastkon_script(output_filsti, output_filnavn, fastkon_dict):

    lines = []

    for k in fastkon_dict.keys():

        omrnavn = k

        lines.append('INNDAT')
        lines.append(omrnavn)
        lines.append('LESKOR')
        lines.append('FASTKON')
        lines.append("SLETT")

        for n in fastkon_dict[k]:
            lines.append(str(n))
            lines.append('JA')

        lines.append("")  # uthopp til pref-meny
        lines.append("")  # uthopp til leskorr-meny
        lines.append("")  # uthopp til hoved-meny

        lines.append("filgen")  # lagrer fil
        lines.append(omrnavn)

    lines.append("EXIT")

    script = "\n".join(lines)

    with open(f'{output_filsti}/{output_filnavn}', "w") as f:
        f.write(script)

