import struct

def read_io_dynmodell(path_file):

    blokk = 0
    with open(path_file, "rb") as f: # aapne fil i binear-lesemodus
        ibl, dynrel, nmod, npump, jant, nser = struct.unpack(6*"i", f.read(6*4))

        nrser = [b"".join(struct.unpack(40*"c", f.read(40*1))).strip() for i in range(nser)]

        eget, = struct.unpack(1*"i", f.read(1*4))
        eget = True if eget == -1 else False

        nkontrakt, = struct.unpack(1*"i", f.read(1*4))
        idkontrakt = struct.unpack(nkontrakt*"i", f.read(nkontrakt*4))
        medtid = struct.unpack(7*"i", f.read(7*4))
        nmapktsum, bytepq = struct.unpack(2*"i", f.read(2*4))

        # leser moduldata for hver uke
        
        moduldata_keys = ["mamax", "mamin", "magref", "enekv_uke", "qmax", "qmin", "qfomin"]
        moduldata = {k : [] for k in moduldata_keys}
        
        pumpedata_keys = ["magpt", "magpf"]
        pumpedata = {k : [] for k in pumpedata_keys}
        
        for uke in range(1, jant+1):
            blokk += 1
            f.seek(ibl*blokk)
            
            moduldata_row = {k : [uke] for k in moduldata_keys}
            for n in range(1, nmod+1):
                values = struct.unpack(7*"f", f.read(7*4))
                for i,k in enumerate(moduldata_keys):
                    moduldata_row[k].append(values[i])
            for k in moduldata_keys:
                moduldata[k].append(moduldata_row[k])
                    
            pumpedata_row = {k : [uke] for k in pumpedata_keys}
            for n in range(1, npump+1):
                values = struct.unpack(2*"i", f.read(2*4))
                for i,k in enumerate(pumpedata_keys):
                    pumpedata_row[k].append(values[i])
            for k in pumpedata_keys:
                pumpedata[k].append(pumpedata_row[k])
                    
        # hopper videre til neste blokk (rec=jant+2 i dok)
        blokk = (jant + 2) - 1
        f.seek(ibl*blokk)
        modnr = struct.unpack(nmod*"i", f.read(nmod*4))
        mnavn = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for n in modnr]
        nvassdrag, = struct.unpack(1*"i", f.read(1*4))

        # hopper videre til neste blokk (rec=jant+3 i dok)
        blokk = (jant + 3) - 1
        f.seek(ibl*blokk)
        snavn = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for n in modnr]
        eierandel = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+4 i dok)
        blokk = (jant + 4) - 1
        f.seek(ibl*blokk)
        index_reg    = struct.unpack(nmod*"i", f.read(nmod*4))
        index_ureg   = struct.unpack(nmod*"i", f.read(nmod*4))
        index_qmin   = struct.unpack(nmod*"i", f.read(nmod*4))
        index_qmax   = struct.unpack(nmod*"i", f.read(nmod*4))
        index_qfomin = struct.unpack(nmod*"i", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+5 i dok)
        blokk = (jant + 5) - 1
        f.seek(ibl*blokk)
        uv = struct.unpack(nmod*"f", f.read(nmod*4))
        ho = struct.unpack(nmod*"f", f.read(nmod*4))
        magma = struct.unpack(nmod*"f", f.read(nmod*4))
        urmid = struct.unpack(nmod*"f", f.read(nmod*4))
        urbmid = struct.unpack(nmod*"f", f.read(nmod*4))
        qmaxfast = struct.unpack(nmod*"f", f.read(nmod*4))
        qmaxforb = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+6 i dok)
        blokk = (jant + 6) - 1
        f.seek(ibl*blokk)
        imodtyp = struct.unpack(nmod*"i", f.read(nmod*4))
        enekv = struct.unpack(nmod*"f", f.read(nmod*4))
        mamaxtyp = struct.unpack(nmod*"i", f.read(nmod*4))
        mamintyp = struct.unpack(nmod*"i", f.read(nmod*4))
        bunnmag = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+7 i dok)
        blokk = (jant + 7) - 1
        f.seek(ibl*blokk)
        # leser topoligimatrise
        topo_st = struct.unpack(nmod*"i", f.read(nmod*4))
        topo_forb = struct.unpack(nmod*"i", f.read(nmod*4))
        topo_flom = struct.unpack(nmod*"i", f.read(nmod*4))
        topo = zip(topo_st, topo_forb, topo_flom)

        # leser hydraulisk kobling
        # feil rekkefolge paa kobl og kap i dokumentasjon 
        # leser i riktig rekkefolge her!
        hydraul_kode = struct.unpack(nmod*"i", f.read(nmod*4))
        hydraul_kap = struct.unpack(nmod*"i", f.read(nmod*4))
        hydraul_kobl = struct.unpack(nmod*"i", f.read(nmod*4))

        # leser pmax
        pmax = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+8 i dok)
        blokk = (jant + 8) - 1
        f.seek(ibl*blokk)
        # leser reguleringsgrad og regulerings-eller buffermagasin
        vmag = struct.unpack(nmod*"f", f.read(nmod*4))
        regmag = struct.unpack(nmod*"i", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+9 i dok)
        blokk = (jant + 9) - 1
        f.seek(ibl*blokk)

        pump_st  = []
        pump_til = []
        pump_fra = []
        for n in range(1, npump + 1):
            p_st, p_til, p_fra = struct.unpack(3*"i", f.read(3*4))
            pump_st.append(p_st)
            pump_til.append(p_til)
            pump_fra.append(p_fra)

        pump_mw  = []
        pump_h   = []
        pump_q   = []
        for n in range(1, npump + 1):
            kap_ms, hoyde_m, kap_mw = struct.unpack(3*"f", f.read(3*4))
            pump_mw.append(kap_mw)
            pump_h.append(hoyde_m)
            pump_q.append(kap_ms)

        pnavn = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for n in range(npump)]
        eierpump = struct.unpack(npump*"f", f.read(npump*4))

        # hopper videre til neste blokk (rec=jant+10 i dok)
        # her ser det ut til aa vaere avvik mellom biearfildata og rapportdata (vansimtap doku rark)
        blokk = (jant + 10) - 1
        f.seek(ibl*blokk)
        nqvar, = struct.unpack(1*"i", f.read(1*4))
        iqvar = struct.unpack(nqvar*"i", f.read(nqvar*4))
        qvar = [struct.unpack(10*"f", f.read(10*4)) for i in range(nqvar)]


    # datastruktur som skal brukes til aa returnere dataene fra filen
    d = dict()
    
    d.update(moduldata) #jeg vet ikke helt hva denne gjør
    d.update(pumpedata)

    d["ibl"]          = ibl
    d["dynrel"]       = dynrel
    d["nmod"]         = nmod
    d["npump"]        = npump
    d["eget"]         = eget
    d["jant"]         = jant
    d["nser"]         = nser
    d["nrser"]        = nrser
    d["nkontrakt"]    = nkontrakt
    d["idkontrakt"]   = idkontrakt
    d["medtid"]       = medtid
    d["nmapktsum"]    = nmapktsum
    d["bytepq"]       = bytepq
    d["modnr"]        = modnr
    d["mnavn"]        = mnavn
    d["nvassdrag"]    = nvassdrag
    d["snavn"]        = snavn
    d["eierandel"]    = eierandel
    d["index_reg"]    = index_reg
    d["index_ureg"]   = index_ureg
    d["index_qmin"]   = index_qmin
    d["index_qmax"]   = index_qmax
    d["index_qfomin"] = index_qfomin
    d["uv"]           = uv
    d["ho"]           = ho
    d["magma"]        = magma
    d["urmid"]        = urmid
    d["urbmid"]       = urbmid
    d["qmaxfast"]     = qmaxfast
    d["qmaxforb"]     = qmaxforb
    d["imodtyp"]      = imodtyp
    d["enekv"]        = enekv
    d["mamaxtyp"]     = mamaxtyp
    d["mamintyp"]     = mamintyp
    d["bunnmag"]      = bunnmag
    d["topo_st"]      = topo_st
    d["topo_forb"]    = topo_forb
    d["topo_flom"]    = topo_flom
    d["hydraul_kode"] = hydraul_kode
    d["hydraul_kobl"] = hydraul_kobl
    d["hydraul_kap"]  = hydraul_kap
    d["pmax"]         = pmax
    d["vmag"]         = vmag
    d["regmag"]       = regmag

    d["pump_st"]      = pump_st
    d["pump_fra"]     = pump_fra
    d["pump_til"]     = pump_til
    d["pump_mw"]      = pump_mw
    d["pump_h"]       = pump_h
    d["pump_q"]       = pump_q

    d["pnavn"]        = pnavn
    d["eierpump"]     = eierpump
    d["nqvar"] = nqvar
    d["iqvar"] = iqvar
    d["qvar"] = qvar
    
    return d
    
