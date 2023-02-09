# coding=cp1252

import os
import pandas as pd

from nve_sintef_model.utils.run_sintef import run_sintef
from nve_sintef_model.utils.get_dos import get_dos 

class Samoverskudd(object):
    
    def __init__(self, conf):
        """
        conf["path_model"]  - sti til emps-modell
        conf["startuke"]    - startuke
        conf["sluttuke"]    - sluttuke
        conf["filnavn"]     - filnavn paa samoverskudd-fil
        conf["path_bin"]    - sti til sintef bin-mappe
        conf["path_hydark"] - sti til sintef hydark-mappe
        """

        self.path_model  = conf["path_model"]
        self.startuke    = conf["startuke"]
        self.sluttuke    = conf["sluttuke"]
        self.filnavn     = conf["filnavn"]
        self.path_bin    = os.path.abspath(conf["path_bin"])
        self.path_hydark = os.path.abspath(conf["path_hydark"])
        self.dos         = get_dos(self.path_bin, self.path_hydark)
        self.path_samov  = os.path.abspath(os.path.join(self.path_model, self.filnavn))
        
        self._output  = None
        self._objects = dict()
        
    def get_fokus_df(self, fokus, omr_df):
        name = "fokus_df"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        
        rows = [(o,n) for o in fokus for n in fokus[o]]
        fokus_df = pd.DataFrame(rows, columns=["fokusomr", "omrnr"])
        fokus_df = fokus_df.merge(omr_df, on="omrnr")
        
        self._objects[name] = fokus_df
        
        return fokus_df
        
        
    def get_fokus_samov_middel(self, fokus, omr_df):
        df = self.get_samoverskudd_middelverdi()
        fokus_df = self.get_fokus_df(fokus, omr_df)
        
        df = df.rename(columns={"Delomraade" : "omrnavn"})
        
        df = df.merge(fokus_df, on="omrnavn")
        
        value_cols = [c for c in df.columns if c not in ["fokusomr", "omrnr", "omrnavn"]]
        df = df.pivot_table(index=["fokusomr"], values=value_cols, aggfunc="sum")
        df = df.reset_index()
        
        return df
    
    def get_fokus_samov_aar(self, fokus, omr_df):
        df = self.get_samoverskudd_alle_aar()
        fokus_df = self.get_fokus_df(fokus, omr_df)
        
        df = df.rename(columns={"Delomraade" : "omrnavn"})
        
        df = df.merge(fokus_df, on="omrnavn")
        
        value_cols = [c for c in df.columns if c not in ["aar", "fokusomr", "omrnr", "omrnavn"]]
        df = df.pivot_table(index=["aar", "fokusomr"], values=value_cols, aggfunc="sum")
        df = df.reset_index()
        
        return df
        
        
    def _set_output(self):
        self.kjor_samoverskudd()
        
        with open(self.path_samov) as f:
            self._output = f.readlines()
        
    def kjor_samoverskudd(self):
        lines = []
        lines.append("REGNEARK")
        lines.append("PUNKTUM")
        lines.append("SEMIKOLON")
        lines.append(self.filnavn)
        lines.append("0") # driftskostnader for vannkraft
        lines.append("JA") # middelverdier + alle aar
        lines.append("%d %d" % (self.startuke, self.sluttuke))
        lines.append("NEI") # ikke bruk realrente
        lines.append("NEI") # snittapskostnadene skal ikke refereres mottaker
        
        dos        = self.dos
        exe        = "samoverskudd"
        script     = "\n".join(lines)
        folder     = self.path_model
        scriptname = "xsamov.script"
        batname    = "xsamov.bat"
        cleanup    = True
        toscreen   = True
        
        run_sintef(dos, exe, script, folder, scriptname, batname, cleanup, toscreen)
        
    def get_samoverskudd_middelverdi(self):
        name = "samoverskudd_middelverdi"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
            
        rows = []
        collect = False
        for line in self._output:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            strings = line.split(";")
            strings = [s.strip() for s in strings]

            if not strings:
                continue

            if strings[0] == "Middelverdier":
                collect = True
                continue

            if strings[0] == "Sum":
                break

            if not collect:
                continue

            if len(strings) != 14:
                continue

            del strings[-1]

            if strings[1] == "GWh":
                continue

            if not strings[1][0].isdigit():
                columns = strings
                continue

            rows.append(strings)

        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index("Delomraade")
        df = df.astype(float)
        df = df.reset_index()
        self._objects[name] = df
        return df
    
    def get_samoverskudd_alle_aar(self):
        name = "samoverskudd_alle_aar"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        
        rows = []
        collect = False
        for line in self._output:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            strings = line.split(";")
            strings = [s.strip() for s in strings]

            if not strings:
                continue

            if "Foerste tilsigsaar" in strings[0]:
                collect = True
                aar = int(strings[0].split()[-1])

            if "Samfunnsokonomisk overskudd alle" in strings[0]:
                break

            if not collect:
                continue

            if len(strings) != 14:
                continue

            del strings[-1]

            if strings[1] == "GWh":
                continue

            if strings[0].lower() == "sum":
                continue

            if not strings[1][0].isdigit():
                columns = ["aar"] + strings
                continue

            rows.append([aar] + strings)
                    
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index(["aar", "Delomraade"])
        df = df.astype(float)
        df = df.reset_index()
        self._objects[name] = df
        return df
    
    def get_flaskehalsinntekt_middelverdier(self):
        name = "flaskehalsinntekt_middelverdier"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        
        rows = []
        collect = False
        for line in self._output:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            strings = line.split(";")
            strings = [s.strip() for s in strings]

            if not strings:
                continue

            if "Utskrift av flaskehalsinntekt for individuelle forbindelser" in strings[0]:
                collect = True

            if not collect:
                continue

            if len(strings) != 8:
                continue

            if strings[0] == "":
                continue

            del strings[-1]

            if strings[0].startswith("Fra"):
                columns = strings
                continue

            if strings[0].lower() == "sum":
                continue

            rows.append(strings)
                    
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index(["Fra omr�de", "Til omr�de", "Res. fra"])
        df = df.astype(float)
        df = df.reset_index()
        self._objects[name] = df
        return df
    
    def get_tso_overskudd_alle_aar(self):
        name = "tso_overskudd_alle_aar"
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
            
        rows = []
        collect1 = False
        collect2 = False
        for line in self._output:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            strings = line.split(";")
            strings = [s.strip() for s in strings]

            if not strings:
                continue

            if "Utskrift av TSO overskudd for tilsig" in strings[0]:
                collect1 = True
                continue

            if not collect1:
                continue

            if strings[0] == "Tilsigsaar":
                collect2 = True
                columns = strings
                del columns[-1]
                continue

            if not collect2:
                continue

            del strings[-1]

            if not len(strings) == len(columns):
                continue


            rows.append(strings)
                    
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index(["Tilsigsaar","Forbindelse","Kilde"])
        df = df.astype(float)
        df = df.stack()
        df = df.reset_index()
        df = df.rename(columns={"level_3":"aar", 0:"tso_overskudd", 
                                "Tilsigsaar" : "omrnavn_fra", "Forbindelse" : "omrnavn_til"})
        df["aar"] = df["aar"].astype(int)
        self._objects[name] = df
        return df
        
        
                        
                
                    
        
        
        
        


