# Original publication figures

`figures.json` records exact arXiv versions, internal source filenames, output
paths and SHA-256 checksums. `prepare_figures.py` verifies each source before
copying unchanged PNGs or converting standalone PDF artwork to SVG with Poppler.
No data fitting, digitization or relabelling is performed.

```sh
python neutrino-telescopes-2026/assets/evidence/prepare_figures.py \
  --cache /tmp/nt-paper-sources --download
```

To verify a prepared source cache without changing the delivered media:

```sh
python neutrino-telescopes-2026/assets/evidence/prepare_figures.py \
  --cache /path/to/source-cache --output /tmp/nt-evidence-check
```

Downloading archives requires network access. Converted SVG bytes can depend
on the Poppler version; original source checksums are the stable scientific
identity. All selected outputs are self-contained local media. Paper archives
and full manuscripts do not enter the public lecture resources.

Scientific sample definitions, dates, conventions and credits are in
`media/diffuse/SOURCES.md`, `media/galactic/SOURCES.md`,
`media/response/SOURCES.md` and `media/source-results/SOURCES.md`.

`vector_paths.py` is the shared reader used by the lecture-style redraws in
`assets/diffuse-figures/` and `assets/source-figures/`: it converts vector
publication artwork to SVG with Poppler and returns drawn paths (colours,
widths, dashes, clip paths, sampled Bezier curves) and text positions.
