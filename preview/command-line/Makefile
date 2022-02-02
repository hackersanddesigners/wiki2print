STYLESHEET:=volumetric-regimes.css

.PHONY: css

all: run

install:
	python3 -m venv venv
	./venv/bin/pip3 install etherpump
	./venv/bin/etherpump init

run:
	python3 -m http.server

update: wiki css

wiki:
	# ---
	# update the materials from the wiki, save it as Unfolded.html
	python3 update.py
	@echo "Pulling updates from the wiki: Unfolded (wiki) --> Unfolded.html (file)"

css:
	# ---
	# sync the CSS on the pad with the local print.css file
	./venv/bin/etherpump gettext $(STYLESHEET) > ./css/print.css
	@echo "Saving CSS: $(STYLESHEET) (pad) --> print.css (file)"

multi:
	# ---
	# multistamp Multi Remix on top of the pdf
	@pdfunite multi-remix/multi-remix.pdf multi-remix/multi-remix-empty.pdf multi-remix/multi-remix.pdf multi-remix/multi-remix-empty.pdf multi-remix/multi-remix-stamp.pdf
	@pdftk Unfolded.pdf multistamp multi-remix/multi-remix-stamp.pdf output Unfolded-with-Multi.pdf

upload:
	scp -r Unfolded.html css js fonts varia:public_html/volumetric-regimes/

uploadimages:
	scp -r images varia:public_html/volumetric-regimes/
