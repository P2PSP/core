all:	index.html

index.html:	*.tex ../*.tex $(HOME)/bib/*.bib *.png

# Regla para generar los .html a partir de los .tex
TEXINPUTS := ":.:..:../pdf:"
BIBINPUTS := ":.:$(HOME)/bib:"
%.html:	%.tex
	(export TEXINPUTS=${TEXINPUTS}; latex $*)
	(export BIBINPUTS=${BIBINPUTS}; bibtex $*)
	(export TEXINPUTS=${TEXINPUTS}; latex $*)
	(export TEXINPUTS=${TEXINPUTS}; latex $*)
	(export TEXINPUTS=${TEXINPUTS}; mk4ht mzlatex $* "html,mathplayer")
#	(export TEXINPUTS=${TEXINPUTS}; tth $* > $*.html)

clean:
	find . -maxdepth 1 \! -name "*.tex" \! -name Makefile \! -name .svn \! -name . -exec rm {} \;

publish:
	rsync -avz * www.ace.ual.es:public_html/proyectos/ofertados/P2PSP/html
