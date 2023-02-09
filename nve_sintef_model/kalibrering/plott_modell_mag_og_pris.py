import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plott_modell_mag_og_pris(df, ymax_krv=60, ymin_krv=0):
    """
    for hvert omr lages to figurer ved siden av hverandre
    den forste figuren plotter fyllingsgrad fra modell (fg_modell)
    den andre figuren plotter kraftpris fra modell (krv)

    df - pandas dataframe med kolonnenavn "aar", "uke", "omrnavn", "fg_modell", "krv", "magkap"

    aar        - simulert aar
    uke        - simulert uke
    omrnavn    - navn paa omraade
    fg_modell  - fyllingsgraf modell
    krv        - simulert kraftverdi (kraftpris) modell
    magkap     - magaisnkapasitet i modell

    """

    # finn omr med storst kvadratisk avvik
    omrnavn_liste = list(df["omrnavn"].unique())

    kap_dict = dict()
    for __,r in df[["omrnavn", "magkap"]].drop_duplicates().iterrows():
        kap_dict[r["omrnavn"]] = r["magkap"]

    aar_liste = list(df.aar.unique())
    colors = plt.cm.jet(np.linspace(0,1,len(aar_liste)))

    for omrnavn in omrnavn_liste:
        fig, axes = plt.subplots(ncols=2)
        fig.suptitle("%s (Magkap modell %4.0f GWh)" % (omrnavn, kap_dict[omrnavn]))
        fig.set_size_inches(14,4)
        c = df[df.omrnavn == omrnavn].copy()
            
        x = pd.pivot_table(c, index="uke", columns="aar", values="fg_modell")
        for i,aar in enumerate(aar_liste):
            color = colors[i]
            x[aar].plot(ax=axes[0], legend=False, title="Modell-Fylling", color=[color], ylim=(0,1))

        x = pd.pivot_table(c, index="uke", columns="aar", values="krv")
        for i,aar in enumerate(aar_liste):
            color = colors[i]
            x[aar].plot(ax=axes[1], legend=False, title="Modell-Pris", color=[color], ylim=(ymin_krv,ymax_krv))

            
        axes[0].legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=3, ncol=10, borderaxespad=0.)
            
        for ax in axes:
            ax.set_xlabel("")
            ax.grid()

