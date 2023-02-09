import os
import sys
import struct
import shutil
import pandas as pd

from nve_sintef_model.io.c20_omrade import read_io_c20_omrade
from nve_sintef_model.io.prisavsnitt import skriv_prisavsnitt_fil
from nve_sintef_model.utils import get_ntimen_from_uketime_tsnitt_map, get_uketime_tsnitt_map

# definerer filnavn for rutine autokalibrering
autkal_script           = "stfil_script_autkal.txt"                 # OBS! Skal være lik som i batch fil
script_hente_faktorer   = "stfil_script_se_kalibfaktorer.txt"       # OBS! Skal være lik som i batch fil
txt_fil_faktorer        = "kalibreringsfaktorer.txt"                # OBS! Skal være lik som i batch fil
excel_fil_faktorer      = "kalib.xlsx"


def main():

    modellmappe = os.getcwd()

    rutine = sys.argv[1]

    if rutine == "bytt_tsnitt":
        antall_tsnitt = int(sys.argv[2])
        rutine_bytt_tsnitt(modellmappe, antall_tsnitt)

    if rutine == "autokalib":
        arg = sys.argv[2]
        rutine_autokalib(modellmappe, arg)    


# ------------ rutine_bytt_tsnitt ----------------------------------

def rutine_bytt_tsnitt(modellmappe, antall_tsnitt):
    print(f' - bytter tidsavsitt til {antall_tsnitt}')
    """
    Bytter tidsoppløsning i modellmappe til antall_tsnitt.

    Å bytte tidsoppløsning innebærer å endre flere filer
    i modellmappen (*.pri, maskenett.data og prisavsnitt.data)
    og kjøre programmene saminn og stfil

    Rutinen forutsetter at det finnes prisrekkefiler i modellmappen med
    navnekonvensjon [omrnavn]_[antall_tsnitt].pri

    Rutinen forutsetter at antall_tsnitt er 1, 5, 28, 56 eller 168,
    som definert i funksjonen uketime_tsnitt_map
    """
    rutine_bytt_tsnitt_prisrekkefiler(modellmappe, antall_tsnitt)
    rutine_bytt_tsnitt_maskenettfil(modellmappe, antall_tsnitt)
    rutine_bytt_tsnitt_prisavsnittfil(modellmappe, antall_tsnitt)
    rutine_bytt_tsnitt_saminnscript(modellmappe, antall_tsnitt)
    rutine_bytt_tsnitt_stfilscript(modellmappe)
    rutine_bytt_tsnitt_styrefil(modellmappe, antall_tsnitt)

def rutine_bytt_tsnitt_config_navn_stfilscript():
    "Må stemme med navn i bytt_tsnitt.bat"
    return "rutine_bytt_tsnitt_stfil.txt"

def rutine_bytt_tsnitt_config_navn_saminnscript():
    "Må stemme med navn i bytt_tsnitt.bat"
    return "rutine_bytt_tsnitt_saminn.txt"

def rutine_bytt_tsnitt_prisrekkefiler(modellmappe, antall_tsnitt):
    omr = sintef_modellmappe_omr_prisrekke(modellmappe)

    for omrnavn in omr["omrnavn"]:
        sti_fra = os.path.join(modellmappe, "%s_%s.pri" % (omrnavn, antall_tsnitt))
        sti_til = os.path.join(modellmappe, "%s.pri" % omrnavn)

        assert os.path.exists(sti_fra)
        assert os.path.exists(sti_til)

        shutil.copy(sti_fra, sti_til)

def rutine_bytt_tsnitt_maskenettfil(modellmappe, antall_tsnitt):
    m = get_uketime_tsnitt_map(antall_tsnitt)
    ntimen = get_ntimen_from_uketime_tsnitt_map(m)

    sti_maskenett = os.path.join(modellmappe, "maskenett.data")

    with open(sti_maskenett) as f:
        lines = f.readlines()

    # endre header
    timer_per_tsnitt_str = ",".join([str(n) for n in ntimen])
    lines[0] = "'MASKENETT',%s,%s,\n" % (antall_tsnitt, timer_per_tsnitt_str)

    string = "".join(lines)

    with open(sti_maskenett, "w") as f:
        f.write(string)

