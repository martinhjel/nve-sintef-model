
def get_ntimen_from_prisavsnitt_fil(path):

    rows = []
    with open(path) as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.replace("\r", "")
            line = line.lower()
            strings = line.split(",")
            if not len(strings) >= 25:
                continue

            rows.append(strings[:-1])

    assert len(rows) == 7

    d = dict()
    for r in rows:
        for ts in r:
            ts = int(ts)
            if not ts in d:
                d[ts] = 0
            d[ts] += 1

    ntimen = [(ts,n) for ts,n in d.items()]                    
    ntimen = sorted(ntimen)
    ntimen = [n for ts,n in ntimen]
    return ntimen
