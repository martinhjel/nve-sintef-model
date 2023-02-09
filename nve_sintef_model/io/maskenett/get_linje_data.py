
def get_linje_data(m, omr):
    """
    Leser dataene i en maskenettfil og returnerer en linje_data liste paa
    samme format som kreves for aa skrive en enkel maskenett-fil med 
    funksjonen nve_sintef_model.io.maskenett.skriv_enkel_maskenett
    
    m - et maskenett-objekt av typen nve_sintef_model.io.maskenett.Maskenett
    omr - en df med omrnr, omrnavn data
    """
    omr["omrnr"] = omr["omrnr"].astype(int)
    omr = omr[["omrnr", "omrnavn"]]
    
    df = m._les_linjer_og_tap()

    df = df.merge(omr, left_on="omrnr_fra", right_on="omrnr")
    del df["omrnr"]
    df["omrnavn_fra"] = df.pop("omrnavn")

    df = df.merge(omr, left_on="omrnr_til", right_on="omrnr")
    del df["omrnr"]
    df["omrnavn_til"] = df.pop("omrnavn")

    df = df.sort_values(by="linjenr")
    df = df.reset_index(drop=True)

    linje_data = []
    for __, r in df.iterrows():
        d = dict()
        d["omrnr_fra"] = int(r["omrnr_fra"])
        d["omrnr_til"] = int(r["omrnr_til"])
        d["omrnavn_fra"] = r["omrnavn_fra"]
        d["omrnavn_til"] = r["omrnavn_til"]
        d["kap_fra"] = float(r["kap_fra"])
        d["kap_til"] = float(r["kap_til"])
        d["tap"] = float(r["tap"])
        d["avgift_fra"] = float(r["avgift_fra"])
        d["avgift_til"] = float(r["avgift_til"])
        linje_data.append(d)
        
    return linje_data