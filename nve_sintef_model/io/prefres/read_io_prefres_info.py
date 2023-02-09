
import struct

def read_io_prefres_info(path):
    "leser sekves/info.data"
    d = dict()
    with open(path, "rb") as f:
        d["iverprefres"],    d["irecl_infofil"],  d["irecl_prefres"]                                = struct.unpack("i"*3,f.read(4*3))
        d["irecl_peg_pkrv"], d["irecl_maske"],    d["jstart"],        d["jslutt"],   d["jslutt_st"] = struct.unpack("i"*5,f.read(4*5))
        d["npenm_u"],        d["npenm"],          d["npref_m_start"], d["ntrinnsum"]                = struct.unpack("i"*4,f.read(4*4))
        d["nfor"],           d["nverk"],          d["npre"]                                         = struct.unpack("i"*3,f.read(4*3))
    return d

