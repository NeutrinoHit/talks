# Galactic emission sources

## Explanatory film and static counterparts

- `milky_way_neutrinos_en.mp4` (72.4 s, 1920 × 1080, 30 fps, no audio,
  SHA-256 `cfffc82b…0d3d`), poster `milky_way_neutrinos_en.jpg` (film time
  63 s: the Baikal-GVD test and verdict) and static sky
  `milky_way_neutrinos_sky.jpg` (36.4 s: the model sky). Rendered on
  13 October 2026 from DN's `dvnanima/milky_way_neutrinos` (`galaxy_model.py`,
  `milky_way_neutrinos.py`, `config.toml`, `texts.toml`, ten tests in
  `test_milky_way_neutrinos.py`); a Russian version exists there. The
  standard `© neutrinohit.github.io` footer is applied. Point clouds are rendered
  in a slightly blurred layer (no grain); re-rendered 13 October 2026. These files replace
  the earlier 48 s film from the lecture-local `assets/galactic/` (that
  generator still writes to the same names; do not rerun it).
- Parts: cosmic-ray protons in a model disc; collisions and straight
  neutrino rays (highlighted ones reach the Sun); lines of sight from the Sun
  and the morph of every gas point to its sky position; fraction of a
  sidereal day the Galactic centre spends below the horizon (IceCube 0 %,
  KM3NeT ARCA 63 %, Baikal-GVD 75 %; geometry only); the eight Baikal-GVD
  cascades above 200 TeV and the published right-ascension shuffling test.
- Computed: the model sky $I(l,b)=\int n_{\rm gas}n_{\rm CR}\,ds$
  (illustrative gas and cosmic-ray profiles, not fitted to surveys; relative
  units, asinh stretch); the horizon fractions; the shuffling test with
  100 000 skies, which reproduces the paper (observed median |b| 10.35°,
  mean shuffled median 31.6° vs 31.4°, p = 0.014). Schematic: proton paths,
  collision times and counts. The verdict quotes the published p-values,
  1.4·10⁻² (GVD alone) and 3.4·10⁻⁴ (with IceCube HESE cascades and ICECAT
  tracks), without trial correction.
- Events: Allakhverdyan et al. (Baikal-GVD) and Kovalev, Plavin, Semikoz,
  Troitsky, ApJ 982 (2025) 73, [arXiv:2411.05608](https://arxiv.org/abs/2411.05608),
  Table 1. Positions are drawn (circles: 90 % containment, as on the static map) but no
  coordinates are written in the frame, per DN.
- Observational context: IceCube Collaboration, *Observation of high-energy
  neutrinos from the Galactic plane*, Science 380 (2023),
  DOI [10.1126/science.adc9818](https://doi.org/10.1126/science.adc9818),
  [arXiv:2307.04427](https://arxiv.org/abs/2307.04427).

## IceCube comparison figure

- Local original: `icecube-multiwavelength-2023.jpg` (2375 × 1354), unchanged.
- Source: [IceCube gallery, 29 June 2023](https://icecube.wisc.edu/gallery/high-energy-neutrinos-from-the-galactic-plane/),
  image caption “Five panels showing the Milky Way in different wavelengths”,
  Figure 1 of the Science paper.
- Direct image: <https://res.cloudinary.com/icecube/images/q_auto/v1671570505/adc9818_Figure_fig1_seq1_v1-1/adc9818_Figure_fig1_seq1_v1-1.jpg>.
- Credit: IceCube Collaboration. Gallery reuse permits educational,
  informational and noncommercial use with the accompanying credit:
  [IceCube multimedia usage guidelines](https://icecube.wisc.edu/press-guide/).
  Retrieved 12 October 2026. No publication is implied by local use.
- Optical and gamma-ray views, the pion-template prediction, analysis
  expectation after detector effects, and the observed pre-trial significance
  map are different quantities. The bottom map is not raw neutrino intensity.
  The paper's 4.5σ result is the global diffuse-template test with trials,
  not the maximum of the bottom map's pre-trial pixel significance.
- [Public data release](https://icecube.wisc.edu/data-releases/2023/06/observation-of-high-energy-neutrinos-from-the-galactic-plane/),
  DOI 10.21234/8v5d-rn16, documents templates, angular reconstruction and the
  per-event likelihood inputs. These data are not consumed by the schematic film.

## Baikal-GVD above 200 TeV

[V. A. Allakhverdyan et al. (Baikal-GVD Collaboration), Y. Y. Kovalev,
A. V. Plavin, D. V. Semikoz, S. V. Troitsky, *Probing the Galactic neutrino flux
at neutrino energies above 200 TeV with the Baikal Gigaton Volume Detector*,
ApJ 982, 73 (2025), arXiv:2411.05608v2](https://arxiv.org/abs/2411.05608v2).

- `gvd-galactic-sky.svg/.png` and `gvd-galactic-test.svg/.png`: lecture-style
  redraw. The map shows the 8 cascades of Table 1 as 90% containment circles in
  Galactic coordinates (those of the table); the paper's Fig. 5 is equatorial
  and also contains IceCube events, which are not redrawn. The histogram
  recomputes the paper's Fig. 1 test from Table 1: median |b| for skies with
  uniformly randomized right ascensions and fixed declinations. Event
  coordinates appear only graphically; no coordinate table is stored.
  Generator, reproduction and checks: `assets/gvd-galactic/README.md`.
- Numbers used on the slide and in notes: 8 cascades with E ≥ 200 TeV
  (spring 2018 – spring 2024, ≈26.8 one-cluster years, ≈64% expected
  astrophysical purity); observed |b|med 10.4° against 31.4° expected;
  p = 1.4·10⁻² (2.5σ, no trials); IceCube cascades p = 8.7·10⁻³, IceCube
  tracks p = 1.8·10⁻³, all combined p = 3.4·10⁻⁴ (3.6σ), Table 2.
  The recomputation gives p = 0.013, consistent with the published value.
- Credit: Baikal-GVD Collaboration and co-authors. The arXiv distribution
  licence is not represented as a new CC licence.

## ANTARES Galactic ridge (text only)

[ANTARES Collaboration, *Hint for a TeV neutrino emission from the Galactic
Ridge with ANTARES*, PLB 841, 137951 (2023), arXiv:2212.11876](https://arxiv.org/abs/2212.11876):
|l| < 30°, |b| < 2°, 1–100 TeV, tracks and showers; background-only hypothesis
disfavoured at ≈96% confidence. No figure is used.

## Diffuse Galactic gamma rays (redrawn)

- `galactic-gamma-diffuse.svg` (slide) and `.png` (review): lecture-style
  redraw of published measurements. Generator, inputs and five checks:
  `assets/gamma-partner/README.md`.
- LHAASO-KM2A: [PRL 131, 151001 (2023), arXiv:2305.05372v2](https://arxiv.org/abs/2305.05372v2),
  Tables S2 (inner Galaxy) and S3 (outer Galaxy), transcribed. Statistical
  (thick) and statistical ⊕ systematic (thin) bars.
- Tibet ASγ: [PRL 126, 141101 (2021), arXiv:2104.05181v2](https://arxiv.org/abs/2104.05181v2),
  digitized from the vector paths of Fig. 4; 1σ statistical bars.
- Common axis E^2.7 dN/dE in GeV^1.7 cm^-2 s^-1 sr^-1 (Tibet convention;
  LHAASO's E^2.5 TeV-unit values converted exactly). Sky regions and
  source masks differ; the slide caption states it. No model curves, fits
  or neutrino predictions are added.
