import os
import struct
import numpy as np
import pandas as pd
import datetime
from copy import deepcopy

def read_energy_inflow_file(path):
    """
    Denne funksjonen leser .U30 og .R30 filer til samkjoringsmodellen
    dokumentert paa side 10 i AN_Filstruktur.pdf
    
    input: path : sti til fil
    output: dictionary med innhold til filen
            d = dict()
            d["nuke"] = nuke
            d["staar"] = staar
            d["naar"] = naar
            d["tid"] = tid
            d["tekst"] = tekst
            d["kbrudd"] = kbrudd
            d["jstbrudd"] = jstbrudd
            d["jslbrudd"] = jslbrudd
            d["blokklengde"] = blokklengde
            d["tilsig"] = dict[aar] -> [tilsig uke 1, tilsig uke 2, ..., tilsig nuke]    
    """
    
    NRWORD = 1
    NWBYTE = 4

    with open(path, "rb") as f:

        # les blokk 0 (dvs. fra start av filen)
        nuke,  = struct.unpack("h", f.read(2))
        staar, = struct.unpack("h", f.read(2))
        naar,  = struct.unpack("h", f.read(2))

        tid = struct.unpack("h"*7, f.read(2*7))

        tekst = struct.unpack("c"*48, f.read(1*48))
        tekst = "".join(c.decode("ascii") for c in tekst)

        kbrudd, = struct.unpack("h", f.read(2))
        jstbrudd, = struct.unpack("h", f.read(2))
        jslbrudd, = struct.unpack("h", f.read(2))


        blokklengde = nuke * NRWORD * NWBYTE

        # lese blokk 1 og utover
        
        tilsig_dict = dict()
        
        iar = 1
        aar = staar
        for __ in range(naar):

            f.seek(blokklengde * iar)
            tilsig = struct.unpack("f"*nuke, f.read(4*nuke))
            
            tilsig_dict[aar] = tilsig

            iar += 1
            aar += 1

    d = dict()
    d["nuke"] = nuke
    d["staar"] = staar
    d["naar"] = naar
    d["tid"] = tid
    d["tekst"] = tekst
    d["kbrudd"] = kbrudd
    d["jstbrudd"] = jstbrudd
    d["jslbrudd"] = jslbrudd
    d["blokklengde"] = blokklengde
    d["tilsig"] = tilsig_dict
    
    return d



def write_energy_inflow_file(path, d):
    """
    skriver energitilsig til fil (.U30 eller .R30) paa plassering path

    datastrukturen d som inneholder innholdet som skal skrives til filen
    er paa samme format som returneres fra funksjonen read_energy_inflow_file(path)

    dette formatet er:
            d = dict()
            d["nuke"] = nuke
            d["staar"] = staar
            d["naar"] = naar
            d["tid"] = tid
            d["tekst"] = tekst
            d["kbrudd"] = kbrudd
            d["jstbrudd"] = jstbrudd
            d["jslbrudd"] = jslbrudd
            d["blokklengde"] = blokklengde
            d["tilsig"] = dict[aar] -> [tilsig uke 1, tilsig uke 2, ..., tilsig nuke]    

    """

    with open(path, "wb") as f:

        # les blokk 0 (dvs. fra start av filen)
        
        f.write(struct.pack("h", d["nuke"]))
        f.write(struct.pack("h", d["staar"]))
        f.write(struct.pack("h", d["naar"]))
        
        f.write(struct.pack("h"*7, *d["tid"]))
        
        # use padding instad of actual text from user..
        f.write(struct.pack("c"*48, *[c.encode("ascii") for c in  "x"*48]))
        
        f.write(struct.pack("h", d["kbrudd"]))
        f.write(struct.pack("h", d["jstbrudd"]))
        f.write(struct.pack("h", d["jslbrudd"]))
        
        iar = 1
        aar = d["staar"]
        for __ in range(d["naar"]):

            f.seek(d["blokklengde"] * iar)
            
            tilsig = d["tilsig"][aar]
            
            f.write(struct.pack("f"*d["nuke"], *tilsig))

            iar += 1
            aar += 1

