#!/usr/bin/env python
import os, fnmatch, shutil, bibtexparser
from fuzzywuzzy import fuzz

###############################################################################
# Compare two entries.
def compare(bib0, bib1):

    # Check if both are from INSPIRE.
    if inspire(bib0["ID"]) and inspire(bib1["ID"]): return 0.
    
    # Check exact not matches.
    for key in ["year", "doi", "eprint", "reportnumber"]:
        if key in bib0 and key in bib1 and len(bib0[key]) > 3:
            if bib0[key] != bib1[key]: return 0.

    # Check exact matches.
    for key in ["doi", "eprint", "reportnumber"]:
        if key in bib0 and key in bib1 and len(bib0[key]) > 5:
            if bib0[key] == bib1[key]: return 100.
            
    # Check the authors and collaborations.
    skip = []
    for key in ["author", "collaboration"]: 
        if key in bib0 and key in bib1:
            if "ATLAS" in bib0[key] and "ATLAS" in bib1[key]: skip += [key]
            elif "CMS" in bib1[key] and "CMS" in bib1[key]: skip += [key]

    # Check the remaining entries.
    scores = []
    for key in ["title", "author"]:
        if not key in skip and key in bib0 and key in bib1:
            scores += [fuzz.ratio(bib0[key], bib1[key])]
    return 0. if not len(scores) else sum(scores)/float(len(scores))

###############################################################################
# Check if an INSPIRE ID.
def inspire(key):
    # Split by colon.
    iid = key.split(":")
    if len(iid) != 2: return False

    # First part is name.
    if any(char.isdigit() for char in iid[0]): return False

    # First four characters of second part is year.
    if len(iid[1]) < 5: return False
    try: int(iid[1][0:4])
    except: return False

    # Final characters of second part are not numbers.
    if not iid[1][4:].isalpha(): return False
    return True

###############################################################################
# Choose which entry to keep.
def choose(bib0, bib1):
    key0, key1 = bib0["ID"], bib1["ID"]
    
    # Keep the INPSIRE entry.
    if inspire(key0): return key0, key1
    if inspire(key1): return key1, key0

    # Keep the entry with more filled fields.
    if len(bib0) >= len(bib1): return key0, key1
    else: return key1, key0

###############################################################################
# Create the bibliography database with unique keys.
bdb = {}
for idx in range(0, 11):
    tex = open("section%i/bib/section.bib" % idx if idx else "bib/chapter.bib")
    for bib in bibtexparser.load(tex).entries:
        key = bib["ID"]
        if not key: continue
        elif key in bdb and len(bib) < len(bdb[key]): continue
        else: bdb[key] = bib
    tex.close()
        
# Create the replace database for new -> old.
rpl, itr = {key: [] for key in bdb}, bdb.items()
while len(itr):
    # Check for fuzzy matching, unless an INSPIRE ID.
    key0, bib0 = itr.pop()
    idxM, keyM, bibM, scoreM = 0, 0, None, 0
    for idx1, (key1, bib1) in enumerate(itr):
        score = compare(bib0, bib1)
        if score > scoreM: idxM, keyM, bibM, scoreM = idx1, key1, bib1, score
        
    # Remove if matched.
    if scoreM > 80:
        new, old = choose(bib0, bibM)
        rpl[new] += rpl[old] + [old]
        del rpl[old]; del bdb[old]
        if old == keyM: del itr[idxM]

# Print the matches.
for key, vals in rpl.items():
    if len(vals): print "\033[91m" + key + "\033[0m"
    for val in vals: print "    " + val
        
# Write out the BibTex.
tex = open("report.bib", "w")
btd = bibtexparser.bibdatabase.BibDatabase()
btw = bibtexparser.bwriter.BibTexWriter()
for key in sorted(bdb):
    # Encode fields as ASCII.
    bib = bdb[key]
    if key in rpl and len(rpl[key]): bib["IDS"] = ", ".join(rpl[key])
    for key, val in bib.items(): bib[key] = val.encode("ascii", "ignore")

    # Fix collaborations.
    author = bib["author"] if "author" in bib else None
    collab = bib["collaboration"] if "collaboraiton" in bib else None
    if author and "ollaboration" in author:
        del bib["author"]
        if not collab: bib["collaboration"] = author

    # Write the entry.
    btd.entries = [bib]
    tex.write(btw.write(btd))
tex.close()
