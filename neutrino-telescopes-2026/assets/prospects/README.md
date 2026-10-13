# Prospects and closing figures

`build_prospects.py` writes four lecture-style figures to `media/prospects/`.
The discovery map reuses the IceCube band and fit from `assets/theory/`.

```sh
MPLCONFIGDIR=/private/tmp/neutrino-prospects-mpl pyenv exec python neutrino-telescopes-2026/assets/prospects/build_prospects.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/prospects -p 'test_*.py'
```

Sources were checked on 13 October 2026.

## `gvd-to-bhunt.svg`

| Milestone | Source |
| --- | --- |
| March 2024: first HUNT prototype string in Lake Baikal, 12 optical modules with 20-inch PMTs | C. Liu et al. (HUNT), PoS(ICRC2025)1101, doi:10.22323/1.501.1101; Science and Technology Daily, 5 Feb 2025 |
| 2025: full-scale string with 20-inch-PMT modules put into operation (24 modules, March 2025, per IHEP slides) | [JINR, 1 Apr 2025](https://www.jinr.ru/posts/2025-expedition-to-deploy-baikal-gvd-telescope-completed/); M. Chen, RICH 2025 talk, 15 Sep 2025 |
| January 2025: South China Sea, 4 prototype detector units and 1 LED calibration unit at 1600 m, connected to the seafloor observation network | [Science and Technology Daily, 5 Feb 2025](https://www.stdaily.com/web/gdxw/2025-02/05/content_293176.html); M. Chen, RICH 2025 |
| 2026: Baikal-GVD 16 clusters, effective volume 0.8 km³ | [baikal-gvd.jinr.ru/telescope](https://baikal-gvd.jinr.ru/telescope) |
| ≈2028: Baikal-GVD effective volume 1 km³ | [JINR, 3 Mar 2026](https://www.jinr.ru/posts/grigory-trubnikov-baikal-gvd-neutrino-telescope-to-reach-1-km-sup-3-sup-volume-by-2028/); JINR weekly no. 10 (4808), 5 Mar 2026 |
| ≈2040: HUNT, 30 km³, in Lake Baikal, Baikal-GVD Collaboration with IHEP | JINR, 3 Mar 2026; [IHEP project page, 11 Oct 2025](https://ihep.cas.cn/astro/en/research/sf/ucp/202510/t20251011_7986821.html) (about 30 km³, proposed by the LHAASO team) |

The two cubes have volumes 1 and 30 km³ (side ratio 30^(1/3) ≈ 3.1). They are
not detector layouts. IHEP lists two candidate sites (Lake Baikal: 2212 strings,
720 m high, 3.8 km radius at ~1300 m depth; South China Sea: 9 clusters), per
M. Chen, RICH 2025; JINR announces the Baikal option. The lecture calls the
Baikal project B-HUNT. Effective volume (GVD) and instrumented volume (HUNT) are
different quantities; the cubes compare stated sizes only.

## `discovery-map.svg`

Open questions placed on the neutrino-energy axis, over the IceCube Combined-Fit
spectrum (band digitized from Fig. 3 of arXiv:2507.22233v3; see `assets/theory/`).

| Item | Position | Source |
| --- | --- | --- |
| Seyfert galaxies | 1.5–15 TeV bar | IceCube NGC 1068, arXiv:2510.13403 (well-constrained range) |
| Spectral break | 10^4.39 GeV | IceCube PRL 136, 121002 (2026), Table III |
| Milky Way and PeVatrons | arrow from 200 TeV | Baikal-GVD, ApJ 982, 73 (2025); LHAASO, PRL 131, 151001 (2023) |
| Cross section from Earth absorption | arrow from 40 TeV | IceCube, Nature 551, 596 (2017): absorption expected above 40 TeV |
| Glashow resonance | 6.3 PeV | IceCube, Nature 591, 220 (2021) |
| KM3-230213A | 220 PeV (median) | KM3NeT, Nature 638, 376 (2025) |

The vertical positions of labels are arbitrary; only the cyan band has a flux scale
(it is drawn without a y-axis because the map shows energies, not fluxes).

## `people-chain.svg`

Symbolic chain programme → people → results → B-HUNT, without names.
ФНАФЧ = «Физика нейтрино и астрофизика частиц». Course list:
[teach-in.ru, tag ФНАФЧ](https://teach-in.ru/course?tags=ФНАФЧ) (12 courses on 13 October 2026).
The example result is Allakhverdyan et al. (Baikal-GVD), ApJ 982, 73 (2025), arXiv:2411.05608.

## `sources-sky.svg`

Equatorial Mollweide map, RA increasing to the left. Source positions from the
Baikal-GVD source list (arXiv:2603.21261v2, Table 1). The Galactic plane and the
|b| = 5° lines are computed from the IAU J2000 Galactic pole (192.85948°, 27.12825°,
l_NCP = 122.93192°). The figure marks where evidence points; it does not show
fluxes, significances or the individual Seyfert and blazar population members.

Tests (`test_prospects.py`): Galactic Centre at (266.40°, −28.94°); plane maximum
declination; published source positions; cube volume ratio; sources and order of
milestones; break consistent with `assets/theory`; no personal names in the chain.