def read_water_inflow_file(path):
    """
    Leser TILSIG.SIMT
    
    Returnerer 
    
    d = dict()
    d["nser"] = nser
    d["staar"] = staar
    d["naar"] = naar
    d["nrser"] = nrser
    d["medtid"] = medtid
    d["midser"] = midser
    d["tilsig"] = tilsig       (array[naar, nser, nuke=52])
    d["middelaar"] = middelaar (array[nser, nuke=52])
    d["nkontr"] = nkontr
    d["jkontr"] = jkontr
    d["rkontr"] = rkontr    
    
    """

    NRWORD = 1
    NWBYTE = 4

    nuke = 52

    with open(path, "rb") as f:
        nser, staar, naar = struct.unpack("i"*3, f.read(4*3))

        nrser = []
        for i in range(nser):
            bokstaver = struct.unpack("c"*40, f.read(1*40))
            bokstaver = [c.decode("ascii") for c in bokstaver]
            tekst = "".join(bokstaver)
            tekst = tekst.strip()
            nrser.append(tekst)

        medtid = struct.unpack("i"*7, f.read(4*7))

        midser = []
        for i in range(nser):
            verdi, = struct.unpack("f", f.read(4))
            midser.append(verdi)

        blokklengde = 52 * nser * NRWORD * NWBYTE


        tilsig = np.zeros((naar, nser, nuke))
        for iaar in range(naar):

            # gaa til blokk iaar + 1
            f.seek(blokklengde * (iaar + 1))

            for iuke in range(nuke):
                for iser in range(nser):
                    verdi, = struct.unpack("f", f.read(4))
                    tilsig[iaar, iser, iuke] = verdi


        # gaa til blokk naar + 1
        f.seek(blokklengde * (naar + 1))
        middelaar = np.zeros((nser, nuke))
        for iuke in range(nuke):
            for iser in range(nser):
                verdi, = struct.unpack("f", f.read(4))
                middelaar[iser, iuke] = verdi


        # gaa til blokk naar + 2
        f.seek(blokklengde * (naar + 2))
        nkontr, = struct.unpack("i", f.read(4))

        jkontr = []
        for i in range(nkontr):
            verdi, = struct.unpack("i", f.read(4))
            jkontr.append(verdi)

        rkontr = []
        for i in range(nkontr):
            verdi, = struct.unpack("f", f.read(4))
            rkontr.append(verdi)
        
    d = dict()
    d["nser"] = nser
    d["staar"] = staar
    d["naar"] = naar
    d["nrser"] = nrser
    d["medtid"] = medtid
    d["midser"] = midser
    d["tilsig"] = tilsig
    d["middelaar"] = middelaar
    d["nkontr"] = nkontr
    d["jkontr"] = jkontr
    d["rkontr"] = rkontr
    
    return d


def write_water_inflow_file(path, d):
    """
    skriver en fil med format TILSIG.SIMT til path
    
    datastrukturen d som inneholder innholdet til filen som skal skrives
    er paa samme format som dataene som returneres av funksjonen read_water_inflow_file(path)
    
    Dette formatet er  
    d = dict()
    d["nser"] = nser
    d["staar"] = staar
    d["naar"] = naar
    d["nrser"] = nrser
    d["medtid"] = medtid
    d["midser"] = midser
    d["tilsig"] = tilsig       (array[naar, nser, nuke=52])
    d["middelaar"] = middelaar (array[nser, nuke=52])
    d["nkontr"] = nkontr
    d["jkontr"] = jkontr
    d["rkontr"] = rkontr        
    """
    NRWORD = 1
    NWBYTE = 4
    nuke = 52

    with open(path, "wb") as f:
        
        f.write(struct.pack("i"*3, *(d["nser"], d["staar"], d["naar"])))

        for i in range(d["nser"]):
            kode = d["nrser"][i]
            
            # legg paa padding saa len(kode) == 40
            kode += " " * (40 - len(kode))
            assert len(kode) == 40
            
            # gjor om til bytes
            kode = [c.encode("ascii") for c in kode]
            
            f.write(struct.pack("c"*40, *kode))
        
        f.write(struct.pack("i"*7, *d["medtid"]))

        f.write(struct.pack("f"*d["nser"], *d["midser"]))

        blokklengde = nuke * d["nser"] * NRWORD * NWBYTE

        for iaar in range(d["naar"]):
                
            # gaa til blokk iaar + 1
            f.seek(blokklengde * (iaar + 1))

            for iuke in range(nuke):
                f.write(struct.pack("f"*d["nser"], *d["tilsig"][iaar, :, iuke]))


        # gaa til blokk naar + 1
        f.seek(blokklengde * (d["naar"] + 1))
        for iuke in range(nuke):
            f.write(struct.pack("f"*d["nser"], *d["middelaar"][:, iuke]))

        # gaa til blokk naar + 2
        f.seek(blokklengde * (d["naar"] + 2))
        f.write(struct.pack("i", d["nkontr"]))
        f.write(struct.pack("i"*d["nkontr"], *d["jkontr"]))
        f.write(struct.pack("i"*d["nkontr"], *d["rkontr"]))



