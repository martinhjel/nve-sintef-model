from nve_sintef_model.utils.run_sintef import run_sintef

def enmdat_lag_enkelt_eksogent_omr(antall_aar, model_dir, dos, navn_vassdrag,
                                   scriptname="kjor_detmod.script",
                                   batname="kjor_detmod.bat",
                                   cleanup=True,
                                   toscreen=True):

    """
    kjorer enmdat i en modellmappe og forsoker aa utvide antall aar
    i dataperioden til antall_aar. hvis dataperioden allerede er >= 
    antall_aar gir enmdat ufarlige feilmeldinger

    antall_aar - antall aar som dataperioden skal utvides til

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

    script = get_enmdat_utvid_dataperiode_script(navn_vassdrag, antall_aar)

    stdout, stderr = run_sintef(dos, "enmdat", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        

def get_enmdat_utvid_dataperiode_script(navn_vassdrag, antall_aar):
    "lager script for aa utvide dataperiode i enmdat"

    lines = []

    lines.append("inn,%s" % navn_vassdrag)
    lines.append("datper")
    lines.append("utvid")
    lines.append(str(antall_aar))
    lines.append("filgen")
    lines.append("")
    lines.append("exit")

    return "\n".join(lines)
