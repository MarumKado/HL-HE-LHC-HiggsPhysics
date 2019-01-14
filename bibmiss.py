#!/usr/bin/env python3
import shutil
from inspiretools import pyinspire

# Determine the repeated entries.
blg = open("report.blg")
bib = open("miss.bib", "w")
for line in blg:
    if line.startswith("Warning--I didn't find a database entry"):
        key = line.split()[-1].replace('"', "")
        if not key: continue
        if not ":" in key: continue
        val = pyinspire.get_text_from_inspire("texkey " + key, "bibtex")
        if val and val.count("@") == 1: bib.write(val)
bib.close()
blg.close()