def inflow_to_inflow_prognosis(d_inflow):
    """
    Gitt en datastruktur paa samme format som returneres
    fra funksjonen read_water_inflow_file(path) returneres
    en ny datastruktur paa formatet som trengs for aa bruke
    funksjonen write_water_inflow_prognosis_file(path, d)
    
    verdiene som trengs som ikke finnes i inputen blir satt
    som defaultverdier
    
    tanken er at man kan ta utgangspunkt i dataene som returneres
    fra denne funksjonen, og deretter legge paa en tilsigsprognose
    i verdiene for tilsig og middelaar
    """
    d_prog = dict()
    
    nprog = 2
    startuke_ix, startuke = 0, 1
    stopuke_ix,  stopuke  = 1, 52

    # hent ut data fra d_tilsig som kan brukes i d_prog
    nser  = d_inflow["nser"]
    staar = d_inflow["staar"]
    naar  = d_inflow["naar"]


    # overfor data som kan overfores fra d_inflow
    d_prog["nser"]  = nser
    d_prog["staar"] = staar
    d_prog["naar"]  = naar
    
    d_prog["tilsig"] = deepcopy(d_inflow["tilsig"])
    d_prog["middelaar"] = deepcopy(d_inflow["middelaar"])


    # legg til data som er spesifikt for tilpro-filer 
    # (gambler paa at disse parameterne ikke brukes av Samkjoringsmodellen i simuleringen
    # dvs. at disse parameterne forst og fremst brukes av programmet tilpro naar 
    # tilsigsprognosedata lages, og for dokumentasjonsformaal)

    t = datetime.date.today()
    d_prog["dag"]  = t.day
    d_prog["mnd"]  = t.month
    d_prog["ar"]   = t.year

    ipuke = np.zeros((nser, nprog, 2), dtype="i4")
    ipuke[:, :, startuke_ix] = startuke
    ipuke[:, :, stopuke_ix]  = stopuke
    d_prog["ipuke"] = ipuke

    tprog = np.zeros((nser, nprog))
    tprog[:, :] = 100.0
    d_prog["tprog"] = tprog

    varko = np.zeros((nser, nprog))
    varko[:, :] = 1.0
    d_prog["varko"] = varko

    altstd = np.zeros((nser))
    altstd[:] = 1.0
    d_prog["altstd"] = altstd
    
    d_prog["vaarflommod"] = ["HBV"]*nser
    
    return d_prog

