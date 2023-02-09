
import os
import pandas as pd

from .read_io_trinnliste import read_io_trinnliste

class Trinnliste(object):
    
    def __init__(self, model_dir, filename="trinnliste.txt"):
        """
        Bruksomraade: Fila brukes til aa skrive ut navn, nummer og kategoritype for alle 
        trinn i datamodell Samkjoringsmodellen. 
        Med trinn menes de som er gitt paa Enmd-fila pluss de automatisk genererte. 
        Hensikten med aa generere denne fila er aa hjelpe brukeren i de utskriftapplikasjoner der en kan velge '
        aa presentere ett eller flere trinn.
        """
        
        self.path = os.path.join(model_dir, filename)
        
        self._output = pd.DataFrame()
        
    def get_df(self):
        if self._output.empty:
            self._set_output()
        return self._output
    
    def get_ntrinn_dict(self):
        df = self.get_df()
        d = df.pivot_table(index="omrnr", values="sumtrinnr", aggfunc="count").to_dict()

        # handterer endring pandas.DataFrame.to_dict mellom python 3.4 og 3.6
        if "sumtrinnr" in d.keys():
            d = d["sumtrinnr"]

        return d

    
    def get_ntrinnsum(self):
        df = self.get_df()
        return df["sumtrinnr"].count()
        
    def _set_output(self):
        self._output = read_io_trinnliste(self.path)
