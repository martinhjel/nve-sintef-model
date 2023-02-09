
def skriv_prisavsnitt_fil(path, uketime_tsnitt_map):
    """
    skriver et uketime_tsnitt_map til en PRISAVSNITT.DATA fil
    
    uketime_tsnitt_map er et dict med key=uketime og value=tsnitt
       hvor uketime = 1,2,3,..,168, og representerer hver time i uken (mandag til sondag)
       og tsnitt = 1,2,..N hvor N <= 168
       som beskriver hvordan timene i en uke er fordelt paa tidsavsnitt
    
    """
    
    # sjekk at time_tsnitt_map er korrekt format
    assert all([isinstance(i, int) for i in uketime_tsnitt_map.keys()])
    assert all([isinstance(i, int) for i in uketime_tsnitt_map.values()])
    assert set(uketime_tsnitt_map.keys()) == set(range(1,169))
    assert set(uketime_tsnitt_map.values()).issubset(set(range(1,169)))
    
    # lag noen hjelpe-strukturer    
    ukedag_map = {1 : "Mon", 2 : "Tue", 3 : "Wed", 4 : "Thu", 5 : "Fri", 6 : "Sat", 7 : "Sun"}
    antall_tsnitt = len(set(uketime_tsnitt_map.values()))
    
    # bygg liste med linjer til filen
    lines = []
    lines.append("    1,   * Versjonsnummer p} fil")
    lines.append(" % 4d,   * Antall prisavsnitt" % antall_tsnitt)

    for nr in range(1, antall_tsnitt + 1):
        lines.append(" % 4d,' TS%03d              '" % (nr, nr))

    for ukedag in range(1,8):
        line = []

        for time in range(1, 25):
            uketime = time + 24*(ukedag-1)
            tsnitt = uketime_tsnitt_map[uketime]
            line.append(" % 4d" % tsnitt)

        line.append(ukedag_map[ukedag])
        line = ",".join(line)
        lines.append(line)
        
    # skriv fil        
    string = "\n".join(lines)
    with open(path, "w") as f:
        f.write(string)