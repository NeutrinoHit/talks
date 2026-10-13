# Diffuse-flux figures in the lecture style

Redraws of white journal figures of the results block. Values come from the
original artwork: vector paths where the paper's figure is a PDF (exact up to
the drawing precision), raster digitization where only a PNG exists (marked
"digitized" on the slide). Quantities, conventions, confidence levels and
binning are unchanged; only colours, fonts and legend wording differ. Full
legends are in the speaker notes.

```sh
# 1. extract tables (original files from the arXiv source archives, not stored here)
pyenv exec python extract.py icecube2013      /path/1311.5238v2/energy_distribution.pdf
pyenv exec python extract.py icecube2026      /path/2507.22233v3/figures/physics_context.pdf
pyenv exec python extract.py icecube2013_zenith  /path/1311.5238v2/zenith_distribution.pdf
pyenv exec python extract.py icecube2026_indices /path/2507.22233v3/figures/BPL_2D_gamma_1_gamma_2.pdf
pyenv exec python extract.py gvd2025_zenith   /path/2507.01893v2/Fig2_bottom.png
pyenv exec python extract.py gvd2025_contours /path/2507.01893v2/Fig3_col9_precise.png
pyenv exec python extract.py icecube2026_events /path/2507.22233v3/figures/data_mc_globalfit_2panel_2yaxes.pdf
pyenv exec python extract.py gvd2025_energy   /path/2507.01893v2/Fig2_top.png
pyenv exec python extract.py gvd2025_spectrum /path/2507.01893v2/Fig4_col5_600.png
pyenv exec python extract.py zathul           /path/2606.00249v2/exsitu_CFBPLLogPSPL.png
# 2. draw (reads data/ only) and test
MPLCONFIGDIR=/private/tmp/nt-mpl pyenv exec python build.py
pyenv exec python -m unittest discover -s . -p 'test_*.py'
```

The vector reader is `assets/evidence/vector_paths.py` (Poppler SVG, Bezier
sampling, clip paths, `pdftotext -bbox` words). Axis calibration always uses
the drawn tick marks or frame lines; the pixel/point values are in the code.

| Output (`media/diffuse/`) | Source | Method |
|---|---|---|
| `icecube-2013-energy-dark` | IceCube, Science 342 (2013), arXiv:1311.5238v2, Fig. 4 left | vector |
| `icecube-spectrum-2026-dark` | IceCube, PRL 136 (2026), arXiv:2507.22233v3, Fig. 3 | vector |
| `icecube-2013-zenith-dark` | IceCube (2013), Fig. 4 right | vector |
| `icecube-spectral-indices-2026-dark` | IceCube PRL 136 (2026), Fig. 2 | vector |
| `gvd-2018-2024-energy-dark` | Baikal-GVD, arXiv:2507.01893v2, Fig. 2 top | digitized raster |
| `gvd-2018-2024-zenith-dark` | Baikal-GVD, arXiv:2507.01893v2, Fig. 2 bottom | digitized raster |
| `gvd-2018-2024-contours-dark` | Baikal-GVD, arXiv:2507.01893v2, Fig. 3 | digitized raster: contours traced along 360 rays from each best-fit marker, outliers (labels, crossings) removed by a running median |
| `icecube-combined-events-2026-dark` | IceCube PRL 136 (2026), Fig. 1 CF panel | vector (two count axes and data/MC ratio retained) |
| `gvd-spectrum-2025-dark` | Baikal-GVD, arXiv:2507.01893v2, Fig. 4 | digitized raster |
| `../multimessenger/diffuse-gamma-neutrino-2026-dark` | Zathul, Fang, Halzen, Hooper, arXiv:2606.00249v2, Fig. 2 (CC BY 4.0) | digitized raster; bands decoded from alpha compositing; IceCube points = CF segmented ×3 |

Checks (`test_figures.py`): 28 IceCube 2013 events in 0.2-dex bins (energy) and in
the zenith panel; best-fit index stars reproduce the published (1.31, 2.735) and
(1.72, 2.839); GVD zenith panel 18 cascades with the same background sums; 13+13
IceCube 2026 segments of 1/3 decade (last 10–100 PeV); 18 GVD cascades;
digitized GVD backgrounds sum to the stated 1.9 atmospheric-neutrino and 0.9
muon events; the digitized GVD fit line reproduces the published normalization
(4.42·10⁻¹⁸ GeV⁻¹ cm⁻² s⁻¹ sr⁻¹ per flavour at 100 TeV, within 3%) and index 2.64.
GVD contour markers reproduce the published fits (GVD 2.64, 4.42; IceCube
cascades 2.53, 1.66; tracks 2.37, 1.44); the CF panel has 18 cascade data points.
Zathul: 19 Fermi IGRB bins (0.15 dex); dashed SPL index 2.52 as in the IceCube CF fit,
its normalization ~15% above 3× the CF SPL value as drawn in the source; axis
calibration confirmed on the IceCube points to ~1%. Each redraw was also
compared visually with the original.
