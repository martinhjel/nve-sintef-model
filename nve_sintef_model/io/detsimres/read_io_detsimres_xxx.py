import struct

def read_io_detsimres_xxx(path, aar, jstart, jslutt, nutv, iverk, npenm, nmodut, nmodsum):
    
    keys = ["totmag", "sumflo", "peg", "sumfor", "elpump", 
            "qpump", "m", "flom", "tilsig", "pn", "qt", "qfor"]
    
    uke_keys    = ["totmag", "sumflo", "m", "flom", "tilsig"]
    tsnitt_keys = ["peg", "sumfor", "elpump", "qpump", "pn", "qt", "qfor"]    
    
    tsnitt_liste = list(range(1, npenm + 1))

    d = {key : [] for key in keys}

    blengde = ( nutv*(2 + 4*npenm) + nmodsum*(3 + 3*npenm) )*4
    blokk = 0
    
    uke_index = 0
    tsnitt_index = 0

    with open(path, "rb") as f:

        for uke in range(jstart, jslutt + 1):

            f.seek(blengde*blokk)
            
            # init ukerader
            uke_rows = dict()
            for k in uke_keys:
                uke_rows[k] = [aar, uke]
                
            # init tsnittrader
            tsnitt_rows = dict()
            for k in tsnitt_keys:
                tsnitt_rows[k] = []
                for tsnitt in tsnitt_liste:
                    tsnitt_rows[k].append([aar, uke, tsnitt])

            for i,omrnr in enumerate(iverk):

                nmod = nmodut[i]
                
                for key in ["totmag", "sumflo"]:
                    uke_rows[key].extend(list(struct.unpack("f", f.read(4)))) 
                    
                for key in ["peg", "sumfor", "elpump", "qpump"]:
                    for i,tsnitt in enumerate(tsnitt_liste):
                        tsnitt_rows[key][i].extend(list(struct.unpack("f", f.read(4))))
                        
                for key in ["m", "flom", "tilsig"]:
                    uke_rows[key].extend(list(struct.unpack(nmod*"f", f.read(nmod*4))))
                    
                for i,tsnitt in enumerate(tsnitt_liste):
                    for key in ["pn", "qt", "qfor"]:
                        tsnitt_rows[key][i].extend(list(struct.unpack(nmod*"f", f.read(nmod*4)))) 
                        
            for key in uke_keys:
                d[key].append(uke_rows[key])
                
            for key in tsnitt_keys:
                for i,tsnitt in enumerate(tsnitt_liste):
                    d[key].append(tsnitt_rows[key][i])

            blokk += 1

    return d

#TODO: samkjøre read io destimres_xxx_vak
def read_io_detsimres_xxx_vak(path, h):
    jstart = h.get("jstart")
    jslutt = h.get("jslutt")
    nutv = h.get("nutv")
    iverk = h.get("iverk")
    npenm = h.get("npenm")
    nmodut = h.get("nmodut")
    nmodsum = h.get("nmodsum")

    d = dict()

    blengde = ( nutv*(2 + 4*npenm) + nmodsum*(3 + 3*npenm) )*4
    blokk = 0

    with open(path, "rb") as f:

        for uke in range(jstart, jslutt + 1):

            f.seek(blengde*blokk)

            for i,omrnr in enumerate(iverk):

                nmod = nmodut[i]

                if uke not in d:
                    d[uke] = dict()

                if omrnr not in d[uke]:
                    d[uke][omrnr] = dict()

                d[uke][omrnr]["totmag"] = struct.unpack(1*"f", f.read(1*4))[0]
                d[uke][omrnr]["sumflo"] = struct.unpack(1*"f", f.read(1*4))[0]

                d[uke][omrnr]["peg"] = struct.unpack(npenm*"f", f.read(npenm*4))
                d[uke][omrnr]["sumfor"] = struct.unpack(npenm*"f", f.read(npenm*4))
                d[uke][omrnr]["elpump"] = struct.unpack(npenm*"f", f.read(npenm*4))
                d[uke][omrnr]["qpump"] = struct.unpack(npenm*"f", f.read(npenm*4))

                d[uke][omrnr]["m"] = struct.unpack(nmod*"f", f.read(nmod*4))
                d[uke][omrnr]["flom"] = struct.unpack(nmod*"f", f.read(nmod*4))
                d[uke][omrnr]["tilsig"] = struct.unpack(nmod*"f", f.read(nmod*4))

                d[uke][omrnr]["pn"] = dict()
                d[uke][omrnr]["qt"] = dict()
                d[uke][omrnr]["qfor"] = dict()

                for j in range(npenm):
                    d[uke][omrnr]["pn"][j] = struct.unpack(nmod*"f", f.read(nmod*4))
                    d[uke][omrnr]["qt"][j] = struct.unpack(nmod*"f", f.read(nmod*4))
                    d[uke][omrnr]["qfor"][j] = struct.unpack(nmod*"f", f.read(nmod*4))

            blokk += 1

    return d

    
