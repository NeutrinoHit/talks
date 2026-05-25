# talks

Quarto sources for conference talks.

## Talks

- `protvino-2026/status-and-prospects-neutrino-physics/`  
  Status and Prospects of Neutrino Physics: Russian Projects in the Global Context.

## Local Build

Install Quarto and a LaTeX distribution with `xelatex`.

```bash
make build
```

The final PDF is copied to:

```text
dist/status-and-prospects-neutrino-physics-protvino-2026.pdf
```

To render only the Protvino 2026 talk:

```bash
quarto render protvino-2026/status-and-prospects-neutrino-physics/status-and-prospects-neutrino-physics.qmd --to beamer
```

## Editing Workflow

1. Edit the `.qmd` file for the talk.
2. Keep figures near the talk source, for example in an `assets/` subfolder.
3. Run `make build`.
4. Use the PDF from `dist/` for the actual presentation.

Generated PDFs and LaTeX intermediates are ignored by git. Remove the `*.pdf`
rule from `.gitignore` if final PDFs should be committed.

## GitHub Build

The workflow in `.github/workflows/build.yml` renders the PDF on push and uploads
it as a GitHub Actions artifact.
