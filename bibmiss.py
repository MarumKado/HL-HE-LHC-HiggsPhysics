#!/usr/bin/env python3
import shutil
from inspiretools import pyinspire

# Determine the repeated entries.
blg = open("report.blg")
bib = open("tmp.bib", "w")
for line in blg:
    if line.startswith("Warning--I didn't find a database entry"):
        key = line.split()[-1].replace('"', "")
        val = pyinspire.get_text_from_inspire("texkey " + key, "bibtex")
        if val and "@" in val: bib.write(val)
bib.close()
blg.close()
