# Rules.


# .svg -> .pdf
../PDFs/%.pdf:	%.svg
	 rsvg-convert -f pdf -o ../PDFs/$*.pdf $*.svg

# .svg -> .eps
../EPSs/%.eps:	%.svg
	rsvg-convert -f ps -o $*.ps $*.svg
	ps2eps --loose < $*.ps > ../EPSs/$*.eps
	rm $*.ps

# Original files
SVGs := $(wildcard *.svg)

# Temporal files
TMPs += $(SVGs:%.svg=../PDFs/%.pdf)
TMPs += $(SVGs:%.svg=../EPSs/%.eps)

all:	$(TMPs)

info:
	@echo $(TMPs)

clean:
	rm -f $(TMPs)
