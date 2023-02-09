import struct

def read_io_prefres_xxx(path, aar, jstart, jslutt, npenm, ntrinnsum, blengde, sumtrinn_order_dict):
    """
    path                - sti til prefres_xx-fil
    aar                 - simulert aar
    jstart              - startuke
    jslutt              - sluttuke
    npenm               - antall prisavsnitt
    ntrinnsum           - totalt anntal trinn
    blengde             - blokklengde paa filen
    """
    d = []
    with open(path, "rb") as f:
        for uke in range(jstart, jslutt + 1):
            sumtrinn_order = sumtrinn_order_dict[uke]
            for tsnitt in range(1, npenm + 1):
                blokk = (uke - jstart)*npenm + tsnitt - 1 
                f.seek(blokk*blengde)
                values = struct.unpack("f"*ntrinnsum, f.read(4*ntrinnsum))
                values = [i for i in zip(sumtrinn_order, values)]
                values = sorted(values)
                values = [x[1] for x in values]
                d.append([aar, uke, tsnitt] + values)
    return d