def write_water_inflow_prognosis_file(path, d):
    """
    Skriver TILPRO.SIMT fil til plassering path
    
    d maa vaere paa samme format som formatet som 
    returneres av funksjonen inflow_to_inflow_prognosis(d_inflow)
    
    dette formatet er:
    
    d = dict()
    d["nser"] = nser
    d["staar"] = staar
    d["naar"] = naar
    d["nrser"] = nrser
    d["medtid"] = medtid
    d["midser"] = midser
    d["tilsig"] = tilsig       (array[naar, nser, nuke=52])
    d["middelaar"] = middelaar (array[nser, nuke=52])
    
    d["dag"] = dag
    d["mnd"] = mnd
    d["ar"]  = ar
    
    d["ipuke"] = ipuke    np.array((nser, nprog, 2))
    d["tprog"] = tprog    np.array((nser, nprog))
    d["varko"] = varko    np.array((nser, nprog))
    d["altstd"] = altstd  np.array((nser))
    
    d["vaarflommod"] = VAARFLOMMOD(1:NSER) C*12  
    """
    NRWORD = 1
    NWBYTE = 4
    nuke = 52
    
    blokklengde = nuke * d["nser"] * NRWORD * NWBYTE

    with open(path, "wb") as f:
        
        f.write(struct.pack("i"*3, *(d["nser"], d["staar"], d["naar"])))
        
        f.write(struct.pack("i"*3, *(d["dag"], d["mnd"], d["ar"])))
        
        ipuke = d["ipuke"]
        nser, nprog, start_stop = ipuke.shape
        for iser in range(nser):
            for iprog in range(nprog):
                for start_stop_ix in range(start_stop):
                    f.write(struct.pack("i", ipuke[iser, iprog, start_stop_ix]))
                        
        tprog = d["tprog"]
        nser, nprog = tprog.shape
        for iser in range(nser):
            for iprog in range(nprog):
                f.write(struct.pack("f", tprog[iser, iprog]))
                        
        varko = d["varko"]
        nser, nprog = varko.shape
        for iser in range(nser):
            for iprog in range(nprog):
                f.write(struct.pack("f", varko[iser, iprog]))

                        
        altstd = d["altstd"]
        nser, = altstd.shape
        for iser in range(nser):
                f.write(struct.pack("f", altstd[iser]))
                        
        for iaar in range(d["naar"]):
            
            # gaa til blokk iaar + 1
            f.seek(blokklengde * (iaar + 1))
            
            for iuke in range(nuke):
                f.write(struct.pack("f"*d["nser"], *d["tilsig"][iaar, :, iuke]))
                        

        # gaa til blokk naar + 1
        f.seek(blokklengde * (d["naar"] + 1))
        for iuke in range(nuke):
            f.write(struct.pack("f"*d["nser"], *d["middelaar"][:, iuke]))
            
        # gaa til blokk naar + 2
        f.seek(blokklengde * (d["naar"] + 2))
        
        f.write(struct.pack("i", d["nser"]))
        for text in d["vaarflommod"]:
            text += " " * (12 - len(text))
            assert len(text) == 12
            text = [c.encode("ascii") for c in text]
            f.write(struct.pack("c"*12, *text))



def read_water_inflow_prognosis_file(path):
    """
    Leser TILPRO.SIMT fil til datastruktur 
    (samme som kan skrives med funksjon write_water_inflow_prognosis_file(path, d))
    
    dette formatet er:
    
    d = dict()
    d["nser"] = nser
    d["staar"] = staar
    d["naar"] = naar
    d["nrser"] = nrser
    d["medtid"] = medtid
    d["midser"] = midser
    d["tilsig"] = tilsig       (array[naar, nser, nuke=52])
    d["middelaar"] = middelaar (array[nser, nuke=52])
    
    d["dag"] = dag
    d["mnd"] = mnd
    d["ar"]  = ar
    
    d["ipuke"] = ipuke    np.array((nser, nprog, 2))
    d["tprog"] = tprog    np.array((nser, nprog))
    d["varko"] = varko    np.array((nser, nprog))
    d["altstd"] = altstd  np.array((nser))
    
    d["vaarflommod"] = VAARFLOMMOD(1:NSER) C*12  
    """
    
    NRWORD = 1
    NWBYTE = 4
    nuke = 52
    nprog = 2
    
    with open(path, "rb") as f:
        
        nser, staar, naar = struct.unpack("i"*3, f.read(4*3))
        
        dag, mnd, ar = struct.unpack("i"*3, f.read(4*3))
        
        ipuke = np.zeros((nser, nprog, 2), dtype="i4")
        for iser in range(nser):
            for iprog in range(nprog):
                ipuke[iser, iprog, :] = struct.unpack("i"*2, f.read(4*2))
                
        tprog = np.zeros((nser, nprog))
        for iser in range(nser):
            tprog[iser, :] = struct.unpack("f"*nprog, f.read(4*nprog))
            
        varko = np.zeros((nser, nprog))
        for iser in range(nser):
            varko[iser, :] = struct.unpack("f"*nprog, f.read(4*nprog))
            
        altstd = np.zeros((nser,))
        altstd[:] = struct.unpack("f"*nser, f.read(4*nser))
        
        blokklengde = 52 * nser * NRWORD * NWBYTE

        tilsig = np.zeros((naar, nser, nuke))
        for iaar in range(naar):

            # gaa til blokk iaar + 1
            f.seek(blokklengde * (iaar + 1))

            for iuke in range(nuke):
                for iser in range(nser):
                    verdi, = struct.unpack("f", f.read(4))
                    tilsig[iaar, iser, iuke] = verdi


        # gaa til blokk naar + 1
        f.seek(blokklengde * (naar + 1))
        middelaar = np.zeros((nser, nuke))
        for iuke in range(nuke):
            for iser in range(nser):
                verdi, = struct.unpack("f", f.read(4))
                middelaar[iser, iuke] = verdi
                
        # gaa til blokk naar + 2
        f.seek(blokklengde * (naar + 2))
        
        nser2, = struct.unpack("i", f.read(4))
        
        vaarflommod = []
        for __ in range(nser2):
            text = struct.unpack("c"*12, f.read(1*12))
            text = "".join([c.decode("ascii") for c in text])
            text = text.strip()
            vaarflommod.append(text)


        
    d = dict()
    d["nser"] = nser
    d["staar"] = staar
    d["naar"] = naar
    d["dag"] = dag
    d["mnd"] = mnd
    d["ar"] = ar
    d["ipuke"] = ipuke
    d["tprog"] = tprog
    d["varko"] = varko
    d["altstd"] = altstd
    d["tilsig"] = tilsig
    d["middelaar"] = middelaar
    d["vaarflommod"] = vaarflommod
        
    return d


