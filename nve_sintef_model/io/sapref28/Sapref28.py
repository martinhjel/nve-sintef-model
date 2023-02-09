import os
import pandas as pd

from .read_io_sapref28 import read_io_sapref28

class Sapref28(object):
    
    def __init__(self, model_dir, ntrinnsum, npenm, nuke, ntrinn, nverk, filename="SAPREF28.SAMK"):
        """
        Bruksomraade: Internfil for overforing av markedsdata som pris og mengde og trinnplassering
        
        model_dir     - sti til modellmappe
        ntrinnsum     - totalt antall trinn i modellen
        ntrinn        - dict[omrnr] = ntrinn
        npenm         - antall tidsavsnitt
        nuke          - antall uker i dataperioden
        nverk         - antall delomraader
        filename      - navn paa sapref28-fil (default SAPREF28.SAMK)
        """
        
        self.path = os.path.join(model_dir, filename)
        
        self.ntrinnsum = ntrinnsum
        self.npenm     = npenm
        self.nuke      = nuke
        self.ntrinn    = ntrinn
        self.nverk     = nverk
        
        self.sumtrinnliste = list(range(1, self.ntrinnsum + 1))
        
        self._output   = None
        self._objects  = dict()
        
    def get_sumtrinn_order_dict(self):
        "dict[uke] = [sumtrinnr sortert i merit-order rekkefolge]"
        name = "sumtrinn_order_dict"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        sumtrinn_dict = self.get_sumtrinn_dict()
        typek = self._output.pop("typek")
        d = dict()
        for i,uke in enumerate(range(1, self.nuke + 1)):
            d[uke] = []
            idx = 0
            for omrnr in range(1, self.nverk + 1):
                for __ in range(self.ntrinn[omrnr]):
                    plassering = typek[i][idx]
                    sumtrinn = sumtrinn_dict[(omrnr, plassering)]                    
                    d[uke].append(sumtrinn)
                    idx +=1
        self._objects[name] = d
        return d

    def get_sumtrinn_dict(self):
        "dict[(omrnr,trinn)] = sumtrinn"
        name = "sumtrinn_dict"
        if name in self._objects:
            return self._objects[name]
        d = dict()
        sumtrinn = 1
        for omrnr in range(1, self.nverk + 1):
            for trinn in range(1, self.ntrinn[omrnr] + 1):
                d[(omrnr,trinn)] = sumtrinn
                sumtrinn += 1
        self._objects[name] = d
        return d
    
    def get_pris(self):
        "Pris paa hvert trinn for alle verk [o/kWh]"
        name = "pris"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        sumtrinn_order_dict = self.get_sumtrinn_order_dict()
        pris = self._output.pop(name)
        rows = []
        for uke, row in enumerate(pris, start=1):
            sumtrinn_order = sumtrinn_order_dict[uke]
            row = [x for x in zip(sumtrinn_order, row)]
            row = sorted(row)
            row = [uke] + [x[1] for x in row]
            rows.append(row)
        cols = ["uke"] + self.sumtrinnliste
        df = pd.DataFrame(rows, columns=cols)
        self._objects[name] = df
        return df
        
        return self._get_df("pris")
    
    def get_mengde(self):
        "Mengde paa hvert trinn for alle verk [GWh]"
        name = "mengde"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        sumtrinn_order_dict = self.get_sumtrinn_order_dict()
        mengde = self._output.pop(name)
        rows = []
        idx = 0
        for uke in range(1, self.nuke + 1):
            sumtrinn_order = sumtrinn_order_dict[uke]
            for tsnitt in range(1, self.npenm + 1):
                row = mengde[idx]
                row = [x for x in zip(sumtrinn_order, row)]
                row = sorted(row)
                row = [uke, tsnitt] + [x[1] for x in row]
                rows.append(row)
                idx += 1
        cols = ["uke", "tsnitt"] + self.sumtrinnliste
        df = pd.DataFrame(rows, columns=cols)
        self._objects[name] = df
        return df
        
    def _set_output(self):
        self._output = read_io_sapref28(self.path, self.ntrinnsum, self.npenm, 
                                        self.nuke, self.ntrinn, self.nverk)