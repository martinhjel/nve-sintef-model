

def get_ntimen_from_uketime_tsnitt_map(uketime_tsnitt_map):
    """
    fra et uketime_tsnitt_map returneres en liste med antall timer i hvert tidsavsnitt
    rekkefolgen paa listen er lik rekkefolgen paa tidsavsnittene
    """

    assert len(uketime_tsnitt_map) == 168
    assert all(isinstance(n,int) for n in uketime_tsnitt_map.keys())
    assert all(isinstance(n,int) for n in uketime_tsnitt_map.values())
    assert all(n > 0 and n < 169 for n in uketime_tsnitt_map.keys())
    assert all(n > 0 and n < 169 for n in uketime_tsnitt_map.values())

    y = dict()
    for __,ts in uketime_tsnitt_map.items():
        y[ts] = y.get(ts, 0) + 1

    y = [(ts, n) for ts,n in y.items()]

    y = sorted(y)
    y = [n for ts,n in y]

    return y
