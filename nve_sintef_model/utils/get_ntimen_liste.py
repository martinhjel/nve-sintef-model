from .get_uketime_tsnitt_map import get_uketime_tsnitt_map
from .get_ntimen_from_uketime_tsnitt_map import get_ntimen_from_uketime_tsnitt_map

def get_ntimen_liste(antall_tsnitt):
    """
    antall_tsnitt (in [1,5,56,168]) returneres en liste med antall timer i hvert tidsavsnitt
    rekkefolgen paa listen er lik rekkefolgen paa tidsavsnittene
    """
    assert antall_tsnitt in [1, 5, 56, 168]

    m = get_uketime_tsnitt_map(antall_tsnitt)
    return get_ntimen_from_uketime_tsnitt_map(m)
    
