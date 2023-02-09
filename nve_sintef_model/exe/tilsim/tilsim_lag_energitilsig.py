from nve_sintef_model.utils import run_sintef

from .get_tilsim_script import get_tilsim_script

def tilsim_lag_energitilsig(model_dir, omr_df, dos, scriptname="kjor_tilsim.script", 
                            batname="kjor_tilsim.bat", cleanup=False, toscreen=True):

    script = get_tilsim_script(omr_df)
    run_sintef(dos, "tilsim", script, model_dir, scriptname, batname, cleanup, toscreen)