#TODO: samkjøre disse to dynmodell-lesefunksjonene! (valentin bruker den nederste) har noen forskjeller i topologi og moduldata
    
def read_io_dynmodell_vak(path_file):
    """
    leser vannkraftdata fra en dynmodelfil (enten vansimtap eller samkjoringsmodellen)
    og returnerer dataene i python-dict.

    Dokumentasjon av binearfilen finnes paa side 16 i dokumentet AN Filstruktur_V9.pdf
    """
    import struct

    blokk = 0
    with open(path_file, "rb") as f: # aapne fil i binear-lesemodus
        # sorg for aa starte paa forste byte i filen
        f.seek(blokk)

        # leser 6 heltall. hvert heltall tar 4 bytes
        ibl, dynrel, nmod, npump, jant, nser = struct.unpack(6*"i", f.read(6*4))

        # for hver serie i, les 40 bokstaver og slaa de sammen til en string og fjern overflodige mellomrom
        # resulterer i en liste med navn paa tilsigsseriene som er brukt
        nrser = [b"".join(struct.unpack(40*"c", f.read(40*1))).strip() for i in range(nser)]

        # leser 1 heltall, som tar 4 bytes
        # gjor saa om til True eller False
        eget, = struct.unpack(1*"i", f.read(1*4))
        eget = True if eget == -1 else False

        # leser flere heltall paa samme maate som over
        nkontrakt, = struct.unpack(1*"i", f.read(1*4))
        idkontrakt = struct.unpack(nkontrakt*"i", f.read(nkontrakt*4))
        medtid = struct.unpack(7*"i", f.read(7*4))
        nmapktsum, bytepq = struct.unpack(2*"i", f.read(2*4))

        # leser moduldata for hver uke
        moduldata = []
        pumpedata = []
        for uke in range(1, jant+1):
            blokk += 1
            f.seek(ibl*blokk)
            for n in range(1, nmod+1):
                # leser 7 flyttall. hvert flyttall tar 4 bytes
                # lagrer dataene i listen moduldata
                mamax, mamin, magref, enekv, qmax, qmin, qfomin = struct.unpack(7*"f", f.read(7*4))
                moduldata.append((uke, n, mamax, mamin, magref, enekv, qmax, qmin, qfomin))
            for n in range(1, npump+1):
                magpt, magpf = struct.unpack(2*"i", f.read(2*4))
                pumpedata.append((uke, n, magpt, magpf))

        # hopper videre til neste blokk (rec=jant+2 i dok)
        blokk = (jant + 2) - 1
        f.seek(ibl*blokk)
        modnr = struct.unpack(nmod*"i", f.read(nmod*4))
        mnavn = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for n in modnr]
        nvassdrag, = struct.unpack(1*"i", f.read(1*4))

        # hopper videre til neste blokk (rec=jant+3 i dok)
        blokk = (jant + 3) - 1
        f.seek(ibl*blokk)
        snavn = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for n in modnr]
        eierandel = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+4 i dok)
        blokk = (jant + 4) - 1
        f.seek(ibl*blokk)
        index_reg = struct.unpack(nmod*"i", f.read(nmod*4))
        index_ureg = struct.unpack(nmod*"i", f.read(nmod*4))
        index_qmin = struct.unpack(nmod*"i", f.read(nmod*4))
        index_qmax = struct.unpack(nmod*"i", f.read(nmod*4))
        index_qfomin = struct.unpack(nmod*"i", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+5 i dok)
        blokk = (jant + 5) - 1
        f.seek(ibl*blokk)
        uv = struct.unpack(nmod*"f", f.read(nmod*4))
        ho = struct.unpack(nmod*"f", f.read(nmod*4))
        magma = struct.unpack(nmod*"f", f.read(nmod*4))
        urmid = struct.unpack(nmod*"f", f.read(nmod*4))
        urbmid = struct.unpack(nmod*"f", f.read(nmod*4))
        qmaxfast = struct.unpack(nmod*"f", f.read(nmod*4))
        qmaxforb = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+6 i dok)
        blokk = (jant + 6) - 1
        f.seek(ibl*blokk)
        imodtyp = struct.unpack(nmod*"i", f.read(nmod*4))
        enekv = struct.unpack(nmod*"f", f.read(nmod*4))
        mamaxtyp = struct.unpack(nmod*"i", f.read(nmod*4))
        mamintyp = struct.unpack(nmod*"i", f.read(nmod*4))
        bunnmag = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+7 i dok)
        blokk = (jant + 7) - 1
        f.seek(ibl*blokk)
        # leser topoligimatrise
        topo_sta = struct.unpack(nmod*"i", f.read(nmod*4))
        topo_forb = struct.unpack(nmod*"i", f.read(nmod*4))
        topo_flom = struct.unpack(nmod*"i", f.read(nmod*4))
        topo = zip(topo_sta, topo_forb, topo_flom)
        # leser hydraulisk kobling
        hydraul_kode = struct.unpack(nmod*"i", f.read(nmod*4))
        hydraul_kobl = struct.unpack(nmod*"i", f.read(nmod*4))
        hydraul_kap = struct.unpack(nmod*"i", f.read(nmod*4))
        hydraul = zip(hydraul_kode, hydraul_kobl, hydraul_kap)
        # leser pmax
        pmax = struct.unpack(nmod*"f", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+8 i dok)
        blokk = (jant + 8) - 1
        f.seek(ibl*blokk)
        # leser reguleringsgrad og regulerings-eller buffermagasin
        vmag = struct.unpack(nmod*"f", f.read(nmod*4))
        regmag = struct.unpack(nmod*"i", f.read(nmod*4))

        # hopper videre til neste blokk (rec=jant+9 i dok)
        blokk = (jant + 9) - 1
        f.seek(ibl*blokk)
        idpump = []
        for n in range(1, npump + 1):
            pump_st, mag_til, mag_fra = struct.unpack(3*"i", f.read(3*4))
            idpump.append((n, pump_st, mag_til, mag_fra))

        pumka = []
        for n in range(1, npump + 1):
            kap_mw, hoyde_m, kap_ms = struct.unpack(3*"f", f.read(3*4))
            pumka.append((n, kap_mw, kap_ms, hoyde_m))

        pnavn = [b"".join(struct.unpack(20*"c", f.read(20*1))).strip() for n in range(npump)]
        eierpump = struct.unpack(npump*"f", f.read(npump*4))

        # hopper videre til neste blokk (rec=jant+10 i dok)
        # her ser det ut til aa vaere avvik mellom biearfildata og rapportdata (vansimtap doku rark)
        blokk = (jant + 10) - 1
        f.seek(ibl*blokk)
        nqvar, = struct.unpack(1*"i", f.read(1*4))
        iqvar = struct.unpack(nqvar*"i", f.read(nqvar*4))
        qvar = [struct.unpack(10*"f", f.read(10*4)) for i in range(nqvar)]


        # de siste to blokkene angaar datatyper som vi ikke modellerer
        # dokumentasjonen ser ut til aa vaere daarlig ogsaa

        # hopper videre til neste blokk (rec=jant+12 i dok)
        # usikker paa om denne leses rikig. har ikke testet
        blokk = (jant + 12) - 1
        f.seek(ibl*blokk)
        nkon, = struct.unpack(1*"i", f.read(1*4))
        nperkon = struct.unpack(nkon*"i", f.read(nkon*4))
        inrkon = struct.unpack(nkon*"i", f.read(nkon*4))
        imodkon = [struct.unpack(n*"i", f.read(n*4)) for n in nperkon]

        # hopper videre til neste blokk (rec=jant+11 i dok)
        # usikker paa om denne leses rikig. har ikke testet
        blokk = (jant + 13) - 1
        f.seek(ibl*blokk)
        jstkon = [struct.unpack(n*"i", f.read(n*4)) for n in nperkon]
        jslebet = [struct.unpack(n*"i", f.read(n*4)) for n in nperkon]
        volkon = [struct.unpack(n*"i", f.read(n*4)) for n in nperkon] # denne bor jo vaere flyttall!!! Elendig dok?

    # datastruktur som skal brukes til aa returnere dataene fra filen
    d = dict()
    d["ibl"] = ibl
    d["dynrel"] = dynrel
    d["nmod"] = nmod
    d["npump"] = npump
    d["eget"] = eget
    d["jant"] = jant
    d["nser"] = nser
    d["nrser"] = nrser
    d["nkontrakt"] = nkontrakt
    d["idkontrakt"] = idkontrakt
    d["medtid"] = medtid
    d["nmapktsum"] = nmapktsum
    d["bytepq"] = bytepq
    d["moduldata"] = moduldata
    d["pumpedata"] = pumpedata
    d["modnr"] = modnr
    d["mnavn"] = mnavn
    d["nvassdrag"] = nvassdrag
    d["snavn"] = snavn
    d["eierandel"] = eierandel
    d["index_reg"] = index_reg
    d["index_ureg"] = index_ureg
    d["index_qmin"] = index_qmin
    d["index_qmax"] = index_qmax
    d["index_qfomin"] = index_qfomin
    d["uv"] = uv
    d["ho"] = ho
    d["magma"] = magma
    d["urmid"] = urmid
    d["urbmid"] = urbmid
    d["qmaxfast"] = qmaxfast
    d["qmaxforb"] = qmaxforb
    d["imodtyp"] = imodtyp
    d["enekv"] = enekv
    d["mamaxtyp"] = mamaxtyp
    d["mamintyp"] = mamintyp
    d["bunnmag"] = bunnmag
    d["topo"] = topo
    d["hydraul"] = hydraul
    d["pmax"] = pmax
    d["vmag"] = vmag
    d["regmag"] = regmag
    d["idpump"] = idpump
    d["pumka"] = pumka
    d["pnavn"] = pnavn
    d["eierpump"] = eierpump
    d["nqvar"] = nqvar
    d["iqvar"] = iqvar
    d["qvar"] = qvar
    d["nkon"] = nkon
    d["nperkon"] = nperkon
    d["inrkon"] = inrkon
    d["imodkon"] = imodkon
    d["jstkon"] = jstkon
    d["jslebet"] = jslebet
    d["volkon"] = volkon
    return d

    

