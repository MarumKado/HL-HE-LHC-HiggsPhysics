# **************************************************************************
# * FCC Conceptual Design Report                                           *
# * Copyright (C) 2017, CERN.                                              *
# * This work is licensed under a Creative Commons                         *
# * Attribution-NonCommercial-NoDerivatives 4.0 International License.     *
# * File Authors: J. Gutleber                                              *
# *                                                                        *
# * For the licensing terms see LICENSE                                    *
# **************************************************************************
#
# This is the default target when make is called without parameters
# it has to be the very first target in the rules
#
default: build

# Declaration of variables
STDTEXFLAGS = -shell-escape -file-line-error
CONTINUEFLAGS = -interaction=nonstopmode
QUIETFLAGS = #--interaction=batchmode
DRAFTFLAGS = --draft

TEX = pdflatex $(STDTEXFLAGS) $(QUIETFLAGS)
BIB = bibtex
GLOSS = makeglossaries
VIEW = open

ifdef TARGET
#$(info ********** TARGET defined '$(TARGET)' **********)
PDF = $(TARGET).pdf
endif

AUXFILE = $(PDF:.pdf=.aux)
BIBFILE = $(PDF:.pdf=.bbl)
SOURCE = $(PDF:.pdf=.tex)
TMP_FILES = *.glg *.gls *.bbl *.blg *.aux *.dvi *.glo *.glsdefs *.log *.tdo *.toc *.xdy
DEL_FILES := $(strip $(foreach tmp_file, $(TMP_FILES), $(wildcard $(tmp_file)) ))

# Main target
$(PDF): $(SOURCE) $(BIBFILE) $(GLOSSFILE)
	$(info ********** MAKE PDF **********)
	$(info PDF='$(PDF)')
	$(info SOURCE='$(SOURCE)')
	$(TEX) $(SOURCE)
	$(TEX) $(SOURCE)

$(BIBFILE): | $(AUXFILE)
	$(info ********** MAKE BIBLIOGRAPHY '$(BIBFILE)' **********)
	$(BIB) $(AUXFILE)

$(AUXFILE): $(SOURCE)
	$(info ********** MAKE FIRST PASS **********)
	$(TEX) $(DRAFTFLAGS) $(SOURCE)

build: $(PDF)

view: $(PDF)
	@open $(PDF)

clean: _cleanall

_cleanall:
ifneq ("$(wildcard *.pdf)","")
		-rm *.pdf 2>/dev/null
else
		$(info No output file to clean)
endif
ifneq ($(DEL_FILES),)
	-rm $(DEL_FILES)
else
	$(info No temporary files to clean)
endif


STYFILES = cernall.sty cernchemsym.sty cernrep.cls cernunits.sty cernyrep.cls heppennames2.sty report.bst rep_common.sty 

newsection:
	mkdir $(newfolder)
	mkdir $(newfolder)/img
	mkdir $(newfolder)/bib
	cp templates/sectiontemplate.tex $(newfolder)/section.tex
	cp templates/sectiontemplate.bib $(newfolder)/bib/section.bib
	cp $(STYFILES) $(newfolder)
