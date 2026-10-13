# Theory-block figures

Two generators for the source-theory slides. Outputs go to `media/theory/`.

```sh
MPLCONFIGDIR=/private/tmp/neutrino-theory-mpl pyenv exec python neutrino-telescopes-2026/assets/theory/build_energy_budget.py
pyenv exec python neutrino-telescopes-2026/assets/theory/converter_cycle.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/theory -p 'test_*.py'
```

## `energy-budget.svg` — three messengers on one axis

Redrawn in the lecture style from published tables. Unmodified LaTeX excerpts
of the source tables are kept in `data/` (arXiv sources retrieved 13 October 2026).

| Series | Source | What is plotted |
| --- | --- | --- |
| Gamma rays | Fermi-LAT, Ackermann et al., ApJ 799, 86 (2015), arXiv:1410.3696, Table 3 (foreground model A) | IGRB bin integrals placed at the geometric bin centre as $E^2\,dN/dE$ for a local $E^{-2.32}$ shape (Table 4 index). Error bars: quoted uncertainties; shaded boxes: foreground-model range. The last bin is the published upper limit. |
| Neutrinos | IceCube, PRL 136, 121002 (2026), arXiv:2507.22233v3 | Best-fit Combined-Fit broken power law from Table III; 68% band and sensitive energy range **digitized from Fig. 3** (vector source, `digitize_icecube_band.py`). Per flavour, $\nu+\bar\nu$. |
| Cosmic rays | Pierre Auger, PRD 102, 062005 (2020), arXiv:2008.06486, Table VI | $E^2J$ with statistical errors; the two empty bins are the published 90% upper limits. |
| WB bound | Waxman & Bahcall, PRD 59, 023002 (1999), hep-ph/9807282, Eqs. (2)–(3) | $I_{\max}\approx1.5\times10^{-8}\xi_Z$ GeV cm⁻² s⁻¹ sr⁻¹ for $\nu_\mu+\bar\nu_\mu$; band $\xi_Z=0.6$ (no evolution) to $3$ (QSO/SFR-like). Converted to per flavour after oscillations: $\tfrac12 I_{\max}$, i.e. $0.45$–$2.25\times10^{-8}$. Drawn over $10^4$–$10^{11}$ GeV, as an $E^{-2}$ extrapolation of a bound derived from cosmic rays above $10^{19}$ eV. |

Units: GeV cm⁻² s⁻¹ sr⁻¹; Auger km⁻² yr⁻¹ (Julian year) and eV are converted.
Neutrinos and the WB bound are per flavour; gamma rays are photons; cosmic rays are
all nuclei. No fit, likelihood, cascade or bound is recomputed. The same comparison
appears, with older data, in Ahlers & Halzen, PPNP 102, 73 (2018), Fig. 9.

Tests (`test_theory.py`): table row counts and selected values; IGRB bin sum against
the published integral above 100 MeV; converted IGRB points against the published
cutoff power-law fit; Auger table against its fitted $J_0$; unit conversion; BPL
normalization at 100 TeV; best fit inside the digitized band; WB per-flavour
bookkeeping. The digitizer prints its calibration residuals (below 0.3 pt) and recovers
the break at $10^{4.393}$ GeV against $10^{4.39}$ in Table III.

## `converter-cycle.svg` — converter acceleration

Editable schematic of one cycle of the converter mechanism of Derishev, Aharonian,
Kocharovsky and Kocharovsky, PRD 68, 043003 (2003), astro-ph/0301263: a proton
converts into a neutron ($p\gamma\to n\pi^+$) inside a relativistic flow, leaves it
unaffected by the field, converts back outside ($n\gamma\to p\pi^-$) and is returned
by the field. The paper's abstract states a gain "roughly equal to the bulk Lorentz
factor squared" per cycle. A flux-weighted Monte Carlo for a planar boundary in
`dvnanima/cosmic_accelerators/concept/physics_checks.py` gives a mean gain
$\approx2.7\,\Gamma^2$ for $\Gamma=3$, 10, 30 (re-run 13 October 2026, read-only),
hence the label "~Γ²". Geometry, paths and the two drawn neutrinos are illustrative;
no conversion rate, loss or spectrum is computed.
