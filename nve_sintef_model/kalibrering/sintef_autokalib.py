'''
Denne funksjonen kan kombineres med kjørefunksjonen for å kjøre emps og gjøre autokalibrering
Områder som skal kalibreres og kalibreringsfaktorer som skal endres spesifiseres i autkal_inn.
'''

import os
import shutil

from nve_sintef_model.utils.run_batch import run_batch
from nve_sintef_model.utils.get_dos import get_dos
from nve_sintef_model.utils.skriv_autkal_inn import skriv_autkal_inn_csv

def autokalibrering(autkal_inn, autokalib_bat, autokali_py, ts, sti_til_modell,  
                    aar, antall_iterasjoner, steg_lengde, pst_steglengde, sti_til_kalib_lagring, 
                    to_screen, path_bin, path_hydark):

    dos = get_dos(path_bin, path_hydark)

    for a in aar:

        modellmappe = os.path.join(sti_til_modell, 'output_sintef', str(a), 'emps')

        shutil.copy(autokalib_bat, modellmappe)
        shutil.copy(autokali_py, modellmappe)

        print(f' - lager AUTKAL_INN.CSV for {a}')
        skriv_autkal_inn_csv(excel_fil = autkal_inn, 
                            antall_iter = antall_iterasjoner, 
                            steglen = steg_lengde,
                            pst_steglen = pst_steglengde,
                            output_sti =  modellmappe)

    
        print(f' - kjører autokalibrering for {a}')
        exe = f"autokalib.bat {ts}"  
        run_batch(dos, exe, modellmappe, cleanup=False, toscreen=to_screen)

        print(f'- lagrer faktorer i excel for {a}')
        shutil.copy(f'{modellmappe}/kalib.xlsx', os.path.join(sti_til_kalib_lagring, str(a)))

        