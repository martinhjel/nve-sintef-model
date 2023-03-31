from pathlib import Path
from typing import Union

import pandas as pd


def les_brensel_enmd_fil(path_enmd: Union[str, Path], encoding: str = "iso-8859-1") -> pd.DataFrame:
    """
    leser enmd-fil og returnerer df med kolonner typenr, brenselnavn

    path_enmd - sti til enmd-fil
    """
    rows = []

    kontrakter = []
    brensler = []

    if isinstance(path_enmd, str):
        path_enmd = Path(path_enmd)

    if not path_enmd.is_file():
        raise FileNotFoundError(f"The file '{path_enmd}' does not exist or is not a valid file.")

    with path_enmd.open(mode="r", encoding=encoding) as f:
        for line in f:
            if "Typenr, Kategori, Navn, Eget(T)" in line:
                kontrakter.append(line)

            if "Sluttuke, Brenselnavn" in line:
                brensler.append(line)

    varme = [s for s in kontrakter if s.split(",")[1].strip() == "3"]

    assert len(varme) == len(brensler), "lesing av %s gikk ikke som forventet" % path_enmd

    for v, b in zip(varme, brensler):
        prefnr = int(v.split(",")[0].strip())
        brensel = b.split(",")[1].replace("'", "").strip()

        rows.append((prefnr, brensel))

    df = pd.DataFrame(rows, columns=["typenr", "brenselnavn"])
    df.columns.name = path_enmd.stem

    return df
