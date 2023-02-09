import struct

def read_io_vverd(path):
    """
    leser innholdet i vverd_nnn.samk til et dict, som returneres
    dimensjonaliteten til vannverdimatrisen er
    (uke, pris, sno, tils, mag) -> vv
    """
    with open(path, "rb") as f:
        blokklengde, ntmag, ntpris, ntsno, nttils, jstart, jslutt = struct.unpack("i"*7, f.read(7*4))     
        realrente, = struct.unpack("f", f.read(4))
        
        vannverdier = dict()
        for uke in range(jstart, jslutt + 1):
            f.seek((uke+1)*blokklengde)
            for pris in range(1, ntpris + 1):
                for sno in range(1, ntsno + 1):
                    for tils in range(1, nttils + 1):
                        for mag in range(1, ntmag + 1):
                            vv, = struct.unpack("f", f.read(4))
                            vannverdier[(uke, pris, sno, tils, mag)] = vv
                    
    d = dict()
    d["blokklengde"] = blokklengde
    d["ntmag"]       = ntmag
    d["ntpris"]      = ntpris
    d["ntsno"]       = ntsno
    d["nttils"]      = nttils
    d["jstart"]      = jstart
    d["jslutt"]      = jslutt
    d["realrente"]   = realrente
    d["vannverdier"] = vannverdier
    
    return d

