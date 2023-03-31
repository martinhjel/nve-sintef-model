from pathlib import Path
from typing import Union

import pandas as pd


def get_fastkontrakter(path_enmd: Union[str, Path], encoding: str = "iso-8859-1") -> pd.DataFrame:
    """
    Aapner enmd fil og finner alle fastkontrakter og lagrer dem i en
    df som returneres
    """

    if isinstance(path_enmd, str):
        path_enmd = Path(path_enmd)

    if not path_enmd.is_file():
        raise FileNotFoundError(f"The file '{path_enmd}' does not exist or is not a valid file.")

    rows = []
    with path_enmd.open(mode="r", encoding=encoding) as f:
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
    df["navn"] = df["navn"].apply(lambda s: s.replace("'", "").strip())
    df.columns.name = path_enmd.stem

    return df
