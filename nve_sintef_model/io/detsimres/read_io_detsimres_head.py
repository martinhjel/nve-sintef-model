import struct
import numpy as np

def read_io_detsimres_head(path):
    with open(path, "rb") as f:
        f.seek(0)
        lblokk, nmodsum, jstart, jslutt, nsim, npenm, nutv = struct.unpack(7*"i", f.read(7*4))
        ntimen = struct.unpack(npenm*"i", f.read(npenm*4))
        mapktsum, = struct.unpack(1*"i", f.read(1*4))
        serie, lses = struct.unpack(2*"i", f.read(2*4))

        f.seek(lblokk*1)
        iverk = struct.unpack(nutv*"i", f.read(nutv*4))
        nmodut = struct.unpack(nutv*"i", f.read(nutv*4))
        npump = struct.unpack(nutv*"i", f.read(nutv*4))
        navnut = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for i in range(nutv)]

        f.seek(lblokk*2)
        modnr = []
        magma = []
        pmax = [] 
        for nmod in nmodut:
            print(nmod)
            modnr.append(struct.unpack(nmod*"i", f.read(nmod*4)))
            magma.append(struct.unpack(nmod*"f", f.read(nmod*4)))
            pmax.append(struct.unpack(nmod*"f", f.read(nmod*4)))

        f.seek(lblokk*3)
        modulnavn = []
        for nmod in nmodut:
            modulnavn.append( [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for i in range(nmod)] )

        f.seek(lblokk*4)
        snavn = []
        for nmod in nmodut:
            snavn.append( [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for i in range(nmod)] )

        f.seek(lblokk*5)
        stmag = []
        eierandel = []
        sumenekv = []
        for nmod in nmodut:
            stmag.append(struct.unpack(nmod*"f", f.read(nmod*4)))
            eierandel.append(struct.unpack(nmod*"f", f.read(nmod*4)))
            sumenekv.append(struct.unpack(nmod*"f", f.read(nmod*4)))

        f.seek(lblokk*6)
        topo_st = []
        topo_forb = []
        topo_flom = []
        for nmod in nmodut:
            topo_st.append(struct.unpack(nmod*"i", f.read(nmod*4)))
            topo_forb.append(struct.unpack(nmod*"i", f.read(nmod*4)))
            topo_flom.append(struct.unpack(nmod*"i", f.read(nmod*4)))

        f.seek(lblokk*7)
        modulnr_pump = []
        modulnr_pump_til = []
        modulnr_pump_fra = []
        for i, nmod in enumerate(npump):
            modulnr_pump.append([])
            modulnr_pump_til.append([])
            modulnr_pump_fra.append([])
            for j in range(nmod):
                n_pump, n_pump_til, n_pump_fra = struct.unpack(3*"i", f.read(3*4))
                modulnr_pump[i].append(n_pump)
                modulnr_pump_til[i].append(n_pump_til)
                modulnr_pump_fra[i].append(n_pump_fra)

        f.seek(lblokk*8)
        runcode = struct.unpack(20*"c", f.read(20*1))

        f.seek(lblokk*9)
        hist = struct.unpack(nsim*"i", f.read(nsim*4))

        modnr_map = {(o,j+1) : n for i,o in enumerate(iverk) for j,n in enumerate(modnr[i])}

        d = dict()

        d["lblokk"] = lblokk
        d["nmodsum"] = nmodsum
        d["jstart"] = jstart
        d["jslutt"] = jslutt
        d["nsim"] = nsim
        d["npenm"] = npenm
        d["nutv"] = nutv
        d["ntimen"] = ntimen
        d["mapktsum"] = mapktsum
        d["serie"] = -1*serie
        d["lses"] = -1*lses
        d["iverk"] = iverk
        d["nmodut"] = nmodut
        d["npump"] = npump
        d["navnut"] = navnut
        d["modnr"] = modnr
        d["magma"] = magma
        d["pmax"] = pmax
        d["modulnavn"] = modulnavn
        d["snavn"] = snavn
        d["stmag"] = stmag
        d["eierandel"] = eierandel
        d["sumenekv"] = sumenekv
        d["topo_st"] = topo_st
        d["topo_forb"] = topo_forb
        d["topo_flom"] = topo_flom
        d["modulnr_pump"] = modulnr_pump
        d["modulnr_pump_til"] = modulnr_pump_til
        d["modulnr_pump_fra"] = modulnr_pump_fra
        d["runcode"] = runcode
        d["hist"] = hist
        d["modnr_map"] = modnr_map

    return d
    
def read_detsimres_params(h):
    import datetime
    params = ['nmodsum', 'jstart', 'jslutt', 'nsim', 'npenm', 'nutv', 'mapktsum', 'serie', 'lses', 'runcode']

    df = []
    for a in params:
        r = h[a]

        if a == 'runcode':
            r = "".join([x.decode('cp865','ignore') for x in r])

        df.append(r)

    df = pd.DataFrame([df], columns=params)

    return df


def read_detsimres_topologi(h):
    modnr = h.get("modnr")
    iverk = h.get("iverk")
    topo_st = h.get("topo_st")
    topo_forb = h.get("topo_forb")
    topo_flom = h.get("topo_flom")
    modnr_map = h.get("modnr_map")

    topo = []
    for i,o in enumerate(iverk):
        for j,n in enumerate(modnr[i]):
            topo.append( (o, n,
                          modnr_map.get((o,topo_st[i][j]), 0),
                          modnr_map.get((o,topo_forb[i][j]), 0),
                          modnr_map.get((o,topo_flom[i][j]), 0)
                         )
                       )

    cols = ["omrnr", "modnr", "topo_st", "topo_forb", "topo_flom"]

    return pandas.DataFrame.from_records(topo, columns=cols)

# TODO: disse bør bygges inn i detres_head objektet etter hvert.
def read_detsimres_module_table(h):
    iverk = h.get("iverk")
    navnut = h.get("navnut")
    modnr = h.get("modnr")
    magma = h.get("magma")
    pmax = h.get("pmax")
    pmax = h.get("pmax")
    modulnavn = h.get("modulnavn")
    snavn = h.get("snavn")
    sumenekv = h.get("sumenekv")
    stmag = h.get("stmag")

    module = []

    for i,o in enumerate(iverk):
        onavn = navnut[i]
        for j,n in enumerate(modnr[i]):
            module.append((o, onavn, n,
                           modulnavn[i][j],
                           snavn[i][j],
                           magma[i][j],
                           pmax[i][j],
                           sumenekv[i][j],
                           stmag[i][j]
                          )
                         )

    cols = ["omrnr", "omrnavn", "modnr", "modnavn", "stnavn",
            "magma", "pmax", "sumenekv", "stmag"]

    return pandas.DataFrame.from_records(module, columns=cols)

def read_detsimres_pumpe_table(h):
    iverk = h.get("iverk")
    npump = h.get("npump")
    modnr_map = h.get("modnr_map")
    modulnr_pump = h.get("modulnr_pump")
    modulnr_pump_til = h.get("modulnr_pump_til")
    modulnr_pump_fra = h.get("modulnr_pump_fra")

    pumpe = []

    for i,o in enumerate(iverk):
        for j,n in enumerate(modulnr_pump[i]):
            pumpe.append((o,
                          modnr_map.get((o,n),0),
                          modnr_map.get((o,modulnr_pump_til[i][j]),0),
                          modnr_map.get((o,modulnr_pump_fra[i][j]),0)
                         )
                        )

    cols = ["omrnr", "modnr", "modnr_til", "modnr_fra"]

    return pandas.DataFrame.from_records(pumpe, columns=cols)

