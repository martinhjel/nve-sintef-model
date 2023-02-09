import os
import pandas as pd

from .read_io_dynmodell import read_io_dynmodell

class Dynmodell(object):
    """
    Henter data fra DYNMODELL-fil
    """
    
    # TODO: kommentere
    # TODO: docs
    
    def __init__(self, path):
        """
        path - sti til dynmodell-fil
        
        get-metoder for alle parametere og 
        get-metoder som lager dict eller df
        
        """
        
        self.path = path
        
        self._output  = None
        self._objects = dict()
        
        self.funcs = dict()
        self.funcs['bunnmag'] = self.get_bunnmag
        self.funcs['bytepq'] = self.get_bytepq
        self.funcs['dynrel'] = self.get_dynrel
        self.funcs['eget'] = self.get_eget
        self.funcs['eierandel'] = self.get_eierandel
        self.funcs['enekv'] = self.get_enekv
        self.funcs['enekv_flom'] = self.get_enekv_flom_map
        self.funcs['enekv_forb'] = self.get_enekv_forb_map
        self.funcs['enekv_st'] = self.get_enekv_st_map
        self.funcs['enekv_uke'] = self.get_enekv_uke
        self.funcs['ho'] = self.get_ho
        self.funcs['hydraul_kap'] = self.get_hydraul_kap
        self.funcs['hydraul_kobl'] = self.get_hydraul_kobl
        self.funcs['hydraul_kode'] = self.get_hydraul_kode
        self.funcs['ibl'] = self.get_ibl
        self.funcs['id_liste_kontrakt'] = self.get_id_liste_kontrakt
        self.funcs['id_liste_mod'] = self.get_id_liste_mod
        self.funcs['id_liste_pump'] = self.get_id_liste_pump
        self.funcs['id_liste_qvar'] = self.get_id_liste_qvar
        self.funcs['id_liste_ser'] = self.get_id_liste_ser
        self.funcs['idkontrakt'] = self.get_idkontrakt
        self.funcs['imodtyp'] = self.get_imodtyp
        self.funcs['iqvar'] = self.get_iqvar
        self.funcs['jant'] = self.get_jant
        self.funcs['magma'] = self.get_magma
        self.funcs['magpf'] = self.get_magpf
        self.funcs['magpt'] = self.get_magpt
        self.funcs['magref'] = self.get_magref
        self.funcs['mamax'] = self.get_mamax
        self.funcs['mamaxtyp'] = self.get_mamaxtyp
        self.funcs['mamin'] = self.get_mamin
        self.funcs['mamintyp'] = self.get_mamintyp
        self.funcs['medtid'] = self.get_medtid
        self.funcs['mnavn'] = self.get_mnavn
        self.funcs['modnr'] = self.get_modnr
        self.funcs['nkontrakt'] = self.get_nkontrakt
        self.funcs['nmapktsum'] = self.get_nmapktsum
        self.funcs['nmod'] = self.get_nmod
        self.funcs['npump'] = self.get_npump
        self.funcs['nqvar'] = self.get_nqvar
        self.funcs['nrser'] = self.get_nrser
        self.funcs['nser'] = self.get_nser
        self.funcs['nvassdrag'] = self.get_nvassdrag
        self.funcs['pmax'] = self.get_pmax
        self.funcs['pnavn'] = self.get_pnavn
        self.funcs['pump_fra'] = self.get_pump_fra
        self.funcs['pump_h'] = self.get_pump_h
        self.funcs['pump_mw'] = self.get_pump_mw
        self.funcs['pump_q'] = self.get_pump_q
        self.funcs['pump_st'] = self.get_pump_st
        self.funcs['pump_til'] = self.get_pump_til
        self.funcs['qfomin'] = self.get_qfomin
        self.funcs['qmax'] = self.get_qmax
        self.funcs['qmaxfast'] = self.get_qmaxfast
        self.funcs['qmaxforb'] = self.get_qmaxforb
        self.funcs['qmin'] = self.get_qmin
        self.funcs['qvar'] = self.get_qvar
        self.funcs['regmag'] = self.get_regmag
        self.funcs['snavn'] = self.get_snavn
        self.funcs['topo_flom'] = self.get_topo_flom
        self.funcs['topo_forb'] = self.get_topo_forb
        self.funcs['topo_st'] = self.get_topo_st
        self.funcs['tser_qfomin'] = self.get_tser_qfomin
        self.funcs['tser_qmax'] = self.get_tser_qmax
        self.funcs['tser_qmin'] = self.get_tser_qmin
        self.funcs['tser_reg'] = self.get_tser_reg
        self.funcs['tser_ureg'] = self.get_tser_ureg
        self.funcs['urbmid'] = self.get_urbmid
        self.funcs['urmid'] = self.get_urmid
        self.funcs['uv'] = self.get_uv
        self.funcs['vmag'] = self.get_vmag

    # maps modul ----------------------------------
        
    def get_bunnmag(self):
        "Bunnmag(1:Nmod) R Bunnmagasin (Mm3)"
        return self._get_map('bunnmag')
    
    def get_eierandel(self):
        "EIERANDEL (1:NMOD) R Eierandel i stasjonene"
        return self._get_map('eierandel')
    
    def get_enekv(self):
        "ENEKV (1:NMOD) R Energiekvivalent (maks. total)"
        return self._get_map('enekv')

    def get_ho(self):
        "HO (1:NMOD) R Nominell fallhoyde"
        return self._get_map('ho')
    
    def get_hydraul_kap(self):
        "Hydraul(1:NMOD) I Koder for hydraulisk kobling, Kapasitet for flytting av vann (m3/s)"
        return self._get_map('hydraul_kap')

    def get_hydraul_kobl(self):
        "Hydraul(1:NMOD) I Koder for hydraulisk kobling, Koblingsnummer (200, 300) eller koblingskonstant"
        return self._get_map('hydraul_kobl')

    def get_hydraul_kode(self):
        "Hydraul(1:NMOD) I Koder for hydraulisk kobling, Kode 100, 200, 300 (eller 120, 130)"
        return self._get_map('hydraul_kode')
    
    def get_imodtyp(self):
        "IMODTYP(1:NMOD) I Modultype (=0 Vannkraft, =1 Vindkraft)"
        return self._get_map('imodtyp')

    def get_magma(self):
        "MAGMA (1:NMOD) R Magasinvolum"
        return self._get_map('magma')

    def get_mamaxtyp(self):
        "MAMAXTYP(1:NMOD) I Type maksimal restriksjon paa magasin"
        return self._get_map('mamaxtyp')

    def get_mamintyp(self):
        "MAMINTYP(1:NMOD) I Type minimal restriksjon paa magasin"
        return self._get_map('mamintyp')
    
    def get_pmax(self):
        "PMAX (1:NMOD) R Maks produksjon (MW)"
        return self._get_map('pmax')
    
    def get_regmag(self):
        "REGMAG (1:NMOD) I Flagg: 0 for buffermagasin, >0 ellers"
        return self._get_map('regmag')

    def get_topo_flom(self):
        "TOPO (1:NMOD) I Topologimatrise, Flom"
        return self._get_map('topo_flom')

    def get_topo_forb(self):
        "TOPO (1:NMOD) I Topologimatrise, Forbitapping"
        return self._get_map('topo_forb')

    def get_topo_st(self):
        "TOPO (1:NMOD) I Topologimatrise, Stasjonsvannforing"
        return self._get_map('topo_st')

    def get_urbmid(self):
        "URBMID (1:NMOD) R Uregulert tilsig (aarsmiddel)"
        return self._get_map('urbmid')

    def get_urmid(self):
        "URMID (1:NMOD) R Regulert tilsig (aarsmiddel)"
        return self._get_map('urmid')

    def get_uv(self):
        "UV (1:NMOD) R Undervannstand"
        return self._get_map('uv')

    def get_vmag(self):
        "VMAG (1:NMOD) R Innlest reguleringsgrad"
        return self._get_map('vmag')
    
    def get_modnr(self):
        "Modnr (1:NMOD) I Modulnummer angitt i MED"
        return self._get_map('modnr')    
    
    def get_snavn(self):
        "SNAVN (1:NMOD) C*20 Stasjonsnavn"
        return self._get_map('snavn', True)
    
    def get_mnavn(self):
        "MNAVN (1:NMOD) C*20 Modulnavn"
        return self._get_map('mnavn', True)
    
    def get_qmaxfast(self):
        "QMAXFAST(1:NMOD) R Maksimal slukeevne i hovedvannvei"
        return self._get_map('qmaxfast')

    def get_qmaxforb(self):
        "QMAXFORB(1:NMOD) R Maksimal forbitapping"
        return self._get_map('qmaxforb')
    
    # maps pumpe ----------------------------------

    def get_pnavn(self):
        "PNAVN (1:NPUMP) C*20 Pumpenavn"
        return self._get_map('pnavn', True)    
    
    def get_pump_st(self):
        "dict[pumpid] -> modid for pumpestasjon"
        return self._get_map('pump_st')    
    
    def get_pump_fra(self):
        "dict[pumpid] -> modid for magasin det pumpes fra"
        return self._get_map('pump_fra')    
    
    def get_pump_til(self):
        "dict[pumpid] -> modid for magasin det pumpes til"
        return self._get_map('pump_til')    
    
    def get_pump_mw(self):
        "dict[pumpid] -> pumpekapasitet mw"
        return self._get_map('pump_mw')    
    
    def get_pump_h(self):
        "dict[pumpid] -> pumpet hoyde"
        return self._get_map('pump_h')    
    
    def get_pump_q(self):
        "dict[pumpid] -> pumpekapasitet m3s"
        return self._get_map('pump_q')    
    
    # maps tilsigsserier
    
    def get_nrser(self):
        return self._get_map('nrser', True)
    
    # maps kontrakt ----------------------------------

    def get_idkontrakt(self):
        "IDKONTRAKT(1:NKONTRAKT) I Angir kontraktsmodulene (intern plassering)"
        return self._get_map('idkontrakt')
    
    
    # maps moduler som har fallhoyde avhengighet ----------------------------------

    def get_iqvar(self):
        "IQVAR (1:NQVAR) I Modul identifikator"
        return self._get_map('iqvar')
    
    # info --------------------------------------------------------

    def get_ibl(self):
        "BLKL I Blokklengde i bytes"
        return self._get_param('ibl')    
    
    def get_dynrel(self):
        "Indikator for aa angi om fil har nytt eller gammelt filformat."
        return self._get_param('dynrel')

    def get_eget(self):
        ".TRUE. hvis bare egne andeler ligger paa filen"
        return self._get_param('eget')
    
    def get_bytepq(self):
        "NBYTEPQ I Antall bytes lagret paa PQKurve.SIMT"
        return self._get_param('bytepq')
    
    def get_medtid(self):
        "MEDTID (1:7) I Tidspunkt da .DETD-filen er generert"
        return self._get_param('medtid')

    # n------------------------------------------

    def get_jant(self):
        "Antall uker i datasyklusen"
        return self._get_param('jant')

    def get_nkontrakt(self):
        "Antall kontraktsmoduler"
        return self._get_param('nkontrakt')

    def get_nmapktsum(self):
        "NMAPKTSUM I Antall magasinpunkt lagret totalt."
        return self._get_param('nmapktsum')

    def get_nmod(self):
        "Antall moduler"
        return self._get_param('nmod')

    def get_npump(self):
        "Antall pumper"
        return self._get_param('npump')

    def get_nqvar(self):
        "NQVAR I Antall moduler med slukeevne lagt inn som en funksjon av fallhoyde"
        return self._get_param('nqvar')

    def get_nser(self):
        "Antall grunnserier paa TILSIG.SIMT"
        return self._get_param('nser')

    def get_nvassdrag(self):
        "NVASSDRAG I Antall uavhengige vassdrag"
        return self._get_param('nvassdrag')
    
    # spesielle---------------------------------------

    def get_qvar(self):
        "d[modid] -> knekkpunkter for slukeevne som funksjon av fallhoyde"
        iqvar = self.get_iqvar()
        qvar = self._output.get("qvar")
        d = {iqvar[i] : x for i,x in enumerate(qvar, start=1)}
        return d
            
    # lister--------------------------------------------------------------
    
    
    def get_id_liste_mod(self):
        "[1,2,..,nmod]"
        return self._get_id_liste("nmod")
    
    def get_id_liste_pump(self):
        "[1,2,..,npump]"
        return self._get_id_liste("npump")
    
    def get_id_liste_ser(self):
        "[1,2,..,nser]"
        return self._get_id_liste("nser")
    
    def get_id_liste_qvar(self):
        "[1,2,..,nqvar]"
        return self._get_id_liste("nqvar")
    
    def get_id_liste_kontrakt(self):
        "[1,2,..,nkontrakt]"
        return self._get_id_liste("nkontrakt")
    

    # df ------------------------------------------

    def get_mamax(self):
        "df[uke + modid_liste] - Variabel maks. magasin (Mm3)"
        return self._get_df("mamax", self.get_id_liste_mod())
    
    def get_mamin(self):
        "df[uke + modid_liste] - Variabel min. magasin (Mm3)"
        return self._get_df("mamin", self.get_id_liste_mod())
    
    def get_qmax(self):
        "df[uke + modid_liste] - Maksimal stasjonsvannforing (m3/s)"
        return self._get_df("qmax", self.get_id_liste_mod())
    
    def get_qmin(self):
        "df[uke + modid_liste] - Minste stasjonsvannforing (m3/s)"
        return self._get_df("qmin", self.get_id_liste_mod())
    
    def get_qfomin(self):
        "df[uke + modid_liste] - Minimum forbitapping (m3/s)"
        return self._get_df("qfomin", self.get_id_liste_mod())
    
    def get_magref(self):
        "df[uke + modid_liste] - Referansemagasin (%)"
        return self._get_df("magref", self.get_id_liste_mod())
    
    def get_enekv_uke(self):
        "df[uke + modid_liste] - Energiekvivalent (totalt ned til havet)"
        return self._get_df("enekv_uke", self.get_id_liste_mod())
    
    def get_magpt(self):
        "df[uke + modid_liste] - Styrekurve for magasin det pumpes til"
        return self._get_df("magpt", self.get_id_liste_pump())
    
    def get_magpf(self):
        "df[uke + modid_liste] - Styrekurve for magasin det pumpes fra"
        return self._get_df("magpf", self.get_id_liste_pump())

    def get_df_pumper(self, names=["pump_st", "pump_fra", "pump_til", "pump_mw", "pump_h", "pump_q"]):
        rows = [(i,) for i in self.get_id_liste_pump()]
        df = pd.DataFrame(rows, columns=["pumpid"])
        for name in names:
            f = self.funcs.get(name)
            d = f()
            df[name] = df["pumpid"].apply(lambda i : d[i])
        return df
    
    def get_df_moduler(self, names=['bunnmag', 'eierandel', 'enekv', 'enekv_flom', 'enekv_forb', 'enekv_st', 
                                    'ho', 'hydraul_kap', 'hydraul_kobl', 'hydraul_kode', 'imodtyp', 
                                    'magma', 'mamaxtyp', 'mamintyp', 'mnavn', 'modnr', 'pmax', 'qmaxfast', 'qmaxforb', 
                                    'regmag', 'snavn', 'topo_flom', 'topo_forb', 'topo_st', 'urbmid', 'urmid', 'uv', 'vmag']):
        rows = [(i,) for i in self.get_id_liste_mod()]
        df = pd.DataFrame(rows, columns=["modid"])
        for name in names:
            f = self.funcs.get(name)
            d = f()
            df[name] = df["modid"].apply(lambda i : d[i])
        return df
    
    def get_df_modul_uke(self, names=["mamax", "mamin", "magref", "enekv_uke", "qmax", "qmin", "qfomin"]):
        """
        df[uke,modid + names], hvor names kan vaere mamax, mamin, magref, enekv_uke, qmax, qmin, qfomin
        
        mamax     - Variabel maks. magasin (Mm3)
        mamin     - Variabel min. magasin (Mm3)
        magref    - Referansemagasin (%)
        enekv_uke - Energiekvivalent (totalt ned til havet)
        qmax      - Maksimal stasjonsvannforing (m3/s)
        qmin      - Minste stasjonsvannforing (m3/s)
        qfomin    - Minimum forbitapping (m3/s)
        """
        dfs = []
        for name in names:
            f = self.funcs[name]
            df = f()
            df = df.set_index("uke")
            df = df.stack()
            df = df.reset_index()
            df = df.rename(columns={"level_1" : "modid", 0 : name})
            df = df.set_index(["uke", "modid"])
            dfs.append(df)
        df = pd.concat(dfs, axis=1)
        df = df.reset_index()
        return df
    
    def get_df_pumpe_uke(self, names=["magpt", "magpf"]):
        """
        df[uke,pumpid + names], hvor names kan vaere magpt, magpf
        
        magpt     - Styrekurve for magasin det pumpes til
        magpf     - Styrekurve for magasin det pumpes fra
        """
        dfs = []
        for name in names:
            f = self.funcs[name]
            df = f()
            df = df.set_index("uke")
            df = df.stack()
            df = df.reset_index()
            df = df.rename(columns={"level_1" : "pumpid", 0 : name})
            df = df.set_index(["uke", "pumpid"])
            dfs.append(df)
        df = pd.concat(dfs, axis=1)
        df = df.reset_index()
        return df    
    
    def get_enekv_st_map(self):
        "dict[modid] -> modulens energiekvivalent"
        return self._get_enekv_lokal(self.get_topo_st())
    
    def get_enekv_forb_map(self):
        "dict[modid] -> modulens energitap ved forbitapping"
        return self._get_enekv_lokal(self.get_topo_forb())
    
    def get_enekv_flom_map(self):
        "dict[modid] -> modulens energitap ved flom"
        return self._get_enekv_lokal(self.get_topo_flom())

    def get_tser_qfomin(self):
        "dict[modid] -> Tlsigsserie for minimum forbitapping"
        return self._get_tser('index_qfomin', self.get_nrser())

    def get_tser_qmax(self):
        "dict[modid] -> Tilsigsserie for maksimalvannforing"
        return self._get_tser('index_qmax', self.get_nrser())

    def get_tser_qmin(self):
        "dict[modid] -> Tilsigsserie for minimum vannforing"
        return self._get_tser('index_qmin', self.get_nrser())

    def get_tser_reg(self):
        "dict[modid] -> Tilsigsserie for regulert tilsig"
        return self._get_tser('index_reg', self.get_nrser())

    def get_tser_ureg(self):
        "dict[modid] -> Tilsigsserie for uregulert tilsig"
        return self._get_tser('index_ureg', self.get_nrser())
    
    def get_opp_st(self):
        topo = self.get_topo_st()
        d = dict()
        for modid_fra,modid_til in topo.items():
            if modid_fra*modid_til == 0:
                continue
            if modid_til not in d:
                d[modid_til] = []
            d[modid_til].append(modid_fra)
        return d
    
    def get_opp_forb(self):
        topo = self.get_topo_forb()
        d = dict()
        for modid_fra,modid_til in topo.items():
            if modid_fra*modid_til == 0:
                continue
            if modid_til not in d:
                d[modid_til] = []
            d[modid_til].append(modid_fra)
        return d
    
    def get_opp_flom(self):
        topo = self.get_topo_flom()
        d = dict()
        for modid_fra,modid_til in topo.items():
            if modid_fra*modid_til == 0:
                continue
            if modid_til not in d:
                d[modid_til] = []
            d[modid_til].append(modid_fra)
        return d
 
    
    # _get-funksjoner-----------------------------------------
    
    def _get_id_liste(self, name):
        "bruker key for aa ikke overskrive navnet"
        key = ("_get_id_liste", name)
        if key in self._objects:
            return self._objects[key]
        if not self._output:
            self._set_output()
        n = self._get_param(name)
        l = list(range(1, n + 1))
        self._objects[key] = l
        return l

    def _get_param(self, name):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        obj = self._output.pop(name)
        self._objects[name] = obj
        return obj
    
    def _get_map(self, name, text=False):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        values = self._output.pop(name)
        if text:
            d = {i:v.decode("cp865", "ignore") for i,v in enumerate(values, start=1)}
        else:
            d = {i:v for i,v in enumerate(values, start=1)}
        self._objects[name] = d
        return d
    
    def _get_df(self, name, id_liste):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        rows = self._output.pop(name)
        cols = ["uke"] + id_liste
        df = pd.DataFrame(rows, columns=cols)
        self._objects[name] = df
        return df
    
    def _get_tser(self, name, serier):
        plassering = self._output.get(name)
        d = {i : serier.get(i) for i in plassering}
        return d
    
    def _get_enekv_lokal(self, topo):
        enekv = self.get_enekv()
        d = dict()
        for modid_fra,modid_til in topo.items():
            e_fra = enekv.get(modid_fra, 0)
            e_til = enekv.get(modid_til, 0)
            e_lokal = e_fra - e_til
            d[modid_fra] = e_lokal
        return d
    
    def _set_output(self):
        self._output = read_io_dynmodell(self.path)
