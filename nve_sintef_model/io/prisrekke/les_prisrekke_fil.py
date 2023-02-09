import pandas

def les_prisrekke_fil(path, med_tsnitt=False):

    def get_delims(path):
        with open(path) as f:
            line = f.readline()
        line = line.replace("\n", "")
        line = line.replace("'", "")
        return line[0], line[1]

    def get_vekter(path, sep):
        with open(path) as f:
            for i in range(6):
                f.readline()
            line = f.readline()
            strings = line.split(sep)
            num_tsnitt = int(strings.pop(0))
            vekter = [s for s in strings[:num_tsnitt]]
            vekter = [s.replace("'", "") for s in vekter]
            vekter = [s.replace(",", ".") for s in vekter]
            vekter = [float(s) / 168.0 for s in vekter]
        return vekter

    def get_header(path, sep):
        with open(path) as f:
            for i in range(7):
                f.readline()
            line = f.readline()
            strings = line.split(sep)
        strings[0] = "aar"
        strings[1] = "tsnitt"
        if strings[-1] == "\n":
            del strings[-1]
        return strings

    sep, dec = get_delims(path)  # skal bare bruke sep
    vekter = get_vekter(path, sep)
    header = get_header(path, sep)

    df = pandas.read_csv(path, names=header, skiprows=8, sep=sep, index_col=False)

    # stable og rydde dataene
    df = df.set_index(["aar", "tsnitt"])
    df = df.stack()
    df = df.reset_index()
    df = df.rename(columns={"level_2": "uke", 0: "pkrv"})
    df["uke"] = df["uke"].astype(int)
    df["omrnr"] = 1 #hack for vansimtap

    if med_tsnitt == True:
        return df

    # aggregere til uke
    vekter = pandas.DataFrame([(i, v) for i, v in enumerate(vekter, start=1)], columns=["tsnitt", "vekt"])
    df = df.merge(vekter, on="tsnitt")
    df["pkrv"] *= df["vekt"]
    df = df.pivot_table(index=["aar", "uke"], values="pkrv", aggfunc="sum")
    df = df.reset_index()

    return df