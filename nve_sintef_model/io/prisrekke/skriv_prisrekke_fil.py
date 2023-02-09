import pandas as pd

def skriv_prisrekke_fil(path, uketime_tsnitt_map, priser_df, antall_uker_dataperiode=156, parallell_serie=0):
    """
    path er stien som filen skal skrives til (f.eks. path = UK_56.PRI)
    priser_df er en df med kolonner: [aar, uke, uketime, pris]
    uketime_tsnitt_map er et dict med keys=uketime og values=tsnitt
    
    denne versjonen stotter ikke annen usikkerhet

    parallell_serie=0 (0=parallell, 1=serie)
    """

    assert antall_uker_dataperiode % 52 == 0
    
    # lag en df fra uketime_tsnitt_map
    uketime_tsnitt_df = pd.DataFrame(sorted([(t,ts) for (t,ts) in uketime_tsnitt_map.items()]), 
                                     columns=["uketime", "tsnitt"])
    
    # jobb med en kopi av prisene for aa sikre at
    # timepriser_df ikke blir modifisert
    df = priser_df.copy()

    # forst koble tsnitt til prisene mhp. felles uketime-kolonne
    df = uketime_tsnitt_df.merge(df, on="uketime")
    
    # saa beregne snittpriser per tsnitt
    df = df.pivot_table(index=["aar", "uke", "tsnitt"], values="pris", aggfunc="mean")
    df = df.reset_index()
    
    # tilslutt sorteres prisene for aa sikre riktig rekkefolge
    if hasattr(df, "sort_values"):
        df = df.sort_values(by=["aar", "uke", "tsnitt"])
    else:
        df = df.sort(columns=["aar", "uke", "tsnitt"])
    df = df.reset_index(drop=True)

    # hent ut statistikker som trengs for aa skrive filen
    antall_aar    = len(set(df["aar"]))
    antall_uker   = len(set(df["uke"]))
    antall_tsnitt = len(set(uketime_tsnitt_map.values()))
    startuke = df["uke"].min()
    sluttuke = df["uke"].max()
    startaar = df["aar"].min()
    sluttaar = df["aar"].max()

    assert startuke == 1
    assert sluttuke == 52
    
    # gjor om prisene til et dict for raske oppslag
    pris_map = dict()
    for i,r in df.iterrows():
        key = (r["aar"], r["uke"], r["tsnitt"])
        value = r["pris"]
        pris_map[key] = value
    
    tsnitt_timer = uketime_tsnitt_df.copy()
    tsnitt_timer = tsnitt_timer.pivot_table(index="tsnitt", values="uketime", aggfunc="count")
    tsnitt_timer = tsnitt_timer.reset_index()
    tsnitt_timer = sorted([(r["tsnitt"].astype(int), r["uketime"].astype(int)) for i,r in tsnitt_timer.iterrows()])
    
    
    # antall_tellere betyr antall dimensjoner prisene er paa
    # mulige dimensjoner er [aar, uke, tsnitt] eller [aar, uke, tsnitt, scenario]
    # vi bruker ikke scenarioer saa antall_tellere = len([aar, uke, tsnitt]) = 3
    antall_tellere = 3 
   
    # bygg linjer til filen    
    to_str = lambda v : "%4.2f" % v # liten hjelpefunksjon for aa runde av tallene i filen

    antall_aar_dataperiode = antall_uker_dataperiode // 52
    aar_liste = sorted(list(set(df.aar)))
    next_aar = {aar_liste[i-1] : aar_liste[i] for i,_ in enumerate(aar_liste)}
    
    lines = []
    lines.append("';.'")
    lines.append("2;'Type data: Prisrekke';;")
    lines.append("3;'Antall tellere';'Parallell=0 Serie=1';'Antall uker i dataperioden';")
    lines.append("3;%d;%d;%d;" % (antall_tellere, parallell_serie, antall_uker_dataperiode))
    lines.append("%d;%d;%d;" % (antall_uker_dataperiode, 1, antall_uker_dataperiode))
    lines.append("%d;%s;" % (antall_aar, ";".join(str(a) for a in range(startaar, sluttaar + 1))))
    lines.append("%d;%s;" % (antall_tsnitt, ";".join(str(n) for t,n in tsnitt_timer)))
    lines.append(";;%s;" % ";".join(str(a) for a in range(startuke, antall_uker_dataperiode + 1)))
    for aar in range(startaar, sluttaar + 1):
        for tsnitt in range(1, antall_tsnitt + 1):
            yr = aar 
            priser = []
            priser.append(str(aar))
            priser.append(str(tsnitt))
            for i in range(antall_aar_dataperiode):
                for uke in range(1, 53):
                    priser.append(to_str(pris_map[(yr,uke,tsnitt)]))
                yr = next_aar[yr]
            lines.append(";".join(priser))
    string = "\n".join(lines)
    
    with open(path, "w") as f:
        f.write(string)