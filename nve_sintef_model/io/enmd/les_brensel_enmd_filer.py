import os
import pandas as pd

from .les_brensel_enmd_fil import les_brensel_enmd_fil

def les_brensel_enmd_filer(model_dir, omr):
    """
    returnerer df med omrnr, prefnr, brenselnavn
      leser enmd filer i model_dir for alle omrnavn i omr

    omr - df med omrnr, omrnavn
    model_dir - sti til mappe med enmd-filer
    """

    dfs = []

    for __, r in omr.iterrows():

        path = os.path.join(model_dir, "%s.ENMD" % r["omrnavn"])

        df = les_brensel_enmd_fil(path)

        df["omrnr"]   = int(r["omrnr"])

        dfs.append(df)

    df = pd.concat(dfs)

    df = df.reset_index(drop=True)
    df = df[["omrnr", "typenr", "brenselnavn"]]

    return df




