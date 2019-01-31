#!/usr/bin/env python3.6
import os, shutil, bibtexparser, titlecase, authors
from fuzzywuzzy import fuzz

###############################################################################
# Clean a BibTex entry.
def clean(bib):
    # Fix the encoding.
    for key in ["author", "title"]:
        if key in bib: bib[key] = authors.toascii(bib[key].strip())

    # Create a list of report numbers for the entry.
    nums = []
    for key in ["reportnumber", "number"]:
        if not key in bib: continue
        if len(bib[key]) < 3: continue
        for num in bib[key].upper().strip().replace(
                ". ", " ").replace(",", " ").split(" "):
            if len(num) > 3: nums += [num]
        del bib[key]
    nums = ", ".join(sorted(list(set(nums))))

    # Include report numbers for the LHC collaborations.
    for collab in ["ALICE", "ATLAS", "CMS", "LHCb"]:
        if collab.upper() in nums:
            bib["collaboration"] = collab + " Collaboration"
            if "author" in bib: del bib["author"]
            bib["number"] = nums

    # Include report numbers if missing info.
    keep = True
    for key in ["journal", "volume", "doi", "eprint"]:
        if key in bib: keep = False
    if keep: bib["number"] = nums
                
    # Fix collaborations.
    author = bib["author"] if "author" in bib else None
    collab = bib["collaboration"] if "collaboration" in bib else None
    if author and "ollaboration" in author:
        del bib["author"]
        if not collab: bib["collaboration"] = author
    collab = bib["collaboration"] if "collaboration" in bib else None
    if collab and collab.lower().startswith("collaboration, "):
        bib["collaboration"] = collab[15:] + " Collaboration"

    # Check if a twiki.
    for key in ["url", "link", "note"]:
        if key in bib and "twiki" in bib[key].lower():
            bib["title"] = bib[key]

    # Check if a thesis.
    for key in ["url", "link", "note"]:
        if key in bib and "thesis" in bib[key].lower():
            bib["title"] = bib[key]
    
    # Remove the unused entries.
    for key in ["address", "institution", "month", "type", "note"]:
        if key in bib: del bib[key]

    # Move conference to journal.
    if "conference" in bib and not "journal" in bib:
        bib["journal"] = bib["conference"]
        
    # Move all url entries to link.
    if "url" in bib:
        if not "link" in bib: bib["link"] = bib["url"]
        del bib["url"]
    return bib

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
# Compare two entries.
def compare(bib0, bib1):
    # Check exact not matches.
    for key in ["year", "doi", "eprint"]:
        if key in bib0 and key in bib1 and len(bib0[key]) > 3:
            if bib0[key] != bib1[key]: return 0.
            
    # Check exact matches.
    for key in ["doi", "eprint", "link"]:
        if key in bib0 and key in bib1 and len(bib0[key]) > 5:
            if bib0[key] == bib1[key]: return 100.

    # Check report numbers.
    num0 = bib0["number"].split(", ") if "number" in bib0 else []
    num1 = bib1["number"].split(", ") if "number" in bib1 else []
    for num in num0:
        if num and num in num1: return 100.
    if len(num0) and len(num1): return 0.
            
    # Check if both are from INSPIRE.
    if inspire(bib0["ID"]) and inspire(bib1["ID"]): return 0.

    # Check the authors and collaborations.
    skip = []
    for key in ["author", "collaboration"]: 
        if key in bib0 and key in bib1:
            if "ATLAS" in bib0[key] and "ATLAS" in bib1[key]: skip += [key]
            elif "CMS" in bib1[key] and "CMS" in bib1[key]: skip += [key]

    # Check the titles.
    for key in ["title"]: 
        if key in bib0 and key in bib1 and bib0[key] == bib1[key]: return 100.
            
    # Check the remaining entries.
    scores = []
    for key in ["title", "author"]:
        if not key in skip and key in bib0 and key in bib1:
            scores += [fuzz.ratio(bib0[key], bib1[key])]
    return 0. if not len(scores) else sum(scores)/float(len(scores))

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
if __name__ == "__main__":
    # Create the bibliography database with unique keys.
    bdb, bad = {}, {}
    for idx in range(0, 11):
        tex = open("section%i/bib/section.bib" % idx if idx
                   else "bib/chapter.bib", encoding = "utf-8")
        for bib in bibtexparser.load(tex).entries:
            key = bib["ID"]
            if not key: continue
            elif key in bdb and len(bib) < len(bdb[key]): continue
            else: bdb[key] = clean(bib)
        tex.close()
            
    # Create the replace database for new -> old.
    rpl, itr = {key: [] for key in bdb}, list(bdb.items())
    while len(itr):
        # Check for fuzzy matching.
        key0, bib0 = itr.pop()
        idxs = []
        for idx1, (key1, bib1) in enumerate(itr):
            score = compare(bib0, bib1)
            
            # Merge if matched.
            if score == 100:
                new, old = choose(bib0, bib1)
                rpl[new] += rpl[old] + [old]
                bad[old] = bdb[old]; del rpl[old]; del bdb[old]
                if old == key0: break
                else: idxs += [idx1]
    
        # Remove matched entries.
        for offset, old in enumerate(idxs): del itr[old - offset]
        
    # Print the matches.
    for key, vals in sorted(rpl.items()):
        if len(vals): print("\033[91m" + key + "\033[0m")
        for val in vals: print("    " + val)
            
    # Write out the BibTex.
    tex = open("report.bib", "w")
    btd = bibtexparser.bibdatabase.BibDatabase()
    btw = bibtexparser.bwriter.BibTexWriter()
    for key in sorted(bdb):
        btd.entries = [bdb[key]]
        tex.write(btw.write(btd))
    tex.close()
    
    # Write out the aliases.
    tex = open("bibaliases.tex", "w")
    for alias, keys in rpl.items():
        for key in keys:
            tex.write(r"\bibalias{%s}{%s}" % (key, alias) + "\n")
            tex.write(r"\bibalias{ %s}{%s}" % (key, alias) + "\n")
    tex.close()
