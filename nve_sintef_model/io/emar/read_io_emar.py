import pandas as pd

def read_io_emar(path):
    "leser emar-fil (ukeverdier) til df"

    def fix_col(s):
        s = s.replace("'", "")
        s = s.replace("(GWh)", "")
        s = s.replace("(MW)", "")
        s = s.replace(".", "")
        s = s.lower()
        s = s.strip()
        return s

    df = pd.read_csv(path)
    df = df.rename(columns={s : fix_col(s) for s in df.columns})
    cols = list(df.columns)
    df = df.reset_index()
    df = df.drop(0)
    del df["minprod"]
    df = df.rename(columns={c : s for s,c in zip(cols, df.columns)})
    df["uke"] = df["uke"].astype(int)
    df["maksmag"] = df["maksmag"].astype(float)
    df["minmag"] = df["minmag"].astype(float)
    df["maksprod"] = df["maksprod"].astype(float)
    df["minprod"] = df["minprod"].astype(float)
    
    return df
