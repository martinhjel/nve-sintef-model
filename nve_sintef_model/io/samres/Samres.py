# coding=cp1252

import os
import pandas as pd

from .read_io_samres import read_io_samres

class Samres(object):
    """
    Henter data fra SAMRES.SAMK
    """
    
    def __init__(self, model_dir, filename="SAMRES.SAMK"):
        """
        model_dir - sti til modellmappe
        filename  - navn på samres-fil (default SAMRES.SAMK)
        """
        
        self.path = os.path.join(model_dir, filename)
        
        self._omr_liste = None # init av self._set_output
        
        self._init_agg_uke = {"vv"   : "min",
                              "mag"  : "sum",
                              "flom" : "sum",
                              "reg"  : "sum",
                              "ureg" : "sum"}
        
        self._agg_omr = {"krv"    : pd.DataFrame.mean, 
                         "vv"     : pd.DataFrame.mean,
                         "mag"    : pd.DataFrame.sum,
                         "flom"   : pd.DataFrame.sum,
                         "reg"    : pd.DataFrame.sum,
                         "ureg"   : pd.DataFrame.sum,
                         "tilsig" : pd.DataFrame.sum,
                         "fast"   : pd.DataFrame.sum,
                         "int"    : pd.DataFrame.sum,
                         "vind"   : pd.DataFrame.sum,
                         "egpr"   : pd.DataFrame.sum}
        
        self._agg_uke = {"krv"    : "mean", 
                         "fast"   : "sum",
                         "int"    : "sum",
                         "vind"   : "sum",
                         "egpr"   : "sum"}
        
        self._output  = None
        self._objects = dict()
        
    def get_ntimen(self):
        "tuple med antall timer per tidsavsnitt"
        return self._get_param("ntimen")

    def get_hist(self):
        "tuple med simulerte år"
        return self._get_param("hist")
    
    def get_npenm(self):
        "antall tidsavsnitt"
        return self._get_param("npenm")
        
    def get_nverk(self):
        "antall omr"
        return self._get_param("nverk")
        
    def get_nsim(self):
        "antall simulerte år"
        return self._get_param("nsim")
        
    def get_nfor(self):
        "antall forbindelser i maskenett.data"
        return self._get_param("nfor")
        
    def get_nuke(self):
        "antall uker i simuleringsperioden"
        return self._get_param("nuke")
        
    def get_jstart(self):
        "første uke i simuleringsperioden"
        return self._get_param("jstart")
        
    def get_jslutt(self):
        "siste uke i simuleringsperioden"
        return self._get_param("jslutt")
        
    def get_serie(self):
        "1 = seriesimulering, 0 = parallellsimulering"
        return self._get_param("serie")
        
    def get_staar(self):
        "første år i simuleringsperioden"
        return self._get_param("staar")
        
    def get_runcode(self):
        """
        Kode som angir type kjøring
        
        Bokstavnr : Kode
           1      : E=Enmagasinsimulering, T=Tappefordeling
           2      : V=Strategi basert på vannverdier, K=Strategi basert på kutt
           3      : L=Samlast
           4      : E=EIC-metoden brukt for modellering av tilgjengelighet på varmekraft
          17      : S=Sekvensielle prisavsnitt i områdemodellen
          18      : S=Startkostnader
          19      : T=Kortsiktig temperaturprognose
          20      : M=Temperaturavhengig kraftvarme
          21      : E=Eget system, T=Totalsystem, B=Både eget- og totalsystem
          22      : F=Forbrukerelastisitet
          40      : S=Samlast, N=Samnett, ' '=Samtap        
        """
        return self._get_param("runcode")
        
    def get_istbl(self):
        "første blokk med resultater i samres.samk"
        return self._get_param("istbl")
        
    def get_blengde(self):
        "blokklengde i bytes i lest samres.samk"
        return self._get_param("blengde")
    
    def get_krv(self):
        "df med kraftverdier i øre/kwh for hvert omr"
        return self._get_df("krv")
        
    def get_vv(self):
        "df med vannverdier i øre/kwh for hvert omr"
        return self._get_df("vv")
        
    def get_mag(self):
        "df med magasinfylling i gwh for hvert omr"
        return self._get_df("mag")

    def get_flom(self):
        "df med flom + forbitapping (vanntap) i gwh for hvert omr"
        return self._get_df("flom")

    def get_reg(self):
        "df med regulert tilsig i gwh for hvert omr"
        return self._get_df("reg")

    def get_ureg(self):
        "df med uregulert tilsig i gwh for hvert omr"
        return self._get_df("ureg")

    def get_fast(self):
        "df med fastkraft i gwh for hvert omr"
        return self._get_df("fast")

    def get_egpr(self):
        "df med vannkraftproduksjon i gwh for hvert omr"
        return self._get_df("egpr")

    def get_int(self):
        "df med prisavhengig nettoproduksjon i gwh for hvert omr"
        return self._get_df("int")

    def get_vind(self):
        "df med vindkraft i gwh for hvert omr"
        return self._get_df("vind")
    
    def get_tilsig(self):
        "df[aar,uke + omrnr_liste] reg + ureg tilsig i gwh"
        key = "tilsig"
        if key in self._objects:
            return self._objects[key]
        
        reg  = self.get_reg()
        ureg = self.get_ureg()
        
        reg  = reg.set_index(["aar", "uke"])
        ureg = ureg.set_index(["aar", "uke"])
        
        df = reg + ureg
        
        df = df.reset_index()
        
        self._objects[key] = df
        
        return df
    
    def get_agg_df(self, name, dim):
        """
        df[dim + omrnr_liste] -> verdi for name
        
        name = ['flom', 'egpr', 'vv', 'krv', 'fast', 'reg', 'vind', 'int', 'ureg', 'mag', 'tilsig']
        
        dim  = ["aar"], ["aar", "uke"], ["uke"] 
            dim kan også være ["aar", "uke", "tsnitt"] for 
            name = ["krv", "egpr", "fast", "vind", "int"]
            men da returneres df som den er (ingen aggregering)
            
        hvis dim = ["uke"] snittes verdi over alle år for alle names
        krv og vv aggregeres med snitt, resten med sum
        """
        
        valid_names = list(self._agg_omr.keys())
        
        assert isinstance(dim, list) or isinstance(dim, tuple), "dim må være list eller tuple"
        assert name in valid_names, "name not in %s" % valid_names
        
        dim     = sorted(list(dim))
        dim_key = tuple(dim)
        
        valid_dims = [("aar",), ("aar", "uke"), ("uke",), ("aar", "tsnitt", "uke")]
        
        assert dim_key in valid_dims, "støtter kun %s" % valid_dims
        
        if dim_key == ("aar", "tsnitt", "uke"):
            assert name in ["krv", "egpr", "fast", "vind", "int"], "ugyldig input"
            return self._get_df(name)
        
        key = ("get_agg_df", name, dim_key)
        
        if key in self._objects:
            return self._objects[key]
        
        if dim_key == ("aar", "uke") and name in self._init_agg_uke:
            return self._get_df(name)
        
        if name == "tilsig":
            df = self.get_tilsig()
        else:
            df = self._get_df(name)
        
        if name == "krv":
            if dim_key == ("aar",):
                df = self.get_agg_df("krv", ["aar", "uke"])
                df = df.pivot_table(index=["aar"], values=self._omr_liste, aggfunc="mean")
                df = df.reset_index()
            
            elif dim_key == ("aar", "uke"):
                ntimen = self.get_ntimen()
                ts_map = {ts : n/168.0 for ts,n in enumerate(ntimen, start=1)}
                df["ntimen"] = df["tsnitt"].apply(lambda ts : ts_map[ts])
                df = df.set_index(["aar", "uke", "tsnitt"])
                df = df.multiply(df["ntimen"], axis="index")
                df = df.reset_index()
                df = df.pivot_table(index=["aar", "uke"], values=self._omr_liste, aggfunc="sum")
                df = df.reset_index()
                
            elif dim_key == ("uke",):
                df = self.get_agg_df("krv", ["aar", "uke"])
                df = df.pivot_table(index=["uke"], values=self._omr_liste, aggfunc="mean")
                df = df.reset_index()
                
            else:
                raise Exception("krv feilet")
                
        elif name == "vv":
            if dim_key == ("aar",):
                df = df.pivot_table(index=["aar"], values=self._omr_liste, aggfunc="mean")
                df = df.reset_index()
                
            elif dim_key == ("uke",):
                df = df.pivot_table(index=["uke"], values=self._omr_liste, aggfunc="mean")
                df = df.reset_index()
                
        elif name in ["mag", "reg", "ureg", "tilsig", "flom"]:
            if dim_key == ("aar",):
                df = df.pivot_table(index=["aar"], values=self._omr_liste, aggfunc="sum")
                df = df.reset_index()
                
            elif dim_key == ("uke",):
                df = df.pivot_table(index=["uke"], values=self._omr_liste, aggfunc="mean")
                df = df.reset_index()
        else:
            if dim_key == ("aar",):
                df = self.get_agg_df(name, ["aar", "uke"])
                df = df.pivot_table(index=["aar"], values=self._omr_liste, aggfunc="sum")
                df = df.reset_index()
                
            elif dim_key == ("uke",):
                df = self.get_agg_df(name, ["aar", "uke"])
                df = df.pivot_table(index=["uke"], values=self._omr_liste, aggfunc="mean")
                df = df.reset_index()
                
            elif dim_key == ("aar", "uke"):
                df = df.pivot_table(index=["aar", "uke"], values=self._omr_liste, aggfunc="sum")
                df = df.reset_index()
                
        self._objects[key] = df
        
        return df
    
    def get_fokus_agg_df(self, fokus, name, dim):
        """
        df[dim + fokusomr_liste] -> verdi for name
        
        fokus - dict[fokusomr] -> omrnr_liste
        
        name = ['flom', 'egpr', 'vv', 'krv', 'fast', 'reg', 'vind', 'int', 'ureg', 'mag', 'tilsig']
        
        dim  = ["aar"], ["aar", "uke"], ["uke"] 
            dim kan også være ["aar", "uke", "tsnitt"] for 
            name = ["krv", "egpr", "fast", "vind", "int"]
            men da returneres df som den er (ingen aggregering)
            
        hvis dim = ["uke"] snittes verdi over alle år for alle names
        krv og vv aggregeres med snitt, resten med sum
        """
        
        if not fokus:
            return self.get_agg_df(name, dim)
        
        valid_names = list(self._agg_omr.keys())
        
        assert isinstance(dim, list), "dim må være liste"
        assert name in valid_names, "name not in %s" % valid_names
        
        dim     = sorted(dim)
        dim_key = tuple(dim)
        
        # endre rekkefølge i case
        if dim_key == ("aar", "tsnitt", "uke"):
            dim = ["aar", "uke", "tsnitt"]
        
        valid_dims = [("aar",), ("aar", "uke"), ("uke",), ("aar", "tsnitt", "uke")]
        
        assert dim_key in valid_dims, "støtter kun %s" % valid_dims
        
        fokus_keys   = tuple(sorted(list(fokus.keys())))
        fokus_values = tuple([tuple(sorted(v)) for v in fokus.values()])
        
        key = (fokus_keys, fokus_values, name, dim_key)
        if key in self._objects:
            return self._objects[key]  
        
        aggf_omr = self._agg_omr[name]
        
        data = dict()
        for fokusomr, omrnr_liste in fokus.items():
            df = self.get_agg_df(name, dim).copy()
            df = df.set_index(dim)
            df = df[omrnr_liste]
            df = aggf_omr(df, axis=1)
            data[fokusomr] = df
        df = pd.DataFrame(data)
        
        df = df.reset_index()
        
        self._objects[key] = df
        
        return df
    
    def get_df(self, names, dim, fokus=None):
        """
        df[dim, omr + names] -> verdier for alle names
        
        hvis fokus er omr=fokusomr, ellers omrnr
        
        fokus - dict[fokusomr] -> omrnr_liste
        
        name = ['flom', 'egpr', 'vv', 'krv', 'fast', 'reg', 'vind', 'int', 'ureg', 'mag', 'tilsig']
        
        dim  = ["aar"], ["aar", "uke"], ["uke"] 
            dim kan også være ["aar", "uke", "tsnitt"] for 
            name = ["krv", "egpr", "fast", "vind", "int"]
            men da returneres df som den er (ingen aggregering)
            
        hvis dim = ["uke"] snittes verdi over alle år for alle names
        krv og vv aggregeres med snitt, resten med sum
        """
        valid_names = list(self._agg_omr.keys())
        
        assert isinstance(dim, list), "dim må være liste"
        for name in names:
            assert name in valid_names, "name not in %s" % valid_names
        
        dim     = sorted(dim)
        
        # endre rekkefølge i case
        if dim == ["aar", "tsnitt", "uke"]:
            dim = ["aar", "uke", "tsnitt"]
        
        dfs = []
        level = len(dim)
        
        if fokus:
            level_name = "fokusomr"
        else:
            level_name = "omrnr"
            
        for name in names:
            df = self.get_fokus_agg_df(fokus, name, dim)
            df = df.set_index(dim)
            df = df.stack()
            df = df.reset_index()
            df = df.rename(columns={"level_%d" % level : level_name, 0 : name})
            df = df.set_index([level_name] + dim)
            dfs.append(df)
            
        df = pd.concat(dfs, axis=1)
        
        df = df.reset_index()
        
        return df
                
    def _get_param(self, key):
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        obj = self._output.pop(key)
        self._objects[key] = obj
        return obj
    
    def _get_df(self, key):
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
            
        rows = self._output.pop(key)
        idx_cols = ["aar", "uke", "tsnitt"]
        cols = idx_cols + self._omr_liste
        df = pd.DataFrame(rows, columns=cols)
        
        if key in self._init_agg_uke:
            aggf = self._init_agg_uke[key]
            df = df.pivot_table(index=["aar","uke"], values=self._omr_liste, aggfunc=aggf)
            df = df.reset_index()
        
        self._objects[key] = df
        
        return df
        
    def _set_output(self):
        self._output = read_io_samres(self.path)
        self._omr_liste = list(range(1, self._output["nverk"] + 1))
