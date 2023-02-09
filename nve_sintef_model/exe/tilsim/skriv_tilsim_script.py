from .get_tilsim_script import get_tilsim_script

def skriv_tilsim_script(path, omr_df):
    s = get_tilsim_script(omr_df)

    with open(path, "w") as f:
        f.write(s)