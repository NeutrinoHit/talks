# Baikal-GVD Galactic test above 200 TeV

Lecture-style redraw for the “Baikal-GVD above 200 TeV” tab of
`galactic-neutrinos`, from V. A. Allakhverdyan et al. (Baikal-GVD), Y. Y. Kovalev,
A. V. Plavin, D. V. Semikoz, S. V. Troitsky, ApJ 982, 73 (2025),
[arXiv:2411.05608v2](https://arxiv.org/abs/2411.05608v2).

```sh
MPLCONFIGDIR=/private/tmp/neutrino-gvd-mpl pyenv exec python neutrino-telescopes-2026/assets/gvd-galactic/build_gvd_galactic.py /path/to/2411.05608v2/GVD-Galactic.tex
NT_GVD_GALACTIC_TEX=/path/to/GVD-Galactic.tex pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/gvd-galactic -p 'test_*.py'
```

The input is Table 1 of the paper, read directly from its arXiv source file.
By agreement, event coordinates are shown only graphically: no coordinate
table is stored here or in `media/`. Outputs in `media/galactic/`:

- `gvd-galactic-sky.svg/.png`: the 8 cascades with reconstructed energy
  ≥ 200 TeV, drawn as their published 90% containment circles (r90), in
  Galactic coordinates (the coordinates of Table 1), Mollweide projection,
  longitude increasing to the left, |b| < 10° band (the band used for the
  paper's excess estimate). The paper's Fig. 5 shows the same GVD events in
  equatorial coordinates together with IceCube events; IceCube events are not
  redrawn here.
- `gvd-galactic-test.svg/.png`: the paper's test (its Fig. 1). The test
  statistic is the median |b| of the sample. The null distribution keeps the
  declinations and draws right ascensions uniformly (10⁵ skies, fixed seed),
  the data-driven method described in the paper; the observed value is the
  vertical line.

## Reproduction

This calculation gives observed median |b| = 10.35° from the rounded table
(paper: 10.4°), mean null median 31.5° (paper: 31.4°) and p = 0.0134
(paper: 1.4·10⁻², 2.5σ, no trials). Slide and notes quote the paper's values.

## Checks

Geometry tests always run: ICRS→Galactic rotation at the Galactic centre and
north Galactic pole, round trip, exact small-circle radius. With
`NT_GVD_GALACTIC_TEX` set, a data test checks 8 events ≥ 200 TeV and reproduces
the published median, null mean and p-value within stated tolerances. The
converted direction of the April 2021 cascade was also checked by hand against
the equatorial direction published in arXiv:2308.13686 (agreement to 0.05°).
