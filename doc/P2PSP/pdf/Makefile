# Regla para crear un .pdf a partir de un .dvi
%.pdf:	%.dvi
	dvipdf $*.dvi $*.pdf

all:	pdf.pdf

pdf.dvi:	*.tex ../*.tex $(HOME)/bib/*.bib *.eps

pdf.pdf:	pdf.dvi

# Regla para generar los .pdf a partir de los .tex
TEXINPUTS := ":.:..:"
BIBINPUTS := ":.:$(HOME)/bib:"
%.dvi:	%.tex
	(export TEXINPUTS=${TEXINPUTS}; latex $*)
	(export BIBINPUTS=${BIBINPUTS}; bibtex $*)
	(export TEXINPUTS=${TEXINPUTS}; latex $*)
	@while ( grep "Rerun to get cross-references" 		\
                        $*.log > /dev/null ); do		\
                echo '** Re-running LaTeX **';			\
                (export TEXINPUTS=${TEXINPUTS}; latex --interaction errorstopmode $*);	\
        done

clean:
	find . -maxdepth 1 \! -name "*.tex" \! -name Makefile \! -name "*.eps" \! -name .svn \! -name . -exec rm {} \;

publish:
	rsync -avz pdf.pdf www.ace.ual.es:public_html/proyectos/ofertados/P2PSP/P2PSP.pdf