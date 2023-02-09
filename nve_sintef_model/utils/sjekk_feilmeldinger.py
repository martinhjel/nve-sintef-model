import os
import pandas as pd

# Dette skriptet leser informasjon i se ut_enkel_samtap.txt filer i alle modellkjøringer og sjekker om det er feilmelding i noen av kjøringene.

def rapportere_feilmeldinger(scenario):
    dir = f'output\{scenario}'
    filename = 'ut_enkel_samtap.txt'

    entries = []

    for root, dirs, files in os.walk(dir):
        for f in files:
            if f == filename:
                path = f"{root}\{f}"
                file = open(path, "r")
                lines = file.readlines()
                if any("Problem abandoned" in line for line in lines):
                    entries.append([root, "Problem abandoned"]) 
                if any("infeasible" in line for line in lines):
                    entries.append([root, "infeasible"]) 

    df = pd.DataFrame(entries, columns = ['Modellsti', 'Feilmelding'])

    return df





            
