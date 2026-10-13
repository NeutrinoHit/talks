# Published Baikal-GVD point-source limits

`build_limits.py` redraws only the 92 source-specific E^-2 upper limits in
Table 1 of [arXiv:2603.21261v2](https://arxiv.org/abs/2603.21261v2).
The unmodified table source is retained in `data/baikal-source-list-2603.21261v2.tex`.
The source archive was retrieved 12 October 2026. Source names, declinations
and flux values are preserved; no fit or statistical limit is recomputed.

```sh
MPLCONFIGDIR=/private/tmp/neutrino-global-sky-mpl pyenv exec python neutrino-telescopes-2026/assets/source-results/build_limits.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/source-results -p 'test_*.py'
```

Outputs: SVG, PNG and numeric CSV in `media/source-results/`.

## Units and scope

For gamma=2, Table 1 reports the normalization of
(E/GeV)^2 Phi(E) in units of 1e-8 cm^-2 s^-1 GeV^-1. Multiplication by
(1 GeV)^2 gives E^2 Phi in GeV cm^-2 s^-1, with the same numerical values
times 1e-8. Phi is the nu_mu+anti-nu_mu differential source flux before Earth
attenuation. These are 90%-confidence upper limits; detector-efficiency
systematic uncertainty is not included. No all-flavour multiplication is used.

All 92 directions are plotted, including directions of sources with no
candidate events. The highlighted names connect the catalogue to previous
result slides and do not identify new detections. No sensitivity curve is
invented from the source limits. The original three-spectrum figure and its
median-sensitivity curves are retained in the separate Spectral assumptions tab.

Four tests check source count, unique names, selected values and unit conversion,
and that every published point lies in the plotted domain.
