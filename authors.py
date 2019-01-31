#!/usr/bin/env python3.6
import csv, collections, json, codecs
from pylatexenc.latexencode import utf8tolatex
from urllib.request import urlopen

###############################################################################
# Fix UTF-8 encoding.
def toascii(val):
    val = utf8tolatex(val)
    for old, new in [(r"{\textquoteright}", "`"), (r"{\textbackslash}", "\\"),
                     (r"{\{}", "{"), (r"{\}}", "}"), (r"\''", r'\"'),
                     (r"{\$}", "$"), (r"{\textasciitilde}", "~")]:
        val = val.replace(old, new)
    return val

###############################################################################
# Write out an author.
def author(authors, institutes, name):
    (aid, name, insts), iids = authors[name], []
    try: aid = str(int(aid))
    except: aid = ""
    for iid, iname in insts:
        try: iid = int(iid)
        except: iid = None
        if not iid: continue
        if not iid in institutes:
            iname = institute(iid)
            institutes[iid] = toascii(iname)
        iids += [iid]
    return r"\iauthor{%s}{%s}{%s}" % (aid, toascii(name), ",".join([
        r"\ref{%s}" % iid for iid in iids]))

###############################################################################
# Write an institute.
def institute(iid):
    try:
        url = urlopen("https://labs.inspirehep.net/api/institutions/%i/" % iid)
        dct = json.load(url)["metadata"]
        url.close()
    except: dct = {}
    if "ICN" in dct and dct["ICN"][0] != "obsolete": name = dct["ICN"]
    elif "legacy_ICN" in dct: name = dct["legacy_ICN"]
    else: name = "None"; print("warning: institute ID %i does not exist" % iid)
    if not isinstance(name, str): name = " ".join(name)
    name = name.replace("(main)", "")
    return r"\iinstitute{%i}{%s}" % (iid, toascii(name))

###############################################################################
if __name__ == "__main__":
    # Load the CSV file.
    dat = urlopen("https://docs.google.com/spreadsheets/d/167WsB2xCklZalMwql"
                  "DOZqb3BKUZTKQFi5jlz2YRt6ak/export?format=csv")
    reader = csv.reader(codecs.iterdecode(dat, "utf-8"), delimiter = ",")
    header = next(reader)
    authors = {}
    
    # Load the authors.
    for row in reader:
        if row[6] == "n": continue
        row = [val.strip() for val in row]
        last, first, aid, iids, inames = row[0:5]
        if not first or not last: continue
        iids = iids.split(",")
        inames = inames.split(";")
        insts = [(iid.strip(), iname.strip()) for iid, iname in
                 zip(iids, inames)]
        key = " ".join([last, first])
        if key in authors: authors[key][2] += insts
        else: authors[key] = [aid, " ".join([first, last]), insts]
    dat.close()
    print("authors:    %i" % len(authors))
    
    # Write the preamble.
    tex = open("authors.tex", "w")
    txt = open("authors.txt", "w")
    tex.write(r"\newcounter{instituteref}" + "\n")
    tex.write(r"\newcommand{\iinstitute}[2]{\refstepcounter{instituteref}"
              r"\label{#1}$^{\ref{#1}}$\href{http://inspirehep.net/record/#1}"
              r"{#2}}" + "\n")
    tex.write(r"\newcommand{\iauthor}[3]{"
              r"\href{http://inspirehep.net/record/#1}{#2}$^{#3}$}")
    
    # Write the conveners.
    conveners = ["Cepeda M.", "Gori S.", "Ilten P.", "Kado M.", "Riva F."]
    institutes = collections.OrderedDict()
    tex.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
              r"\author{Convenors: \\ " + "\n")
    tex.write(",\n".join([author(authors, institutes, name)
                          for name in conveners]))
    txt.write(", ".join([authors[name][1] for name in conveners]))
    txt.write(", ")
    for name in conveners: del authors[name]
    
    # Write the authors.
    tex.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
              r"\\ \vspace*{4mm} Contributors: \\" + "\n")
    tex.write(",\n".join([author(authors, institutes, name) for name in
                          sorted(authors, key = lambda key: key.lower())]))
    txt.write(", ".join([authors[name][1] for name in
                         sorted(authors, key = lambda key: key.lower())]))
    
    # Write the institutes.
    tex.write("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
              r"\vspace*{1cm}} \institute{\small " + "\n")
    tex.write(";\n".join([institutes[iid] for iid in institutes]))
    tex.write(r"}" + "\n")
    tex.close()
    print("institutes: %i" % len(institutes))
