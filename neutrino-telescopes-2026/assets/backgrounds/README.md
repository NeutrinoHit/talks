# Slide 13: background-rate graph

This is a reproducible interaction-rate calculation, not a telescope response
simulation or a forecast of selected events. No new animation or CSS is used.

From the talks checkout, using the configured NeutrinoHit Python:

```sh
MPLCONFIGDIR=/private/tmp/neutrino-backgrounds-mpl pyenv exec python neutrino-telescopes-2026/assets/backgrounds/build_rates.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/backgrounds -p 'test_*.py'
```

Dependencies: NumPy, SciPy and Matplotlib, already available in `neutrinohit`.
No nuflux installation or network connection is needed to regenerate the graph.
Parameters and colours are in `rates.toml`. Outputs: SVG (slide), PNG (review)
and CSV (numeric values), in `media/backgrounds/`.

## Definition

One Julian year; 1 km³ water at 1 g/cm³; downward hemisphere 2π; all flavours
and both signs. The ordinate is dN/dlog10(Eν), **per energy decade**, not dN/dE
or the integral above a threshold. Separate ν and anti-ν cross sections multiply
separate fluxes. The volume is treated as thin target for contained interactions.

No selections, vetoes, effective areas, Earth/overburden attenuation, detector
threshold, smearing or through-going muons are included. Cross sections are
isoscalar-nucleon DIS CC+NC; water's proton excess, tau-mass corrections and
ν–electron channels, including the Glashow resonance, are not included.

## Scientific inputs and provenance

- Conventional: `H3a_SIBYLL23C_conv`, the MCEq/Hillas–Gaisser H3a/SIBYLL 2.3c
  model shipped in [IceCube nuflux](https://github.com/icecube/nuflux) 2.0.7.
  Four files retain distinct νe, anti-νe, νμ, anti-νμ fluxes; no conventional
  atmospheric tau component. No extra knee reweighting: H3a is already included.
  [MCEq paper](https://arxiv.org/abs/1503.00544).
- Prompt: `BERSS_H3p_central/lower/upper`, also from nuflux 2.0.7, based on
  [Bhattacharya et al.](https://arxiv.org/abs/1502.01076). The identical flux is
  assigned to each of νe, anti-νe, νμ, anti-νμ as specified by nuflux; no tau.
  The shaded envelope is the supplied QCD-uncertainty prediction, **not** a
  measured confidence interval. H3p uses a proton-only extragalactic CR component;
  conventional H3a uses mixed composition. These explicit benchmarks are not
  components fitted together in one model. No experimental detection is claimed.
- Astrophysical: [IceCube MESE BPL fit](https://arxiv.org/html/2507.22234#S4.T3),
  PRD 113 (2026) 062002, Table 3, arXiv v2: per-flavour ν+anti-ν normalization
  2.28e-18 at 100 TeV, indices 1.72 and 2.839, break 10^4.524 GeV.
  Equal e:μ:τ and equal ν/anti-ν splitting. Dotted extensions outside
  6.1 TeV–7.5 PeV are not measurements. No fabricated statistical band.
  The **per-flavour** convention is explicit on the ordinate of the source's
  Figure 12 (and companion-paper Figure 3); do not treat 2.28e-18 as all-flavour.
- Cross sections: [CSMS](https://arxiv.org/html/1106.3723), Tables 1 and 2,
  HERAPDF1.5 central CC/NC values, pb converted to cm², log-log interpolation.

The seven small FITS files are unmodified copies from `nuflux-2.0.7.tar.gz`
([PyPI release](https://pypi.org/project/nuflux/2.0.7/)). Its LGPL-3.0 licence
is retained in `data/LICENSE.nuflux`. They are public scientific model tables,
not DN's private detector-event files. The Python reader uses a standard FITS
image parser and SciPy tensor-product B-splines; no C++ code is vendored.
Zero-padding preserves photospline's compact basis near the horizon, rather
than extrapolating the boundary polynomial or omitting near-horizontal flux.

## Checks

Eight automated tests: source-reference flux values, angular-quadrature
convergence, 2π normalization, cross-section signs/units/domain, continuity and
100 TeV normalization of the BPL, prompt-envelope ordering, all-flavour annual
rate normalization. During preparation, all four conventional signs/flavours
and three BERSS variants were additionally compared to upstream nuflux regression
tables at five energies (1 TeV–10 PeV) and five zenith cosines: agreement within
1e-5 relative tolerance, consistent with upstream float32 basis evaluation.

Atmospheric muons are shown separately in the slide table. Their event/sample
rates have different cuts/configurations and cannot be put on this true-ν-energy
interaction graph. Full rate sources and sample definitions are in speaker notes.
