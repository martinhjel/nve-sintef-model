import re

def get_filnavn_prisrekke(enmd_str):

    """
    Gitt innholdet (str) i en enmd-fil brukes regex til aa soke frem
    navnet paa en prisrekkefil (.PRI)

    returnerer False hvis man ikke finner noe 
    """

    pattern = "(\w*\.[Pp][Rr][Ii])"

    m = re.search(pattern, enmd_str)
    if m:
        filename = m.group()
    else:
        filename = False

    return filename