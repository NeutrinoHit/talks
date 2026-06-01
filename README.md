# talks

Quarto RevealJS sources for conference talks.

The default style follows the dark slide style used in the lecture repositories:
black background, light text, blue links, orange progress bar and a fixed logo
from `shared/figures/dvnlogo.png`. The bottom logo and channel links are added
by `shared/reveal/neutrinohit-reveal-footer.js`; its canonical source is kept
in the main NeutrinoHit site repository.

## Talks

- `protvino-2026/dnaumov.qmd`  
  «Статус и перспективы физики нейтрино: российские проекты в глобальном
  контексте».

## Local Build

Install Quarto.

```bash
make build
```

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

1. Edit the relevant `.qmd` file in `protvino-2026/`.
2. Keep figures and animations for the Russian neutrino overview in
   `protvino-2026/media/`.
3. Run `make publish` to prepare the complete site locally.
4. Push `main` to publish the updated HTML and PDF automatically.

The HTML version can contain animations. For the PDF version, provide a static
poster frame or a separate static figure on each slide that contains an
animation: PDF files do not play embedded video or animated images reliably.

Generated HTML and PDFs are ignored by git. GitHub Actions rebuilds them from
the tracked sources.

## GitHub Build

The workflow in `.github/workflows/build.yml` renders the HTML presentations,
exports PDFs with Decktape, and publishes the complete `_site` directory to
GitHub Pages.

Published Russian neutrino overview:

```text
https://neutrinohit.github.io/talks/protvino-2026/dnaumov.html
https://neutrinohit.github.io/talks/protvino-2026/neutrino-overview-protvino-2026.pdf
```
