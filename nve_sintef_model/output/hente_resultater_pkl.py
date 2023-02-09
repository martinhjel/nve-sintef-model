# disse funkjsonene henter diverse resultater fra pickle filer i mappe emps/samnett_resultater
# og sammenstiller tabeller til en brukervenlig format
# de inneholder også dokumentasjon av hva ulike filer inneholder og hvordan dataene skal behandles

import os
import pandas as pd


def hente_priser(modell, sti, aar, vaar):
    # priser hentes fra fil krv.plk, og riktige områdenavn settes inn

    filsti_priser = os.path.join(sti, str(aar), f'resultater_{modell}', "krv.pkl")
    filsti_omr = os.path.join(sti, str(aar), f'resultater_{modell}', "omr.pkl")
    print(f' - henter priser: {filsti_priser}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_priser)
    df = df.loc[df['aar'].isin(vaar)]
    df = df.melt(id_vars = ['aar', 'uke', 'tsnitt'], var_name = 'omrnr')
    df = df.rename(columns = {
        'aar' : 'vaeraar',
        'delomraade' : 'omrnr'
        })

    # slår sammen med områdenavn
    df_omr = pd.read_pickle(filsti_omr)
    df = df.merge(df_omr, on = 'omrnr')

    # setter inn modellår og rydder i tabellen
    df['modaar'] = aar 
    df = df[['modaar', 'vaeraar', 'uke', 'tsnitt', 'omrnavn', 'value', 'omrnr']]

    return df


def hente_produksjon(modell, sti, aar, vaar):
    # samlet produksjon (vindsol + vann) hentes fra fil vind.plk, og riktige områdenavn settes inn

    filsti_prod = os.path.join(sti, str(aar), f'resultater_{modell}', "produksjon.pkl")
    filsti_omr = os.path.join(sti, str(aar), f'resultater_{modell}', "omr.pkl")
    print(f' - henter produksjon: {filsti_prod}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_prod)
    df = df.loc[df['aar'].isin(vaar)]
    df = df.melt(id_vars = ['aar', 'uke', 'tsnitt'], var_name = 'omrnr')
    df = df.rename(columns = {
        'aar' : 'vaeraar',
        'delomraade' : 'omrnr'
        })

    # slår sammen med områdenavn
    df_omr = pd.read_pickle(filsti_omr)
    df = df.merge(df_omr, on = 'omrnr')

    # setter inn modellår og rydder i tabellen
    df['modaar'] = aar 
    df = df[['modaar', 'vaeraar', 'uke', 'tsnitt', 'omrnavn', 'value', 'omrnr']]

    return df


def hente_forbruk(modell, sti, aar, vaar):
    # forbruk hentes fra forbruk.plk, og riktige områdenavn settes inn
    # i denne funksjonen fratrekkes IKKE flomkraft  

    filsti_forb = os.path.join(sti, str(aar), f'resultater_{modell}', "forbruk.pkl")
    #filsti_flomkr = os.path.join(sti, str(aar), f'resultater_{modell}', "flomkraft.pkl")
    filsti_omr = os.path.join(sti, str(aar), f'resultater_{modell}', "omr.pkl")
    print(f' - henter forbruk: {filsti_forb}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_forb)
    df = df.loc[df['aar'].isin(vaar)]
    df = df.melt(id_vars = ['aar', 'uke', 'tsnitt'], var_name = 'omrnr')
    df = df.rename(columns = {
        'aar' : 'vaeraar',
        'delomraade' : 'omrnr'
        })

    # slår sammen med områdenavn
    df_omr = pd.read_pickle(filsti_omr)
    df = df.merge(df_omr, on = 'omrnr')

    # setter inn modellår og rydder i tabellen
    df['modaar'] = aar 
    df = df[['modaar', 'vaeraar', 'uke', 'tsnitt', 'omrnavn', 'value', 'omrnr']]

    return df


def hente_vind(modell, sti, aar, vaar):
    # vind- og solkraftresultater hentes fra fil vind.plk, og riktige områdenavn settes inn

    filsti_vindsol = os.path.join(sti, str(aar), f'resultater_{modell}', "vind.pkl")
    filsti_omr = os.path.join(sti, str(aar), f'resultater_{modell}', "omr.pkl")
    print(f' - henter vind- og solkraft: {filsti_vindsol}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_vindsol)
    df = df.loc[df['aar'].isin(vaar)]
    df = df.melt(id_vars = ['aar', 'uke', 'tsnitt'], var_name = 'omrnr')
    df = df.rename(columns = {
        'aar' : 'vaeraar',
        'delomraade' : 'omrnr'
        })

    # slår sammen med områdenavn
    df_omr = pd.read_pickle(filsti_omr)
    df = df.merge(df_omr, on = 'omrnr')

    # setter inn modellår og rydder i tabellen
    df['modaar'] = aar 
    df = df[['modaar', 'vaeraar', 'uke', 'tsnitt', 'omrnavn', 'value', 'omrnr']]

    return df


def hente_samf(modell, sti, aar, vaar):
    # i denne filen finnes data om produksjon, forbruk, tap, samfunnsøkonomisk overskudd, flaskehalsinntekter mm.
    # filen inneholder årlige tall
    # merk at forbruk i denne filen inneholder flomkraft og produksjon inneholder rasjonering
    # derfor legger vi til flomkraft og rasjonering som kan senere fratrekkes ved behov

    filsti_samf = os.path.join(sti, str(aar), f'resultater_{modell}', "samf.pkl")
    filsti_flomkraft = os.path.join(sti, str(aar), f'resultater_{modell}', "flomkraft.pkl")
    filsti_rasjonering = os.path.join(sti, str(aar), f'resultater_{modell}', "rasjonering.pkl")
    filsti_omr = os.path.join(sti, str(aar), f'resultater_{modell}', "omr.pkl")
    print(f' - henter data fra filen: {filsti_samf}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_samf)
    df = df.loc[df['aar'].isin(vaar)]
    df = df.rename(columns = {'Delomraade' : 'omrnavn'})

    # slår sammen med områdenummer
    df_omr = pd.read_pickle(filsti_omr)
    df = df.merge(df_omr, on = 'omrnavn')

    # legger til info om flomkraft g rasjonering til videre bruk
    flomkraft = pd.read_pickle(filsti_flomkraft)
    flomkraft = flomkraft.groupby('aar').sum().reset_index()
    flomkraft = flomkraft.drop(columns = ['uke', 'tsnitt'], axis = 1)
    flomkraft = pd.melt(flomkraft, id_vars = 'aar', var_name = 'omrnr', value_name = 'flomkraft')

    rasjonering = pd.read_pickle(filsti_rasjonering)
    rasjonering = rasjonering.groupby('aar').sum().reset_index()
    rasjonering = rasjonering.drop(columns = ['uke', 'tsnitt'], axis = 1)
    rasjonering = pd.melt(rasjonering, id_vars = 'aar', var_name = 'omrnr', value_name = 'rasjonering')

    df = df.merge(flomkraft, on = ['omrnr', 'aar']).merge(rasjonering, on = ['omrnr', 'aar'])
    df = df.rename(columns = {
        'aar'           : 'vaeraar',
        'Produksjon'    : 'produksjon_med_rasjonering',
        'Konsum'        : 'forbruk_med_flomkraft',
        })
    df['modaar'] = aar 

    return df


def hente_nettflyt(modell, sti, aar, vaar):
    # henter strømflyt over nett i Norge og Sverige som er detaljert modellert i Samnett
    # fra fil nettflyt.pkl som har flyt per ts for hver snitt i nettet (i kolonnenumre):
    # - enten mellom emps-områder 
    # - eller over egendefinerte snitt
    # nettlyt.pkl sammenstilles med kombsnitt.pkl som inneholder oversikt over snittnumre og områdenavn
    # merk: data i denne filen er snitt per tidsavsnitt (for å få energimengde må man gange med antall timer i ts)
    # ???? Bør vi fratrekke noen tapsprosent her? Tapsprosenter ligger i maskenett.pkl.

    filsti_nettflyt = os.path.join(sti, str(aar), f'resultater_{modell}', "nettflyt.pkl")
    filsti_kombsnitt = os.path.join(sti, str(aar), f'resultater_{modell}', "kombsnitt.pkl")
    print(f' - henter nettflyt: {filsti_nettflyt}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_nettflyt)
    df = df.loc[df['aar'].isin(vaar)]
    
    df = df.set_index(['aar',  'uke', 'tsnitt'])
    df = df.stack()
    df = df.reset_index()
    df = df.rename(columns = {'level_3' : 'snittnr', 0: 'value'})

    # slår sammen med kombsnitt som inneholder områdenavn
    kombsnitt = pd.read_pickle(filsti_kombsnitt)
    df = df.merge(kombsnitt, on = ['snittnr'])

    df = df.rename(columns={'aar': 'vaeraar'})
    df['modaar'] = aar 

    return df

def hente_utveksling(modell, sti, aar, vaar):

    # henter strømflyt for områder som ikke har detaljert nettmodellering, fra fil utv.pkl 
    # utv.pkl sammenstilles med maskenett.pkl og omr.pkl som inneholder linjenumre, kapasiteter og områdenavn
    # merk: data i denne filen er snitt per tidsavsnitt (for å få energimengde må man gange med antall timer i ts)

    filsti_utv = os.path.join(sti, str(aar), f'resultater_{modell}', "utv.pkl")
    filsti_maskenett = os.path.join(sti, str(aar), f'resultater_{modell}', "maskenett.pkl")
    filsti_omr = os.path.join(sti, str(aar), f'resultater_{modell}', "omr.pkl")
    print(f' - henter utveksling: {filsti_utv}')

    # leser inn data og filtrerer værår
    df = pd.read_pickle(filsti_utv)
    df = df.loc[df['aar'].isin(vaar)]

    df = df.set_index(['aar',  'uke', 'tsnitt'])
    df = df.stack()
    df = df.reset_index()
    df = df.rename(columns = {'level_3' : 'linjenr', 0: 'value'})

    # slår sammen med maskenett og områdenavn
    maskenett = pd.read_pickle(filsti_maskenett)
    df_omr = pd.read_pickle(filsti_omr)
    df_omr['omrnr_fra'] = df_omr['omrnr']
    df_omr['omrnr_til'] = df_omr['omrnr']
    df_omr['omrnavn_fra'] = df_omr['omrnavn']
    df_omr['omrnavn_til'] = df_omr['omrnavn']

    maskenett = maskenett.merge(df_omr[['omrnr_fra', 'omrnavn_fra']], on = 'omrnr_fra')
    maskenett = maskenett.merge(df_omr[['omrnr_til', 'omrnavn_til']], on = 'omrnr_til')
    df = df.merge(maskenett, on = ['linjenr'])

    df = df.rename(columns={'aar': 'vaeraar'})
    df['modaar'] = aar 

    return df

    