def get_inflow_info_df(dynmod):
    """
    Lager df med info om sumsenegiekvivalenter og tilsig per modul i et delomr
    
    returnerer df["modnr", "enekv", "type", "serie", "tilsig_aar_hm3"]
      hvor 
       - modnr = modulnummer
       - enekv = sumenergiekvivalent
       - type  = regulerbart tilsig ("reg") eller uregulerbart ("ureg")
       - serie = tilsigsseriekode
       - tilsig_aar_hm3 = midlere aarstilsig i mill. m3 
    """
    modnr = dynmod["modnr"]
    
    enekv = dict(enumerate(dynmod["enekv"], start=1))
    
    nrser = dict(enumerate([s.decode("ascii") for s in dynmod['nrser']], start=1))
    
    reg  = dict(enumerate([nrser[i] for i in dynmod["index_reg"]], start=1))
    ureg = dict(enumerate([nrser[i] for i in dynmod["index_ureg"]], start=1))
    
    reg_aar  = dict(enumerate(dynmod["urmid"], start=1))
    ureg_aar = dict(enumerate(dynmod["urbmid"], start=1))

    rows = []
    for i, nr in enumerate(modnr, start=1):
        rows.append((nr, enekv[i],  "reg",  reg[i],  reg_aar[i]))
        rows.append((nr, enekv[i], "ureg", ureg[i], ureg_aar[i]))

    df = pd.DataFrame(rows, columns=["modnr", "enekv", "type", "serie", "tilsig_aar_hm3"])
    
    return df


def get_scale_factors(d_inflow):
    """
    returnerer liste med faktor for hver tilsigsserie,
    som man maa gange profilen til serien (d_inflow["tilsig"]) med
    for at midlere arstilsig skal stemme med seriens midlere aarstilsig (d_inflow["midser"])
    """
    a = d_inflow["tilsig"]
    m = d_inflow["midser"]
    
    factors = []
    for i, middel in enumerate(m):
        f = middel / (a[:, i, :].mean() * 52.0)
        factors.append(f)

    return factors

def get_vv_energitilsig_df(path_emps, omrnavn):
    """
    Leser energitilsigsfilene til omrnavn (<omrnavn>.U30 og <omrnavn>.R30)
    til et dict "files", og lager en df med ukeverdiene df[aar, uke, R, U],
    hvor R er regulerbart energitilsig (dvs. tilsiget fra .R30 fil), og U
    er uregulerbart energitilsig (dvs. tilsiget fra .U30 fil)
    """
    rows = []
    
    files = dict()
    
    for etype in ["R", "U"]:
        path = os.path.join(path_emps, "%s.%s30" % (omrnavn, etype))
        d = read_energy_inflow_file(path)
        files[etype] = d
        
        for iaar, aar in enumerate(range(d["staar"], d["staar"] + d["naar"])):
            for iuke, uke in enumerate(range(1, d["nuke"] + 1)):
                rows.append((aar, uke, etype, d["tilsig"][aar][iuke]))
                
    df = pd.DataFrame(rows, columns=["aar", "uke", "etype", "vv_tilsig"])
    df = df.pivot_table(index=["aar", "uke"], columns="etype", values="vv_tilsig")
    df = df.reset_index()
    df.columns.name = ""
    
    return df, files


