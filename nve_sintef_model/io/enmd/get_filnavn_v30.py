import re

def get_filnavn_v30(enmd_str):

    """
    Gitt innholdet (str) i en enmd-fil brukes regex til aa soke frem
    navnet paa en .V30 fil

    returnerer False hvis man ikke finner noe 
    """

    pattern = "(\w*\.[Vv]30)"

    m = re.search(pattern, enmd_str)
    if m:
        filename = m.group()
    else:
        filename = False

    return filename