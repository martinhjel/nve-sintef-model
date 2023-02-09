import pandas as pd
import os

def skriv_autkal_inn_csv(excel_fil, antall_iter, steglen, pst_steglen, output_sti):
    '''
    Funksjonen skriver AUTKAL_INN.CSV fil basert på excel fil

    antall_iter -  Antall hovediterasjoner             
    steglen  - Steglengde 
    pst_steglen -  Prosentvis steglengde i neste hovediterasjon
    output_sti - hvor csv fil skal lagres
    
    '''

    df_rekkeflg = pd.read_excel(excel_fil, sheet_name = 'Rekkefølge')
    df_vekting  = pd.read_excel(excel_fil, sheet_name = 'Vekting')

    lines = []

    # linjer med hovedparametere
    lines.append(f" Antall hovediterasjoner                        ,    {antall_iter}")
    lines.append(f" Steglengde                                     ,{steglen:.3f},{steglen:.3f},{steglen:.3f}")
    lines.append(f" Prosentvis steglengde i neste       hoveditera ,{pst_steglen:.3f}")
    lines.append("")

    # linjer med rekkefølgen for kalibrringsfaktorer
    lines.append(" Omradenummer , Omradenavn , Tilbakekobling , Form , Elastisitet")
    for i in df_rekkeflg.iterrows():
        line = f"    {i[1][0]},{i[1][1]},{i[1][2]},{i[1][3]},{i[1][4]}" 
        lines.append(line)

    # linjer med vekting av samf.øk. overskudd
    lines.append(" Omradenummer , Omradenavn , Vekting av samf.ok. overskudd ")
    for i in df_vekting.iterrows():
        line = f"    {i[1][0]},{i[1][1]},{i[1][2]:.3f}"
        lines.append(line)
    
    text = "\n".join(lines)

    # lager csv fil i den spesifiserte mappen
    with open(os.path.join(output_sti, 'AUTKAL_INN.csv'), 'w') as file:
        file.write(text)


