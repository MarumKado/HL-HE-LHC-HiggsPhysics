#!/usr/bin/env python3.5
import shutil, glob
from inspiretools import pyinspire

###############################################################################
if __name__ == "__main__":
    # Determine the repeated entries.
    blg = open("report.blg")
    bib = open("miss.bib", "w")
    misses = {}
    for line in blg:
        if line.startswith("Warning--I didn't find a database entry"):
            key = line.split()[-1].replace('"', "")
            if not key: continue
            else: misses[key] = ""
            if not ":" in key: continue
            val = pyinspire.get_text_from_inspire("texkey " + key, "bibtex")
            if val and val.count("@") == 1: bib.write(val)
    bib.close()
    blg.close()
    
    # Determine the files with the missing keys.
    for name in glob.iglob('**/*.tex', recursive=True):
        tex = open(name)
        txt = tex.read()
        for miss in misses:
            if miss in txt: misses[miss] += " " + name
        tex.close()
    red, end = "\033[91m", "\033[0m"
    for miss in sorted(misses): print(red + miss + end + ":" + misses[miss])