def read_dynmodell_topologi(d):
    import pandas
    modnr = d.get("modnr")
    # lager en mapping
    modnr_map = {i+1 : n for i,n in enumerate(modnr)}

    topo = d.get("topo")

    topo = pandas.DataFrame(list(topo), columns=["topo_st", "topo_forb", "topo_flom"])
    topo["modnr"] = topo.index + 1

    # bytter rekkefolge paa kolonnene
    topo = topo[["modnr", "topo_st", "topo_forb", "topo_flom"]]

    # bytter ut internid med modulnr
    default = 0
    topo["modnr"] = topo["modnr"].apply(lambda x : modnr_map.get(x, default))
    topo["topo_st"] = topo["topo_st"].apply(lambda x : modnr_map.get(x, default))
    topo["topo_forb"] = topo["topo_forb"].apply(lambda x : modnr_map.get(x, default))
    topo["topo_flom"] = topo["topo_flom"].apply(lambda x : modnr_map.get(x, default))

    return topo

def read_dynmodell_modul_uke(d):
    import pandas
    modnr = d.get("modnr")
    modnr_map = {i+1 : n for i,n in enumerate(modnr)}

    df = d.get("moduldata")
    columns=["uke", "modnr", "mamax", "mamin", "magref", "enekv", "qmax", "qmin", "qfomin"]
    df = pandas.DataFrame(df, columns=columns)

    # bytter ut internid med modulnr
    default = 0
    df["modnr"] = df["modnr"].apply(lambda x : modnr_map.get(x, default))


    #df = df.reset_index()
    return df

