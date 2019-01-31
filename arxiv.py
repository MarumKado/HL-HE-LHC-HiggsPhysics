#!/usr/bin/env python3.6
import shutil, tarfile, os

###############################################################################
# Files to ignore.
def ignore(base, objs):
    igns = []

    # Base level.
    print(base)
    if base == "./":
        igns += [obj for obj in objs if not (
            obj.endswith(".tex") or obj.endswith(".bbl") or
            obj.endswith(".sty") or obj.endswith(".bst") or
            obj.endswith(".cls") or obj.endswith(".jpg") or
            obj.startswith("section"))
        ]
        
    # Section level.
    elif base[:-1] == "./section" or base[:-2] == "./section":
        igns += [obj for obj in objs if not (
            obj.endswith(".tex") or obj == "plots")
        ]

    # Plot directories.
    elif "plots" in base:
        igns += [obj for obj in objs if not (
            obj.endswith(".pdf") or obj.endswith(".png") or
            os.path.isdir(os.path.join(base, obj)))
        ]
        
    return igns

###############################################################################
if __name__ == "__main__":
    try: shutil.rmtree("arxiv")
    except: pass
    shutil.copytree("./", "arxiv", ignore = ignore)

    # Fix the hyperref issue.
    readme = open("arxiv/00README.XXX", "w")
    readme.write("nohypertex\n")
    readme.close()
    
    # Create the tarball.
    tar = tarfile.open("arxiv.tgz", "w:gz")
    tar.add("arxiv")
    tar.close()
