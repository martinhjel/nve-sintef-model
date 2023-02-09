import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plott_fg_magstat_vs_modell(df):
    """
    for hvert omr lages to figurer ved siden av hverandre
    den forste figuren plotter fyllingsgrad fra magasinstatistikk (fg_magstat)
    den andre figuren plotter fyllingsgrad fra modell (fg_modell)
    
    sorterer omrnavn mhp storste kvadratiske avvik, slik at omraadene med storst 
    avvik fra statistikken plottes forst

    df - pandas dataframe med kolonnenavn "aar", "uke", "omrnavn", "fg_magstat", "fg_modell", "magkap"

    aar        - simulert aar
    uke        - simulert uke
    omrnavn    - navn paa omraade
    fg_magstat - fyllingsgraf statistikk
    fg_modell  - fyllingsgraf modell
    magkap     - magaisnkapasitet i modell

    """

    # finn omr med storst kvadratisk avvik
    c = df.copy()
    c = c[["omrnavn", "fg_modell", "fg_magstat"]]
    c["av"] = (c["fg_magstat"] - c["fg_modell"])**2
    c = c.pivot_table(index="omrnavn", values="av")
    c = c.reset_index()
    c = c.sort_values(by="av", ascending=False)
    c = c.reset_index(drop=True)
    omrnavn_liste = list(c["omrnavn"])

    kap_dict = dict()
    for __,r in df[["omrnavn", "magkap"]].drop_duplicates().iterrows():
        kap_dict[r["omrnavn"]] = r["magkap"]

    aar_liste = list(df.aar.unique())
    colors = plt.cm.jet(np.linspace(0,1,len(aar_liste)))

    for omrnavn in omrnavn_liste:
        fig, axes = plt.subplots(ncols=2)
        fig.suptitle("%s (Magkap modell %4.0f GWh)" % (omrnavn, kap_dict[omrnavn]))
        fig.set_size_inches(12,4)
        c = df[df.omrnavn == omrnavn].copy()
            
        x = pd.pivot_table(c, index="uke", columns="aar", values="fg_magstat")
        for i,aar in enumerate(aar_liste):
            color = colors[i]
            x[aar].plot(ax=axes[0], legend=False, title="Magstat", color=[color], ylim=(0,1))
            
        x = pd.pivot_table(c, index="uke", columns="aar", values="fg_modell")
        for i,aar in enumerate(aar_liste):
            color = colors[i]
            x[aar].plot(ax=axes[1], legend=False, title="Modell", color=[color], ylim=(0,1))
            
        axes[0].legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=3, ncol=6, borderaxespad=0.)
            
        for ax in axes:
            ax.set_xlabel("")
            ax.grid()

