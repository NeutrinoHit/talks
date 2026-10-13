# Diffuse neutrino and gamma-ray comparison

## `diffuse_gamma_neutrino_2026.png`

- Original file: `exsitu_CFBPLLogPSPL.png`, Figure 2 in **The Delta Resonance
  in the Neutrino Sky**, Arifa Khatee Zathul, Ke Fang, Francis Halzen and
  Dan Hooper, [arXiv:2606.00249v2](https://arxiv.org/abs/2606.00249v2),
  revised 13 August 2026.
- Retrieved 12 October 2026 from the [arXiv source archive](https://arxiv.org/src/2606.00249v2).
- Licence: CC BY 4.0, as identified on the arXiv HTML and abstract record.
  Attribution is visible on the slide. No scientific or graphical changes;
  only the local filename is different. The imported source image is not a
  new calculation.
- Image dimensions: 8706 × 6052 pixels.
- SHA-256: `e514b944bd6976c91b6532b7bef78b30043e02f147d9b47eb53abcb933787473`.
- Grey points: IceCube combined-fit diffuse neutrino spectrum. Purple points:
  Fermi-LAT IGRB. Dashed lines: single power law, broken power law and log
  parabola. Solid lines: corresponding electromagnetic cascades for transparent
  extragalactic sources. Neutrinos include all flavours and both signs.
- The source uses a p-gamma pion-yield benchmark, gamma-transparent sources,
  star-formation-rate source evolution and cascades through EBL/CMB radiation.
  Photon envelopes combine spectral-fit uncertainties and EBL-model variation.
  They must not be labelled as gamma-ray measurements or a confidence interval
  on an independently fitted source population.
- Interpretation: extending a soft single power law to 1 TeV exceeds part
  of the IGRB; the broken spectrum reduces the predicted photon contribution.
  Spectral suppression and internal absorption are possible ways to ease the
  tension. This figure does not establish that all neutrino sources are opaque,
  nor prove the proposed Delta-resonance explanation.

To refresh, retrieve the exact v2 source archive, extract only
`exsitu_CFBPLLogPSPL.png`, verify its checksum, and copy it to the local filename.
Preserve source version, all curves, bands, points, labels and legend.

## `diffuse-gamma-neutrino-2026-dark.svg/.png` (lecture-style redraw, 13 October 2026)

Digitized from the same Figure 2 (`exsitu_CFBPLLogPSPL.png`, CC BY 4.0;
attribution on the slide). Bands decoded from the alpha-composited fills
(model: line colours, alpha 0.3 for cascades and 0.4 for neutrino fits, drawn
in the order SPL, BPL, LP; all observed overlap colours reproduced within two
units). Lines, Fermi IGRB points and bins digitized; IceCube points are the
published Combined Fit segmented flux (PRL 136, 2026, Fig. 3) times three,
identical to the grey points of the original within ~1–4%. Band edges hidden
by the original legend are not recovered; the redraw's y axis therefore starts at
7·10⁻¹⁰ GeV cm⁻² s⁻¹ sr⁻¹ and its legend sits above the plot (colour = model,
line style = neutrino fit or cascade photons). As drawn in the source, the dashed single power law is ~15% above
3 × the IceCube CF SPL normalization (1.80·10⁻¹⁸ per flavour at 100 TeV); its
index (2.52) matches. Generator, tables and checks: `assets/diffuse-figures/README.md`.
The original PNG is kept unchanged.
