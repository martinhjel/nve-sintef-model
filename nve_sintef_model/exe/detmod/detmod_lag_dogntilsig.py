from nve_sintef_model.utils.run_sintef import run_sintef

def detmod_lag_dogntilsig(model_dir, dos, navn_vassdrag,
                          scriptname="kjor_detmod.script",
                          batname="kjor_detmod.bat",
                          cleanup=True,
                          toscreen=True, antall_aar="", forste_aar=""):

    """
    kjorer detmod i en modellmappe slik at det blir laget en fil
    med dogntilsig der (DGN-TILSIG.SIMT)

    model_dir - sti til modellmappe

    dos - string med miljovariabler og sti til bin-mappe

    navn_vassdrag - navnet paa vassdraget (maa stemme med .ENMD og .DETD fil i model_dir)

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

    script = get_detmod_lag_dogntilsig_script(navn_vassdrag, antall_aar, forste_aar)

    stdout, stderr = run_sintef(dos, "detmod", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        

def get_detmod_lag_dogntilsig_script(navn_vassdrag, antall_aar="", forste_aar=""):
    "lager detmod-script for aa lage fil med dogntilsig for et vassdrag"

    lines = []

    lines.append("D")
    lines.append("")
    lines.append("%s.DETD" % navn_vassdrag)
    lines.append("%s.ENMD" % navn_vassdrag)
    lines.append("")
    lines.append(str(antall_aar))
    lines.append(str(forste_aar))
    lines.append("")

    return "\n".join(lines)
