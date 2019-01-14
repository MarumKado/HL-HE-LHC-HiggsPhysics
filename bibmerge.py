#!/usr/bin/env python
import shutil

# Create the bibliography database.
bdb = {}

# Loop over the bibliographies.
for idx in range(0, 11):
    bib = open("section%i/bib/section.bib" % idx if idx else "bib/chapter.bib")
    for line in bib:
        if line.strip().startswith("@"):
            ob = line.count("{")
            cb = line.count("}")
            key = line.split("{")[1].split(",")[0]
            val = line
            if not key: continue
            if key in bdb: continue
            while ob != cb:
                line = next(bib)
                ob += line.count("{")
                cb += line.count("}")
                val += line
            bdb[key] = val
    bib.close()

# Write the output.
bib = open("report.bib", "w")
for key in sorted(bdb):
    bib.write(bdb[key] + "\n")
bib.close()
