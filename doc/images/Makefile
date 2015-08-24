
IMAGES_TXT=$(wildcard *.txt)
IMAGES_SVG=$(IMAGES_TXT:.txt=.svg)
IMAGES_PNG=$(IMAGES_SVG:.svg=.png)

all: images.create

images.create: $(IMAGES_SVG) $(IMAGES_PNG)

%.svg: %.txt
	@sed -e 's/\([^ ]\)$$/\1 /g' -e :a -e '/^\n*$$/{$$d;N;};/\n$$/ba' $< > $<.improved
	echo >> $<.improved
	@mv $<.improved $<
	# This uses https://bitbucket.org/dhobsd/asciitosvg
	a2s -i$< -o$@

%.png: %.svg
	rsvg-convert $< -b white -o $@

images.clean:
	rm -f $(IMAGES_SVG) $(IMAGES_PNG)

