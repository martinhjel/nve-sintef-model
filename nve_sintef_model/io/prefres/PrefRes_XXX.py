import pandas as pd

from .read_io_prefres_xxx import read_io_prefres_xxx

class PrefRes_XXX(object):
    
    def __init__(self, path, aar, jstart, jslutt, npenm, ntrinnsum, blengde, sumtrinn_order_dict):
        """
        path                - sti til prefres_xx-fil
        aar                 - simulert aar
        jstart              - startuke
        jslutt              - sluttuke
        npenm               - antall prisavsnitt
        ntrinnsum           - totalt anntal trinn
        blengde             - blokklengde paa filen
        sumtrinn_order_dict - dict[uke] -> [sumtrinnr sortert etter merit order]
        """
        self.path                = path
        self.aar                 = aar
        self.jstart              = jstart
        self.jslutt              = jslutt
        self.npenm               = npenm
        self.ntrinnsum           = ntrinnsum
        self.blengde             = blengde
        self.sumtrinn_order_dict = sumtrinn_order_dict
        
        self.sumtrinnliste = list(range(1, self.ntrinnsum + 1))
        
        self._df      = pd.DataFrame()
        
    def get_sumtrinn_df(self):
        if not self._df.empty:
            return self._df
        rows = self._output = read_io_prefres_xxx(self.path, self.aar, self.jstart, self.jslutt, 
                                                  self.npenm, self.ntrinnsum, self.blengde, self.sumtrinn_order_dict)
        cols = ["aar", "uke", "tsnitt"] + self.sumtrinnliste
        df = pd.DataFrame(rows, columns=cols)
        self._df = df
        return df
    
    
    def get_kategori_uke(self, trinnliste_df, fokus=False):
        df = self.get_sumtrinn_df()
        
        df = df.pivot_table(index=["aar", "uke"], values=self.sumtrinnliste, aggfunc="sum")
        
        df = df.stack()
        df = df.reset_index()
        df = df.rename(columns={"level_2" : "sumtrinnr", 0 : "gwh"})
        
        df = df.merge(trinnliste_df, on="sumtrinnr")
        
        df = df.pivot_table(index=["aar", "uke", "omrnr", "katnr"], values="gwh", aggfunc="sum")
        df = df.reset_index()
        
        if fokus:
            rows = [(o,n) for o in fokus for n in fokus[o]]
            fokus_df = pd.DataFrame(rows, columns=["fokusomr", "omrnr"])
            df = df.merge(fokus_df, on="omrnr")
            df = df.pivot_table(index=["aar", "uke", "fokusomr", "katnr"], values="gwh", aggfunc="sum")
            df = df.reset_index()
            
        return df
    
    def get_avregn_uke(self, trinnliste_df, brensler_df, fokus=False):
        df = self.get_sumtrinn_df()
        
        kat_df = trinnliste_df.copy()
        kat_df = kat_df[["katnr", "katnavn"]]
        
        df = df.pivot_table(index=["aar", "uke"], values=self.sumtrinnliste, aggfunc="sum")
        
        df = df.stack()
        df = df.reset_index()
        df = df.rename(columns={"level_2" : "sumtrinnr", 0 : "gwh"})
        
        trinn_med_brensel = trinnliste_df.merge(brensler_df, how="left")
        
        df = df.merge(trinn_med_brensel, on="sumtrinnr")
        
        varme = df.copy()
        rest  = df.copy()
        
        varme = varme[varme["brensel"].isnull() == False]
        rest  = rest[rest["brensel"].isnull() == True]

        gruppe = {
            1  : "annen_produksjon",
            2  : "prisavhengig_forbruk",
            3  : "annen_produksjon",
            4  : "annen_produksjon",
            5  : "prisavhengig_forbruk",
            6  : "annen_produksjon",
            7  : "prisavhengig_forbruk",
            8  : "annen_produksjon",
            9  : "prisavhengig_forbruk",
            20 : "flomkraft",
            30 : "prisavhengig_forbruk",
            40 : "rasjonering"}
       
        rest["katnr"] = rest["katnr"].apply(lambda x : gruppe.get(x, x))
        rest = rest.pivot_table(index=["aar", "uke", "omrnr", "katnr"], values="gwh", aggfunc="sum")
        rest = rest.reset_index()
        rest = rest.rename(columns={"katnr" : "kat"})
        
        varme = varme.pivot_table(index=["aar", "uke", "omrnr", "brensel"], values="gwh", aggfunc="sum")
        varme = varme.reset_index()
        varme = varme.rename(columns={"brensel" : "kat"})
        
        df = pd.concat([rest, varme])
        
        df = df.reset_index(drop=True)
        
        if fokus:
            rows = [(o,n) for o in fokus for n in fokus[o]]
            fokus_df = pd.DataFrame(rows, columns=["fokusomr", "omrnr"])
            df = df.merge(fokus_df, on="omrnr")
            df = df.pivot_table(index=["aar", "uke", "fokusomr", "kat"], values="gwh", aggfunc="sum")
            df = df.reset_index()        
            
        return df
        
        
        
        
    
            
        
        

