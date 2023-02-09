import os
import pandas as pd

from .read_io_detsimres_head import read_io_detsimres_head

class DetRes_Head(object):
    """
    Henter data fra DetRes_Head.SIMT
    """
    
    # TODO: hent resterende objekter
    # endre fra self._output[name] til get_<name>() 
    
    def __init__(self, model_dir, detsimres_dir="DetSimRes", filename="DetRes_Head.SIMT"):
        """
        model_dir     - sti til modellmappe
        detsimres_dir - Navn paa detsimres-mappe
        filename      - Navn paa DetRes_Head-fil
        """
        self._output  = None
        self._objects = dict()
        
        self.path = os.path.join(model_dir, detsimres_dir, filename)
        
    def get_jstart(self):
        "startuke"
        return self._get_param("jstart")
        
    def get_jslutt(self):
        "sluttuke"
        return self._get_param("jslutt")
        
    def get_nutv(self):
        "antall delomraader som detaljsimuleres"
        return self._get_param("nutv")
        
    def get_iverk(self):
        "tuple med omrnr som har vannkraft"
        return self._get_param("iverk")
        
    def get_npenm(self):
        "antall prisavsnitt"
        return self._get_param("npenm")
        
    def get_nmodut(self):
        "liste med antall moduler i hver omraade"
        return self._get_param("nmodut")
        
    def get_nmodsum(self):
        "totalt antall moduler i alle omraader"
        return self._get_param("nmodsum")
        
    def get_hist(self):
        "tuple med simulerte aar"
        return self._get_param("hist")
        
    def get_ntimen(self):
        "tuple med antall timer for hvert tidsavsnitt"
        return self._get_param("ntimen")
    
    def get_modid_df(self):
        "df[modid,omrnr,modnr]"
        return self._get_modid_df()
    
    def get_omrnr_modid_map(self):
        "dict[omrnr] -> modid_liste"
        return self._get_omrnr_modid_map()
    
    def get_modnavn_map(self):
        "dict[modid] -> modnavn"
        return self._get_modnavn_map()
    
    def get_topo_st_map(self):
        "dict[modid_fra] -> modid_til (stasjonsvannforing)"
        return self._get_topo_map("topo_st")
        
    def get_topo_forb_map(self):
        "dict[modid_fra] -> modid_til (forbitappet vann)"
        return self._get_topo_map("topo_forb")
        
    def get_topo_flom_map(self):
        "dict[modid_fra] -> modid_til (flomvann)"
        return self._get_topo_map("topo_flom")
    
    def get_internid_modid_map(self):
        "dict[internid] -> modid, hvor internid=(omrnr,modindex)"
        return self._get_internid_modid_map()
    
    def _get_modid_df(self):
        key = "_get_modid_df"
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        modid = 1
        rows = []
        for i,omrnr in enumerate(self.get_iverk()):
            for modnr in self._output["modnr"][i]:
                rows.append((modid, omrnr, modnr))
                modid += 1
        cols = ["modid", "omrnr", "modnr"]
        df = pd.DataFrame(rows, columns=cols)
        self._objects[key] = df
        return df
    
    def _get_omrnr_modid_map(self):
        key = "_get_omrnr_modid_map"
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        d = dict()
        modid = 1
        for i,omrnr in enumerate(self.get_iverk()):
            d[omrnr] = []
            for __ in self._output["modnr"][i]:
                d[omrnr].append(modid)
                modid += 1
        self._objects[key] = d
        return d
    
    def _get_modnavn_map(self):
        key = "_get_modnavn_map"
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        d = dict()
        modid = 1
        for __,names in enumerate(self._output["modulnavn"]):
            for bts in names:
                d[modid] = self._decode(bts)
                modid += 1
        self._objects[key] = d
        return d
    
    def _get_internid_modid_map(self):
        key = "_get_internid_modid_map"
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        iverk = self.get_iverk()
        d = {omrnr : {} for omrnr in iverk}
        modid = 1
        for i,omrnr in enumerate(iverk):
            for j,modnr in enumerate(self._output["modnr"][i], start=1):
                d[omrnr][j] = modid
                modid += 1
        self._objects[key] = d
        return d
    
    def _get_topo_map(self, name):
        key = ("_get_topo_map", name)
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        id_map = self.get_internid_modid_map()
        d = dict()
        for omrnr, intern_liste in enumerate(self._output[name], start=1):
            for i,j in enumerate(intern_liste, start=1):
                modid_fra = id_map[omrnr].get(i, 0)
                modid_til = id_map[omrnr].get(j, 0)
                d[modid_fra] = modid_til 
        self._objects[key] = d
        return d
    
    def _get_param(self, name):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        p = self._output.pop(name)
        self._objects[name] = p
        return p
    
    def _set_output(self):
        self._output = read_io_detsimres_head(self.path)
        
    def _decode(self, bts, encoding="cp865", mode="ignore"):
        return bts.decode(encoding, mode)
        
    
