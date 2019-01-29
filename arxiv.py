#!/usr/bin/env python3.6
import shutil, os

def ig_f(base, objs):
    ignore = []

    # Base level.
    print(base)
    if base == "./":
        ignore += [obj for obj in objs if not (
            obj.endswith(".tex") or obj.endswith(".bbl") or
            obj.endswith(".sty") or obj.endswith(".bst") or
            obj.endswith(".cls") or obj.endswith(".jpg") or
            obj.startswith("section"))
        ]
        
    # Section level.
    elif base[:-1] == "./section" or base[:-2] == "./section":
        ignore += [obj for obj in objs if not (
            obj.endswith(".tex") or obj == "plots")
        ]

    # Plot directories.
    elif "plots" in base:
        ignore += [obj for obj in objs if not (
            obj.endswith(".pdf") or obj.endswith(".png") or
            os.path.isdir(os.path.join(base, obj)))
        ]
        
    return ignore

###############################################################################
if __name__ == "__main__":
    shutil.copytree("./", "arxiv", ignore=ig_f)