def read_detsimres_params(h):
    import datetime
    import pandas as pd
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
    import pandas
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


def read_detsimres_module_table(h):
    import pandas
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
    
    m = pandas.DataFrame.from_records(module, columns=cols)
    # Dekode modulcharset før det går videre
    m.omrnavn = m.omrnavn.apply(lambda x: x.decode("cp865", "ignore"))
    m.modnavn = m.modnavn.apply(
        lambda x: x.decode("cp865", "ignore").replace("\\", "Ø").replace("[", "Æ").replace("]", "Å"))
    m.stnavn = m.stnavn.apply(
        lambda x: x.decode("cp865", "ignore").replace("\\", "Ø").replace("[", "Æ").replace("]", "Å"))

    return m

def read_detsimres_pumpe_table(h):
    import pandas
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

def read_detsimres_omr_uke(n, d, h):
    import pandas
    y = h["hist"][n-1]
    iverk = h.get("iverk")
    jstart = h.get("jstart")
    jslutt = h.get("jslutt")
    npenm = h.get("npenm")
     #skrive ut tidsavsnittdata

    r = [(o, y, u,
          d[u][o]["totmag"],
          d[u][o]["sumflo"]
         ) for u in range(jstart, jslutt+1) for o in iverk]

    r_tsnitt = [(o, y, u, i,
          d[u][o]["peg"][i],
          d[u][o]["sumfor"][i],
          d[u][o]["elpump"][i],
          d[u][o]["qpump"][i]
         ) for u in range(jstart, jslutt+1) for o in iverk for i in range(npenm)]

    cols = ["omrnr", "aar", "uke","totmag", "sumflo"]
    cols_tsnitt = ["omrnr", "aar", "uke", "tsnitt", "peg", "sumfor", "elpump", "qpump"]

    df = pandas.DataFrame.from_records(r, columns=cols)
    df_tsnitt = pandas.DataFrame.from_records(r_tsnitt, columns=cols_tsnitt)

    return [df, df_tsnitt]

def read_detsimres_modul_uke(n, d, h):
    import pandas
    y = h["hist"][n-1]
    iverk = h.get("iverk")
    modnr = h.get("modnr")
    jstart = h.get("jstart")
    jslutt = h.get("jslutt")
    npenm = h.get("npenm")
    ntimen = h.get("ntimen")

    r = []


    for u in range(jstart, jslutt+1):
        for i,o in enumerate(iverk):
            for m,v,a,b in zip(modnr[i], d[u][o]["m"], d[u][o]["flom"], d[u][o]["tilsig"]):
                r.append((o, y, u, m, v, a, b))


    cols = ["omrnr", "aar", "uke", "modnr", "m", "flom", "tilsig"]

    df = pandas.DataFrame.from_records(r, columns=cols)

    return df

def read_detsimres_modul_uke_tsnitt(n, d, h):
    import pandas
#     lager dataframe istedenfor sql
    y = h["hist"][n-1]
    iverk = h.get("iverk")
    modnr = h.get("modnr")
    jstart = h.get("jstart")
    jslutt = h.get("jslutt")
    npenm = h.get("npenm")
    ntimen = h.get("ntimen")

    r = []

    #vurdere å dele på 168 om det gjør ting enklere
    ts_weights = {ts : t for ts,t in enumerate(ntimen)}
    for u in range(jstart, jslutt+1):
        for i,o in enumerate(iverk):
            for ts in range(npenm):
                for m,pn,qt,qfor in zip(modnr[i], d[u][o]['pn'][ts], d[u][o]['qt'][ts], d[u][o]['qfor'][ts]):
                    r.append((o, m, y, u, ts+1, ts_weights[ts], pn, qt, qfor))



    cols = ["omrnr", "modnr", "aar", "uke", "tsnitt",  "vekt", 'pn', 'qt', 'qfor']

    df = pandas.DataFrame.from_records(r, columns=cols)
    #print(df)


    return df


