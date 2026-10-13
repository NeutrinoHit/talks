# ANTARES + IceCube joint search: lecture-style redraw

```sh
MPLCONFIGDIR=/private/tmp/neutrino-joint-mpl pyenv exec python neutrino-telescopes-2026/assets/joint-search/joint_discovery.py --digitize
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/joint-search -p 'test_*.py'
```

Original: ANTARES & IceCube, ApJ 892, 92 (2020), arXiv:2001.04412, Fig. 2 left
(`DiscoveryX20.pdf`), local Poppler copy `media/source-results/joint-discovery-flux.svg`
(unchanged). The three curves are polylines with nine vertices; the digitized
declinations are −85°, −75°, …, −5° to better than 0.05°, which checks the x
calibration. Quantity: 5σ discovery flux (50% of trials) of the one-flavour
normalization, $E_\nu^2\Phi_0^{5\sigma}$ in GeV cm⁻² s⁻¹, for an unbroken $E^{-2}$
spectrum; seven-year IceCube and nine-year ANTARES southern-sky samples.

For $E^{-2}$ the joint discovery flux is lower than the better single sample by up
to a factor of about 1.7 (digitized values); the paper quotes improvements of up
to about 2 in sensitivity, depending on the spectrum. At −5° the joint curve
coincides with IceCube within 2%. Data: `data/joint-discovery-flux-e2-digitized.csv`.
Tests: decade grid, integer declinations, joint ≤ 1.03 × best individual, CSV = source.
