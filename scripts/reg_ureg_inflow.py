from pathlib import Path
import pickle
import pandas as pd
import plotly.graph_objects as go
import yaml
from entsoe import EntsoePandasClient

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

pd.options.plotting.backend = "plotly"


# Lag Prognoseresultater-objekt
r = Prognoseresultater()


# params = read_params(path / simulation / "SAMRES.SAMK")
# c20_omr = read_c20_omrade(path / simulation / "C20_OMRADE.EMPS")
# linjer = read_maskenett_linjer(path / simulation / "MASKENETT.DATA")

# Lag sti til modellmappe
modellmappe = Path("C:/Users/martinhj/EMPS/dataset/lyse_Dataset_v10prep")
modellmappe.exists()

# Read cached samres if it exists
cached_samres_file = Path("samres.pkl")
if cached_samres_file.exists()and cached_samres_file.stat().st_size != 0:
    with open(cached_samres_file, "rb") as file:
        samres = pickle.load(file)
else:
    samres = les_samres(modellmappe / "SAMRES.SAMK")
    with open(cached_samres_file, "w") as file:
        pickle.dumps(samres)

minmax = les_minmax(modellmappe / "MINMAX.SAMK", samres["nverk"], samres["nuke"], samres["npenm"])
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

def vannkraft(samres):
    df = samres["egpr"].copy()
    df = df.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="vannkraft")
    return df

def tilsig(samres):
    # hent reg + ureg
    dfr = samres["reg"].copy()
    dfu = samres["ureg"].copy()

    dfr = dfr.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="reg")
    dfr = dfr.pivot_table(index=["aar", "uke", "omrnr"], values="reg", aggfunc="sum").reset_index()

    dfu = dfu.melt(id_vars=["aar", "uke", "tsnitt"], var_name="omrnr", value_name="ureg")
    dfu = dfu.pivot_table(index=["aar", "uke", "omrnr"], values="ureg", aggfunc="sum").reset_index()

    df = dfr.merge(dfu, on=["aar", "uke", "omrnr"])
    df["bruttotilsig"] = df["reg"] + df["ureg"]

    return df

df_tilsig = tilsig(samres)
df_vannkraft = vannkraft(samres)

df_vannkraft_week = (
    df_vannkraft.groupby(["aar", "uke", "omrnr"])["vannkraft"].sum().reset_index()
)  # sum over week

omr_nr = 6
df_vannkraft_week.query(f"omrnr == {omr_nr}").pivot(
    columns="aar", values="vannkraft", index="uke"
).mean(axis=1).plot()

df_vannkraft_week.query(f"omrnr == {omr_nr}").pivot(
    columns="aar", values="vannkraft", index="uke"
).mean(axis=1)[:52].sum()

nor_areas = [i for i in range(1, 16)]
df_vannkraft_week.query(f"omrnr in {nor_areas}")
df_vannkraft_week.query(f"omrnr in {nor_areas}").groupby(["aar", "uke"])[
    "vannkraft"
].sum().reset_index().pivot(columns="aar", values="vannkraft", index="uke").mean(axis=1)[
    104:156
].sum()

area_mapping = {
    "ostland": 1,
    "sorost": 2,
    "hallingdal": 3,
    "telemark": 4,
    "sorland": 5,
    "vestsyd": 6,
    "vestmidt": 7,
    "nordvest": 8,
    "norgemidt": 9,
    "helgeland": 10,
    "troms": 11,
    "finnmark": 12,
    "haugesund": 13,
    "moere": 14,
    "svartisen": 15,
    "SVER-ON1": 16,
    "SVER-ON2": 17,
    "SVER-NN1": 18,
    "SVER-NN2": 19,
    "SVER-MIDT": 20,
    "SVER-SYD": 21,
}


mapping_table = {
    "NO1": {"ostland": 0.9, "hallingdal": 0.2},
    "NO2": {"telemark": 1.0, "sorland": 1.0, "sorost": 1.0, "haugesund": 1.0},
    "NO3": {"moere": 1.0, "norgemidt": 1.0, "nordvest": 1.0, "ostland": 0.1},
    "NO4": {"helgeland": 1.0, "troms": 1.0, "finnmark": 1.0, "svartisen": 1.0},
    "NO5": {"vestsyd": 1.0, "vestmidt": 1.0, "hallingdal": 0.8},
    "SWE": {
        "SVER-ON1": 1.0,
        "SVER-ON2": 1.0,
        "SVER-NN1": 1.0,
        "SVER-NN2": 1.0,
        "SVER-MIDT": 1.0,
        "SVER-SYD": 1.0,
    },
}


