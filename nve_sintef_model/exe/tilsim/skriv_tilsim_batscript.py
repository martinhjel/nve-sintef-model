from .get_tilsim_batscript import get_tilsim_batscript

def skriv_tilsim_batscript(path, dos, fn_script):
    s = get_tilsim_batscript(dos, fn_script)

    with open(path, "w") as f:
        f.write(s)