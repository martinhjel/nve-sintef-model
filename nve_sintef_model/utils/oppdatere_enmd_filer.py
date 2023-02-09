import os
import shutil
from nve_modell.sintef.utils.run_sintef import run_sintef
from nve_modell.sintef.utils.get_dos import get_dos


def oppdater_enmd_fil(sti_til_modell, modaar, scriptfil_dict, path_bin, path_hydark):
    '''
    Funksjonen som oppdaterer enmd-filer:
    1. Lager midlertidig mappe hvor enmd-filene skal oppdateres.
    2. Kopierer filer som trengs til den midlertidige mappen (ENMD, ARCH, script)
    3. Kjører script i enmdat.
    4. Kopierer de oppdaterte enmd-filene tilbake til destinasjonen.
    5. Rydder opp (dvs.sletter den midlertidige mappen)

    Laget av H. Endresen, G. Kirkerud, A. Roos, EK.
    Sist oppdatert: 30.05.2022

    :param sti_til_modell:      stien til mappen som inneholder mappene [arch, detd, enmd, kalib, pris....]
    :param modaar:              årstall i format 2025
    :param scriptfil_dict:      dictionary med script-filer i format {'scriptfil' : 'sti til scriptfil'}

    :param path_bin:            sti til bin i Powel-mappe
    :param path_hydark:         sti til HYDARK i Powel-mappe
    :return:
    '''

    # sett opp midlertidig mappe med alle filene som trengs for å kjøre enmdat-programmet
    temp_folder = f'{sti_til_modell}/_temp_enmd_{modaar}'

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)

    os.makedirs(temp_folder)

    # kopierer enmd-filene til midlertidig mappe
    for fn in os.listdir(f'{sti_til_modell}/enmd/{modaar}'):
        if fn.lower().endswith(".enmd"):
            src = f'{sti_til_modell}/enmd/{modaar}/{fn}'
            dst = f'{temp_folder}/{fn}'
            shutil.copyfile(src, dst)

    # kopierer inn arch-filene til midlertidig mappe
    for fn in os.listdir(f'{sti_til_modell}/arch/{modaar}'):
        if fn.lower().endswith(".arch"):
            src =  f'{sti_til_modell}/arch/{modaar}/{fn}'
            dst =  f'{temp_folder}/{fn}'
            shutil.copyfile(src, dst)

    # kopierer inn script-filer og kjører enmdat
    for k, v in scriptfil_dict.items():
        script_filnavn = k
        sti_til_scriptfil = v
        src = f'{sti_til_scriptfil}/{script_filnavn}'
        dst = f'{temp_folder}/{script_filnavn}'
        shutil.copyfile(src, dst)

        dos = get_dos(path_bin, path_hydark)
        exe = "enmdat"
        with open(dst) as f:
            script = f.read()

        run_sintef(dos, exe, script, temp_folder, cleanup=False, toscreen=False)

    # kopiere de oppdaterte enmd-filene tilbake
    for fn in os.listdir(temp_folder):
        if fn.lower().endswith(".enmd"):
            src = f'{temp_folder}/{fn}'
            dst = f'{sti_til_modell}/enmd/{modaar}/{fn}'
            shutil.copyfile(src, dst)

    # fjerner midlertidig mappe
    shutil.rmtree(temp_folder)