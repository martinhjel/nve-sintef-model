import pandas as pd

def les_kombsnitt_kapasiteter(path):
    """
    leser snittnr, omrnavn_fra, omrnavn_til, snittkap_fra, snittkap_til 
    fra kombsnitt.dat til en df
    """

    read_next = False
    snittnr = 0
    rows = []
    with open(path) as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.replace("\r", "")
            strings = line.split(",")

            if not strings:
                continue
            if strings[0].startswith("'"):
                snittnr += 1
                read_next = True
                navn_fra, navn_til = [s.replace("'", "") for s in strings[:2]]
                continue

            if read_next:
                kap_fra, kap_til = [float(s) for s in strings[1:3]]
                read_next = False
                rows.append([snittnr, navn_fra, navn_til, kap_fra, kap_til])
                continue

    df = pd.DataFrame(rows, columns=["snittnr", "omrnavn_fra", "omrnavn_til", "snittkap_fra", "snittkap_til"])
    
    return df
