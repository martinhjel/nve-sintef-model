from nve_sintef_model.utils.run_sintef import run_sintef
    
def med_legg_inn_restriksjoner(restriksjoner, model_dir, dos, navn_vassdrag,
                               scriptname="kjor_detmod.script",
                               batname="kjor_detmod.bat",
                               cleanup=True,
                               toscreen=True):

    """
    kjorer med.exe i en modellmappe og legger inn restriksjoner 
    (minstevannforing eller magasinrestriksjon) 

    restriksjoner er paa formen [(modulnr, restriksjonstype, detaljer), ...]

        restriksjonstype in ["mvf_forbitapp", "mvf_stasjon", "mag_max_myk", "mag_min_myk", 
                             "mag_max_absolutt", "mag_min_absolutt"]

        detaljer = [(sluttuke, verdi), ..]

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

    script = get_med_legg_inn_restriksjoner_script(navn_vassdrag, restriksjoner)

    stdout, stderr = run_sintef(dos, "med", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr        

def get_med_legg_inn_restriksjoner_script(navn_vassdrag, restriksjoner):
    """
    lager med-script for aa legge inn restriksjoner 
    (minstevannforing eller magasinrestriksjon) 

    navn_vassdrag - navnet paa vassdraget (maa stemme med .ENMD og .DETD fil i model_dir)

    restriksjoner er paa formen [(modulnr, restriksjonstype, detaljer), ...]

        restriksjonstype in ["mvf_forbitapp", "mvf_stasjon", "mag_max_myk", "mag_min_myk", 
                             "mag_max_absolutt", "mag_min_absolutt"]

        detaljer = [(sluttuke, verdi), ..]
    """

    lines = []
    lines.append("inn,%s" % navn_vassdrag)
    lines.append('les')
        
    for modnr, rtype, detaljer in restriksjoner:
            
        if rtype == "mvf_forbitapp":
            lines.extend(_add_mvf("21", modnr, detaljer))
                
        elif rtype == "mvf_stasjon":
            lines.extend(_add_mvf("20", modnr, detaljer))
                
        elif rtype == "mag_max_myk":
            lines.extend(self._add_mag("17", "1", modnr, detaljer))
                
        elif rtype == "mag_min_myk":
            lines.extend(_add_mag("18", "1", modnr, detaljer))
                
        elif rtype == "mag_max_absolutt":
            lines.extend(_add_mag("17", "2", modnr, detaljer))
                
        elif rtype == "mag_min_absolutt":
            lines.extend(_add_mag("18", "2", modnr, detaljer))

    lines.append("") # hoppe ut til hovedmeny
        
    lines.append("filgen")
    lines.append("")
    lines.append("exit")
    
    return "\n".join(lines)
    
def _add_mvf(nr, modnr, detaljer):
    "med-kommandoer for aa legge inn minstevannforing-restriksjon"

    lines = []
    lines.append(str(modnr))
    lines.append('S ' + nr) # slette gammel restriksjon
    lines.append(nr)
    lines.append('N') # ikke koble mot tilsigsserie

    for v in detaljer:
        lines.append(str(v[0]) + ' ' + str(v[1]))

    lines.append('S') # uthopp
    lines.append('Y') # data er ok
    lines.append('')  # hoppe ut til modulliste-meny

    return lines

def _add_mag(nr, abs_myk, modnr, detaljer):
    "med-kommandoer for aa legge inn magasin-restriksjon"

    lines = []
    lines.append(str(modnr))
    lines.append('S ' + nr) # slette gammel restriksjon
    lines.append(nr)

    for v in detaljer:
        lines.append(str(v[0]) + ' ' + str(v[1]))

    lines.append('S') # uthopp
    lines.append(abs_myk) # 2 hvis abs, 1 hvis myk
    lines.append('')  # data er ok
    lines.append('')  # hoppe ut til modulliste-meny

    return lines 
