DIRs := $(shell find . -maxdepth 1 \! -name .svn \! -name . -type d)

default:	README.md

all:	all
	@for i in $(DIRs); do \
		make -C "$$i" all;\
	done

clean:
	rm -f README.md

mrproper:	clean
	@for i in $(DIRs); do \
		make -C "$$i" clean;\
	done

info:
	@echo $(DIRs)

README.md:	README.tex
		pandoc --number-sections -s --mathml -i README.tex -t markdown -o README.md
