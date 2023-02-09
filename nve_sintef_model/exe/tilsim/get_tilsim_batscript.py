def get_tilsim_batscript(dos, fn_script):

    lines = []
    lines.append(dos)
    lines.append("tilsim < %s" % fn_script)

    string = "\n".join(lines)

    return string
