# Diffuse-flux figures

All figures are selected original publication artwork. Scientific axes, legends,
data points, confidence definitions and source dates are retained. PNG files are
unchanged; standalone source PDFs are converted to vector SVG with Poppler.
No events, likelihoods or detector responses are recalculated. Retrieved
12 October 2026. Source and output checksums: `assets/evidence/figures.json`.

## IceCube discovery

[IceCube Collaboration, Science 342 (2013), arXiv:1311.5238v2](https://arxiv.org/abs/1311.5238v2).

- `icecube-2013-energy.svg`: source `energy_distribution.pdf`, Fig. 4 left.
- `icecube-2013-zenith.svg`: source `zenith_distribution.pdf`, Fig. 4 right.
- `icecube-2013-veto.svg`: source `vetoregion_new_side.pdf`, Fig. 1 right.

The 2010–2012 sample has 28 events over 662 live days. Deposited energy is
30–1200 TeV. The reported combined evidence is 4.1 sigma for the specified
benchmark atmospheric model. These figures are historical; the gray E^-2
fit is not the current measured spectrum. Background uncertainties and prompt
assumptions matter. The veto side-view is a complete original panel.

## Baikal-GVD six seasons

[Baikal-GVD Collaboration, arXiv:2507.01893v2 (2025)](https://arxiv.org/abs/2507.01893v2).

- `gvd-2018-2024-energy.png`: source `Fig2_top.png`, Fig. 2 upper panel.
- `gvd-2018-2024-zenith.png`: source `Fig2_bottom.png`, Fig. 2 lower panel.
- `gvd-2018-2024-contours.png`: source `Fig3_col9_precise.png`, Fig. 3.
- `gvd-spectrum-2025.png`: source `Fig4_col5_600.png`, Fig. 4.

The selected sample is 18 upward-going cascades in April 2018–March 2024,
with expected atmospheric background 2.8±1.0 and 5.1-sigma significance including
systematic effects. The flux normalization is per flavour, nu+antinu at 100 TeV.
Figure 3 uses a common single-power-law parameterization, but GVD's outer contour
is 90% and the IceCube outer contours are 95%. Figure 4 retains preliminary
IceCube combined-fit points, explicitly labelled on the slide.

## IceCube finalized spectral-feature result

[IceCube Collaboration, PRL 136 (2026), arXiv:2507.22233v3](https://arxiv.org/abs/2507.22233v3).

- `icecube-spectrum-2026.svg`: source `figures/physics_context.pdf`, Fig. 3.
- `icecube-spectral-indices-2026.svg`: source
  `figures/BPL_2D_gamma_1_gamma_2.pdf`, Fig. 2.
- `icecube-combined-events-2026.svg`: source
  `figures/data_mc_globalfit_2panel_2yaxes.pdf`, Fig. 1 CF panel.

Figure 3 is per flavour with both signs. Segmented estimates assume E^-2 within
each true-neutrino-energy bin. BPL bands are 68% parameter uncertainties and
sensitive ranges; arrows represent upper limits. The index contours are 68%
and 95%. CF event proxies and track/cascade count axes are distinct.
The two analysis significances are not added. Curvature and broken power laws
test the spectral shape without identifying a unique source mechanism.

Credits: IceCube Collaboration and Baikal-GVD Collaboration. These attributed
scientific excerpts do not assert a new ownership or blanket CC licence.
Full source archives are outside the public media directory.

## Glashow resonance and tau neutrinos

- `icecube-glashow-event-2021.jpg`: IceCube gallery image
  [“IceCube sees a Glashow resonance event”](https://icecube.wisc.edu/gallery/icecube-sees-a-glashow-resonance-event/),
  item “Figure 1 from Nature paper”, <https://res.cloudinary.com/icecube/images/q_auto/v1615149084/Fig1/Fig1.jpg?_i=AA>,
  1061 × 896, unchanged. Credit: IceCube Collaboration; visualization adapted
  from Fig. 1 of [IceCube, Nature 591, 220 (2021)](https://doi.org/10.1038/s41586-021-03256-1),
  [arXiv:2110.15051](https://arxiv.org/abs/2110.15051). Reuse under the IceCube
  gallery terms (educational, noncommercial, with credit). Retrieved 13 October 2026.
  SHA-256 `2a07765a1a616c21ea3e5b3aabba94bae90eb8b0d63667315fdf933f62085c66`.
- Numbers: visible energy 6.05 ± 0.72 PeV (8 December 2016, PEPE sample,
  4.6 years); resonance at 6.3 PeV; DIS-background rejection p = 0.01 (2.3σ,
  one-sided) for the assumed flux. anti-ν_e:ν_e at Earth 1:1 (pp) and 1:3.5
  (simple pγ), as stated in the paper.
- Tau neutrinos: [IceCube, PRL 132, 151001 (2024), arXiv:2403.02516](https://arxiv.org/abs/2403.02516):
  9.7 years, seven candidates, ≈0.5 background events, no-ν_τ hypothesis
  excluded at 5.1σ (GlobalFit flux). Text only; no figure.

## Lecture-style redraws (13 October 2026)

`icecube-2013-energy-dark`, `icecube-spectrum-2026-dark` (redrawn from the vector
artwork), `gvd-2018-2024-energy-dark`, `gvd-spectrum-2025-dark` (digitized from
the published PNG figures). Same papers and figure numbers as above; quantities,
conventions and confidence levels unchanged. Generator, tables and checks:
`assets/diffuse-figures/README.md`. The original files above are kept unchanged.

Further redraws (13 October 2026): `icecube-2013-zenith-dark`, `icecube-spectral-indices-2026-dark` (vector) and
`gvd-2018-2024-zenith-dark` (digitized). Same papers and figure numbers as
listed above; methods and checks in the generator README. Originals kept unchanged.

Last redraws (13 October 2026): `gvd-2018-2024-contours-dark` (digitized) and `icecube-combined-events-2026-dark` (vector). Same papers and figure numbers as
listed above; methods and checks in the generator README. Originals kept unchanged.
