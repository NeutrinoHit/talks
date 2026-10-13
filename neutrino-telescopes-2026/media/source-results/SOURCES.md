# Point-source results and the global network

Scientific graphics retain their original axes, legends, confidence definitions
and flavour conventions. PDF figures were converted to vector SVG with Poppler,
without recolouring, tracing data or changing their scientific content.
Source versions are fixed below. Retrieved 12 October 2026.

## TXS 0506+056

- `icecube-170922a.mp4`: recorded IceCube-170922A event display, 11.776 s,
  H.264, 1440×1080. Original file from the
  [IceCube 2018 multimessenger gallery](https://icecube.wisc.edu/gallery/in-science-icecube-neutrinos-point-to-long-sought-cosmic-ray-accelerator/):
  `gal_Multimessenger_NoRotate_Enhanced.mp4`,
  <https://res.cloudinary.com/icecube/video/upload/f_auto,q_auto/v1602528664/gal_Multimessenger_NoRotate_Enhanced.mp4?_i=AA>.
  Unchanged movie, muted on the slide. Poster: frame at 8 s, ffmpeg.
  Credit: IceCube Collaboration. The official
  [gallery terms](https://icecube.wisc.edu/press-guidelines/) allow educational,
  informational, noncommercial reuse with the supplied credit.
- `txs-archival-flare-2018.svg`: original figure 2 of
  [IceCube, Science (2018), arXiv:1807.08794v1](https://arxiv.org/abs/1807.08794v1),
  `fig2_Tdep_IC86b_lightcurve.pdf` from its source archive. Event weights and
  fitted time profile, not a histogram of excess-event counts. Historical
  analysis: 13±5 signal events, 3.5 sigma after time-search trials.
- `txs-original-directions.svg` and `txs-updated-directions.svg`: original
  panels of figure 3 in [IceCube, ICRC 2023, arXiv:2307.14559v1](https://arxiv.org/abs/2307.14559v1).
  Original source files `figures/PSTracksv2evtplot.pdf` and
  `figures/ntv5evts.pdf`. The updated processing removes two cascade-like
  events and changes reconstructed directions, angular uncertainties and
  energy proxies. No new fit is performed.
- `txs-baikal-directions.png`: full source figure 3 of
  [Baikal-GVD, arXiv:2308.13686v1](https://arxiv.org/abs/2308.13686v1), original
  `skymapTXS.png`, 965×829. It depicts directional compatibility, not proof
  that TXS produced the April 2021 cascade. Original ±75 TeV energy uncertainty
  is a three-sigma interval; directional 6.2-degree radius is 90% containment.

Paper-figure credits: IceCube Collaboration / Baikal-GVD Collaboration.
The arXiv distribution licence is not asserted to be a blanket CC reuse licence.
The attributed scientific figures are retained as excerpts for this lecture;
no relicensing or ownership claim is made.

## NGC 1068 and X-ray-selected AGN

- `ngc1068-multimessenger-2022.svg`: complete original Figure 4 of
  [IceCube, Science (2022), arXiv:2211.09972v1](https://arxiv.org/abs/2211.09972v1),
  source `fig4.pdf`, converted to SVG with Poppler. Dark-blue line/band: the
  historical nu_mu+anti-nu_mu fit and 95% confidence band in 1.5–15 TeV.
  Green: Fermi/MAGIC photon measurements and limits. Grey points: archival
  photon data. Light-blue shading and grey line: theoretical core models.
  The slide explicitly dates this comparison to 2022; no 2026 curve is overlaid.
  Credit: IceCube Collaboration. Source checksum: `assets/evidence/figures.json`.

- `ngc1068-hubble-2025.jpg`: actual Hubble UV/optical observation, image
  [potw2515a, 14 April 2025](https://esahubble.org/images/potw2515a/),
  <https://cdn.esahubble.org/archives/images/large/potw2515a.jpg>, 3774×4101.
  Unchanged image. Required credit: **ESA/Hubble & NASA, L. C. Ho, D. Thilker**.
  [ESA/Hubble image terms](https://esahubble.org/copyright/): CC BY 4.0.
  The photo does not resolve the neutrino-emission region.
- `ngc1068-neutrino-scan-2026.svg`: source `finescan_ngc1068_fixed.pdf`,
  figure 2 right panel in [IceCube, arXiv:2510.13403v2](https://arxiv.org/abs/2510.13403v2).
  Local scan contours retain their original definition; catalogue and all-sky
  trial-corrected significances are separate quantities.
- `xray-agn-population.svg`: source
  `population_excess_seyfert_floating_gamma_without_NGC1068.pdf`, original
  X-ray-catalogue binomial-test panel in the same v2 paper. NGC 1068 excluded,
  47 X-ray AGN, most significant 11-source ensemble; not eleven discoveries.
- `xray-agn-spectra.jpg`: official IceCube research figure,
  <https://res.cloudinary.com/icecube/images/q_auto/v1760555822/Xray_bright_AGN_spectra/Xray_bright_AGN_spectra.jpg?_i=AA>,
  1422×813, from the [2025 research announcement](https://icecube.wisc.edu/news/research/2025/10/evidence-for-neutrino-emission-from-x-ray-emitting-galaxies/).
  Credit: IceCube Collaboration. Reuse follows the gallery terms above.
  Original all-flavour source spectra and diffuse-flux normalization retained.
  The slide uses `xray-agn-spectra.svg`, converted from the unmodified v2
  source `some_seyfert_spectra_broken_PL.pdf`, figure 5, for sharper labels.

## KM3-230213A

- The event movie/poster are the existing originals in `media/events/`;
  their credit and reuse record remain in `media/events/SOURCES.md`.
- `km3-energy-calibration.png`: complete figure 2 of
  [Aiello et al., Nature 638 (2025) 376–382](https://doi.org/10.1038/s41586-024-08543-1),
  <https://media.springernature.com/lw1200/springer-static/image/art%3A10.1038%2Fs41586-024-08543-1/MediaObjects/41586_2024_8543_Fig2_HTML.png>,
  1056×833. No modifications, crops or overlaid annotations.
  Article licence: CC BY-NC-ND 4.0. Credit: KM3NeT Collaboration / Aiello et al.
  Muon energies in the simulated PMT distributions are 10, 100 and 1000 PeV;
  the observed triggered-PMT count is 3672. The inferred parent-neutrino
  distribution assumes an E^-2 incident spectrum, not direct calorimetry.

## Point-source limits

- `baikal-source-limits-e2.svg/.png/.csv`: independent rendering of all 92
  published E^-2 source upper limits in Table 1 of the same v2 paper. No new
  fit, confidence interval or sensitivity curve. The source normalization
  is multiplied by the Table 1 scale 1e-8 and expressed as E^2 Phi in
  GeV cm^-2 s^-1 for nu_mu+anti-nu_mu. Complete input table and four checks:
  `assets/source-results/README.md`.
- `baikal-source-limits.svg`: original figure 2, source
  `figures/uplims_scl_s2019-2023_different_spectra.pdf` in
  [Baikal-GVD, arXiv:2603.21261v2](https://arxiv.org/abs/2603.21261v2).
- `baikal-antares-limits.svg`: original figure 3, source
  `figures/uplims_scl_s2019-2023_comapred2ANTARES_different_spectra_correct_ytitlte_mod_legend_inside.pdf`
  in the same archive. Both retain the complete figure, including all spectra.
  Credit: Baikal-GVD Collaboration. Original paper distribution licence is
  not represented as a new CC licence. Data span April 2019–March 2024;
  the 2019–2023 labels refer to seasons. Lines are median expected sensitivity,
  symbols are 90%-confidence source limits. Efficiency systematic uncertainty
  is not included. The flux is nu_mu+anti-nu_mu before Earth attenuation.

## Global network

- `global-sites.svg/.png` and `sky-coverage.svg/.png`: locally calculated
  site map and geometrical below-horizon fractions. No detector response,
  attenuation or sensitivity forecast is calculated. Source inputs,
  regeneration and five numerical geometry tests: `assets/global-sky/README.md`.
- `joint-discovery-flux.svg`: original E^-2 panel of figure 2 in
  [ANTARES & IceCube, ApJ 892 (2020) 92, arXiv:2001.04412](https://arxiv.org/abs/2001.04412),
  source `DiscoveryX20.pdf`. The SVG conversion resolves the original PDF page
  rotation. No scientific content is cropped or altered. Seven-year IceCube
  and nine-year ANTARES samples; green is the joint five-sigma discovery flux,
  not measured source emission or present KM3NeT/GVD performance.

Temporary source archives and full article PDFs are outside the public media
directory. Local slide assets are only the selected figures and event movie.

## Blazars: radio flares and radio-bright jets (added 13 October 2026)

- `txs-radio-gamma-2023.png`: full source Fig. 4 of
  [Baikal-GVD, ICRC 2023, arXiv:2308.13686v1](https://arxiv.org/abs/2308.13686v1),
  original `lc_Fermi_RATAN_11GHz.png`, 1695 × 800, unchanged. Fermi-LAT
  gamma-ray light curve, RATAN-600 11 GHz light curve with a three-flare
  decomposition, IceCube-170922A and GVD210418CA arrival dates, and the
  2014–2015 IceCube excess. Credit: Baikal-GVD Collaboration et al.
- `radio-blazars-sky-2020.svg`: source `figures/skymap.pdf`, Fig. 1, and
  `radio-blazars-vlbi-flux-2020.svg`: source `figures/avg_flux.pdf`, Fig. 3, of
  [A. V. Plavin, Y. Y. Kovalev, Y. A. Kovalev, S. V. Troitsky, ApJ 894, 101 (2020),
  arXiv:2001.00930v3](https://arxiv.org/abs/2001.00930v3). Converted with
  Poppler, unchanged. Error regions enlarged by 0.5° as in the paper. Numbers:
  56 IceCube events above 200 TeV; post-trial chance probability p = 2·10⁻³ (0.2%);
  four strongest associations 3C 279, NRAO 530, PKS 1741−038, PKS 2145+067.
- [Plavin, Kovalev, Kovalev, Troitsky, ICRC 2021, arXiv:2112.09053](https://arxiv.org/abs/2112.09053):
  joint chance probability 4·10⁻⁵ (4.1σ) with lower-energy IceCube sky-map data.
  Cited in notes; no figure used.
- The slide states that the association is debated, citing
  [IceCube, arXiv:2304.12675](https://arxiv.org/abs/2304.12675): no significant
  correlation of IceCube alert events with radio-bright AGN; more event
  information and more data make the result compatible with background.
- Checksums of the converted figures and the PNG: `assets/evidence/figures.json`.

## Lecture-style redraws (13 October 2026)

`txs-archival-flare-2018-dark`, `ngc1068-neutrino-scan-2026-dark`,
`ngc1068-multimessenger-2022-dark`, `radio-blazars-sky-2020-dark`,
`radio-blazars-vlbi-flux-2020-dark`, `txs-baikal-directions-dark`: redraws of the
figures listed above (same papers and figure numbers). Methods per figure
(vector paths, colour-bar decoding, recoloured raster layers, digitized
IceCube-170922A contour) and checks: `assets/source-figures/README.md`.
The original files are kept unchanged.

Further redraws (13 October 2026): `txs-radio-gamma-2023-dark` (digitized), `baikal-source-limits-dark` and
`baikal-antares-limits-dark` (Table 1 limits + vector curves/markers),
`xray-agn-spectra-dark` (vector). Same papers and figure numbers as
listed above; methods and checks in the generator README. Originals kept unchanged.

Last redraws (13 October 2026): `xray-agn-population-dark`, `txs-original-directions-dark` and `txs-updated-directions-dark` (vector). Same papers and figure numbers as
listed above; methods and checks in the generator README. Originals kept unchanged.

- `km3-energy-intervals-dark.svg/png` (13 October 2026): the "From light to energy"
  tab. Drawn only from numbers stated in the text of Aiello et al., Nature 638 (2025) 376:
  muon energy 120 (+110, −60) PeV (68 %), 35–380 PeV (90 %); parent neutrino for an
  E^-2 spectrum, median 220 PeV, 110–790 PeV (68 %), 72 PeV–2.6 EeV (90 %); 3672
  triggered PMTs. No curve or element of the CC BY-NC-ND Fig. 2 is traced.
  Generator and test: `assets/km3-energy/`.
