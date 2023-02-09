import os
import struct
import pandas as pd

def read_kalib_df(model_dir, fn="FEEDBACK.EMPS"):
    """
    leser kalibreringsfaktorer fra filen FEEDBACK.EMPS 
    returnerer en df med kolonner omrnr, tilb, form, elast
    """
    
    path = os.path.join(model_dir, fn)

    with open(path, "rb") as f:
        blengde, nverk = struct.unpack(2*"i", f.read(2*4))

        f.seek(1*blengde)
        tbfaktor = struct.unpack(nverk*"f", f.read(nverk*4))

        f.seek(2*blengde)
        formfa = struct.unpack(nverk*"f", f.read(nverk*4))

        f.seek(3*blengde)
        fkorr = struct.unpack(nverk*"f", f.read(nverk*4))

    omrnr = [i for i in range(1, nverk + 1)]

    d = [i for i in zip(omrnr, tbfaktor, formfa, fkorr)]
    
    df = pd.DataFrame.from_records(d, columns=["omrnr", "tilb", "form", "elast"])
    
    df["tilb"] = df["tilb"].round(3)
    df["form"] = df["form"].round(3)
    df["elast"] = df["elast"].round(3)    
    
    return df