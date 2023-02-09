import os

from .skriv_tilsim_script    import skriv_tilsim_script
from .skriv_tilsim_batscript import skriv_tilsim_batscript


def skriv_tilsim_script_og_bat(output_dir, omr_df, dos, 
                               fn_script="kjor_tilsim.script", fn_bat="kjor_tilsim.bat"):

    path_script = os.path.join(output_dir, fn_script)
    path_bat    = os.path.join(output_dir, fn_bat)

    skriv_tilsim_script(path_script, omr_df)
    skriv_tilsim_batscript(path_bat, dos, fn_script)