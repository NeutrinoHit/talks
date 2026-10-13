# Diffuse Galactic gamma rays above 10 TeV

Lecture-style redraw for the γ-partner tab of `galactic-neutrinos`. It shows
only published measurements: no fit, model band or neutrino conversion.

```sh
MPLCONFIGDIR=/private/tmp/neutrino-gamma-mpl pyenv exec python neutrino-telescopes-2026/assets/gamma-partner/build_gamma.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/gamma-partner -p 'test_*.py'
```

Outputs: `media/galactic/galactic-gamma-diffuse.svg` (slide) and `.png` (review).

## Inputs

- `data/lhaaso-km2a-diffuse-2305.05372v2.csv`: Tables S2 (inner Galaxy,
  15°<l<125°) and S3 (outer Galaxy, 125°<l<235°), both |b|<5°, of
  LHAASO Collaboration, *Measurement of ultra-high-energy diffuse gamma-ray
  emission of the Galactic plane from 10 TeV to 1 PeV with LHAASO-KM2A*,
  PRL 131, 151001 (2023), [arXiv:2305.05372v2](https://arxiv.org/abs/2305.05372v2).
  Transcribed from the active (uncommented) table rows of the arXiv source.
  Flux per TeV, mean energy per reconstructed-energy bin, 1σ statistical and
  systematic uncertainties. Known sources are masked; the paper estimates that
  unmasked inner-region emission would be about 61% higher.
- `data/tibet-asgamma-fig4-2104.05181v2.csv`: Tibet ASγ Collaboration,
  *First detection of sub-PeV diffuse gamma rays from the Galactic disk*,
  PRL 126, 141101 (2021), [arXiv:2104.05181v2](https://arxiv.org/abs/2104.05181v2),
  **digitized from Fig. 4** (panels a: 25°<l<100°, b: 50°<l<200°, |b|<5°).
  The flux table S2 is only in the journal Supplemental Material, so
  `digitize_tibet.py` reads the red markers and error bars from the vector
  paths of `f4.eps` in the arXiv source (not stored here). Error bars are 1σ
  statistical, as in the original; the paper quotes ≈30% systematic energy-scale
  uncertainty. Contributions within 0.5° of known TeV sources are removed.

## Conventions

Both datasets are drawn as E^2.7 dN/dE in GeV^1.7 cm^-2 s^-1 sr^-1, the Tibet
figure's convention. LHAASO's own Fig. 2 uses E^2.5 in TeV units; the
conversion is exact and tested. Thick LHAASO bars: statistical; thin bars:
statistical and systematic in quadrature. Sky regions and source masks differ,
so the two experiments' normalizations are not directly comparable; the slide
caption says so.

## Checks

Five tests: LHAASO row counts; the first inner LHAASO point reproduces the
published E^2.5 axis value and the unit conversion; Tibet horizontal error bars
recover the published 100–158–398–1000 TeV bins to 1% (an independent check of
the axis calibration); all error intervals bracket their points; all points
lie in the plotted domain. A manual overlay of the digitized markers and
error-bar ends on the rasterized original Fig. 4 agreed within the marker size.
