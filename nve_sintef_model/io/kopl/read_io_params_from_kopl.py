import struct

def read_io_params_from_kopl(path):
    """
    leser ut modellparametere som trengs for aa lese minmax.samk
    verdiene hentes fra filen kopl.samk, men de kan ogsaa hentes fra
    samres.samk eller andre filer i emps
    
    path  - sti til kopl.samk
    nverk - antall delomraader i modellen
    nuke  - antall uker i simuleringsperioden
    npenm - antall tidsavsnitt i simuleringen
    """

    with open(path, "rb") as f:
        nverk, nuke, npenm = struct.unpack("i"*3, f.read(4*3))

    return nverk, nuke, npenm

