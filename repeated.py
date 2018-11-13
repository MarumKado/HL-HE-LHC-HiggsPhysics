#!/usr/bin/env python
import shutil

# Determine the repeated entries.
blg = open("report.blg")
bibs = {}
for line in blg:
    if line.startswith("Repeated entry"):
        bib = line.split()[-1]
        line = next(blg)
        key = line.split()[-1].split("{")[-1]
        if not bib in bibs: bibs[bib] = []
        bibs[bib] += [key]
blg.close()

# Clean the bibliography files.
for name, keys in bibs.items():
    bib  = open(name)
    tmp  = open("tmp", "w")
    reps = []
    for line in bib:
        skip = False
        for rep in reps:
            if rep in line: skip = True; break
        if skip:
            ob = line.count("{")
            cb = line.count("}")
            while ob != cb:
                line = next(bib)
                ob += line.count("{")
                cb += line.count("}")
        else:
            tmp.write(line)
            for key in keys:
                if key in line:
                    reps += [key]
    tmp.close()
    bib.close()
    shutil.move("tmp", name)
