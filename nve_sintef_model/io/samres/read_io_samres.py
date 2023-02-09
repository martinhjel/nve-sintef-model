import struct

def read_io_samres(path):
    
    names = ["krv", "vv", "mag", "flom", "reg", "ureg", "fast", "egpr", "int", "vind"]
    
    d = {n : [] for n in names}
    
    with open(path, "rb") as f:

        nverk, jstart, jslutt = struct.unpack(3 * "i", f.read(3 * 4))
        serie = struct.unpack(1 * "i", f.read(1 * 4))[0] * -1
        nsim, nuke, staar = struct.unpack(3 * "i", f.read(3 * 4))
        runcode = struct.unpack(40 * "c", f.read(40 * 1))
        npenm, istbl, nfor = struct.unpack(3 * "i", f.read(3 * 4))

        blengde = max([10 * nverk * 4 * 1, (npenm + 2 * 1) * 4, 40 + 12 * 4])

        f.seek(2 * blengde)
        ntimen = struct.unpack(npenm * "i", f.read(npenm * 4))

        f.seek(4 * blengde)
        hist = struct.unpack(nsim * "i", f.read(nsim * 4))

        blokk = istbl

        for aar in hist:
            for uke in range(jstart, jslutt + 1):
                for tsnitt in range(1, npenm + 1):
                    f.seek(blokk * blengde)
                    row = {n : [aar, uke, tsnitt] for n in names}
                    for omrnr in range(1, nverk + 1):
                        values = struct.unpack(10 * "f", f.read(10 * 4))
                        for i, value in enumerate(values):
                            name = names[i]
                            row[name].append(value)
                    blokk += 1
                    for name in names:
                        d[name].append(row[name])
                        
    runcode = b"".join(runcode).decode("utf-8")
                        
    d["nverk"]   = nverk
    d["jstart"]  = jstart
    d["jslutt"]  = jslutt
    d["serie"]   = serie
    d["nsim"]    = nsim
    d["nuke"]    = nuke
    d["staar"]   = staar
    d["runcode"] = runcode
    d["npenm"]   = npenm
    d["istbl"]   = istbl
    d["nfor"]    = nfor
    d["blengde"] = blengde
    d["ntimen"]  = ntimen
    d["hist"]    = hist
    
    return d