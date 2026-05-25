TALK = protvino-2026/status-and-prospects-neutrino-physics/status-and-prospects-neutrino-physics.qmd
PDF = protvino-2026/status-and-prospects-neutrino-physics/status-and-prospects-neutrino-physics.pdf
DIST = dist/status-and-prospects-neutrino-physics-protvino-2026.pdf

.PHONY: build clean

build:
	mkdir -p dist
	quarto render $(TALK) --to beamer
	cp $(PDF) $(DIST)

clean:
	rm -rf dist
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.aux
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.log
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.nav
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.out
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.snm
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.toc
	rm -f protvino-2026/status-and-prospects-neutrino-physics/*.vrb
