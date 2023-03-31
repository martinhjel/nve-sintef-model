from typing import Union, Dict, List
from pathlib import Path
import struct

from .Enmres import EnmresProperty

def read_io_enmres(
    path: Union[str, Path]
) -> Dict[str, Union[str, int, float, List[List[Union[int, float]]]]]:
    """
    Reads the binary data from the ENMRES file and returns it as a dictionary.

    Parameters
    ----------
    path : Union[str, Path]
        Path to the ENMRES file.

    Returns
    -------
    Dict[str, Union[str, int, float, List[List[Union[int, float]]]]]
        A dictionary containing the data read from the ENMRES file.
    """
    encoding = "cp865"

    with open(path, "rb") as f:
        enmfil = b"".join([i for i in struct.unpack("c" * 60, f.read(60))]).decode(encoding).strip()
        enmtid = struct.unpack("i" * 7, f.read(7 * 4))
        runcode = struct.unpack("c" * 40, f.read(40))
        npre, nsim, naar, staar, innaar, nuke, ntrinn, jstart, jslutt, serie, npenm = struct.unpack(
            "i" * 11, f.read(11 * 4)
        )
        ntimen = struct.unpack("i" * npenm, f.read(npenm * 4))
        (stmag,) = struct.unpack("f", f.read(4))
        hist = struct.unpack("i" * nsim, f.read(nsim * 4))
        (tprog,) = struct.unpack("i", f.read(4))
        tprog = int(tprog != 0)
        (realrente,) = struct.unpack("f", f.read(4))

        blokklengde = max(12 * 4 * npenm * (jslutt - jstart + 1), 100 + (npenm + nsim + 19 + 2) * 4)

        blokknr = lambda n: n

        data = dict()

        data["enmfil"] = enmfil
        data["enmtid"] = enmtid
        data["runcode"] = runcode
        data["npre"] = npre
        data["nsim"] = nsim
        data["naar"] = naar
        data["staar"] = staar
        data["innaar"] = innaar
        data["nuke"] = nuke
        data["ntrinn"] = ntrinn
        data["jstart"] = jstart
        data["jslutt"] = jslutt
        data["serie"] = serie
        data["npenm"] = npenm
        data["ntimen"] = ntimen
        data["stmag"] = stmag
        data["hist"] = hist
        data["tprog"] = tprog
        data["realrente"] = realrente
        data["blokklengde"] = blokklengde

        rows = {k.value: [] for k in EnmresProperty}

        for n, aar in enumerate(hist, start=1):
            f.seek(blokklengde * blokknr(n))

            for uke in range(jstart, jslutt + 1):
                for tsnitt in range(1, npenm + 1):
                    values = struct.unpack("f" * 12, f.read(4 * 12))
                    for k, value in zip(EnmresProperty, values):
                        rows[k.value].append([aar, uke, tsnitt, value])

        data.update(rows)

        return data
