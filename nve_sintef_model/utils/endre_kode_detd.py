import os
import re
import codecs

def endre_kode_detd_dir(detd_dir, old_char, new_char, encoding="cp865"):
    "bytter -old_char med -new_char i alle detd-filer i detd_dir"
    
    for fn in os.listdir(detd_dir):

        if not fn.upper().endswith() == ".DETD":
            continue

        path = os.path.join(detd_dir, fn)

        endre_kode_detd_file(path, old_char, new_char, encoding)


def endre_kode_detd_file(path, old_char, new_char, encoding="cp865"):
    "bytter -old_char med -new_char i en detd-fil"
    
    with codecs.open(path, "r", encoding=encoding) as f:
        string = f.read()

    string = re.sub(r"(\d+-)(%s)" % old_char, r"\1%s" % new_char, string)

    with codecs.open(path, "w", encoding=encoding) as f:
        f.write(string)