TALK = protvino-2026/dnaumov.qmd
HTML = _site/protvino-2026/dnaumov.html
PDF = dist/neutrino-overview-protvino-2026.pdf
PUBLISH_DIR = _site/protvino-2026
DECKTAPE_ARGS ?=

.PHONY: build pdf publish clean

build:
	quarto render

pdf: build
	mkdir -p dist
	npx --yes decktape $(DECKTAPE_ARGS) reveal "file://$(CURDIR)/$(HTML)" "$(PDF)"

publish: build
	mkdir -p dist "$(PUBLISH_DIR)"
	npx --yes decktape $(DECKTAPE_ARGS) reveal "file://$(CURDIR)/$(HTML)" "$(PDF)"
	cp "$(PDF)" "$(PUBLISH_DIR)/"
	touch _site/.nojekyll

clean:
	rm -rf _site .quarto dist
