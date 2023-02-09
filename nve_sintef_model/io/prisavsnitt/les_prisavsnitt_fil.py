import pandas as pd

def les_prisavsnitt_fil(path):
    """
    leser en prisavsnitt-fil til en df med kolonner:
        uketime = 1,2,3, .., 168    
        ukedag = 1,2,3, .., 7, 1,2..    
        dogntime = 1,2,3, .., 24, 1,2,..    
        helg = True hvis ukedag in [6,7] else False 
        tsnitt = tidsavsnitt (int) den aktuelle uketimen tilhorer   
    """
    data = []
    with open(path) as f:
        for line in f:

            line = line.replace("\n", "")
            line = line.replace("\r", "")

            strings = line.split(",")

            if len(strings) != 25:
                continue

            strings = [int(s) for s in strings[:-1]]

            data.append(strings)

    rader = []
    uketime = 0
    for ukedag, time_liste in enumerate(data, start=1):
        for dogntime, tsnitt in enumerate(time_liste, start=1):
            uketime += 1
            helg = ukedag in [6,7]
            rader.append((uketime, ukedag, helg, dogntime, tsnitt))

    kolonner = ["uketime", "ukedag", "helg", "dogntime", "tsnitt"]
    df = pd.DataFrame(rader, columns=kolonner)

    return df
            

    
    
