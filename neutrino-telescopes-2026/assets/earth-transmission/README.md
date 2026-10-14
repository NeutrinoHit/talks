# Earth transmission, charged-current absorption only

Survival probability of a neutrino crossing the Earth without a charged-current
interaction, averaged over neutrino and antineutrino:
T(E, θ) = exp(−N_A σ_CC(E) X(θ)).

- σ_CC: CSMS, arXiv:1106.3723, Tables I–II (HERAPDF1.5 NLO, isoscalar nucleons);
  below 50 GeV σ/E is held constant.
- X(θ): column through PREM (Dziewonski & Anderson 1981) from a detector 1 km deep;
  diameter column 1.095·10¹⁰ g/cm² (Gandhi et al.: about 1.1·10¹⁰).
- Not included: neutral-current and tau regeneration. The full transport solution
  is V. A. Allakhverdyan's (dissertation 2026, Fig. 4.20), a flux ratio for an
  assumed source spectrum.

```sh
python build_transmission.py          # media/propagation/earth-transmission-cc-dark.{svg,png,csv}
python -m pytest -q test_transmission.py
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
