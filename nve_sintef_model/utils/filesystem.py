import os
import shutil

def copy_files_in_dir(src, dst):
    "kopierer alle filer fra en mappe til en annen (subfolders blir ikke kopiert)"

    for fn in os.listdir(src):
        shutil.copy(os.path.join(src, fn), os.path.join(dst, fn))

def lag_output_mappe(path_output, exist_ok=False):
    if os.path.exists(path_output):
        if exist_ok:
            shutil.rmtree(path_output)
    os.makedirs(path_output, exist_ok=False)

