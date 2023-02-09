
def get_tilsim_script(omr_df):

    lines = []
    for __,r in omr_df.iterrows():
        lines.append(str(int(r["omrnr"])))
        lines.append("ja") # skal brukes for hele simuleringsperioden
        lines.append(r["omrnavn"])
        lines.append("")
    lines.append("EXIT")

    string = "\n".join(lines)

    return string
