import pandas as pd

def get_fastkontrakter(path_enmd):

    """
    Aapner enmd fil og finner alle fastkontrakter og lagrer dem i en 
    df som returneres
    """
    rows = []
    with open(path_enmd) as f:
        for line in f:
            if "* Dellastnr, Kategori, Navn, Eget(T)" in line:
                ss = line.split(",")
                ss = [s.strip() for s in ss][:4]
                if ss[0] == "99":
                    break
                rows.append(ss)
    df = pd.DataFrame(rows, columns=["fastnr", "katnr", "navn", "eget"])
    df["fastnr"] = df["fastnr"].astype(int)
    df["katnr"] = df["katnr"].astype(int)
    df["navn"] = df["navn"].apply(lambda s : s.replace("'", "").strip())
    return df

