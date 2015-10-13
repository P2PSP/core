default:	all

DIRs := $(shell find . -maxdepth 1 \! -name .svn \! -name . -type d)

all:	index.html
	@for i in $(DIRs); do \
		make -C "$$i" all;\
	done
	rm -f index.html

clean:
	@for i in $(DIRs); do \
		make -C "$$i" clean;\
	done

info:
	@echo $(DIRs)

index.html:	index.md
		pandoc --number-sections -c ../templates/utf-8.css -c ../templates/table.css -i index.md -o index.html
