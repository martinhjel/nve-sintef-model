import struct

def read_io_minmax(path, nverk, nuke, npenm):
    
    keys = ["maxmag", "minmag", "maxpro", "minpro"]
    out = {k : [] for k in keys}
    out["fastk"] = []

    with open(path, "rb") as f:
        
        for uke in range(1, nuke + 1):
            
            restr_rows = {k : [uke] for k in keys}
            fastk_rows = [[uke,tsnitt] for tsnitt in range(1, npenm + 1)]
            
            for omrnr in range(1, nverk + 1):
                
                values = list(struct.unpack("f" * 4, f.read(4 * 4)))
                for key,value in zip(keys, values):
                    restr_rows[key].append(value)
                    
                values = struct.unpack("f" * npenm, f.read(npenm * 4))
                for idx, value in enumerate(values):
                    fastk_rows[idx].append(value)
            
            for key in keys:
                out[key].append(restr_rows[key])
            
            for row in fastk_rows:
                out["fastk"].append(row)
                
    return out
