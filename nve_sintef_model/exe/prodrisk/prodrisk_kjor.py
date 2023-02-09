from nve_sintef_model.utils.run_sintef import run_sintef

def prodrisk_kjor(parallell, forste_uke_sim, siste_uke_sim, siste_uke_kutt, stmag,
                  forste_aar_sim, antall_aar_sim, model_dir, dos,
                  antall_kjerner, cmd_args,
                  scriptname="kjor_prodrisk.script",
                  batname="kjor_prodrisk.bat",
                  cleanup=True,
                  toscreen=True):

    """
    kjorer prodrisk i en modellmappe

    parallell - True hvis parallellsimulering, False hvis seriesimulering

    forste_uke_sim - forste simuleringsuke
    siste_uke_sim  - siste simuleringsuke
    siste_uke_kutt - siste uke det skal beregnes kutt for (bor vaere minst 52 uker mer enn siste_uke_sim)
    forste_aar_sim - forste simuleringsaar (kun disse aarene som brukes i strategiberegning)
    antall_aar_sim - antall simuleringsaar (kun disse aarene som brukes i strategiberegning)

    antall_aar - antall aar som dataperioden skal utvides til

    model_dir - sti til modellmappe

    dos - string med miljovariabler og sti til bin-mappe

    antall_kjerner - antall kjerner i multiprossessering av prodrisk
    cmd_args       - liste med kommando-linje argumenter til prodrisk

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

    lines = []
    lines.append("")
        
    if parallell:
        lines.append("paral")
    else:
        lines.append("serie")
        siste_uke_sim = forste_uke_sim + 51

    lines.append(str(forste_uke_sim))
    lines.append(str(siste_uke_sim))
            
    lines.append(str(siste_uke_kutt))
    lines.append("1") #startdogn hvis aktuelt

    lines.append("%s %s" % (forste_aar_sim, antall_aar_sim))

    lines.append(stmag)
    lines.append("") # bruk default utforingskoder
    lines.append("") # bruk default beregningsparams
    lines.append("") # en enter til for aa starte

    script = "\n".join(lines)

    args = cmd_args
    args = [s.upper() for s in args]
    args = " ".join(args)

    cmd = "mpiexec -n %d prodrisk_ms_mpi.exe %s" % (antall_kjerner, args)

    stdout, stderr = run_sintef(dos, cmd, script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        
