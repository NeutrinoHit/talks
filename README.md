# talks

Quarto RevealJS sources for conference talks.

The default style follows the dark slide style used in the lecture repositories:
black background, light text, blue links, orange progress bar and a fixed logo
from `shared/figures/dvnlogo.png`. The bottom logo and channel links are added
by `shared/reveal/neutrinohit-reveal-footer.js`; its canonical source is kept
in the main NeutrinoHit site repository.
`shared/reveal/neutrinohit-video-seek.js` (included by the two neutrino-telescope lectures) makes slide
videos seekable on servers without HTTP range requests, such as the local `quarto preview`: a video that
cannot seek is read once into memory when the pointer reaches it; `#t=` start fragments are kept.

## Talks

- `neutrino-telescopes-2026/lecture.qmd`
  **Neutrino Telescopes: Principles, Results, and Prospects** (English, 60 minutes).
  A 33-slide deck, including the title, with seven independently
  editable blocks. Opening and history have illustrated tabsets; detection
  starts with the propagation estimate and NTSim films. Results use publication figures, followed by photon constraints and source evidence. See [the lecture guide](neutrino-telescopes-2026/README.md).

- `protvino-2026/dnaumov.qmd`  
  «Статус и перспективы физики нейтрино: российские проекты в глобальном
  контексте».

## Local Build

`modular-symmetry/lecture.qmd` is temporarily excluded in `_quarto.yml`.
Its source and assets remain intact. To re-enable it, remove the `!` from
its render entry and restore the two modular-symmetry resource patterns;
first supply its required Reveal footer context.

Install Quarto.

```bash
make site
```

A push to `main` publishes the site automatically. `workflow_dispatch`
allows the publication to be run manually again.

The HTML presentation is built at:

```text
_site/protvino-2026/dnaumov.html
```

To build a PDF without LaTeX, use Decktape through `npx`:

```bash
make pdf
```

The PDF is written to:

```text
dist/neutrino-overview-protvino-2026.pdf
```

This route uses a browser renderer, not LaTeX. You can also open the HTML
presentation in a browser and print/export it as PDF from there.

## Editing Workflow

1. Edit the relevant `.qmd` file in its talk folder.
2. Keep figures and animations for each talk in that talk's `media/` folder.
3. Run `make site` to rebuild the HTML site.

The HTML version can contain animations. For the PDF version, provide a static
poster frame or a separate static figure on each slide that contains an
animation: PDF files do not play embedded video or animated images reliably.

Generated HTML and PDFs are ignored by git. PDF export is an optional,
separate `make pdf` command and is not part of the website build.

Published Russian neutrino overview:

```text
https://neutrinohit.github.io/talks/protvino-2026/dnaumov.html
https://neutrinohit.github.io/talks/protvino-2026/neutrino-overview-protvino-2026.pdf
```
