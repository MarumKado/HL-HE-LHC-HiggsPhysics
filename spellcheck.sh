#!/usr/bin/env bash
ASPELL="aspell --lang=en_GB-ise --mode=tex"

# Spell check the main report.
HEAD=`cat -n report.tex | grep Abstract | awk '{print $1}'`
tail -n +$HEAD report.tex | $ASPELL list > list.dct

# Spell check the remaining section files.
TEXS=`find . -name "*.tex"`
for TEX in $TEXS; do
    if [[ "$TEX" != "./section"* ]]; then continue; fi
    echo $TEX
    cat $TEX | $ASPELL list >> list.dct
done

# Create the unique dictionary.
echo "personal_ws-1.1 en 0" > spellcheck.dct
cat list.dct | sort | uniq >> spellcheck.dct
rm list.dct
