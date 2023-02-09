import os
from subprocess import Popen, PIPE

def run_batch(dos, exe, folder, batname="run_batch.bat", cleanup=True, toscreen=True):
    """
    kjorer en batch fil inn i sintef-program 

    parametere:

    dos - string med miljovariabler (sti til hydark osv)

    exe - string med navn paa batch fil ('bytt_tsnitt.bat' osv.)

    folder - sti til modellmappen som sintef-programmet skal kjores fra

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

    with open(os.path.join(abspath_folder, batname), "w") as f:
        f.write("\n".join([dos, "%s" % (exe)]))

    if toscreen:
        p = Popen(os.path.join(abspath_folder, batname), cwd=abspath_folder)

    else:
        p = Popen(os.path.join(abspath_folder, batname), cwd=abspath_folder, stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()

    if cleanup:
        os.remove(os.path.join(abspath_folder, batname))

    return stdout, stderr
