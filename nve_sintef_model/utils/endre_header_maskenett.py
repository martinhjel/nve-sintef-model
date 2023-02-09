import os

def endre_header_maskenett(path, ntimen, path_new=False):
    """
    leser en maskenettfil (path)
    oppdaterer headeren med korrekt info ihht ntimen
    skriver ny maskenettfil til path_new. hvis path_new=False overskrives filen bak path
    """

    if not path_new:
        path_new = path

    with open(path, "r") as f:
        lines = f.readlines()

    ny_header = "'MASKENETT',%s,%s,\n" % (len(ntimen), ",".join(str(i) for i in ntimen))
    lines[0] = ny_header
        
    with open(path_new, "w") as f:
        f.write("".join(lines))
