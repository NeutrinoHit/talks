# Detector-response figures

`compact_source.py` writes the schematic `media/response/compact-source.svg`.

Lecture-style redraws of the two effective-area figures (13 October 2026):

```sh
pyenv exec python neutrino-telescopes-2026/assets/response/digitize_effective_areas.py
MPLCONFIGDIR=/private/tmp/neutrino-response-mpl pyenv exec python neutrino-telescopes-2026/assets/response/build_response_figures.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/response -p 'test_*.py'
```

| Output | Original | Method |
| --- | --- | --- |
| `icecube-hese-2013-effective-area-dark.svg/.png` | IceCube, Science 342 (2013), arXiv:1311.5238v2, Fig. 7 top panel (`eff_area.pdf`; local Poppler copy `media/response/icecube-hese-2013-effective-area.svg`) | Vector digitization of the step-histogram vertices; calibration on the dotted decade grid (x 10–10⁴ TeV, y 10⁻³–10³ m²; the y axis extends to 10^3.3 as in the original). 0.08-dex bins. Per flavour, equal ν/ν̄ flux, 4π-averaged, Earth attenuation and the Glashow peak included, 662 days of livetime in the original caption. |
| `icecube-directional-area-dark.svg/.png` | Spiering, arXiv:2609.26436v1, Fig. 6 (`Definitions/eff-area.png`; local copy `media/response/icecube-directional-area-2026.png`) | Raster only: colour tracing per pixel column, piecewise-linear calibration on the drawn tick marks, 5-column running median (≈0.01 dex), resampled every 0.05 dex in log E. Where curves overlap, the visible upper curve supplies the hidden one (red under green below log E = 3.2, red under blue above 8.86). Illustrative curves of the review, not a calibrated acceptance. |

Data: `data/hese2013-effective-area-digitized.csv` (the first ν_e bin lies below the
plotted 10⁻³ m² and is flagged), `data/spiering2026-fig6-digitized.csv`.
Tests: grid linearity, common 0.08-dex binning, Glashow bin containing 6.3 PeV,
flavour ordering at low energy, ≥97% of traced points on the original curve pixels,
the upward-curve maximum and the convergence of the two upper curves at 10⁹ GeV.
The original files are kept unchanged (their checksums are in `assets/evidence/figures.json`).
