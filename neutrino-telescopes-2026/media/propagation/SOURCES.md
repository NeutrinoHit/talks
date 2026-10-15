
## Computed Earth transmission (13 October 2026)

`earth-transmission-cc-dark.svg/png/csv`: lecture calculation from
`assets/earth-transmission/` (config, generator, four tests). Survival probability
against charged-current interactions, averaged over neutrino and antineutrino,
T = exp(-N_A sigma_CC X): CSMS cross sections (arXiv:1106.3723, Tables I-II),
PREM density (Dziewonski & Anderson 1981), detector 1 km deep, 10 GeV-100 PeV,
zenith 90-180 degrees. No NC or tau regeneration; not a flux ratio for a source
spectrum. Replaced the white dissertation figure on the slide on 13 October and was itself replaced on
15 October by the full-transport redraw below; it remains the CC-only comparison; the original
`rzf_2dxsCT10nlo.png` (Allakhverdyan, dissertation 2026, Fig. 4.20) stays here.

## Computed tomography contrast (14 October 2026)

`earth-tomography-contrast-dark.svg/png`: `assets/earth-transmission/build_tomography.py` (three tests).
The same CC survival probability through PREM and through a homogeneous Earth of the same mass
(5.514 g/cm³): left, survival against zenith angle at 10, 30 and 100 TeV; right, the relative difference.
Illustrates where up-going neutrinos are sensitive to the core. No NC or tau regeneration, no flux model or
detector response. The measured tomography on the same slide is quoted from Donini, Palomares-Ruiz & Salvado,
Nature Physics 15 (2019) 37, arXiv:1803.05901 (Table I and text: 68 % credible intervals, default flux model).

## Full transport with regeneration (15 October 2026)

`earth-transport-full-dark.svg/png`: `assets/earth-transmission/build_transport.py` (three tests), on the
slide "Through the Earth" (EN principles, RU appendix). Redraw of V. A. Allakhverdyan's transport
calculation with NC regeneration (dissertation 2026, Fig. 4.20; Allakhverdyan, Zavyalov & Naumov 2026, Fig. 9),
from his 100 x 100 table (version of 14 October 2026; not redistributed). Colour: flux at the detector over flux
entering the Earth; dashed: the same levels without regeneration.
