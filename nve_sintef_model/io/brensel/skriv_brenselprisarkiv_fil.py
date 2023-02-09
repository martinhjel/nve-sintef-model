

def skriv_brenselprisarkiv_fil(path, brensler, sluttuke, filversjon=1,
                               kommentar_header  = "** filversjon, antall_brensler, sluttuke",
                               kommentar_brensel = "** brenselnavn, co2_cont, energi_koef",
                               kommentar_uke     = "** sluttuke, brenselpris, brenselavgift, co2_pris"):

    """
    path - sti som filen skal skrives til

    brensler - liste med brenseldata (dict) (brenslets plassering i listen angir brenslets brenselnr)

            brenseldata = {'brenselnavn' : navn paa brensel (str), 
                           'co2_cont'    : co2-innhold i brensel (float),
                           'energi_koef' : energi_koef i brensel (float),
                           'priser'      : liste med ukedata (dict)}

            ukedata = {'sluttuke'      : siste uke disse dataene gjelder frem til (int),
                       'brenselspris'  : pris paa brensel (float),
                       'brenselavgift' : avgift paa brensel (float),
                       'co2_pris'      : pris paa co2 (float)}

    sluttuke - siste uke i dataperioden (ofte 156)

    filversjon - versjonsnummer paa filen (default 1)

    kommentar_header - valgfri kommentar i forste linje i brenselarkiv-filen

    kommentar_brensel - valgfri kommentar ved definisjon av hvert brensel i brenselarkiv-filen

    kommentar_uke - valgfri kommentar ved hver rad med ukedata i brenselarkiv-filen

    """

    antall_brensler = len(brensler)

    lines = []

    lines.append("%d, %d, %d, %s" % (filversjon, antall_brensler, sluttuke, kommentar_header))

    for d in brensler:

        brenselnavn  = d["brenselnavn"]
        co2_cont     = d["co2_cont"]
        energi_koef  = d["energi_koef"]

        priser       = d["priser"]

        lines.append("'%s', %4.2f, %4.2f, %s" % (brenselnavn, co2_cont, energi_koef, kommentar_brensel))

        for p in priser:
            uke           = p["sluttuke"]
            brenselpris   = p["brenselpris"]
            brenselavgift = p["brenselavgift"]
            co2_pris      = p["co2_pris"]

            lines.append("% 4d, %4.2f, %4.2f, %4.2f, %s" % (uke, brenselpris, brenselavgift, co2_pris, kommentar_uke))

    s = "\n".join(lines)

    with open(path, "w") as f:
        f.write(s)
