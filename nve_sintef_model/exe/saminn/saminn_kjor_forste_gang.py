from nve_sintef_model.utils.run_sintef import run_sintef
    
def saminn_kjor_forste_gang(model_dir, dos, 
                            antall_omr, antall_aar_data,antall_tsnitt, 
                            antall_aar_tilsig, startaar_tilsig, omrnavn_liste, 
                            grupper, prisnivaa,
                            scriptname="xrun_saminn_kjor_forste_gang.script",
                            batname="xrun_saminn_kjor_forste_gang.bat",
                            cleanup=True,
                            toscreen=True):

    """
    kjorer script for aa kjore saminn.exe for forste gang.

    forste gang saminn kjores er det viktig aa sette alle parametere riktig, som
       antall omr
       tilsigsstatistikk
       antall_prisavsnitt
       hvert omr maa legges inn
       eventuelle grupper legges inn
       om det skal kjores med eksogene prisnivaa

    model_dir - sti til modellmappe

    dos - string med miljovariabler og sti til bin-mappe
 
    antall_omr - antall delomraader i modellen
    antall_aar_data - antall aar i dataperioden
    antall_tsnitt - antall tidsavsnitt i modellen
    startaar_tilsig - forste aar i tilsigsstatistikken
    antall_aar_tilsig - antall aar i tilsigsstatistikken
    omrnavn_liste - liste med alle omraadene i modellen
                    ma stemme med navn paa .ENMD filer
                    rekkefolge maa stemme med omrnr i .ENMD filer
    grupper - liste med (gruppenavn, omrnr_liste) som sier hvilke omrnr som finnes i gruppene
              omrnr kan bare finnes i en gruppe
              alle omrnr i modellen maa tilhore en gruppe for gyldig gruppering

    prisnivaa - hvis True skal det kjores med eksogene prisnivaa, False ellers (default)

    scriptname - navn paa filen med script til sintef-program

    batname - navn paa .bat fil som skal sette miljovariabler og deretter
              kjore sintef-programmet med hensyn paa scriptfilen
              merk at denne filen maa ha et navn som slutter med .bat
              funksjonen sjekker dette og feiler hvis filen ikke ender
              med .bat

    cleanup - hvis True saa slettes filene scriptfilen
              og batfilen etter at sintef-programmet er kjort

    toscreen - hvis True saa printes output fra detmod paa skjermen
               hvis False saa sendes stdout og stderr til variabler som returneres
               av funksjonen
    """

    script = get_saminn_kjor_forste_gang_script(antall_omr, antall_aar_data,antall_tsnitt, 
                                                antall_aar_tilsig, startaar_tilsig, omrnavn_liste, 
                                                grupper, prisnivaa)

    stdout, stderr = run_sintef(dos, "saminn", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        

def get_saminn_kjor_forste_gang_script(antall_omr, antall_aar_data,antall_tsnitt, 
                                       antall_aar_tilsig, startaar_tilsig, omrnavn_liste, 
                                       grupper=None, prisnivaa=False):
    """
    lager script for aa kjore saminn.exe for forste gang.
    forste gang saminn kjores er det viktig aa sette alle parametere riktig, som
       antall omr
       tilsigsstatistikk
       antall_prisavsnitt
       hvert omr maa legges inn
       eventuelle grupper legges inn
       om det skal kjores med eksogene prisnivaa
 
    antall_omr - antall delomraader i modellen
    antall_aar_data - antall aar i dataperioden
    antall_tsnitt - antall tidsavsnitt i modellen
    startaar_tilsig - forste aar i tilsigsstatistikken
    antall_aar_tilsig - antall aar i tilsigsstatistikken
    omrnavn_liste - liste med alle omraadene i modellen
                    ma stemme med navn paa .ENMD filer
                    rekkefolge maa stemme med omrnr i .ENMD filer
    grupper - liste med (gruppenavn, omrnr_liste) som sier hvilke omrnr som finnes i gruppene
              omrnr kan bare finnes i en gruppe
              alle omrnr i modellen maa tilhore en gruppe for gyldig gruppering

    prisnivaa - hvis True skal det kjores med eksogene prisnivaa, False ellers (default)
    """

    lines = []

    lines.append(str(antall_omr))
    lines.append(str(antall_aar_data))
    lines.append("") # forste aar default innevaernde
    lines.append(str(antall_tsnitt))
    lines.append(str(antall_aar_tilsig))
    lines.append(str(startaar_tilsig))
    lines.append("")        

    for omrnavn in omrnavn_liste:
        lines.append(omrnavn)

    lines.append("ja") # alt ok

    if prisnivaa:
        lines.append("ja")
    else:
        lines.append("nei")

    if grupper:
        lines.append("ja")
        for gruppe, omrnr_liste in grupper:
            lines.append(gruppe)
            omr_str = " ".join([str(i) for i in omrnr_liste])
            lines.append(omr_str)
    else:
        lines.append("nei")

    lines.append("ja") # alt ok

    script = "\n".join(lines)

    return script