def get_tprog_energitilsig_df(inflow_info_df, d_tilsig, d_tilpro):
    """
    Bergener brutto energitilsig fra tilsigsprognose for et delomraade
    inflow_info_df - info om modulenes tilsig og sumenergiekvivalenter
    d_tilsig - info om historiske tilsigsserier (middeltilsig og profil)
    
    d_tilpro - info om tilsigsprognose 
        (bruker bare profilen, hvor tilsigsprognosen er skalert inn i forhold til historisk profil)
        
    returnerer df[aar, uke, tprog], hvor tprog er bruttotilsig i tilsigsprognosen i GWh/uke
    
    """
    skaleringsfaktorer = get_scale_factors(d_tilsig)

    serienavn = d_tilsig["nrser"]
    staar = d_tilsig["staar"]
    naar = d_tilsig["naar"]

    skaleringsfaktorer = dict(zip(serienavn, skaleringsfaktorer))
    serietilsig        = dict(zip(serienavn, d_tilsig["midser"]))

    tilsig_array = d_tilpro["tilsig"]

    naar, nser, nuke = tilsig_array.shape

    index = pd.MultiIndex.from_product(iterables=[range(staar, staar + naar),
                                                  serienavn,
                                                  range(1, nuke + 1)],
                                       names=["aar", "serie", "uke"])

    df = pd.DataFrame(data=tilsig_array.reshape((naar*nser*nuke, 1)), index=index, columns=["tprog"])
    df.reset_index(inplace=True)


    # koble paa inflow_info_df
    df = df.merge(inflow_info_df, on=["serie"])

    # skaler tilsiget
    df["scale_factor"] = df["serie"].apply(lambda s : skaleringsfaktorer[s])
    df["tprog"] *= df["scale_factor"]
    del df["scale_factor"]

    # fra serietilsig til modultilsig
    df["midser"] = df["serie"].apply(lambda s : serietilsig[s])
    df["tprog"] *= df["tilsig_aar_hm3"] / df["midser"]
    del df["midser"]

    df["tprog"] *= df["enekv"]

    df = df.pivot_table(index=["aar", "uke"], values="tprog", aggfunc="sum")
    df = df.reset_index()

    return df

def get_modified_inflow_df(tprog_df, vv_df):
    """
    Kobler sammen tprog_df og vv_df og beregner nye kolonner R_mod og U_mod
    som inneholder hhv. modifisert regulerbart og uregulerbart energitilsig.
    Modifiseringen er aa skalere opp det opprinnelige tilsiget i .R30 og .U30
    filene slik at det stemmer med summen i tprog.
    
    Siden regulertbart energitilsig kan vaere negativt haandteres dette i skaleringen
    paa denne maaten:
    
        if R < 0:
            f = (tprog - R) / U
            U_mod = U * f
            R_mod = R

        else:
            f = tprog / (R + U)
            U_mod = U * f
            R_mod = R * f
    
    """
    df = pd.merge(tprog_df, vv_df, on=["aar", "uke"])        

    def add_modified_inflow(row):
        R = row["R"]
        U = row["U"]
        tprog = row["tprog"]

        if R < 0.0:
            f = (tprog - R) / U
            row["U_mod"] = row["U"] * f
            row["R_mod"] = row["R"]

        else:
            f = tprog / (R + U)
            row["U_mod"] = row["U"] * f
            row["R_mod"] = row["R"] * f

        return row

    df = df.apply(add_modified_inflow, axis=1)
    
    df["aar"] = df["aar"].astype(int)
    df["uke"] = df["uke"].astype(int)
    
    return df

def get_modify_dict(mod_df, colname):
    "lager dict[aar][uke] -> df[colname]"
    d = dict()
    for __, row in mod_df.iterrows():
        aar = int(row["aar"])
        uke = int(row["uke"])
        value = row[colname]
        if aar not in d:
            d[aar] = dict()
        d[aar][uke] = value
    return d

        
    return factors
