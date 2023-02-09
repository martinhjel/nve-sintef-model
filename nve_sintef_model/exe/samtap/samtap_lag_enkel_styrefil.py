
def samtap_lag_enkel_styrefil(path, sekv=False, samnett=False, 
                              navn_script="samtap_lag_enkel_styrefil.script"):

    """
    skriver enkel styrefil for samtap (3x enter) som kan handtere samnett og
    sekvensielle tsnitt
    """

    lines = []
    lines.append("echo. >   %s" % navn_script)
    lines.append("echo. >>  %s" % navn_script)
    lines.append("echo. >>  %s" % navn_script)

    if samnett:
        exe = "samnett"
    else:
        exe = "samtap"

    if sekv:
        lines.append("%s sekv < %s" % (exe, navn_script))
    else:
        lines.append("%s < %s" % (exe, navn_script))

    script = "\n".join(lines)

    with open(path, "w") as f:
        f.write(script)