def rutine_bytt_tsnitt_prisavsnittfil(modellmappe, antall_tsnitt):
    m = get_uketime_tsnitt_map(antall_tsnitt)
    sti_fil = os.path.join(modellmappe, "PRISAVSNITT.DATA")
    skriv_prisavsnitt_fil(sti_fil, m)

def rutine_bytt_tsnitt_saminnscript(modellmappe, antall_tsnitt):
    kommandoer = kommandoer_saminn_bytt_tsnitt(antall_tsnitt)
    scriptnavn = rutine_bytt_tsnitt_config_navn_saminnscript()
    rutine_utils_skriv_kommandofil(modellmappe, kommandoer, scriptnavn)

def kommandoer_saminn_bytt_tsnitt(antall_tsnitt):
    kommandoer = []
    kommandoer.append("nei")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("%s" % antall_tsnitt)
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("ja")
    kommandoer.append("ja")
    kommandoer.append("nei")
    kommandoer.append("ja")
    return kommandoer

def rutine_bytt_tsnitt_stfilscript(modellmappe):
    utnavn = config_navn_styrefil_samtap_utfil()
    batnavn = config_navn_styrefil_samtap_batfil()
    kommandoer = kommandoer_stfil_sett_styrefil(batnavn, utnavn)
    scriptnavn = rutine_bytt_tsnitt_config_navn_stfilscript()
    rutine_utils_skriv_kommandofil(modellmappe, kommandoer, scriptnavn)

def kommandoer_stfil_sett_styrefil(batnavn, utnavn):
    kommandoer = []
    kommandoer.append("")
    kommandoer.append("SERIE")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("tapp")
    kommandoer.append("%s" % batnavn)
    kommandoer.append("%s" % utnavn)
    kommandoer.append("avsl")
    return kommandoer


def rutine_bytt_tsnitt_styrefil(modellmappe, antall_tsnitt):
    scriptnavn = config_navn_styrefil_samtap_scriptfil()
    batnavn = config_navn_styrefil_samtap_batfil()
    kommandoer = kommandoer_batfil_enkel_samtap(antall_tsnitt, scriptnavn)
    rutine_utils_skriv_kommandofil(modellmappe, kommandoer, batnavn)

def kommandoer_batfil_enkel_samtap(antall_tsnitt, scriptnavn):
    kommandoer = []
    kommandoer.append("echo. >   %s" % scriptnavn)
    kommandoer.append("echo. >>  %s" % scriptnavn)
    kommandoer.append("echo. >>  %s" % scriptnavn)
    sekv = "" if antall_tsnitt <= 5 else "sekv"
    kommandoer.append("samtap %s < %s" % (sekv, scriptnavn))
    return kommandoer


def kommandoer_batfil_samtap_med_tprog(omrnr_liste, antall_tsnitt, scriptnavn):
    kommandoer = []
    kommandoer.append("echo. >   %s" % scriptnavn)
    for omrnr in omrnr_liste:
        kommandoer.append("echo %s PRO 1 >>  %s" % (omrnr, scriptnavn))
    kommandoer.append("echo. >>  %s" % scriptnavn)
    kommandoer.append("echo. >>  %s" % scriptnavn)
    kommandoer.append("echo. >>  %s" % scriptnavn)
    sekv = "" if antall_tsnitt <= 5 else "sekv"
    kommandoer.append("samtap %s < %s" % (sekv, scriptnavn))
    return kommandoer


# ----------- rutine_kalib ----------------------------------
def rutine_autokalib(modellmappe, arg):

    if arg == "run":
        print('- kjører autokalibrering')
        kjore_autokalib(modellmappe)

    if arg == "hent":
        print('- henter kaliberingsfaktorer')
        hente_koeff(modellmappe)

    if arg == "excel":
        print('- lagrer kaliberingsfaktorer i excel')
        koeff_til_excel(modellmappe)

