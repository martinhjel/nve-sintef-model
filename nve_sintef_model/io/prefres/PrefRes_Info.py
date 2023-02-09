import os

from .read_io_prefres_info import read_io_prefres_info

class PrefRes_Info(object):

    """
    Fellesinformasjon om beregning for resultatfilene: SekvRes/PrefRes_XXX.SAMK, 
    SekvRes/PEG_PKRV_XXX.SAMK 
    og SekvRes/MASKE_XXX.SAMK lagt paa egen fil: SekvRes/info.data
    
    inneholder ogsaa informajson om startkostnader, men dette leses ikke
    i denne versjonen
    """
    
    def __init__(self, model_dir, sekvres_dir="SekvRes", filename="info.data"):
        self.path     = os.path.join(model_dir, sekvres_dir, filename)
        self._output  = None
        self._objects = dict()
        
    def get_irecl_infofil(self):
        'Blokkstorrelse'
        return self._get_name('irecl_infofil')

    def get_irecl_maske(self):
        'Blokkstorrelse paa UTMASKE-filene'
        return self._get_name('irecl_maske')

    def get_irecl_peg_pkrv(self):
        'Blokkstorrelse paa PEG_PKRV-filene'
        return self._get_name('irecl_peg_pkrv')

    def get_irecl_prefres(self):
        'Blokkstorrelse paa PREFRES-filene'
        return self._get_name('irecl_prefres')

    def get_iverprefres(self):
        'Versjonsnummer'
        return self._get_name('iverprefres')

    def get_jslutt(self):
        'Sluttuke'
        return self._get_name('jslutt')

    def get_jslutt_st(self):
        'Sluttuke for periode med sekvensielle prisavsnitt'
        return self._get_name('jslutt_st')

    def get_jstart(self):
        'Startuke'
        return self._get_name('jstart')

    def get_nfor(self):
        'Antall linjeforbindelser'
        return self._get_name('nfor')

    def get_npenm(self):
        'Antall prisavsnitt'
        return self._get_name('npenm')

    def get_npenm_u(self):
        'Antall sekvensielle prisavsnitt'
        return self._get_name('npenm_u')

    def get_npre(self):
        'Antall skift paa preferansefunksjonen'
        return self._get_name('npre')

    def get_npref_m_start(self):
        'Antall prisavsnitt'
        return self._get_name('npref_m_start')

    def get_ntrinnsum(self):
        'Totalt antall preferansetrinn'
        return self._get_name('ntrinnsum')

    def get_nverk(self):
        'Antall delomraader paa fil'
        return self._get_name('nverk')

    def _get_name(self, name):
        if name in self._objects:
            return self._objects[name]
        if not self._output:
            self._set_output()
        obj = self._output.pop(name)
        self._objects[name] = obj
        return obj
        
    def _set_output(self):
        self._output = read_io_prefres_info(self.path)


