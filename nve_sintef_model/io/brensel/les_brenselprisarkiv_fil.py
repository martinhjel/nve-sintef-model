import os
import pandas as pd

def les_brenselprisarkiv_fil(path):
    """
    leser brensel.arch til en df
    """

    rows = []
    with open(path, "r", encoding="cp1252", errors="surrogateescape") as f:

        versionsnr, antall_brensler, sluttuke = [int(i) for i in f.readline().split(",")[:3]]

        for brenselnr in range(1, antall_brensler + 1):

            navn, utslipp, energi = f.readline().split(",")[:3]
            navn = navn.replace("'", "").strip()
            utslipp = float(utslipp)
            energi = float(energi)

            uke = 1
            last_uke = 0

            while uke < sluttuke:
                uke, brenselpris, brenselavgift, co2avgift = f.readline().split(",")[:4]
                brenselpris = float(brenselpris)
                brenselavgift = float(brenselavgift)
                co2avgift = float(co2avgift)
                uke = int(uke)
                u = last_uke + 1

                while u <= uke:
                    rows.append((brenselnr, navn, u, utslipp, energi, brenselpris, brenselavgift, co2avgift))
                    u += 1

                last_uke = uke

    cols = ["brenselnr", "brenselnavn", "uke", "utslipp", "energi", 
            "brenselpris", "brenselavgift", "co2_avgift"]

    df = pd.DataFrame(rows, columns=cols)

    return df 