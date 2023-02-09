import struct

def write_io_vverd(path, d):
    """
    skriver vverd_nnn.samk til en sti gitt et dict med nodvendige data
    d maa vaere paa samme form som det som returneres fra funksjonen les_vverd_fil
    
    dimensjonaliteten til vannverdiene er (uke, pris, sno, tils, mag) -> vv
    
    merk at jstart og jslutt har uventet verdi i denne filen: i forhold til jstart og jslutt
    i andre .samk filer er jstart og jslutt i denne filen fratrukket 1
    i tillegg er det en ekstra vannverdikurve for terminalperioden (sluttverdifunksjonen)
    """
    blokklengde = d["blokklengde"]
    ntmag       = d["ntmag"]
    ntpris      = d["ntpris"]
    ntsno       = d["ntsno"]
    nttils      = d["nttils"]
    jstart      = d["jstart"]
    jslutt      = d["jslutt"]
    realrente   = d["realrente"]
    vannverdier = d["vannverdier"]
    
    with open(path, "wb") as f:
        f.write(struct.pack("i", blokklengde))
        f.write(struct.pack("i", ntmag))
        f.write(struct.pack("i", ntpris))
        f.write(struct.pack("i", ntsno))
        f.write(struct.pack("i", nttils))
        f.write(struct.pack("i", jstart))
        f.write(struct.pack("i", jslutt))
        f.write(struct.pack("f", realrente))

        for uke in range(jstart, jslutt + 1):
            f.seek((uke+1)*blokklengde)
            for pris in range(1, ntpris + 1):
                for sno in range(1, ntsno + 1):
                    for tils in range(1, nttils + 1):
                        for mag in range(1, ntmag + 1):
                            vv = vannverdier[(uke, pris, sno, tils, mag)]
                            f.write(struct.pack("f", vv))

