# Point-source figures in the lecture style

Redraws of white journal figures of the source slides; same principles as
`assets/diffuse-figures/README.md` (vector paths where possible, raster
digitization otherwise; quantities and conventions unchanged; short legends,
full descriptions in the notes).

```sh
pyenv exec python extract.py txs_flare  /path/1807.08794v1/fig2_Tdep_IC86b_lightcurve.pdf
pyenv exec python extract.py ngc_scan   /path/2510.13403v2/finescan_ngc1068_fixed.pdf
pyenv exec python extract.py ngc_sed    /path/2211.09972v1/fig4.pdf
pyenv exec python extract.py radio_sky  /path/2001.00930v3/figures/skymap.pdf
pyenv exec python extract.py radio_flux /path/2001.00930v3/figures/avg_flux.pdf
pyenv exec python extract.py txs_radio  /path/2308.13686v1/lc_Fermi_RATAN_11GHz.png
pyenv exec python extract.py baikal_limits  /path/2603.21261v2/figures/uplims_scl_s2019-2023_different_spectra.pdf ../source-results/data/baikal-source-list-2603.21261v2.tex
pyenv exec python extract.py baikal_antares /path/2603.21261v2/figures/uplims_scl_s2019-2023_comapred2ANTARES_different_spectra_correct_ytitlte_mod_legend_inside.pdf
pyenv exec python extract.py xray_spectra   /path/2510.13403v2/some_seyfert_spectra_broken_PL.pdf
pyenv exec python extract.py xray_population /path/2510.13403v2/population_excess_seyfert_floating_gamma_without_NGC1068.pdf
pyenv exec python extract.py txs_original /path/2307.14559v1/figures/PSTracksv2evtplot.pdf
pyenv exec python extract.py txs_updated  /path/2307.14559v1/figures/ntv5evts.pdf
MPLCONFIGDIR=/private/tmp/nt-mpl pyenv exec python build.py
MPLCONFIGDIR=/private/tmp/nt-mpl pyenv exec python build_txs_directions.py /path/2308.13686v1
pyenv exec python -m unittest discover -s . -p 'test_*.py'
```

| Output (`media/source-results/`) | Source | Method |
|---|---|---|
| `txs-archival-flare-2018-dark` | IceCube, Science 361, 147 (2018), arXiv:1807.08794v1, Fig. 2 | vector; energy proxy decoded from the embedded colour bar (approximate) |
| `ngc1068-neutrino-scan-2026-dark` | IceCube, arXiv:2510.13403v2, Fig. 2 right | embedded raster map decoded to −log₁₀p via its colour bar; vector contours |
| `ngc1068-multimessenger-2022-dark` | IceCube, Science 378 (2022), arXiv:2211.09972v1, Fig. 4 | vector |
| `radio-blazars-sky-2020-dark` | Plavin et al., ApJ 894, 101 (2020), arXiv:2001.00930v3, Fig. 1 | recoloured: the four binary raster layers kept as masks in the original page coordinates; vector stars, flux from the colour bar |
| `radio-blazars-vlbi-flux-2020-dark` | same paper, Fig. 3 | vector |
| `txs-radio-gamma-2023-dark` | Baikal-GVD, ICRC 2023, arXiv:2308.13686v1, Fig. 4 | digitized raster: Fermi points with bars, RATAN diamonds (k-means split of merged markers) with bars, flare sum and components separated by stroke thickness |
| `baikal-source-limits-dark` | Baikal-GVD, arXiv:2603.21261v2, Fig. 2 | limits = Table 1 (column scales 1e-8, 1e-6, 1e-3 fixed by matching the plotted markers, agreement 0.05%); sensitivity curves from the vector artwork |
| `baikal-antares-limits-dark` | same paper, Fig. 3 | ANTARES 15-yr markers from the vector artwork; GVD limits from Table 1; the original's four source labels are not repeated |
| `xray-agn-population-dark` | IceCube, arXiv:2510.13403v2, X-ray population test | vector; broken N axis and inverted p_local axis as in the original |
| `txs-original-directions-dark`, `txs-updated-directions-dark` | IceCube, ICRC 2023, arXiv:2307.14559v1, Fig. 3 | vector circles and event dots; energy proxy decoded from the embedded colour bar (approximate); the plotted TXS marker (77.39, 5.64) is reproduced as drawn |
| `xray-agn-spectra-dark` | IceCube, arXiv:2510.13403v2, Fig. 5 | vector bands |
| `txs-baikal-directions-dark` | Baikal-GVD, ICRC 2023, arXiv:2308.13686v1, Fig. 3 | GVD direction and 50%/90% radii read from the paper text at build time (not stored); IceCube 90% contour digitized from the raster; TXS catalogue position |

By agreement, Baikal cascade coordinates appear only graphically:
`build_txs_directions.py` reads them from the paper's source file at build time.

Checks (`test_figures.py`): two dashed (removed) of 14 circles in the original TXS
processing, 13 circles after reprocessing; binomial minimum of the X-ray population
test at N = 11; TXS box duration 158 days; light-curve neutrino lines at
2017.72 and 2021.29 and main radio-flare peak near 2020.15; Baikal Table 1 scaling
(NGC 1068 in all three spectra); 167+167 ANTARES markers; five X-ray AGN bands; NGC 1068 scan maximum
−log₁₀p ≈ 6.5 (local 5.0σ) and marker at the catalogue position; recovered Fermi
4FGL band edges 0.05–0.1–0.3–1–3–10–30–300 GeV; 36 AGN in both Plavin figures
(as in their Fig. 2 caption); digitized IceCube-170922A contour within 0.06° of
the published 90% extents (Science 361, 2018). Names in the radio sky map use
the common names given in the paper text (3C 279 = 1253−055, NRAO 530 = 1730−130).
