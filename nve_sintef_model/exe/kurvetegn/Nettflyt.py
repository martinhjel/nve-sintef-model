import os
import pandas as pd
import numpy as np

from nve_sintef_model.utils import (get_path_from_dict,
                                     get_dos,
                                     run_sintef)

class Nettflyt(object):
    
    def __init__(self, conf):
        """
        self.model_dir      = get_path_from_dict(conf, "model_dir")
        
        self.path_bin       = get_path_from_dict(conf, "path_bin")
        self.path_hydark    = get_path_from_dict(conf, "path_hydark")
        self.snittnr_liste  = conf["snittnr_liste"]
        self.hist           = conf["hist"]
        self.npenm          = conf["npenm"]
        self.jstart         = conf["jstart"]
        self.jslutt         = conf["jslutt"]
                                   
        self.filnavn_script = "kurvetegn_nettflyt.script"
        self.filnavn_ut     = "kurvetegn_nettflyt.txt"
        
        self.sep = ";"
        
        self.dos = get_dos(self.path_bin, self.path_hydark)
        
        self._output = False
        
        """
        
        self.model_dir      = get_path_from_dict(conf, "model_dir")
        
        self.path_bin       = get_path_from_dict(conf, "path_bin")
        self.path_hydark    = get_path_from_dict(conf, "path_hydark")
        self.snittnr_liste  = conf["snittnr_liste"]
        self.hist           = conf["hist"]
        self.npenm          = conf["npenm"]
        self.jstart         = conf["jstart"]
        self.jslutt         = conf["jslutt"]
                                   
        self.filnavn_script = "kurvetegn_nettflyt.script"
        self.filnavn_ut     = "kurvetegn_nettflyt.txt"
        
        self.sep = ";"
        
        self.dos = get_dos(self.path_bin, self.path_hydark)
        
        self._output = False
        
    def _set_output(self):
        self._lag_kurvetegn_script()
        self._kjor_kurvetegn()
        self._les_resultatfil()
        self._output = True
               
    def get_nettflyt(self):
        if not self._output:
            self._set_output()
        return self._df
    
    def _lag_kurvetegn_script(self):
        lines = []
        lines.append("la")
        lines.append("")
        lines.append("")
        lines.append("a") # alle aar
        lines.append("a") # alle tsnitt
        for snittnr in self.snittnr_liste:
            lines.append("nett")
            lines.append(str(snittnr))
        lines.append("")
        lines.append("")
        lines.append("form")
        lines.append(self.filnavn_ut)
        lines.append("ja") # ja regneark
        lines.append("p") # punktum
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("nei")
        lines.append("")
        lines.append("exit")
        
        self.script = "\n".join(lines)
        
    def _kjor_kurvetegn(self):
        run_sintef(self.dos, "kurvetegn", self.script, self.model_dir, self.filnavn_script)
    
    def _les_resultatfil(self):
        df = pd.read_csv(os.path.join(self.model_dir, self.filnavn_ut), low_memory=False, sep=self.sep, names=self.snittnr_liste + ["slett"])
        del df["slett"]
        idx = pd.MultiIndex.from_product(iterables=[self.hist, 
                                                    range(self.jstart, self.jslutt + 1), 
                                                    range(1, self.npenm + 1)], 
                                         names=["aar", "uke", "tsnitt"])
        df.index = idx
        
        df = df.astype(float, errors="ignore")
        
        df = df.reset_index()

        self._df = df
