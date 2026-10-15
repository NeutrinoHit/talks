# Earth transmission, charged-current absorption only

Survival probability of a neutrino crossing the Earth without a charged-current
interaction, averaged over neutrino and antineutrino:
T(E, θ) = exp(−N_A σ_CC(E) X(θ)).

- σ_CC: CSMS, arXiv:1106.3723, Tables I–II (HERAPDF1.5 NLO, isoscalar nucleons);
  below 50 GeV σ/E is held constant.
- X(θ): column through PREM (Dziewonski & Anderson 1981) from a detector 1 km deep;
  diameter column 1.095·10¹⁰ g/cm² (Gandhi et al.: about 1.1·10¹⁰).
- Not included: neutral-current and tau regeneration. The slide now shows the full
  transport (below); this map stays as the CC-only comparison.

```sh
python build_transmission.py          # media/propagation/earth-transmission-cc-dark.{svg,png,csv}
python -m pytest -q test_transmission.py
```

## Full transport with regeneration (on the slide)

`build_transport.py` redraws V. A. Allakhverdyan's calculation (dissertation 2026, Fig. 4.20;
Allakhverdyan, Zavyalov & Naumov, Phys. Part. Nucl. Lett. 23 (2026), Fig. 9): CT10nlo cross sections,
PREM, detector 1 km deep, R_E = 6378 km, 100 x 100 grid in log E (10 GeV - 100 PeV) and zenith (90 - 180 deg).
Colour: Phi_full / Phi_surf, flux at the detector over flux entering the Earth, NC regeneration included.
Dashed: Phi_cc / Phi_surf of the same table, equal to its `prob` = exp(-N_A sigma_tot X) (CC + NC, neutrino):
no interaction at all, so its optical depth is 1.3-1.4 times the CC-only one above.

Input: `talks/data/allakhverdyan-transport/icecube_plot_data_CT10nlo.npz` (git-ignored, not redistributed;
received from V. A. Allakhverdyan as `icecube_plot.zip` with his `plot_icecube.py`, version of 14 October 2026,
sha256 in `config.toml`). An earlier version of the same day had Phi_full/Phi_surf of about 0.1 at the horizon;
this one gives 1 at the horizon and Phi_full >= Phi_cc everywhere (checked by the tests). The incident flux
Phi_surf falls roughly as E^-3 and depends on zenith below about 100 TeV (factor up to 5.7); with
regeneration the ratio depends on that spectrum. No CSV is written for this figure.

```sh
python build_transport.py             # media/propagation/earth-transport-full-dark.{svg,png}
python -m pytest -q test_transport.py # skipped without the input table
```

## Tomography contrast

`build_tomography.py` compares the same CC survival probability through PREM with that through a homogeneous
Earth of the same mass (mean density 5.514 g/cm³ from the PREM integral): survival against zenith angle at
10, 30 and 100 TeV, and the relative difference (PREM − homogeneous)/homogeneous over energy and zenith.
Through the centre at 30 TeV PREM transmits 18 % less. Same limitations as above (no NC or tau regeneration,
no flux or detector response). Measurement with IceCube data: Donini, Palomares-Ruiz & Salvado,
Nature Physics 15 (2019) 37, arXiv:1803.05901.

```sh
python build_tomography.py            # media/propagation/earth-tomography-contrast-dark.{svg,png}
python -m pytest -q test_tomography.py
```
