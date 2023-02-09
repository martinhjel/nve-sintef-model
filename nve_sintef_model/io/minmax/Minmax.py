import os
import pandas as pd

from .read_io_minmax import read_io_minmax

class Minmax(object):
    """
    Henter data fra MINMAX.SAMK
    """
    
    def __init__(self, model_dir, nverk, nuke, npenm, filename="MINMAX.SAMK"):
        """
        model_dir - sti til modellmappe
        nverk     - antall delomraader i modellen
        nuke      - antall uker i analyseperioden
        npenm     - antall tidsavsnitt paa PRISAVSNITT.DATA
        filename  - navn paa MINMAX-fil (default MINMAX.SAMK)
        """
        
        self.path  = os.path.join(model_dir, filename)
        self.nverk = nverk
        self.nuke  = nuke
        self.npenm = npenm
        
        self._dims      = {"fastk" : ["uke", "tsnitt"]} 
        self._omr_liste = list(range(1, nverk + 1))
        
        self._output  = None
        self._objects = dict()
        
    def get_maxmag(self):
        "df med ovre magasingrense (GWh) for enmagasin i hvert omr"
        return self._get_df("maxmag")
    
    def get_minmag(self):
        "df med nedre magasingrense (GWh) for enmagasin i hvert omr"
        return self._get_df("minmag")
    
    def get_maxpro(self):
        "df med ovre produksjonsgrense (GWh) for enmagasin i hvert omr"
        return self._get_df("maxpro")
    
    def get_minpro(self):
        "df med nedre produksjonsgrense (GWh) for enmagasin i hvert omr"
        return self._get_df("minpro")
    
    def get_fastk(self):
        "df med fastkraft (GWh) (for strategiberegninger) for hvert tidsavsnitt i hvert omr"
        return self._get_df("fastk")
    
    def get_agg(self, name, fokus):
        """
        df[dim + fokusomr_liste] -> verdi for name
        
        name  - 'maxmag', 'minmag', 'maxpro', 'minpro' eller 'fastk'
        dim   - ['uke', 'tsnitt'] hvis 'fastk' ellers ['uke']
        fokus - dict[fokusomr] - > omrnr_liste
        
        summerer langs kolonnene til fokusomr
        """
        dim = self._dims.get(name, ["uke"])
        data = dict()
        for fokusomr, omrnr_liste in fokus.items():
            df = self._get_df(name).copy()
            df = df.set_index(dim)
            df = df[omrnr_liste]
            data[fokusomr] = df.sum(axis=1)
        df = pd.DataFrame(data)
        df = df.reset_index()
        return df
        
    def _get_df(self, name):
        if name in self._objects:
            return self._objects[name]
        
        if not self._output:
            self._set_output()
        
        # uke hvis ikke tsnitt
        dim = self._dims.get(name, ["uke"])
            
        rows = self._output.pop(name)
        cols = dim + self._omr_liste
        
        df = pd.DataFrame(rows, columns=cols)
        
        self._objects[name] = df
        
        return df
    
    def _set_output(self):
        self._output = read_io_minmax(self.path, self.nverk, self.nuke, self.npenm)
