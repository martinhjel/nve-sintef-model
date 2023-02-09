import pandas as pd

def read_io_trinnliste(path):
    "path - sti til trinnliste.txt"
    sumtrinnr = 1
    rows = []
    with open(path, "r", encoding="ascii", errors="surrogateescape") as f:
        antall_omr = int(f.readline().split(",")[0])
        for omrnr in range(1, antall_omr + 1):
            omrnr, omrnavn = f.readline().split(",")[:2]
            omrnr = int(omrnr)
            omrnavn = omrnavn.replace("'", "")
            omrnavn = omrnavn.strip()
            antall_trinn = int(f.readline().split(",")[0])
            for i in range(antall_trinn):
                typenr, navn, katnr, katnavn = f.readline().split(",")[:4]
                typenr = int(typenr)
                katnr = int(katnr)
                navn = navn.replace("'", "").strip()
                katnavn = katnavn.replace("'", "").strip()
                rows.append([sumtrinnr, omrnr, omrnavn, typenr, navn, katnr, katnavn])
                sumtrinnr += 1
    cols = ["sumtrinnr", "omrnr", "omrnavn", "typenr", "navn", "katnr", "katnavn"]
    return pd.DataFrame(rows, columns=cols)
