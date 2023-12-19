from pathlib import Path

from nve_sintef_model.prognoseresultater.prognoseresultater import (
    Prognoseresultater,
    les_brensel,
    les_maskenett,
    les_minmax,
    les_omr,
    les_prisavsnitt,
    les_samres,
    les_trinnliste,
    les_utveksling,
)

# Lag Prognoseresultater-objekt
r = Prognoseresultater()


params = read_params(path / simulation / "SAMRES.SAMK")
c20_omr = read_c20_omrade(path / simulation / "C20_OMRADE.EMPS")
linjer = read_maskenett_linjer(path / simulation / "MASKENETT.DATA")

# Lag sti til modellmappe
modellmappe = Path("C:/Users/martinhj/EMPS/dataset/lyse_Dataset_v10prep")
modellmappe.exists()

samres = les_samres(modellmappe / "SAMRES.SAMK")
minmax = les_minmax(modellmappe/"MINMAX.SAMK", samres["nverk"], samres["nuke"], samres["npenm"])
trinnliste = les_trinnliste(modellmappe, "trinnliste.txt")
omr = les_omr(modellmappe, "C20_OMRADE.EMPS")
utv = les_utveksling(
    modellmappe / "UTVEKSLING.SAMK",
    samres["nfor"],
    samres["hist"],
    samres["jstart"],
    samres["jslutt"],
    samres["npenm"],
)

prisavsnitt = les_prisavsnitt(modellmappe / "PRISAVSNITT.DATA")
maskenett = les_maskenett(modellmappe / "MASKENETT.DATA", samres["nuke"], samres["npenm"])
brensel = les_brensel(modellmappe / "BRENSEL.ARCH")
# Les data fra modellmappe inn til Prognoseresultater-objekt

df = tilsig(samres)

df.head()

df["aar-uke"] = df["aar"].astype(str) + "-" + df["uke"].astype(str)

df.info()
df.describe()

# Under kaller jeg på funksjoner som er definert for Prognoseresultater-objektet
# De forskjellige funksjonene sammenstiller data fra modellen og returnerer det
# som en dataframe, slik at brukeren enkelt kan jobbe videre med dataene


df = r.utveksling()
print(df.head(), "\n")

# df.to_excel("utveksling.xlsx")

df = r.tilsig()
print(df.head(), "\n")

df = r.magasinfylling()
print(df.head(), "\n")

df = r.kraftpris()
print(df.head(), "\n")


df = r.forbruk()
print(df.head(), "\n")

df = r.produksjon()
print(df.head(), "\n")

df = r.industriforbruk()
print(df.head(), "\n")

df = r.termisk()
print(df.head(), "\n")

df = r.tidsoppløsning()
print(df.head(), "\n")

mapping_table = {
    "NO1": {"ostland": 0.9, "hallingdal": 0.2},
    "NO2": {"telemark": 1.0, "sorland": 1.0, "sorost": 1.0, "haugesund": 1.0},
    "NO3": {"moere": 1.0, "norgemidt": 1.0, "nordvest": 1.0, "ostland": 0.1},
    "NO4": {"helgeland": 1.0, "troms": 1.0, "finnmark": 1.0, "svartisen": 1.0},
    "NO5": {"vestsyd": 1.0, "vestmidt": 1.0, "hallingdal": 0.8},
}


def tilsig(samres):
    # hent reg + ureg
    dfr = samres["reg"].copy()
    dfu = samres["ureg"].copy()

    dfr = dfr.melt(id_vars=["aar", "uke","tsnitt"], var_name="omrnr", value_name="reg")
    dfr = dfr.pivot_table(index=["aar", "uke", "omrnr"], values="reg", aggfunc="sum").reset_index()

    dfu = dfu.melt(id_vars=["aar", "uke","tsnitt"], var_name="omrnr", value_name="ureg")
    dfu = dfu.pivot_table(index=["aar", "uke","omrnr"], values="ureg", aggfunc="sum").reset_index()

    df=dfr.merge(dfu, on=["aar","uke","omrnr"])
    df["bruttotilsig"]=df["reg"]+df["ureg"]

    return df