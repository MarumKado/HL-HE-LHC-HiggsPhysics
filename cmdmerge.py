#!/usr/bin/env python
import shutil

###############################################################################
if __name__ == "__main__":
    # Determine the repeated commands.
    tex = open("report.tex")
    tmp = open("tmp.tex", "w")
    cmds = []
    for line in tex:
        if line.startswith(r"\newcommand{"):
            cmd = line[11:].split("}")[0]
            if cmd in cmds:
                ob = line.count("{")
                cb = line.count("}")
                while ob != cb:
                    line = next(texd)
                    ob += line.count("{")
                    cb += line.count("}")
            else:
                cmds += [cmd]
                tmp.write(line)
        else: tmp.write(line)
    tex.close()
    tmp.close()
    shutil.move("tmp.tex", "report.tex")
