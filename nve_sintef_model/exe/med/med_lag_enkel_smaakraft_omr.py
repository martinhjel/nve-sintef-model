from nve_sintef_model.utils.run_sintef import run_sintef

def med_lag_enkel_smaakraft_omr(model_dir, dos, omrnavn, modnr, modnavn, 
                                seriekode, forste_aar_tilsig, siste_aar_tilsig, maks_vf, gwh,
                                scriptname="kjor_med_lag_enkel_smaakraft_omr.script",
                                batname="kjor_med_lag_enkel_smaakraft_omr.bat",
                                cleanup=True,
                                toscreen=True):

    """

    kjorer med og lager en detd-fil med en modul som har smaakraft 

    model_dir - sti til modellmappe

    omrnavn - navn paa omr
    modnr - modulnr
    modnavn - modulnavn (blir ogsaa brukt som stasjonsnavn)
    seriekode - seriekode for tilsiget (legges som regulert tilsig, men magasinkap er 0)
    forste_aar_tilsig - forste referanseaar i tilsigsstatistikken (typisk 1961)
    siste_aar_tilsig - forste referanseaar i tilsigsstatistikken (typisk 1990)
    maks_vf - maks vannforing i m3s
    gwh - midlere aarsproduksjon for modulen

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


    lines = []
    lines.append("les")

    lines.append(str(modnr))
    lines.append("ja")        # riktig modnr -> lag ny modul

    lines.append("VA")        # Type modul Vannkraft, Vindkraft (VA VI)

    lines.append(modnavn)     # modnavn
    lines.append("100")       # Eierandel (%)  (100)
    lines.append("0")         # Magasinvolum (Mm3)  (0)
    lines.append("10000")     # Maks. forbitapping (m3/sek)  (10000)
    lines.append("1")         # Midlere energiekvivalent (kWh/m3)  (0)
    lines.append(str(maks_vf))# Maks. vassforing (m3/s)  (0)

    lines.append("0")         # Midlere fallhoyde (m)  (0)
    lines.append("0")         # Utlopskote (m.o.h.)  (0)

    lines.append("0")         # Produksjonsvann mottas av modul nummer  (0)
    lines.append("0")         # Flomvann mottas av modul nummer  (0) 
    lines.append("0")         # Forbitapping mottas av modul nummer  (0) 
    lines.append("0")         # Kode for hydraulisk kobling  (0)

    lines.append(str(gwh))    # Midlere regulerbart tilsig (Mm3/aar)  (0)
    lines.append(seriekode)   # Serieversjonskode for regulerbart tilsig
    lines.append("B")         # Tast kode <NYLES BEHOLD FORKAST>

    lines.append(str(forste_aar_tilsig)) # forste ref-aar tilsigsstatistikk
    lines.append(str(siste_aar_tilsig))  # siste ref-aar tilsigsstatistikk        

    lines.append("0")         # Midlere uregulerbart tilsig (Mm3/aar) (0)
    lines.append(modnavn)     # Stasjonsnavn

    lines.append("")          # modul ok

    lines.append("")          # uthopp til hovedmeny

    lines.append("filgen")    # lagre fil
    lines.append(omrnavn)     # gi omrnavn

    lines.append("exit")      # avslutt med

    script = "\n".join(lines)


    stdout, stderr = run_sintef(dos, "med", script, 
                                model_dir, scriptname, 
                                batname, cleanup, toscreen)

    return stdout, stderr

