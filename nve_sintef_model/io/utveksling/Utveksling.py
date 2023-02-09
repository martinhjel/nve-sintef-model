import os
import pandas as pd

from .read_io_utveksling import read_io_utveksling

class Utveksling(object):
    """
    Henter data fra UTVEKSLING.SAMK
    """
    
    def __init__(self, model_dir, nfor, hist, jstart, jslutt, npenm, filename="UTVEKSLING.SAMK"):
        """
        model_dir - sti til modellmappe
        nfor      - antall forbindelser i maskenett.data
        hist      - liste med simulerte aar
        jstart    - startuke
        jslutt    - sluttuke
        npenm     - antall tidsavsnitt
        filename  - navn paa utveksling-fil (default UTVEKSLING.SAMK)
        """
        self.path = os.path.join(model_dir, filename)
        
        self.nfor   = nfor
        self.hist   = hist
        self.jstart = jstart
        self.jslutt = jslutt
        self.npenm  = npenm
        
        self.linjenr_liste = list(range(1, self.nfor + 1))
        
        self._output  = None
        self._objects = dict()
        
    def get_utv(self):
        key = "get_utv"
        if key in self._objects:
            return self._objects[key]
        rows = read_io_utveksling(self.path, self.nfor, self.hist, self.jstart, self.jslutt, self.npenm)
        cols = ["aar", "uke", "tsnitt"] + self.linjenr_liste
        df = pd.DataFrame(rows, columns=cols)
        self._objects[key] = df
        return df
    
    def get_linje_nettoeksport(self, ntimen, uke, gwh):
        
        key = ("get_linje_nettoeksport", ntimen, uke, gwh)
        if key in self._objects:
            return self._objects[key]
        
        
        df = self.get_utv().copy()
        
        if uke:
            # mw tsnitt til mw uke
            ts_map = {ts : n for ts,n in enumerate(ntimen, start=1)}
            df["ntimen"] = df["tsnitt"].apply(lambda ts : ts_map[ts])
            df = df.set_index(["aar", "uke", "tsnitt"])
            df = df.multiply(df["ntimen"]/168, axis="index")
            df = df.reset_index()
            df = df.pivot_table(index=["aar", "uke"], values=self.linjenr_liste, aggfunc="sum")
            
            # mw/uke til gwh
            if gwh:
                df = df*168/1000 
            df = df.reset_index()
            
        else:
            if gwh:
                # mw/tsnitt til gwh
                ts_map = {ts : n for ts,n in enumerate(ntimen, start=1)}
                df["ntimen"] = df["tsnitt"].apply(lambda ts : ts_map[ts])
                df = df.set_index(["aar", "uke", "tsnitt"])
                df = df.multiply(df["ntimen"], axis="index")
                del df["ntimen"]
                df = df/1000 
                df = df.reset_index()
                
        self._objects[key] = df
        
        return df
    
    def get_omr_nettoeksport(self, fokus, ntimen, maskenett, uke, gwh):
        
        fokus_keys   = tuple(sorted(list(fokus.keys())))
        fokus_values = tuple([tuple(sorted(v)) for v in fokus.values()])
        
        key = ("get_omr_nettoeksport", fokus_keys, fokus_values, ntimen, uke, gwh)
        if key in self._objects:
            return self._objects[key]


        df = self.get_linje_nettoeksport(ntimen, uke, gwh).copy()
        
        if uke:
            idx = ["aar", "uke"]
        else:
            idx = ["aar", "uke", "tsnitt"]
            
        data = dict()
        for navn, omrnr_liste in fokus.items():
            med_liste, snu_liste = maskenett.get_agg_lister(tuple(omrnr_liste))
            c = df.copy()
            c = c.set_index(idx)
            c = c[med_liste]
            c[snu_liste] = c[snu_liste]*-1
            c = c.sum(axis=1)
            data[navn] = c
        
        df = pd.DataFrame(data)
        df = df.reset_index()
        
        self._objects[key] = df
        
        return df