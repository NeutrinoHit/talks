# talks

Quarto RevealJS sources for conference talks.

## Talks

- `protvino-2026/`  
  Status and Prospects of Neutrino Physics: Russian Projects in the Global Context.

## Local Build

Install Quarto.

```bash
make build
```

The HTML presentation is built at:

```text
_site/protvino-2026/index.html
```

To build a PDF without LaTeX, use Decktape through `npx`:

```bash
make pdf
```

The PDF is written to:

```text
dist/status-and-prospects-neutrino-physics-protvino-2026.pdf
```

This route uses a browser renderer, not LaTeX. You can also open the HTML
presentation in a browser and print/export it as PDF from there.

## Editing Workflow

1. Edit `protvino-2026/index.qmd`.
2. Keep figures near the talk source, for example in `protvino-2026/assets/`.
3. Run `make build`.
4. Use `_site/protvino-2026/index.html` for a browser talk, or run `make pdf`
   for a PDF copy.

Generated HTML and PDFs are ignored by git. Remove the relevant rules from
`.gitignore` if final artifacts should be committed.

## GitHub Build

The workflow in `.github/workflows/build.yml` renders the HTML presentation,
exports a PDF with Decktape, and uploads both as a GitHub Actions artifact.
