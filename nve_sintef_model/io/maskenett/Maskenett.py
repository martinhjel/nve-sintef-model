
import os
import pandas as pd

from .read_io_maskenett import read_io_maskenett

class Maskenett(object):
    
    def __init__(self, model_dir, filename="MASKENETT.DATA"):
        """
        model_dir - sti til modellmappe
        filename  - navn paa MASKENETT-fil
        """
        self._objects = dict()
        self._output  = None
        self.path     = os.path.join(model_dir, filename)
        
    def get_linjer(self):
        "df[linjenr, omrnr_fra, omrnr_til, kap_fra, kap_til]"
        key = "get_linjer"
        if key in self._objects:
            return self._objects[key]
        obj = self._les_linjer()
        self._objects[key] = obj
        return obj

    def get_linjer_og_tap(self):
        "df[linjenr, omrnr_fra, omrnr_til, kap_fra, kap_til, tap, avgift_fra, avgift_til]"
        key = "get_linjer_og_tap"
        if key in self._objects:
            return self._objects[key]
        obj = self._les_linjer_og_tap()
        self._objects[key] = obj
        return obj

    def get_maske_avvik(self):
        """
        tsnitt i maskenett kan ha verdien 0, som betyr alle tsnitt (dvs. hele uken)
        df[linjenr, uke, maskenett_tsnitt, avvik_fra og avvik_til]
        """
        key = "get_maske_avvik"
        if key in self._objects:
            return self._objects[key]
        obj = self._les_avvik()
        self._objects[key] = obj
        return obj
    
    def get_linjenr_liste(self):
        key = "get_linjenr_liste"
        if key in self._objects:
            return self._objects[key]
        df = self.get_linjer()
        linjenr_liste = sorted(list(df["linjenr"]))
        self._objects[key] = linjenr_liste
        return linjenr_liste
    
    def get_avvik(self, npenm):
        """
        tsnitt i maskenett kan ha verdien 0, som betyr alle tsnitt (dvs. hele uken)
        denne funksjonen bytter ut 0 med alle tsnitt og returnerer
        df[linjenr, uke, tsnitt, avvik_fra og avvik_til]
        """
        avvik = self.get_maske_avvik()
        rows = []
        for ts in range(1, npenm + 1):
            rows.append((ts, 0))
            rows.append((ts, ts))
        df = pd.DataFrame(rows, columns=["ts_ny", "tsnitt"])
        df = avvik.merge(df, on="tsnitt")
        df["tsnitt"] = df["ts_ny"]
        del df["ts_ny"]
        return df
    
    def get_agg_lister(self, omrnr_tuple):
        """
        returnerer med_liste, snu_liste
        med_liste - linjenr som grenser til andre omrnr enn i omrnr_liste
        snu_liste - linjenr som maa byttes fra 'fra-til' til 'til-fra' i aggregering
        """
        key = ("get_agg_lister", omrnr_tuple)
        if key in self._objects:
            return self._objects[key]
        df = self.get_linjer().copy()
        df["er_fra"] = df["omrnr_fra"].apply(lambda x : x in omrnr_tuple)
        df["er_til"] = df["omrnr_til"].apply(lambda x : x in omrnr_tuple)
        df["skal_med"] = df["er_fra"].astype(int) + df["er_til"].astype(int)
        df = df[df["skal_med"] == 1]
        df["snu"] = df["er_til"].astype(int)
        med_liste = list(df["linjenr"])
        df = df[df.snu == 1]
        snu_liste = list(df["linjenr"])
        ret = (med_liste, snu_liste)
        self._objects[key] = ret
        return ret

    def get_linje_installert(self, fra, uke, ntimen, uker, gwh):
        """
        df[dim + linjenr_liste] -> installert kapasitet retning
        
        fra    - hvis True saa retning fra ellers til
        uke    - hvis True saa dim uke ellers tsnitt,uke
        ntimen - tuple med antall timer for hvert tidsavsnitt
        uker   - tuple med ukenr
        gwh    - hvis True saa gwh ellers mw
        """
        key = ("get_linje_installert", fra, uke, ntimen, uker, gwh)
        if key in self._objects:
            return self._objects[key]  
        npenm = len(ntimen)
        df = self.get_linjer()
        df["cj"] = 1
        if fra:
            df = df.pivot_table(index="cj", columns="linjenr", values="kap_fra")
        else:
            df = df.pivot_table(index="cj", columns="linjenr", values="kap_til")
        df = df.reset_index()
        tid_df = self._get_tid_df(uke, npenm, uker).copy()
        tid_df["cj"] = 1
        df = tid_df.merge(df, on="cj")
        del df["cj"]
        if gwh:
            if uke:
                df = df.set_index("uke")
                df = df*168/1000
                df = df.reset_index()
            else:
                ts_map = {ts : n for ts,n in enumerate(ntimen, start=1)}
                df["n"] = df["tsnitt"].apply(lambda ts : ts_map[ts])
                df = df.set_index(["uke", "tsnitt"])
                df = df.multiply(df["n"], axis="index")
                del df["n"]
                df = df/1000
                df = df.reset_index()
        self._objects[key] = df
        return df
    
    def get_linje_avvik(self, fra, uke, ntimen, uker, gwh):
        """
        df[dim + linjenr_liste] -> avvik fra installert kapasitet retning
        
        fra    - hvis True saa retning fra ellers til
        uke    - hvis True saa dim uke ellers tsnitt,uke
        ntimen - tuple med antall timer for hvert tidsavsnitt
        uker   - tuple med ukenr
        gwh    - hvis True saa gwh ellers mw
        """
        key = ("get_linje_avvik", fra, uke, ntimen, uker, gwh)
        if key in self._objects:
            return self._objects[key]  
        npenm = len(ntimen)
        df = self.get_avvik(npenm)
        linjenr_liste = self.get_linjenr_liste()
        if fra:
            df = df.pivot_table(index=["uke","tsnitt"], columns="linjenr", values="avvik_fra")
        else:
            df = df.pivot_table(index=["uke","tsnitt"], columns="linjenr", values="avvik_til")
        if df.empty:
            df = pd.DataFrame([], columns=["uke","tsnitt"] + linjenr_liste)
        else:
            missing = [nr for nr in linjenr_liste if nr not in df.columns]
            for nr in missing:
                df[nr] = 0
            df = df[linjenr_liste]
            df = df.reset_index()
        tid_df = self._get_tid_df(uke, npenm, uker)
        if uke:
            ts_map = {ts : n/168.0 for ts,n in enumerate(ntimen, start=1)}
            df["n"] = df["tsnitt"].apply(lambda ts : ts_map[ts])
            df = df.set_index(["uke", "tsnitt"])
            df = df.multiply(df["n"], axis="index")
            df = df.reset_index()
            df = df.pivot_table(index="uke", values=linjenr_liste, aggfunc="sum")
            df = df.reset_index()
            df = tid_df.merge(df, on="uke", how="left")
            df = df.fillna(0)
        else:
            df = tid_df.merge(df, on=["tsnitt", "uke"], how="left")
            df = df.fillna(0)
        if gwh:
            if uke:
                df = df.set_index("uke")
                df = df*168/1000
                df = df.reset_index()
            else:
                ts_map = {ts : n for ts,n in enumerate(ntimen, start=1)}
                df["n"] = df["tsnitt"].apply(lambda ts : ts_map[ts])
                df = df.set_index(["uke", "tsnitt"])
                df = df.multiply(df["n"], axis="index")
                del df["n"]
                df = df/1000
                df = df.reset_index()
        self._objects[key] = df
        return df
    
    def get_linje_tilgjengelig(self, fra, uke, ntimen, uker, gwh):
        """
        df[dim + linjenr_liste] -> tilgjengelig kapasitet retning
        
        fra    - hvis True saa retning fra ellers til
        uke    - hvis True saa dim uke ellers tsnitt,uke
        ntimen - tuple med antall timer for hvert tidsavsnitt
        uker   - tuple med ukenr
        gwh    - hvis True saa gwh ellers mw
        """
        key = ("get_linje_tilgjengelig", fra, uke, ntimen, uker, gwh)
        if key in self._objects:
            return self._objects[key]  
        kap   = self.get_linje_installert(fra, uke, ntimen, uker, gwh)
        avvik = self.get_linje_avvik(fra, uke, ntimen, uker, gwh)
        if uke:
            idx = ["uke"]
        else:
            idx = ["uke", "tsnitt"]
        kap = kap.set_index(idx)
        avvik = avvik.set_index(idx)
        df = kap + avvik
        df = df.reset_index()
        self._objects[key] = df
        return df
    
    def get_omr_installert(self, fokus, fra, uke, ntimen, uker, gwh):
        """
        df[dim + fokusomr] -> installert kapasitet retning
        
        fokus  - dict[fokusomr] -> omrnr_liste
        fra    - hvis True saa retning fra ellers til
        uke    - hvis True saa dim uke ellers tsnitt,uke
        ntimen - tuple med antall timer for hvert tidsavsnitt
        uker   - tuple med ukenr
        gwh    - hvis True saa gwh ellers mw
        """
        return self._get_omr(self.get_linje_installert, "get_omr_installert", fokus, fra, uke, ntimen, uker, gwh)
    
    def get_omr_avvik(self, fokus, fra, uke, ntimen, uker, gwh):
        """
        df[dim + fokusomr] -> avvik fra installert kapasitet retning
        
        fokus  - dict[fokusomr] -> omrnr_liste
        fra    - hvis True saa retning fra ellers til
        uke    - hvis True saa dim uke ellers tsnitt,uke
        ntimen - tuple med antall timer for hvert tidsavsnitt
        uker   - tuple med ukenr
        gwh    - hvis True saa gwh ellers mw
        """
        return self._get_omr(self.get_linje_avvik, "get_omr_avvik", fokus, fra, uke, ntimen, uker, gwh)
    
    def get_omr_tilgjengelig(self, fokus, fra, uke, ntimen, uker, gwh):
        """
        df[dim + fokusomr] -> avvik fra tilgjengelig kapasitet retning
        
        fokus  - dict[fokusomr] -> omrnr_liste
        fra    - hvis True saa retning fra ellers til
        uke    - hvis True saa dim uke ellers tsnitt,uke
        ntimen - tuple med antall timer for hvert tidsavsnitt
        uker   - tuple med ukenr
        gwh    - hvis True saa gwh ellers mw
        """
        return self._get_omr(self.get_linje_tilgjengelig, "get_omr_tilgjengelig", fokus, fra, uke, ntimen, uker, gwh)
        
    def _get_omr(self, f, name, fokus, fra, uke, ntimen, uker, gwh):
        fokus_keys   = tuple(sorted(list(fokus.keys())))
        fokus_values = tuple([tuple(sorted(v)) for v in fokus.values()])
        
        key = (name, fokus_keys, fokus_values, fra, uke, ntimen, uker, gwh)
        if key in self._objects:
            return self._objects[key]  
        
        linje_fra = f(True,  uke, ntimen, uker, gwh).copy()
        linje_til = f(False, uke, ntimen, uker, gwh).copy()
        
        if uke:
            idx = ["uke"]
        else:
            idx = ["uke", "tsnitt"]
            
        fra_data = dict()
        til_data = dict()
        for navn, omrnr_liste in fokus.items():
            med_liste, snu_liste = self.get_agg_lister(tuple(omrnr_liste))
            
            cfra = linje_fra.copy()
            ctil = linje_til.copy()
            
            cfra = cfra.set_index(idx)
            ctil = ctil.set_index(idx)
            
            cfra = cfra[med_liste]
            ctil = ctil[med_liste]
            
            cfra[snu_liste], ctil[snu_liste] = ctil[snu_liste], cfra[snu_liste]
            
            cfra = cfra.sum(axis=1)
            ctil = ctil.sum(axis=1)
            
            fra_data[navn] = cfra
            til_data[navn] = ctil
            
        fra_df = pd.DataFrame(fra_data)
        til_df = pd.DataFrame(til_data)
        
        key_fra = ("get_omr_installert", fokus_keys, fokus_values, True, uke, ntimen, uker, gwh)
        self._objects[key_fra] = fra_df
        
        key_til = ("get_omr_installert", fokus_keys, fokus_values, False, uke, ntimen, uker, gwh)
        self._objects[key_til] = til_df
        
        if fra:
            return fra_df
        else:
            return til_df
        
    def _get_tid_df(self, uke, npenm, uker):
        
        key = ("_get_tid_df", uke, npenm, uker)
        
        if key in self._objects:
            return self._objects[key]
        
        if uke:
            rows = [(u,) for u in uker]
            df = pd.DataFrame(rows, columns=["uke"])
        else:
            rows = [(u,ts) for u in uker for ts in range(1, npenm + 1)]
            df = pd.DataFrame(rows, columns=["uke", "tsnitt"])
    
        self._objects[key] = df
        
        return df
    
    def _les_linjer(self):
        if not self._output:
            self._set_output()
        
        rows = []
        connection_nr = 0

        for line in self._output:

            strings = line.split(",")
            strings = [self._clean(s) for s in strings]
            strings = [s for s in strings if s]

            if self._is_connection(strings):
                connection_nr += 1
                count = 0
                from_nr, from_name, to_nr, to_name = strings[:4]
                continue

            try:
                count += 1
            except:
                continue

            if not count == 2:
                continue

            from_cap, to_cap = strings[1:3]

            row = (connection_nr, from_nr, to_nr, from_cap, to_cap)
            rows.append(row)

        cols = ["linjenr", "omrnr_fra", "omrnr_til", "kap_fra", "kap_til"]
        df = pd.DataFrame(rows, columns=cols)

        df["linjenr"]   = df["linjenr"].astype(int)
        df["omrnr_fra"] = df["omrnr_fra"].astype(int)
        df["omrnr_til"] = df["omrnr_til"].astype(int)
        df["kap_fra"]   = df["kap_fra"].astype(float)
        df["kap_til"]   = df["kap_til"].astype(float)
                
        return df
        
    def _les_avvik(self):
        if not self._output:
            self._set_output()
        
        rows = []
        connection_nr = 0
        
        for line in self._output:
            strings = line.split(",")
            strings = [self._clean(s) for s in strings]
            strings = [s for s in strings if s]

            if len(strings) < 5:
                continue

            if self._is_connection(strings):
                connection_nr += 1
                from_nr, from_name, to_nr, to_name = strings[:4]
                continue

            if not all([self._is_number(s) for s in strings[:5]]):
                continue

            tsnitt, start, stop, from_cap, to_cap = strings[:5]

            for week in range(int(start), int(stop) + 1):
                row = (connection_nr, week, tsnitt, from_cap, to_cap)
                rows.append(row)

        cols = ["linjenr", "uke", "tsnitt", "avvik_fra", "avvik_til"]
        df = pd.DataFrame(rows, columns=cols)

        df["linjenr"]   = df["linjenr"].astype(int)
        df["uke"]       = df["uke"].astype(int)
        df["tsnitt"]    = df["tsnitt"].astype(int)
        df["avvik_fra"] = df["avvik_fra"].astype(float)
        df["avvik_til"] = df["avvik_til"].astype(float)

        return df

    def _les_linjer_og_tap(self):
        if not self._output:
            self._set_output()
        
        rows = []
        connection_nr = 0

        for line in self._output:

            strings = line.split(",")
            strings = [self._clean(s) for s in strings]
            strings = [s for s in strings if s]

            if self._is_connection(strings):
                connection_nr += 1
                count = 0
                from_nr, from_name, to_nr, to_name = strings[:4]
                continue

            try:
                count += 1
            except:
                continue

            if count not in [1,2]:
                continue

            elif count == 1:
                tap, from_avgift, to_avgift = strings[:3]
                continue

            if count == 2:
                from_cap, to_cap = strings[1:3]
                row = (connection_nr, from_nr, to_nr, from_cap, to_cap, tap, from_avgift, to_avgift)
                rows.append(row)
                continue

        cols = ["linjenr", "omrnr_fra", "omrnr_til", "kap_fra", "kap_til", "tap", "avgift_fra", "avgift_til"]
        df = pd.DataFrame(rows, columns=cols)

        df["linjenr"]    = df["linjenr"].astype(int)
        df["omrnr_fra"]  = df["omrnr_fra"].astype(int)
        df["omrnr_til"]  = df["omrnr_til"].astype(int)
        df["kap_fra"]    = df["kap_fra"].astype(float)
        df["kap_til"]    = df["kap_til"].astype(float)
        df["tap"]        = df["tap"].astype(float)
        df["avgift_fra"] = df["avgift_fra"].astype(float)
        df["avgift_til"] = df["avgift_til"].astype(float)
                
        return df

    
    def _clean(self, string):
        string = string.replace("\n", "")
        string = string.replace("\r", "")
        string = string.replace("'", "")
        string = string.strip()
        return string

    def _is_number(self, string):
        try:
            float(string)
            return True
        except:
            return False

    def _is_connection(self, strings):
        if len(strings) < 4:
            return False
        return (strings[0].isdigit()
                and not strings[1].isdigit()
                and strings[2].isdigit()
                and not strings[3].isdigit())
    
    def _set_output(self):
        self._output = read_io_maskenett(self.path)

