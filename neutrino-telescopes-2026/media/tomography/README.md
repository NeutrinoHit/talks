# User-supplied tomography figures

Supplied through Downloads, 8 October 2026. The matching files found there are
PNG, not PDF. Original raster data and Russian labels are preserved. These
figures are staged for the later tomography discussion; they are not yet added
to the narrated lecture. Do not describe them as measured density maps or
neutrino transmission probabilities.

The CT10nlo figures below match the totals and shapes of the corresponding
dissertation plots. Source definitions: Allakhverdyan (2026), pp. 113–116,
equation 4.26 and figures 4.22–4.24:
https://issc.jinr.ru/files/326/f_2_5830.pdf

Related publication: Allakhverdyan, Zavyalov and Naumov (2026), section 6
and Appendix D:
https://www1.jinr.ru/Pepan_letters/panl_2026_2/05_Allahverd_rus.pdf

| Filename | Alternative to PREM in the source text | Total printed on plot | Source figure |
| --- | --- | --- | --- |
| `chi2_rzf_2dxsCT10nlo_PREM_vs_PREM_man_and_ker.png` | Uniform core and mantle out to radius 5600 km, density 8.853 g/cm^3; PREM outside | 6.840 | Thesis 4.22; paper 14 |
| `chi2_rzf_2dxsCT10nlo_PREM_vs_PREM_av_ext_ker.png` | Uniform inner and outer core, density 11.87 g/cm^3; PREM outside | 0.114 | Thesis 4.23; paper 18 |
| `chi2_rzf_2dxsCT10nlo_PREM_vs_PREM_lin_ker.png` | A linear core density profile; PREM outside | 0.601 | Thesis 4.24; paper 19 |

The suffixes alone do not establish model definitions. In particular, the
separate `PREM_vs_PREM_av.png` supplied in Downloads has total 4.557; do not
confuse it with the 0.114 uniform-core case. `PREM_vs_PREM_quad_ker.png` has
total 0.621. Those two variants are not imported pending their exact model
definitions and matching documentation. Older CT18ZNNLO files are not mixed
with the CT10nlo set.

The source calculation compares expected event counts for 1 km^3 of water
and one year, using the muon-neutrino plus antineutrino component and the
stated atmospheric and astrophysical fluxes. This is a forecast under those
assumptions, not an achieved experiment sensitivity. Detector response,
reconstruction and systematic treatment must be made explicit before giving
an experimental interpretation.

The colour scale gives per-bin contributions to the stated likelihood-ratio
statistic; the scales differ among plots. The number in each title is the
total. Do not compare colours across independently normalised scales or
silently turn sqrt(total) into a calibrated discovery significance.

For later slide development, use one model per tab with the profile, exposure,
and likelihood definition visible or in notes. Keep source images intact until
the original plotting code/data are available for an English-label export.
