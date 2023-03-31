from enum import Enum
from typing import Union, Callable
from pathlib import Path
import pandas as pd
import numpy as np

from .read_io_enmres import read_io_enmres


class EnmresProperty(Enum):
    PKRV="pkrv"
    V="v"
    TOTMAG="totmag"
    FLOM="flom"
    TAPP="tapp"
    TREG="treg"
    TUREG="tureg"
    FASTK="fastk"
    PEG="peg"
    PR="pr"
    ELPUMP="elpump"
    QPUMP="qpump"


class Enmres:
    """
    Retrieves data from ENMRES.DATA
    """

    def __init__(self, file: Union[str, Path]):
        """
        Initializes the Enmres object.

        Parameters
        ----------
        file : Union[str, Path]
            Path to the ENMRES file.
        """

        self._output = None
        self._objects = dict()

        if isinstance(file, str):
            file = Path(file)

        if not file.is_file():
            raise FileNotFoundError(f"The file '{file}' does not exist or is not a valid file.")

        self.path = file

        self._aggfuncs = {
            EnmresProperty.V: np.min,
            EnmresProperty.TOTMAG: np.min,
            EnmresProperty.FLOM: np.sum,
            EnmresProperty.TREG: np.sum,
            EnmresProperty.TUREG: np.sum,
            EnmresProperty.ELPUMP: np.sum,
            EnmresProperty.QPUMP: np.sum,
        }

    def _get_df(self, enmres_property: EnmresProperty) -> pd.DataFrame:
        """
        Returns the data for the specified property.

        Parameters
        ----------
        enmres_property : EnmresProperty
            The EnmresProperty enum value representing the desired data property.

        Returns
        -------
        pd.DataFrame
            The corresponding data as a Pandas DataFrame.
        """

        if enmres_property.value in self._objects:
            return self._objects[enmres_property.value]
        if not self._output:
            self._set_output()
        cols = ["aar", "uke", "tsnitt"] + [enmres_property.value]
        rows = self._output.pop(enmres_property.value)
        df = pd.DataFrame(rows, columns=cols)
        aggf = self._aggfuncs.get(enmres_property)
        if aggf:
            df = df.pivot_table(index=["aar", "uke"], values=enmres_property.value, aggfunc=aggf)
            df = df.reset_index()
        self._objects[enmres_property.value] = df
        return df

    def _set_output(self) -> None:
        """
        Reads the data from the ENMRES file and sets the output dictionary.
        """

        self._output = read_io_enmres(self.path)

    def get_data(self, enmres_property: EnmresProperty) -> pd.DataFrame:
        """
        Returns the data for the specified property.

        Parameters
        ----------
        enmres_property : EnmresProperty
            The EnmresProperty enum value representing the desired data property.

        Returns
        -------
        pd.DataFrame
            The corresponding data as a Pandas DataFrame.
        """

        return self._get_df(enmres_property)

    def __getattr__(self, enmres_property_value: str) -> Callable[[], pd.DataFrame]:
        """
        Returns a method that retrieves the data for the specified property.

        Parameters
        ----------
        enmres_property_value : str
            The EnmresProperty enum value representing the desired data property.

        Returns
        -------
        Callable[[], pd.DataFrame]
            A method that returns the corresponding data as a Pandas DataFrame when called.
        """
        def get_enum(value):
            for i in EnmresProperty:
                if i.value == value:
                    return i
            return None
        enmres_property = get_enum(enmres_property_value)
        if enmres_property:
            return self.get_data(enmres_property)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{enmres_property_value}'")