def weight_over_region(df, area_mapping, mapping_table, values):
    region = {}
    for region_area in mapping_table:
        df_region = pd.DataFrame()
        for emps_area in mapping_table[region_area]:
            omr_nr = area_mapping[emps_area]
            if df_region.empty:
                df_region = (
                    df.query(f"omrnr == {omr_nr}").pivot(columns="aar", values=values, index="uke")[
                        :52
                    ]
                    * mapping_table[region_area][emps_area]
                )
            else:
                df_region += (
                    df.query(f"omrnr == {omr_nr}").pivot(columns="aar", values=values, index="uke")[
                        :52
                    ]
                    * mapping_table[region_area][emps_area]
                )

        region[region_area] = df_region
    return region

vankr = weight_over_region(df_vannkraft_week, area_mapping, mapping_table, values="vannkraft")

##### Scale hydropower to the actual yearly mean production
vank_lst = []
for a in [f"NO{i}" for i in range(1,6)]:
    df_temp = vankr[a].mean(axis=1)
    df_temp.name = a
    vank_lst.append(df_temp)

df_vank_area = pd.concat(vank_lst,axis=1)
df_vank_area.sum()/1e3
yearly_mean_hydro = df_vank_area.sum().sum()/1e3
actual_yearly_mean_hydro = 136.9
scale = actual_yearly_mean_hydro/yearly_mean_hydro

for a in vankr:
    if "NO" in a:
        vankr[a]*=scale

for region_area in vankr:
    print(
        f"{region_area}: {vankr[region_area][:52].sum().mean()}"
    )  # Sum over year and mean over scenarios

with pd.ExcelWriter("Hydropower_production.xlsx", engine="xlsxwriter") as writer:
    for region_area in vankr:
        vankr[region_area].to_excel(writer, sheet_name=f"{region_area}")

reg = weight_over_region(df_tilsig, area_mapping, mapping_table, values="reg")

for region_area in reg:
    print(
        f"{region_area}: {reg[region_area][:52].sum().mean()}"
    )  # Sum over year and mean over scenarios

with pd.ExcelWriter("Hydropower_regulated_inflow.xlsx", engine="xlsxwriter") as writer:
    for region_area in reg:
        reg[region_area].to_excel(writer, sheet_name=f"{region_area}")

ureg = weight_over_region(df_tilsig, area_mapping, mapping_table, values="ureg")

for region_area in ureg:
    print(
        f"{region_area}: {ureg[region_area][:52].sum().mean()}"
    )  # Sum over year and mean over scenarios

with pd.ExcelWriter("Hydropower_unregulated_inflow.xlsx", engine="xlsxwriter") as writer:
    for region_area in ureg:
        ureg[region_area].to_excel(writer, sheet_name=f"{region_area}")

# ureg["NO1"]

# df_reg = df_tilsig.query(f"omrnr == {omr_nr}").pivot(columns="aar", values="reg", index="uke")
# df_ureg = df_tilsig.query(f"omrnr == {omr_nr}").pivot(columns="aar", values="ureg", index="uke")


fig = go.Figure()

def add_traces(df, name_prefix):
    for col in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode="lines", name=f"{name_prefix}_{col}"))


region = "NO1"
add_traces(ureg[region], "reg")
add_traces(reg[region], "ureg")
add_traces(vankr[region], "vankr")

fig.show()

for a in vankr:
    fig = go.Figure()
    add_traces(vankr[a], "vankr")
    fig.update_layout(title=f"{a}")
    fig.show()


## ENTSOE DATA

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

client = EntsoePandasClient(api_key=config["entsoe-token"])

start = pd.Timestamp("20220101", tz="Europe/Oslo")
end = pd.Timestamp("20230101", tz="Europe/Oslo")
code = "NO_2"

elspot_areas = [f"NO_{i}" for i in range(1, 6)]
entsoe = {}
for a in elspot_areas:
    file = Path(f"{a}.csv")
    if file.exists():
        df = pd.read_csv(f"{a}.csv", index_col=0, parse_dates=[0])
    else:
        df = client.query_generation(a, start=start, end=end, psr_type=None)
        df.to_csv(f"{a}.csv")

    df.index = pd.to_datetime(df.index, utc=True)
    df.index = df.index.tz_convert("Europe/Oslo")
    
    df = df[[i for i in df.columns if "hydro" in i.lower()]]
    entsoe[a] = df


lst = []
for a in elspot_areas:
    df_temp = entsoe[a].sum(axis=1)
    df_temp.name = f"{a}"
    lst.append(df_temp)



df_sum = pd.concat(lst, axis=1)

df_sum.resample("1D").sum().plot()
df_sum.sum()/1e6
df_sum.sum().sum()/1e6

df_sum.sum(axis=1).plot()

