
from nve_sintef_model.utils.type_check import get_type_from_dict

def skriv_enkel_maskenett(path, ntimen_liste, linje_data):

    """
    path - sti der maskenett-filen skal skrives

    ntimen_liste - liste med antall timer for hvert tidsavsnitt (forste element i listen er antall timer 
                                                                 i forste tidsavsnitt, osv)

    linje_data   - liste med d, hvor d er python dict som 
                     maa ha keys og og datatyper paa verdiene
                         omrnr_fra (datatype int)      
                         omrnr_til (datatype int)      
                         omrnavn_fra (datatype str)      
                         omrnavn_til (datatype str)      
                         kap_fra (datatype float eller int)      
                         kap_til (datatype float eller int)      

                     kan ha keys (alle har default-verdi paa 0)
                         tap (datatype float eller int)      
                         avgift_fra (datatype float eller int)      
                         avgift_til (datatype float eller int)      

    """

    assert isinstance(ntimen_liste, list), "ntimen_liste maa vaere liste"
    assert all([isinstance(n, int) for n in ntimen_liste]), "elementer i ntimen_liste maa vaere int"
    assert sum(ntimen_liste) == 168, "timene i ntimen_liste maa summeres til 168"
    assert all([n >= 0 for n in ntimen_liste]), "kan ikke ha negativt antall timer i ntimen_liste"
    assert len(ntimen_liste) <= 168, "kan ikke vaere mer enn 168 tidsavsnitt i ntimen_liste"

    antall_tsnitt = len(ntimen_liste)
    ntimen_str = ",".join([str(n) for n in ntimen_liste])

    lines = []
    lines.append("'MASKENETT',%s,%s," % (antall_tsnitt, ntimen_str) )

    def get_err_msg(k,n): 
        return "Fant ikke %s for linje %s" % (k,n)

    number = (int,float)

    for i,d in enumerate(linje_data, start=1):
        omrnr_fra   = get_type_from_dict(d, "omrnr_fra", int,    err=True,  err_msg=get_err_msg("omrnr_fra", i))
        omrnr_til   = get_type_from_dict(d, "omrnr_til", int,    err=True,  err_msg=get_err_msg("omrnr_til", i))
        omrnavn_fra = get_type_from_dict(d, "omrnavn_fra", str,  err=True,  err_msg=get_err_msg("omrnavn_fra", i))
        omrnavn_til = get_type_from_dict(d, "omrnavn_til", str,  err=True,  err_msg=get_err_msg("omrnavn_til", i))
        kap_fra     = get_type_from_dict(d, "kap_fra", number, err=True,  err_msg=get_err_msg("kap_fra", i))
        kap_til     = get_type_from_dict(d, "kap_til", number, err=True,  err_msg=get_err_msg("kap_til", i))

        tap         = get_type_from_dict(d, "tap", number, 0)
        avgift_fra  = get_type_from_dict(d, "avgift_fra", number, 0)
        avgift_til  = get_type_from_dict(d, "avgift_til", number, 0)


        lines.append("%s, '%s', %s, '%s'," % (omrnr_fra, omrnavn_fra, omrnr_til, omrnavn_til))
        lines.append("%s, %s, %s," % (tap, avgift_fra, avgift_til))
        lines.append("0, %s, %s," % (kap_fra, kap_til))
        lines.append("0,")

    lines.append("-1,'AVSLUTT',-1,'SLUTT'")

    string = "\n".join(lines)

    with open(path, "w") as f:
        f.write(string)
    

    