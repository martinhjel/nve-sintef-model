import struct

def read_io_samres_input(path):
    "leser header info fra samres.samk"

    with open(path, "rb") as f:       
        nverk, jstart, jslutt = struct.unpack(3*"i", f.read(3*4))
        serie = struct.unpack(1*"i", f.read(1*4))[0]*-1
        nsim, nuke, staar = struct.unpack(3*"i", f.read(3*4))
        runcode = struct.unpack(40*"c", f.read(40*1))
        npenm, istbl, nfor = struct.unpack(3*"i", f.read(3*4))
        blengde = max([10*nverk*4*1, (npenm+2*1)*4, 40+12*4])
        f.seek(2*blengde) # gaa til blokk 3
        ntimen = struct.unpack(npenm*"i", f.read(npenm*4))
        f.seek(4*blengde) # gaa til blokk 5
        hist = struct.unpack(nsim*"i", f.read(nsim*4))

    d = dict()
    d["nverk"] = nverk
    d["jstart"] = jstart
    d["jslutt"] = jslutt
    d["serie"] = serie
    d["nsim"] = nsim
    d["nuke"] = nuke
    d["staar"] = staar
    d["runcode"] = runcode
    d["npenm"] = npenm
    d["istbl"] = istbl
    d["nfor"] = nfor
    d["blengde"] = blengde
    d["ntimen"] = ntimen
    d["hist"] = hist

    return d


