import struct

def read_io_sapref28(path, ntrinnsum, npenm, nuke, ntrinn, nverk):
    """
    Leser bare typek, pris og mengde fra denne fila, det andre
    finnes i trinnlisten og ser til og med ut til aa vaere feil i
    denne fila

    path          - sti til sapref28-fil
    ntrinnsum     - totalt antall trinn i modellen
    ntrinn        - dict[omrnr] = ntrinn
    npenm         - antall tidsavsnitt
    nuke          - antall uker i dataperioden
    nverk         - antall delomraader
    """
    d = dict()
    
    d["typek"]        = []
    d["pris"]         = []
    d["mengde"]       = []
    
    blengde = ntrinnsum*4
    with open(path, "rb") as f:
        
        for uke in range(1, nuke + 1):
            
            blokk = (uke-1)*(npenm+2) + 3
            f.seek(blokk*blengde)
            d["typek"].append(struct.unpack("i"*ntrinnsum, f.read(4*ntrinnsum)))
            
            blokk = (uke-1)*(npenm+2) + 4
            f.seek(blokk*blengde)
            d["pris"].append(struct.unpack("f"*ntrinnsum, f.read(4*ntrinnsum)))
            
            for tsnitt in range(1, npenm + 1):
                blokk = (uke-1) + 5 + tsnitt
                f.seek(blokk*blengde)
                d["mengde"].append(struct.unpack("f"*ntrinnsum, f.read(4*ntrinnsum)))
            
    return d
