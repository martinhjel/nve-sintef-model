import struct

def read_io_c20_omrade(path):
    """
    Leser innholdet i filen C20_OMRADE.EMPS til en pandas.DataFrame
    med kolonner omrnr, omrnavn
    """
    rows = []

    with open(path, "rb") as f:
        blengde, nverk = struct.unpack(2 * "i", f.read(2 * 4))
        f.seek(blengde)

        for omrnr in range(1, nverk + 1):
            omrnavn = struct.unpack(20 * "c", f.read(20 * 1))
            omrnavn = b"".join(omrnavn)
            omrnavn = omrnavn.strip()
            try:
                omrnavn = omrnavn.decode("cp865")
            except:
                omrnavn = omrnavn.decode("utf-8", "ignore")
                

            rows.append([omrnr, omrnavn])

    return rows
