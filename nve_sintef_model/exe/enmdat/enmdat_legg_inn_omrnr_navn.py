from nve_sintef_model.utils.run_sintef import run_sintef

def enmdat_legg_inn_omrnr_navn(omrnr, omrnavn, model_dir, dos,
                               scriptname="kjor_enmdat_legg_inn_omrnr_navn.script",
                               batname="kjor_enmdat_legg_inn_omrnr_navn.bat",
                               cleanup=True,
                               toscreen=True):

    """
    kjorer enmdat i en modellmappe og setter omrnr og omrnavn i sys-menyen

    omrnr - nr paa delomraade
    omrnavn - navn paa delomraade (maa stemme med navn paa enmd-fil i modellmappen)

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

    script = get_enmdat_legg_inn_omrnr_navn_script(omrnr, omrnavn)

    stdout, stderr = run_sintef(dos, "enmdat", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        

def get_enmdat_legg_inn_omrnr_navn_script(omrnr, omrnavn):
    "lager script for aa legge inn omrnr og navn i enmdat"

    lines = []
    lines.append("inn,%s" % omrnavn)
    lines.append("les")
    lines.append("sys")
    lines.append(str(omrnr))
    lines.append(omrnavn)
    lines.append("")
    lines.append("filgen")
    lines.append(str(omrnavn))
    lines.append("exit")

    return "\n".join(lines)
