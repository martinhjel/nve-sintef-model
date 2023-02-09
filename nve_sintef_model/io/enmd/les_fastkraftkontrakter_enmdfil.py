import pandas as pd

def les_fastkraftkontrakter_enmdfil(filsti):
    rader = []
    with open(filsti) as f:
        linjer = f.readlines()

    i = 0
    while i < len(linjer):
        line = linjer[i]

        if "Dellastnr, Kategori, Navn" in line:
            kandidatrader = []
            try:
                nr, kat, navn = line.split(",")[:3]
                nr = int(nr.strip())
                kat = int(kat.strip())
                navn = navn.replace("'", "").strip()

                i += 2
                line = linjer[i]

                antall_perioder = int(line.split(",")[0].strip())
                for periode in range(1, antall_perioder + 1):
                    i += 1
                    line = linjer[i]
                    startuke, sluttuke, mengde = line.split(",")[:3]
                    startuke = int(startuke.strip())
                    sluttuke = int(sluttuke.strip())
                    mengde = pd.to_numeric(mengde.strip())

                    kandidatrader.append((nr, kat, navn, periode, startuke, sluttuke, mengde))

                # det gikk ok
                for rad in kandidatrader:
                    rader.append(rad)
            except:
                pass
        i += 1

    df = pd.DataFrame(rader, columns=["nr", "kat", "navn", "periode", "startuke", "sluttuke", "mengde"])

    return df


