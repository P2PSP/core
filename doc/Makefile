default:	all

DIRs := $(shell find . -maxdepth 1 \! -name .svn \! -name . -type d)

all:	index.html
	@for i in $(DIRs); do \
		make -C "$$i" all;\
	done

clean:
	rm -f index.html
	@for i in $(DIRs); do \
		make -C "$$i" clean;\
	done

info:
	@echo $(DIRs)

index.html:	index.md
		pandoc --number-sections -s --mathml -i index.md -o index.html
