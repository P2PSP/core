# Rules

# .fig -> .eps
pdf/%.eps: %.fig
	fig2dev -L pstex $*.fig > tmp.eps
	fig2dev -L pstex_t -f sf -p tmp.eps $< > tmp.tex
	latex << EOF \
\\documentclass{article} \
\\usepackage{epsfig} \
\\usepackage{amsmath} \
\\usepackage{amssymb} \
\\usepackage{color} \
\\usepackage[latin1]{inputenc} \
\\usepackage[spanish,activeacute]{babel} \
\\begin{document} \
\\sffamily \
\\def\\normalfont{\\sffamily} \
\\renewcommand{\\familydefault}{cmss} \
\\pagestyle{empty} \
\\thispagestyle{empty} \
\\resizebox{1.0\\textwidth}{!}{\\input{tmp}} \
\\end{document} \
EOF
	mv article.dvi $*.dvi
	dvips $*.dvi
	ps2eps --loose < $*.ps > pdf/$*.eps
	rm $*.ps
	rm tmp.eps
	rm $*.dvi
	rm tmp.tex
	rm article.aux
	rm article.log

# .eps -> .png
html/%.png:	pdf/%.eps
	convert pdf/$*.eps html/$*.png

# Original files
FIGs := $(wildcard *.fig)

# Temporal files
TMPs += $(FIGs:%.fig=pdf/%.eps)
TMPs += $(FIGs:%.fig=html/%.png)

# Subdirectories
DIRs := $(shell find . -maxdepth 1 \! -name .svn \! -name . -type d)

all:	$(TMPs)
	make -C html all
	make -C pdf all

clean:
	rm -f $(TMPs)

publish:
	rsync -avz index.html www.ace.ual.es:public_html/proyectos/ofertados/P2PSP/index.html
	make -C html publish
	make -C pdf publish
