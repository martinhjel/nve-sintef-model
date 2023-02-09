import os
import pandas as pd
import numpy  as np

from .read_io_enmres import read_io_enmres

class Enmres(object):
    """
    Henter data fra ENMRES.DATA
    """
    
    # TODO: Implementer resten av objektene i self._output
    
    def __init__(self, model_dir, filename="ENMRES.DATA"):
        """
        model_dir - sti til modellmappe
        filename  - navn paa ENMRES-fil
        """
        
        self._output  = None
        self._objects = dict()
        
        self.path = os.path.join(model_dir, filename)
        
        self._aggfuncs = {"v"       : np.min, 
                          "totmag"  : np.min,
                          "flom"    : np.sum,
                          "treg"    : np.sum,
                          "tureg"   : np.sum,
                          "elpump"  : np.sum,
                          "qpump"   : np.sum}
        
    def get_pkrv(self):
        "df[aar,uke,tsnitt] Kraftverdi"
        return self._get_df("pkrv")
        
    def get_v(self):
        "df[aar,uke] Vannverdi"
        return self._get_df("v")
    
    def get_totmag(self):
        "df[aar,uke] Magasininnhold i enmagasinmodellen (GWh)"
        return self._get_df("totmag")
    
    def get_flom(self):
        "df[aar,uke] Flom i enmagasinmodellen"
        return self._get_df("flom")
    
    def get_tapp(self):
        "df[aar,uke,tsnitt] Tapping fra magasinet"
        return self._get_df("tapp")
    
    def get_treg(self):
        "df[aar,uke] Regulert tilsig"
        return self._get_df("treg")
    
    def get_tureg(self):
        "df[aar,uke] Uregulert tilsig"
        return self._get_df("tureg")
    
    def get_fastk(self):
        "df[aar,uke,tsnitt] Fastkraft (GWh)"
        return self._get_df("fastk")
    
    def get_peg(self):
        "df[aar,uke,tsnitt] Sum produksjon (- ELPUMP)"
        return self._get_df("peg")
    
    def get_pr(self):
        "df[aar,uke,tsnitt] Mengde kjop/salg"
        return self._get_df("pr")
    
    def get_elpump(self):
        "df[aar,uke] Energi brukt til pumping"
        return self._get_df("elpump")

    def get_qpump(self):
        "df[aar,uke] Energi vunnet ved pumping"
        return self._get_df("qpump")
    
    def _get_df(self, name):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        cols = ["aar", "uke", "tsnitt"] + [name]
        rows = self._output.pop(name)
        df = pd.DataFrame(rows, columns=cols)
        aggf = self._aggfuncs.get(name)
        if aggf:
            df = df.pivot_table(index=["aar", "uke"], values=name, aggfunc=aggf)
            df = df.reset_index()
        self._objects[name] = df
        return df
    
    def _set_output(self):
        self._output = read_io_enmres(self.path)
