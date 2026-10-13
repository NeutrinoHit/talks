# Theory-block figures

Generated lecture-style figures. Generators, unmodified table excerpts, the
digitizer and tests are in `assets/theory/` (see its README). Source data were
retrieved from arXiv on 13 October 2026.

## `energy-budget.svg`, `energy-budget.png`, `energy-budget.csv`

Redrawn comparison of three messengers on one $E^2\Phi$ axis, with the
Waxman–Bahcall bound. Only published values are plotted:

- Gamma rays: Fermi-LAT isotropic gamma-ray background, foreground model A,
  [Ackermann et al., ApJ 799, 86 (2015)](https://arxiv.org/abs/1410.3696), Table 3.
- Neutrinos: IceCube Combined-Fit broken power law, per flavour $\nu+\bar\nu$,
  [IceCube, PRL 136, 121002 (2026)](https://arxiv.org/abs/2507.22233v3), Table III;
  68% band and sensitive range digitized from Fig. 3.
- Cosmic rays: [Pierre Auger Collaboration, PRD 102, 062005 (2020)](https://arxiv.org/abs/2008.06486),
  Table VI; statistical errors and 90% upper limits.
- Bound: [Waxman & Bahcall, PRD 59, 023002 (1999)](https://arxiv.org/abs/hep-ph/9807282),
  Eqs. (2)–(3), $\xi_Z=0.6$–3, converted to per flavour after oscillations
  ($0.45$–$2.25\times10^{-8}$ GeV cm⁻² s⁻¹ sr⁻¹).

The CSV lists every plotted value. Nothing is fitted or recomputed. The same
comparison with older data: [Ahlers & Halzen, PPNP 102, 73 (2018), Fig. 9](https://arxiv.org/abs/1805.11112).

## `converter-cycle.svg`

Schematic of one cycle of converter acceleration,
[Derishev et al., PRD 68, 043003 (2003)](https://arxiv.org/abs/astro-ph/0301263):
energy gain of order $\Gamma^2$ per cycle. Paths and drawn neutrinos are
illustrative; no rate or spectrum is computed.
