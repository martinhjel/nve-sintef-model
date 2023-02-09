import os
from subprocess import Popen, PIPE

def run_sintef(dos, exe, script, folder, scriptname="run_sintef.script", batname="run_sintef.bat", 
               cleanup=True, toscreen=True):
    """
    kjorer et sintef-program med hensyn paa et script

    parametere:

    dos - string med miljovariabler (sti til hydark osv)

    exe - string med navn paa sintef-program ('enmdat', 'vansimtap' osv)

    script - string med kommandoer til sintef-programmet (eks 'ja\nja\nja')

    folder - sti til modellmappen som sintef-programmet skal kjores fra

    scriptname - navn paa filen med script til sintef-program

    batname - navn paa .bat fil som skal sette miljovariabler og deretter
              kjore sintef-programmet med hensyn paa scriptfilen
              merk at denne filen maa ha et navn som slutter med .bat
              funksjonen sjekker dette og feiler hvis filen ikke ender
              med .bat

    cleanup - hvis True saa slettes filene scriptfilen
              og batfilen etter at sintef-programmet er kjort
    """
    assert batname.lower().endswith(".bat"), "batname maa ende med .bat"

    abspath_folder = os.path.abspath(folder)

    with open(os.path.join(abspath_folder, scriptname), "w") as f:
        f.write(script)

    with open(os.path.join(abspath_folder, batname), "w") as f:
        f.write("\n".join([dos, "%s < %s" % (exe, scriptname)]))

    if toscreen:
        p = Popen(os.path.join(abspath_folder, batname), cwd=abspath_folder)

    else:
        p = Popen(os.path.join(abspath_folder, batname), cwd=abspath_folder, stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()

    if cleanup:
        os.remove(os.path.join(abspath_folder, scriptname))
        os.remove(os.path.join(abspath_folder, batname))

    return stdout, stderr
