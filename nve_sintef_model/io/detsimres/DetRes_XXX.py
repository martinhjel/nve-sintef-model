import pandas as pd

from .read_io_detsimres_xxx import read_io_detsimres_xxx

class DetRes_XXX(object):
    """
    Henter data fra DetRes_xxx.SIMT-fil
    """
    def __init__(self, path, aar, jstart, jslutt, nutv, iverk, npenm, nmodut, nmodsum, hist):
        """
        path          - sti til fil
        aar           - simulert aar
        jstart        - startuke
        jslutt        - sluttuke
        nutv          - antall omraader paa filen
        iverk         - tuple med omrnr paa filen
        npenm         - antall prisavsnitt
        nmodut        - liste med antall moduler in hvert omr
        nmodsum       - totalt antall moduler
        """
        
        self._output   = None
        self._objects  = dict()
        
        self.path      = path
        self.aar       = aar
        self.jstart    = jstart
        self.jslutt    = jslutt
        self.nutv      = nutv
        self.iverk     = iverk
        self.npenm     = npenm
        self.nmodut    = nmodut
        self.nmodsum   = nmodsum
        self.hist      = hist
        
        self._omr_liste    = list(self.iverk)
        self._mod_liste    = list(range(1, nmodsum + 1))
        
        self._dim_col = {"totmag" : "omr",
                         "sumflo" : "omr",
                         "peg"    : "omr",
                         "sumfor" : "omr",
                         "elpump" : "omr",
                         "qpump"  : "omr",
                         "m"      : "modul",
                         "flom"   : "modul",
                         "tilsig" : "modul",
                         "pn"     : "modul",
                         "qt"     : "modul",
                         "qfor"   : "modul"}
        
        self._dim_row = {"totmag" : "uke",
                         "sumflo" : "uke",
                         "peg"    : "tsnitt",
                         "sumfor" : "tsnitt",
                         "elpump" : "tsnitt",
                         "qpump"  : "tsnitt",
                         "m"      : "uke",
                         "flom"   : "uke",
                         "tilsig" : "uke",
                         "pn"     : "tsnitt",
                         "qt"     : "tsnitt",
                         "qfor"   : "tsnitt"}
         
    def get_totmag(self):
        "df[[aar,uke] + omrnr_liste]], Sum magasin (GWh)"
        return self._get_df("totmag")
    
    def get_sumflo(self):
        "df[[aar,uke] + omrnr_liste], Sum flom (GWh)"
        return self._get_df("sumflo")
    
    def get_peg(self):
        "df[[aar,uke,tsnitt] + omrnr_liste], Sum produksjon (GWh)"
        return self._get_df("peg")
    
    def get_sumfor(self):
        "df[[aar,uke,tsnitt] + omrnr_liste], Forbitapping (GWh)"
        return self._get_df("sumfor")
    
    def get_elpump(self):
        "df[[aar,uke,tsnitt] + omrnr_liste], Energi brukt til pumping (GWh)"
        return self._get_df("elpump")

    def get_qpump(self):
        "df[[aar,uke,tsnitt] + omrnr_liste], Pumpet energi (GWh)"
        return self._get_df("qpump")
    
    def get_m(self):
        "df[[aar,uke] + modid_liste], Magasinfylling (Mm3)"
        return self._get_df("m")
    
    def get_flom(self):
        "df[[aar,uke] + modid_liste], Flom (Mm3)"
        return self._get_df("flom")
    
    def get_tilsig(self):
        "df[[aar,uke] + modid_liste], Sum lokaltilsig (Mm3)"
        return self._get_df("tilsig")
    
    def get_pn(self):
        "df[[aar,uke,tsnitt] + modid_liste], Produksjon (MW)"
        return self._get_df("pn")
    
    def get_qt(self):
        "df[[aar,uke,tsnitt] + modid_liste], Stasjonsvannforing (Mm3)"
        return self._get_df("qt")
    
    def get_qfor(self):
        "df[[aar,uke,tsnitt] + modid_liste], Forbitapping (Mm3)"
        return self._get_df("qfor")
        
    def _get_df(self, name):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        rows = self._output.pop(name)
        cols = self._get_cols(name)
        df = pd.DataFrame(rows, columns=cols)
        return df
    
    def _get_cols(self, name):
        if self._dim_col[name] is "omr":
            dim = self._omr_liste
        else:
            dim = self._mod_liste
            
        if self._dim_row[name] is "uke":
            idx = ["aar", "uke"]
        else:
            idx = ["aar", "uke", "tsnitt"]
            
        cols = idx + dim
        
        return cols
        
    def _set_output(self):
        self._output = read_io_detsimres_xxx(self.path, self.aar, self.jstart, 
                                             self.jslutt, self.nutv, self.iverk, 
                                             self.npenm, self.nmodut, self.nmodsum)
