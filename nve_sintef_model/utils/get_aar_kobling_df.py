import pandas as pd

def get_aar_kobling_df(startaar_inn, sluttaar_inn, startaar_ut, sluttaar_ut):

    """
    returnerer en df med kolonner (aar, kobling_aar) hvor

        aar = aarene fra startaar_ut til sluttaar_ut

        kobling_aar = sekvens med aarene fra startaar_inn til sluttaar_inn
                      sekvensen repeteres og er skiftet slik at aarene matcher der
                      sekvensen overlapper aarene i aar-kolonnen

    typisk bruk: vi har data for 1981-2010 men trenger et datasett med periode 1958-2016, og
                 onsker aa repetere aarene mellom 1981-2010. kode under viser bruk og resultat

    KODE:

    startaar_inn = 1981
    sluttaar_inn = 2010
    startaar_ut = 1958
    sluttaar_ut = 2016
    df = get_aar_kobling_df(startaar_inn, sluttaar_inn, startaar_ut, sluttaar_ut)
    print(df) 

    RESULTAT:

         aar  aar_kobling
    0   1958         1988
    1   1959         1989
    2   1960         1990
    3   1961         1991
    4   1962         1992
    5   1963         1993
    6   1964         1994
    7   1965         1995
    8   1966         1996
    9   1967         1997
    10  1968         1998
    11  1969         1999
    12  1970         2000
    13  1971         2001
    14  1972         2002
    15  1973         2003
    16  1974         2004
    17  1975         2005
    18  1976         2006
    19  1977         2007
    20  1978         2008
    21  1979         2009
    22  1980         2010
    23  1981         1981
    24  1982         1982
    25  1983         1983
    26  1984         1984
    27  1985         1985
    28  1986         1986
    29  1987         1987
    30  1988         1988
    31  1989         1989
    32  1990         1990
    33  1991         1991
    34  1992         1992
    35  1993         1993
    36  1994         1994
    37  1995         1995
    38  1996         1996
    39  1997         1997
    40  1998         1998
    41  1999         1999
    42  2000         2000
    43  2001         2001
    44  2002         2002
    45  2003         2003
    46  2004         2004
    47  2005         2005
    48  2006         2006
    49  2007         2007
    50  2008         2008
    51  2009         2009
    52  2010         2010
    53  2011         1981
    54  2012         1982
    55  2013         1983
    56  2014         1984
    57  2015         1985
    58  2016         1986

                     
    """

    assert isinstance(startaar_inn, int)
    assert isinstance(sluttaar_inn, int)
    assert isinstance(startaar_ut, int)
    assert isinstance(sluttaar_ut, int)
    assert startaar_inn <= sluttaar_inn
    assert startaar_ut  <= sluttaar_ut
    assert startaar_inn <= sluttaar_ut
    assert sluttaar_inn >= startaar_ut

    ut_liste = list(range(startaar_ut, sluttaar_ut + 1))

    start = max(startaar_inn, startaar_ut)
    slutt = min(sluttaar_inn, sluttaar_ut)

    midten_liste = list(range(start, slutt + 1))

    idx_start = ut_liste.index(start)
    idx_slutt = ut_liste.index(slutt)

    bak_liste = []
    i = idx_start
    aar = start - 1
    while i > 0:
        if aar < startaar_inn:
            aar = sluttaar_inn
        bak_liste.append(aar)
        i   -= 1
        aar -= 1

    foran_liste = []
    i = idx_slutt
    aar = slutt + 1
    while i < len(ut_liste) - 1:
        if aar > sluttaar_inn:
            aar = startaar_inn
        foran_liste.append(aar)
        i   += 1
        aar += 1

    kobling_liste = list(reversed(bak_liste)) + midten_liste + foran_liste

    assert len(kobling_liste) == len(ut_liste)

    rows = list(zip(ut_liste, kobling_liste))
    df = pd.DataFrame(rows, columns=["aar", "aar_kobling"])

    return df