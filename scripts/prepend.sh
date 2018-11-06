#!/bin/sh
# --------------------------------------------------------------------------------------------
# -- Prepend the contents of file file_header.txt to the file indicated by the first parameter
# --------------------------------------------------------------------------------------------
mv $1 $1.bak
cat file_header.txt $1.bak > $1
