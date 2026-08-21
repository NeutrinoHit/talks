TALK = protvino-2026/dnaumov.qmd
HTML = _site/protvino-2026/dnaumov.html
PDF = dist/neutrino-overview-protvino-2026.pdf
DECKTAPE_ARGS ?=

.PHONY: site build pdf clean

site:
	quarto render

build: site

pdf: site
	mkdir -p dist
	npx --yes decktape $(DECKTAPE_ARGS) reveal "file://$(CURDIR)/$(HTML)" "$(PDF)"

clean:
	rm -rf _site .quarto dist