def kjore_autokalib(modellmappe):
    kommandoer = []
    kommandoer.append("")
    kommandoer.append("SERIE")
    kommandoer.append("1")
    kommandoer.append("JA")
    kommandoer.append("JA")
    kommandoer.append("NEI")
    kommandoer.append("")
    kommandoer.append("KALIB")
    kommandoer.append("")
    kommandoer.append("")
    scriptnavn = autkal_script
    rutine_utils_skriv_kommandofil(modellmappe, kommandoer, scriptnavn)

def hente_koeff(modellmappe):
    kommandoer = []
    kommandoer.append("")
    kommandoer.append("PARAL")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("KOPL")
    kommandoer.append("")
    kommandoer.append("")
    kommandoer.append("AVSL")
    scriptnavn = script_hente_faktorer
    rutine_utils_skriv_kommandofil(modellmappe, kommandoer, scriptnavn)

def rutine_kalib_endre_les_kalibreringsfaktorer(modellmappe):
    filnavn = txt_fil_faktorer
    sti_fil = os.path.join(modellmappe, filnavn)
    with open(sti_fil) as f:
        kal = f.readlines()
    kal = [line for line in kal if len(line.split(":")) == 6]
    kal = [[s.lower().strip() for s in line.split(":")] for line in kal]
    kal = [a[1:] for a in kal]
    kal = [a for a in kal if a[0].isdigit()]
    return kal

def koeff_til_excel(modellmappe):
    kalibreringsfaktorer = rutine_kalib_endre_les_kalibreringsfaktorer(modellmappe)
    df_kalibreringsfaktorer = pd.DataFrame(kalibreringsfaktorer, columns = ['omrnr', 'omrnavn', 'tilb', 'form', 'elast'])
    df_kalibreringsfaktorer['omrnr'] = df_kalibreringsfaktorer['omrnr'].astype(int)
    df_kalibreringsfaktorer['omrnavn'] = df_kalibreringsfaktorer['omrnavn'].str.upper()
    df_kalibreringsfaktorer['tilb'] = df_kalibreringsfaktorer['tilb'].astype(float)
    df_kalibreringsfaktorer['form'] = df_kalibreringsfaktorer['form'].astype(float)
    df_kalibreringsfaktorer['elast'] = df_kalibreringsfaktorer['elast'].astype(float)
    print(df_kalibreringsfaktorer)
    df_kalibreringsfaktorer.to_excel(excel_fil_faktorer, index = False)



def rutine_utils_skriv_kommandofil(modellmappe, kommandoer, scriptnavn):
    script = "\n".join(kommandoer)
    sti_fil = os.path.join(modellmappe, scriptnavn)
    with open(sti_fil, "w") as f:
        f.write(script)


def sintef_modellmappe_omr_prisrekke(modellmappe):
    """
    Returnerer df med kolonner omrnr, omrnavn
    med alle omr som har prisrekke
    (dvs. alle eksogene omr)
    """
    sti_omr = os.path.join(modellmappe, "C20_OMRADE.EMPS")
    rows = read_io_c20_omrade(sti_omr)
    omr = pd.DataFrame(rows, columns=["omrnr", "omrnavn"])

    alle_omrnavn = set(omr["omrnavn"].str.lower())

    omrnavn_prisrekke = set()
    for fn in os.listdir(modellmappe):
        fn = fn.lower()
        if fn.endswith(".pri"):
            mulig_omrnavn = fn.split(".pri")[0]
            if mulig_omrnavn in alle_omrnavn:
                omrnavn_prisrekke.add(mulig_omrnavn)

    omr = omr[omr["omrnavn"].str.lower().isin(omrnavn_prisrekke)]
    omr = omr.reset_index(drop=True)

    return omr


def config_navn_styrefil_samtap_batfil():
    return "samtap_styrefil.bat"

def config_navn_styrefil_samtap_scriptfil():
    return "samtap_styrefil_script.txt"

def config_navn_styrefil_samtap_utfil():
    return "samtap_styrefil_ut.txt"



