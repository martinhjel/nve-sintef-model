from pathlib import Path
from typing import Union

import pandas as pd

def read_io_emar(path_emar: Union[str, Path]) -> pd.DataFrame:
    """
    Leser emar-fil (ukeverdier) til df.

    Parameters
    ----------
    path_emar : Union[str, Path]
        The file path of the EMAR file to read, either as a string or a
        pathlib.Path object.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the data from the EMAR file.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist or is not a valid file.

    Examples
    --------
    >>> emar_df = read_io_emar("path/to/emar_file.emar")
    >>> emar_df.head()
    """

    if isinstance(path_emar, str):
        path_emar = Path(path_emar)

    if not path_emar.is_file():
        raise FileNotFoundError(f"The file '{path_emar}' does not exist or is not a valid file.")

    def fix_col(s):
        s = s.replace("'", "")
        s = s.replace("(GWh)", "")
        s = s.replace("(MW)", "")
        s = s.replace(".", "")
        s = s.lower()
        s = s.strip()
        return s

    df = pd.read_csv(path_emar)
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
    df.columns.name = path_emar.stem
    df.set_index("uke", inplace=True)

    return df
