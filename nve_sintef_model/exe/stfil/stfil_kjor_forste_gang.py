import os

from nve_sintef_model.utils.run_sintef import run_sintef

from nve_sintef_model.exe.samtap.samtap_lag_enkel_styrefil import samtap_lag_enkel_styrefil

def stfil_kjor_forste_gang(model_dir, dos, parallell, startuke, sluttuke, omr_df, kalib_df,
                           navn_samtap_styrefil="xrun_enkel_samtap.bat",
                           navn_samtap_loggfil="ut_enkel_samtap.txt",
                           scriptname="stfil_kjor_forste_gang.script",
                           batname="stfil_kjor_forste_gang.bat",
                           cleanup=True,
                           toscreen=True,
                           versjon=""):

    """
    kjorer stfil-script for aa kjore stfil for forste gang

    model_dir - sti til modellmappe hvor stfil skal kjores

    dos - string med miljovariabler og sti til bin-mappe

    parallell - True hvis parallellsimulering, False hvis seriesimulering

    startuke  - forste simuleringsuke

    sluttuke  - siste simuleringsuke (hvis utenfor dataperiode feiler stfil)

    omr_df    - df med info om omraadene i emps (skal bruke omrnr og omrtype)

    navn_samtap_styrefil - navn paa styrefil for samtap

    navn_samtap_loggfil - navn paa loggfil for output fra samtap

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

    versjon - feks "992" eller "962"

    """

    samtap_lag_enkel_styrefil(os.path.join(model_dir, navn_samtap_styrefil))

    script = get_stfil_kjor_forste_gang_script(parallell, startuke, sluttuke, omr_df, kalib_df,
                                               navn_samtap_styrefil, navn_samtap_loggfil, versjon)

    run_sintef(dos, "stfil", script, model_dir, scriptname, batname, cleanup, toscreen)


def get_stfil_kjor_forste_gang_script(parallell, startuke, sluttuke, omr_df, kalib_df,
                                      navn_samtap_styrefil="xrun_enkel_samtap.bat",
                                      navn_samtap_loggfil="ut_enkel_samtap.txt", versjon=""):

    """
    lager stfil-script for aa kjore stfil for forste gang
    
    parallell - True hvis parallellsimulering, False hvis seriesimulering
    startuke  - forste simuleringsuke
    sluttuke  - siste simuleringsuke (hvis utenfor dataperiode feiler stfil)
    omr_df    - df med info om omraadene i emps (skal bruke omrnr og omrtype)
    navn_samtap_styrefil - navn paa styrefil for samtap
    navn_samtap_loggfil - navn paa loggfil for output fra samtap
    versjon - feks "992" eller "962"
    """

    det_omrnr_liste = [r["omrnr"] for __,r in omr_df.iterrows() if r["omrtype"] == "DET"]
    det_omrnr_liste = sorted(det_omrnr_liste) # sorterer for sikkerhets skyld
    det_omrnr_liste = [str(i) for i in det_omrnr_liste]

    antall_ing_omr = omr_df[omr_df.omrtype != "DET"].omrnr.count()

    lines = []
    lines.append(" ".join([str(n) for n in det_omrnr_liste]))

    if parallell:
        lines.append("PARAL")
        lines.append(str(startuke))
        lines.append(str(sluttuke))
    else:
        lines.append("SERIE")
        lines.append(str(startuke))

    lines.append("JA")    # med vannverdiberegning
    lines.append("JA")    # med tappefordeling

    # sett stmag = 0 for alle omr som ikke er omrtype=DET
    for i in range(antall_ing_omr):
            lines.append("")

    lines.append("NEI") # ikke endre stmag
        
    if not kalib_df.empty:
        lines.append("KOPL")
        lines.append("NEI")

        # for aa handtere nytt meny-valg i v99
        if versjon.startswith("99"):
            lines.append("1")
            lines.append(str(sluttuke))

        for __, r in kalib_df.iterrows():
            lines.append("%s %s %s" % (r["tilb"], r["form"], r["elast"]))
            lines.append("")
        lines.append("JA")
            
    lines.append("")    # ikke endre kalib-fakt ol.

    # sett kjore-innstillinger
    lines.append("tapp")               # gi styrefil for samtap
    lines.append(navn_samtap_styrefil) # styrefil for samtap
    lines.append(navn_samtap_loggfil)  # logfil for output for samtap
    lines.append("AUTO")               # start simulering

    script     = "\n".join(lines)

    return script
