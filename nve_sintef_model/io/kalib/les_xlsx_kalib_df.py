import os
import pandas as pd

def les_xlsx_kalib_df(path):

    """
    leser kalibreringsfakorer for emps fra en xlsx fil til en df
    """

    if not path:
        return pd.DataFrame([], columns=['omrnr', 'tilb', 'form', 'elast'])

    path = os.path.abspath(path)

    df = pd.read_excel(path)

    assert "omrnr" in df.columns, "kolonne 'omrnr' mangler i %s" % path
    assert "tilb"  in df.columns, "kolonne 'tilb' mangler i %s"  % path
    assert "form"  in df.columns, "kolonne 'form' mangler i %s"  % path
    assert "elast" in df.columns, "kolonne 'elast' mangler i %s" % path

    return df
