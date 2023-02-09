import struct

def read_io_utveksling(path, nfor, hist, jstart, jslutt, npenm):
    rows = []
    with open(path, "rb") as f:
        for aar in hist:
            for uke in range(jstart, jslutt + 1):
                for tsnitt in range(1, npenm + 1):
                    utv = struct.unpack(nfor*"f", f.read(nfor*4))
                    rows.append([aar, uke, tsnitt] + list(utv))
    return rows
