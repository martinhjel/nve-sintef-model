def brensel_df_til_brensler(df):
    """
    konverterer en brensel_df (som returneres les_brenselprisarkiv_fil)
    til en liste med brensler (som trengs som input av skriv_brenselprisarkiv_fil)
    """

    info = df.pivot_table(index=["brenselnr", "brenselnavn"], values=["energi", "utslipp"])
    info = info.reset_index()

    brensler = []
    for __,r in info.iterrows():
        brenselnavn = r["brenselnavn"]
        energi_koef = float(r["energi"])
        co2_cont = float(r["utslipp"])

        priser = []
        c = df.copy()
        c = c[c["brenselnavn"] == brenselnavn]
        c = c.pivot_table(index="uke", values=["brenselpris", "brenselavgift", "co2_avgift"])
        c = c .reset_index()
        for __, r2 in c.iterrows():
            sluttuke = int(r2["uke"])
            brenselavgift = r2["brenselavgift"]
            brenselpris = r2["brenselpris"]
            co2_avgift = r2["co2_avgift"]

            priser.append({"sluttuke" : sluttuke,
                           "brenselavgift" : brenselavgift,
                           "brenselpris" : brenselpris,
                           "co2_pris" : co2_avgift})

        d = dict()
        d["brenselnavn"] = brenselnavn
        d["energi_koef"] = energi_koef
        d["co2_cont"] = co2_cont
        d["priser"] = priser

        brensler.append(d)
        
    return brensler