def read_dynmodell_params(d):
    """lager dataframe med generelle simuleringsparemetere fra dynmodell"""
    import datetime
    import pandas as pd
    params = ['nmod','npump','jant','nser','eget','medtid','nmapktsum','bytepq','nvassdrag']

    df = []
    for a in params:
        r = d[a]
        if a == 'medtid':
            #convert time to timestamp

            r = datetime.datetime(year=r[6], month=r[5], day=r[4], hour=r[3],minute=r[2],second=r[1])

        df.append(r)

    df = pd.DataFrame([df],columns=params)

    return df
    
def read_dynmodell_modul(d):
    import pandas
    modnr = d.get("modnr")
    mnavn = d.get("mnavn")
    mnavn = [s.decode("cp865",'ignore') for s in mnavn]
    snavn = d.get("snavn")
    snavn = [s.decode("cp865",'ignore') for s in snavn]
    uv = d.get("uv")
    ho = d.get("ho")
    magma = d.get("magma")
    urmid = d.get("urmid")
    urbmid = d.get("urbmid")
    qmaxfast = d.get("qmaxfast")
    qmaxforb = d.get("qmaxforb")
    mamaxtyp = d.get("mamaxtyp")
    mamintyp = d.get("mamintyp")
    bunnmag = d.get("bunnmag")
    pmax = d.get("pmax")
    vmag = d.get("vmag")
    regmag = d.get("regmag")
    reg_tilsig = d.get("urmid")
    ureg_tilsig = d.get("urbmid")

    # sette navn på tilsigsserier
    reg_serie = [d.get("nrser")[s - 1] for s in d.get("index_reg")]
    ureg_serie = [d.get("nrser")[s - 1] for s in d.get("index_ureg")]

    # gjøre om bytestring til string
    reg_serie = [x.decode("cp865",'ignore') for x in reg_serie]
    ureg_serie = [x.decode("cp865",'ignore') for x in ureg_serie]

    data = [i for i in zip(modnr, mnavn, snavn, uv, ho, magma,
                           urmid, urbmid, qmaxfast, qmaxforb,
                           mamaxtyp, mamintyp, bunnmag, pmax,
                           vmag, regmag, reg_tilsig, ureg_tilsig, reg_serie, ureg_serie)]
    columns = ["modnr", "mnavn","snavn", "uv", "ho", "magma",
               "urmid", "urbmid", "qmaxfast", "qmaxforb",
               "mamaxtyp", "mamintyp", "bunnmag", "pmax",
               "reggrad", "regmag", "reg_tilsig", "ureg_tilsig", "reg_serie", "ureg_serie"]
    df = pandas.DataFrame(data, columns=columns)

    return df