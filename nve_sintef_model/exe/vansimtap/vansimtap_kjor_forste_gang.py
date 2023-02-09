from nve_sintef_model.utils.run_sintef import run_sintef
    
def vansimtap_kjor_forste_gang(model_dir, dos, 
                               omrnavn,
                               omrtype,
                               startaar_tilsig,
                               antall_aar_tilsig,
                               startuke = 1,
                               sluttuke = 156,
                               stmag = "A,60,,",
                               parallell = True,
                               scriptname="xrun_vansimtap_kjor_forste_gang.script",
                               batname="xrun_vansimtap_kjor_forste_gang.bat",
                               cleanup=True,
                               toscreen=True,
                               sim=False,
                               forste_aar_sim=None, 
                               antall_aar_sim=None):

    """
    kjorer vansimtap.exe i en modellmappe for forste gang, og setter verdier som tilsigsstatistikk, kjoremodus (parallell eller serie),
    stmag, start og sluttuke. dataene lagres uten simulering.

    model_dir - sti til modellmappe

    dos - string med miljovariabler og sti til bin-mappe

    omrnavn - navn paa omraade (maa stemme med .DETD og .ENMD fil)

    omrtype - DET eller ING (DET = detaljert vannkraft (ie. har .DETD fil), ING = omr har kun .ENMD fil)

    startaar_tilsig - forste aar i tilsigsstatistikken

    antall_aar_tilsig - antall aar i tilsigsstatistikken

    startuke - forste uke i simuleringsperioden

    sluttuke - siste uke i simuleringsperioden

    parallell - True hvis vansimtap skal settes opp for parallellsimulering
                False hvis vansimtap skal settes opp for seriesimulering
                  nb! hvis prisrekkefil ikke stemmer med simuleringsmodus begynner vansimtap aa gi 
                      advarsler, noe som kan medfore feil i vansimtap

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
 
    sim - True hvis simulering, False hvis exit etter DAT (bare mulig hvis omrtype = DET)

    forste_aar_sim - forste simuleringsaar (bare brukt hvis sim og omrtype = DET)
    antall_aar_sim - antall simuleringsaar (bare brukt hvis sim og omrtype = DET)

    """

    script = get_vansimtap_kjor_forste_gang_script(omrnavn, omrtype, startaar_tilsig,
                                                   antall_aar_tilsig, startuke, sluttuke,
                                                   stmag, parallell, sim, forste_aar_sim, antall_aar_sim)

    stdout, stderr = run_sintef(dos, "vansimtap", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        

def get_vansimtap_kjor_forste_gang_script(omrnavn, omrtype, startaar_tilsig,
                                                   antall_aar_tilsig, startuke, sluttuke,
                                                   stmag, parallell, sim, forste_aar_sim, antall_aar_sim):
    """
    lager script for aa kjore vansimtap.exe i en modellmappe for forste gang, 
    og setter verdier som tilsigsstatistikk, kjoremodus (parallell eller serie),
    stmag, start og sluttuke. dataene lagres uten simulering.

    omrnavn - navn paa omraade (maa stemme med .DETD og .ENMD fil)

    omrtype - DET eller ING (DET = detaljert vannkraft (ie. har .DETD fil), ING = omr har kun .ENMD fil)

    startaar_tilsig - forste aar i tilsigsstatistikken

    antall_aar_tilsig - antall aar i tilsigsstatistikken

    startuke - forste uke i simuleringsperioden

    sluttuke - siste uke i simuleringsperioden

    parallell - True hvis vansimtap skal settes opp for parallellsimulering
                False hvis vansimtap skal settes opp for seriesimulering
                  nb! hvis prisrekkefil ikke stemmer med simuleringsmodus begynner vansimtap aa gi 
                      advarsler, noe som kan medfore feil i vansimtap

    sim - True hvis simulering, False hvis exit etter DAT (bare mulig hvis omrtype = DET)

    forste_aar_sim - forste simuleringsaar (bare brukt hvis sim og omrtype = DET)
    antall_aar_sim - antall simuleringsaar (bare brukt hvis sim og omrtype = DET)

    """

    if not parallell:
        if not ((sluttuke - startuke) == 51):
            print("endrer sluttuke fra %s til %s" % (sluttuke, startuke + 51))
            sluttuke = startuke + 51

    assert sluttuke >= 52
    assert sluttuke % 52 == 0

    omrtype = omrtype.upper()
    assert omrtype in ["DET", "ING"]

    if omrtype == "DET":
        return _get_vansimtap_script_det(omrnavn, startaar_tilsig,
                                         antall_aar_tilsig, startuke, sluttuke,
                                         stmag, parallell, sim, forste_aar_sim, antall_aar_sim)

    if omrtype == "ING":
        return _get_vansimtap_script_ing(omrnavn, startaar_tilsig, antall_aar_tilsig, 
                                         startuke, sluttuke, parallell)

def _get_vansimtap_script_det(omrnavn, startaar_tilsig, antall_aar_tilsig, 
                              startuke, sluttuke, stmag, parallell, sim, forste_aar_sim, antall_aar_sim):
        lines = []
        lines.append(omrnavn)
        lines.append("ja")

        lines.append("DET")
        lines.append(str(startaar_tilsig))
        lines.append(str(antall_aar_tilsig))

        lines.append("DAT")

        lines.append("start")
        lines.append(str(startuke))
        lines.append(stmag)

        lines.append("serie")
        if parallell:
            lines.append("paral")
            lines.append(str(startuke))
            lines.append("slutt")
            lines.append(str(sluttuke))
        else:
            lines.append("serie")
            lines.append(str(startuke))

        if sim and forste_aar_sim and antall_aar_sim:
            lines.append("nsim")
            lines.append(str(antall_aar_sim))

            lines.append("hist")
            lines.append("tilfeldig")
            lines.append("nei") # ikke random
            for aar in range(forste_aar_sim, forste_aar_sim + antall_aar_sim):
                lines.append(str(aar))

        lines.append("") # uthopp til hoved

        if sim:
            lines.append("SIM")

        lines.append("exit") # forste exit lagrer
        lines.append("exit") # andre exit gaar ut

        script = "\n".join(lines)

        return script

def _get_vansimtap_script_ing(omrnavn, startaar_tilsig, antall_aar_tilsig, 
                              startuke, sluttuke, parallell):
        lines = []
        lines.append(omrnavn)
        lines.append("ja")
        lines.append("ING")

        lines.append("DAT") # taes til annen meny
        lines.append("tils") 
        lines.append(str(startaar_tilsig))
        lines.append(str(antall_aar_tilsig))
        lines.append("") # uthopp til hovedmeny

        lines.append("DAT") # denne gangen gaar man til dat-meny

        lines.append("start")
        lines.append(str(startuke))

        lines.append("serie")
        if parallell:
            lines.append("paral")
            lines.append(str(startuke))
            lines.append("slutt")
            lines.append(str(sluttuke))
        else:
            lines.append("serie")
            lines.append(str(startuke))

        lines.append("") # uthopp til hoved

        lines.append("exit") # forste exit lagrer
        lines.append("exit") # andre exit gaar ut

        script = "\n".join(lines)

        return script
