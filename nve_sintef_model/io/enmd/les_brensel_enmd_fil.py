import pandas as pd

def les_brensel_enmd_fil(path):
    """
    leser enmd-fil og returnerer df med kolonner typenr, brenselnavn
    
    path - sti til enmd-fil
    """
    rows = []

    kontrakter = []
    brensler = []

    with open(path) as f:

        for line in f:
            if "Typenr, Kategori, Navn, Eget(T)" in line:
                kontrakter.append(line)

            if "Sluttuke, Brenselnavn" in line:
                brensler.append(line)

    varme = [s for s in kontrakter if s.split(",")[1].strip() == "3"]

    assert len(varme) == len(brensler), "lesing av %s gikk ikke som forventet" % path

    for v,b in zip(varme, brensler):

        prefnr = int(v.split(",")[0].strip())
        brensel = b.split(",")[1].replace("'", "").strip()

        rows.append((prefnr, brensel))

    df = pd.DataFrame(rows, columns=["typenr", "brenselnavn"])

    return df


