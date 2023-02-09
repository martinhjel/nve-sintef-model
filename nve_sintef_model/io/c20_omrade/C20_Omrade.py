import os
import pandas as pd

from .read_io_c20_omrade import read_io_c20_omrade

class C20_Omrade(object):
    
    def __init__(self, model_dir, filename="C20_OMRADE.EMPS"):
        """
        model_dir - sti til modellmappe
        filename  - navn paa C20_OMRADE-fil
        """
        self.path = os.path.join(model_dir, filename)
        
    def get_omr(self):
        "df[omrnr, omrnavn]"
        rows = read_io_c20_omrade(self.path)
        return pd.DataFrame(rows, columns=["omrnr", "omrnavn"])

