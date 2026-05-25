TALK = protvino-2026/index.qmd
HTML = _site/protvino-2026/index.html
PDF = dist/status-and-prospects-neutrino-physics-protvino-2026.pdf

.PHONY: build pdf clean

build:
	quarto render $(TALK)

pdf: build
	mkdir -p dist
	npx --yes decktape reveal "file://$(CURDIR)/$(HTML)" "$(PDF)"

clean:
	rm -rf _site .quarto dist
