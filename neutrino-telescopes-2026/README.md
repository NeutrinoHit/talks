# Neutrino Telescopes: Principles, Results, and Prospects

Dmitry Naumov. English. Audience: non-specialists. Target 60 minutes; the full review
version assembled on 13 October 2026 is longer and will be recomposed into a
main route plus a backup section (see `REWORK-PLAN.md`).

## Lecture and scientific scope

The lecture connects Cherenkov detection and event reconstruction to selected
samples, detector response, diffuse spectra and source searches. Publication figures are redrawn in the lecture's dark style from paper tables,
public data or vector artwork (digitized where only a raster exists, and labelled
so); only a few agreed originals remain. Photon and
neutrino comparisons follow the measured spectrum; compact-source opacity is
a physical interpretation rather than an observed production-site image.
The deck contains 36 slides including the title. Historical portraits and
additional analysis tabs are reserve material for questions.

Scientific model assumptions, sample dates, flavour conventions and confidence
levels are in the speaker notes and each media directory's SOURCES.md.
The lecture consumes only selected figures, films and self-contained teaching
assets. No private event files or external sibling runtime is needed.

The portrait pairs currently cover Markov, Reines, Chudakov and Domogatsky.
Chudakov's photographs are explicitly dated 1946 and 1985. The early Domogatsky
portrait is labelled 1980 in the original Keynote asset filename. Unknown dates
remain marked undated. Documented early-career images of Halzen and Spiering,
and a later Learned portrait, remain desirable. No synthetic historical
portraits are used. Full provenance is in
[media/history/SOURCES.md](media/history/SOURCES.md).

DN supplied two additional source decks: Stony Brook (26 October 2020)
and HyperWebinarGVD (November 2021). Their historical sections were inspected
in Keynote; the 2020 section was also checked in a temporary PDF export.
Original embedded portraits have been extracted without altering the source
decks. The Baikal tabset now includes DN's three-string-race anecdote,
attributed to those slides rather than to an independently verified letter.

`lecture.qmd` assembles seven blocks. Edit one block at a time, preserving slide
IDs so links remain stable. All authored mathematics uses LaTeX/MathJax; source figures retain their original labels. Styling comes
from the canonical NeutrinoHit Reveal assets; there is no lecture-specific CSS
or JavaScript. Keep future substantial code in `assets/` and consumed public
media in `media/`, with a static poster for each video.

| Block | Slides | Source | First slide ID |
| --- | --- | --- | --- |
| Opening | 1–2 | `blocks/_01-opening.qmd` plus title | `a-new-window` |
| History | 3–6 | `blocks/_02-history.qmd` | `markovs-idea` |
| Detection and response | 7–14 | `blocks/_03-principles.qmd` and includes | `interaction-probability` |
| Source physics | 15–19 | `blocks/_04-sources.qmd`, pion include, energy budget | `cosmic-messengers` |
| Results and interpretation | 20–29 | `blocks/_05-results.qmd` and includes | `icecube-diffuse-flux` |
| Sensitivity and observatories | 30–33 | `blocks/_06-observatories.qmd` and includes | `source-sensitivity` |
| Prospects and closing | 34–36 | `blocks/_07-outlook.qmd` | `next-questions` |

Slide order of the results block: diffuse flux (IceCube, Baikal-GVD), spectral
structure with Glashow and flavour, the Milky Way, gamma-ray budget, hidden
sources, NGC 1068, blazars (TXS 0506+056, GVD 2021, radio flares, radio-bright
blazars), KM3-230213A, Baikal-GVD source searches. New slides: `energy-budget`,
`b-hunt`, `what-we-need`; `next-questions` is now "What we want to discover" and
`conclusions` "Where are the sources?". Timing per block will be set when the
lecture is recomposed.

If the session includes five minutes of questions, reduce detection by two
minutes, results by two and observatories by one. No extra slide is required.

## Build and navigation

From the `talks` root:

```sh
quarto render neutrino-telescopes-2026/lecture.qmd --to revealjs
```

The normal repository build remains `make site`. It includes this lecture.
On this Mac, follow the workspace Quarto/Python configuration and request
the documented scoped permission for render checks (Sass cache).

Output: `_site/neutrino-telescopes-2026/lecture.html`.

Expected URL after Dmitry publishes the repository:
`https://neutrinohit.github.io/talks/neutrino-telescopes-2026/lecture.html`.
This is an intended URL, not a claim that the page is published.

The Reveal menu provides slide navigation. `S` opens speaker notes.
Block entry links append, for example, `#/interaction-probability` or
`#/icecube-diffuse-flux`. The footer returns to the already registered English
neutrino-telescope material section:
`https://neutrinohit.github.io/en/outreach.html#neutrino-telescopes`.

The repository publication workflow already delegates to the canonical
NeutrinoHit reusable workflow. No extra deployment workflow is needed.
Adding a new inbound card to the central map is a later, explicitly scoped
central-site change. No central-site files are changed here.

## What to take from Spiering's review

[Neutrino Astronomy at High Energies: An Experimental Review](https://arxiv.org/html/2609.26436)
is the experimental backbone. Select the following ideas and figures when
developing each block; verify figure reuse terms and retain original credits.

- Historical engineering choices, not a complete list of detector milestones.
- Figure 3: light propagation in water and ice. Explain absorption and
  scattering separately. Neither medium is universally superior.
- Figures 4–6: angular resolution, the distinction between deposited/muon/
  neutrino energy, and effective area with Earth absorption. Preserve event
  selections, energy ranges and statistical definitions.
- Figure 7: detector geometry and optical-module technology. Recheck current
  configurations against collaboration updates; the review's configuration
  snapshot is May 2026, not the publication date.
- Diffuse flux and spectral shape, Galactic emission, individual-source
  evidence and limits as different observational questions.
- Statistical caveats: trial factors, catalogue definitions, source
  association, reconstruction changes and the meaning of an upper limit.
- Joint sky coverage, real-time alerts and the Global Neutrino Network.

Use primary collaboration papers for numerical claims. Read the source-theory
block alongside [D'Ammando's AGN review](https://arxiv.org/html/2606.30764).
Do not inherit a review's interpretation as a unique physical conclusion.

## Animation roadmap for later stages

Paths below are workspace-relative source references, not web dependencies.
The deployed lecture must not load private HDF5 files or depend on sibling
checkouts. No package changes or transport reruns are required for the lecture assets.

| ID | Sequence | Existing material | Remaining work |
| --- | --- | --- | --- |
| A01 | Cherenkov threshold and cone | Existing English `cherenkov_radiation_en.mp4`, 40 s, copied with poster into `media/principles` | Connected on slide 9; preserve phase/group distinction |
| A02 | Photoelectron multiplication | Existing English `pmt_multiplication_en.mp4`, 40 s; four real OM photos | Connected on slide 10, with Optical modules tab; TRIDENT is a prototype |
| A03 | Tracks, photon births and time–angle production | `dvnanima/neutrino_telescope`; muon 20 s (1 TeV / 1 PeV, fixed view, 2 m transverse extent only), electron 20 s (100 GeV / 1 TeV, unchanged); portrait exports separately for YouTube | Genuine electron PeV event pending; propagation and module hits belong to the next stage |
| A04 | Direct and scattered light | LightHit viewer now records actual WebGL MP4/WebM, with static camera and optional local saving; two 15 s direct-light demonstrations | Slide 11 compares measured KM3NeT/IceCube displays and calculated means. Scattered-light movies remain a later step |
| A05 | Reconstructing a hidden track | New 48 s English film + interactive, same sampled synthetic event and validated direct-light timing model | Connected on slide 12; known crossing point, direction/time fit only, not calibrated angular uncertainty |
| A06 | Earth filtering and local optical background | Earth shield and separate seawater K-40 films retained in media/backgrounds | Not embedded on slide 13; retained for optional later use |
| A07 | Transparent versus hidden cosmic source | Astrophysical context videos exist; no complete production/opacity sequence identified | New explanatory Manim scene for matter/photon targets, pion decay and reprocessing |

Priority: reuse A01/A02; use the completed A03 source films and develop A04;
then develop A07. A05 and A06 have separately validated, explicitly simplified models.
Manim is suitable for explanatory choreography. Physics event displays should
consume approved `ntsim`/`lighthit` results. Styling of the surrounding Reveal
slide continues to use the shared NeutrinoHit components.

## Slides 9–11: media and viewer capture

Slide 9 has three concise tabs: **Animation**, **Why a cone?**, and
**Which way does light go?** Two lecture-local vector diagrams show same-age
wavefronts below/above threshold and the light direction normal to the common
tangent front. Circle crossings are not presented as the radiation criterion.
Only the speed conditions and the emission-angle formula remain visible;
kinetic thresholds, ring geometry and model limitations are in speaker notes.
All equations are LaTeX. The new 40-second `cherenkov_steps_en.mp4` keeps
four wavefronts, separate constant-speed trials, teaching pauses, the common
tangent front and normal light directions. The graph and ring are removed.
Source: `dvnanima/cherenkov_radiation/cherenkov_radiation.py`, `config.toml` and
`texts.toml`. The lecture uses the four-step wavefront construction.
The slide is authored separately in `blocks/_03a-cherenkov.qmd`.

Slide 10 plays the PMT
animation and compares actual IceCube, KM3NeT, Baikal-GVD and TRIDENT module
photographs. The TRIDENT image is explicitly a laboratory prototype.
Source credits/reuse notes: `media/principles/SOURCES.md` and
`media/optical-modules/SOURCES.md`.

Slide 11 has pattern comparison, measured KM3NeT track, online IceCube event
compilation and two captured model-response tabs. The IceCube compilation
requires Internet and mixes data with one simulated illustration; the other
assets are local. The model is not an observed event reconstruction, and
both model films use a detector-clock replay. The cascade's display timing
was restored from its stored G4 source/pose contract, with source yield and
centroid checked; its detector response arrays were not recalculated.
Full scientific/capture provenance is in `media/events/SOURCES.md`.

To refresh a local recordable viewer without rerunning transport:

```sh
python neutrino-telescopes-2026/assets/prepare_recordable_viewers.py
python neutrino-telescopes-2026/assets/serve_recordable_viewers.py
```

Then open the printed localhost URL (`?local_save=1`), select the event,
component, time mode, Detector array framing and Presentation view. For the
current clips choose Unscattered, Cumulative, 15 s and 30 FPS, with the
Detector clock. Record
and Save to local server; ordinary download remains available in a browser
that handles Blob downloads. Raw results/viewers stay in LightHit `.build`.
Encode a captured movie for this lecture:

```sh
python neutrino-telescopes-2026/assets/encode_viewer_movie.py --kind muon --input /path/to/capture.mp4
```

Use local LightHit source when regenerating viewers; the installed package
can differ from the local source. The preparation script selects it explicitly and preserves
physics arrays. Never copy the raw result JSON or local viewer HTML into
public `media`/`assets`. Viewer feature documentation and focused tests are
in `lighthit/docs/VIEWER_VIDEO_EXPORT.md` and
`lighthit/tests/test_viewer_video_export.py`.

## Slide 12: explanatory movie, then interactive

The default **The idea** tab plays a new 48-second English movie with a fixed
camera and genuine sampled detections. A hidden generated track is reconstructed
from arrival times by a real fit, independently of truth. **Try it** repeats the
experiment with direction sliders, a likelihood-map click, New event, Fit,
Reveal truth and Reset. Photoelectron budget and timing jitter apply to new
events; the assumed group index changes predictions while observations stay
fixed. **The model** explains the equations and scientific limits.

The crossing point is explicitly known and fixed. Only direction and global
time offset are fitted; there is no vertex, energy or telescope-resolution
claim. The map shows relative conditional timing likelihood, not calibrated
confidence. The movie, exercise and formulas distinguish phase and group indices.
All mathematical labels use LaTeX. A static poster is provided for PDF.

Sources/configuration: `dvnanima/neutrino_reconstruction/README.md` and `MODEL.md`;
local exercise regeneration and six numerical parity checks:
`assets/reconstruction/README.md`. Movie provenance: `media/reconstruction/SOURCES.md`.

## Slide 13: backgrounds

Two tabs only: **Detector backgrounds** has a compact IceCube/KM3NeT/Baikal-GVD
table with optical sources, single-PMT pulse rates and explicitly labelled
atmospheric-muon sample rates. **Neutrino backgrounds** has a large static graph
of conventional atmospheric, prompt-charm and astrophysical νN interactions
per year per energy decade in 1 km³ water, downward hemisphere, before selection.
Muon event rates, optical singles and neutrino interaction rates are distinct
quantities. Sample definitions, model assumptions and citations are in notes.
Canonical Reveal classes are used.

Earth shield and radioactivity videos were removed **only from this slide**;
all media/source files are retained. Earth opacity remains on slide 7. Stable
`backgrounds-and-earth` anchor retained.
Source: `blocks/_03b-backgrounds.qmd`; graph generator, scientific data and
eight focused tests: `assets/backgrounds/README.md`. No publication performed.

## Jet power and neutrino production

**Where jets get their power**, has four tabs. **Tidal disruption**
plays DN's English `jet_launch_en.mp4` (98.4 s), following returning debris
and a schematic magnetic engine. **AGN** and **Gamma-ray bursts** are static
comparisons of other fuel supplies and engine contexts. **Cosmic messengers**
retains the short comparison of charged particles, photons and neutrinos.
Bulk plasma acceleration in the film is distinct from non-thermal proton
acceleration on the next slide.

**How jets produce neutrinos**, has four tabs. **Star in the jet**
plays DN's English `jet_star_en.mp4` (97.4 s), changing scenario to a star
entering an existing jet. **Gas targets** and **Photon targets** are static
comparisons of $pp$ and $p\gamma$ production. **Acceleration and confinement**
retains the gyroradius criterion. Gas in the film comes from an axisymmetric,
non-relativistic hydro model, while protons and neutrinos are schematic.
Speaker notes explain model limits, the one-crossing pion yield and references
for the static variants. Only the two supplied films are embedded on these slides.

Both complete films take 3 min 15.8 s together. Allow about four minutes for
the two films within the seven-minute source block. Discuss static
alternatives selectively to keep the block within its time allocation. Media are copied
unchanged into `media/jets/`, with posters at 75 s and 56 s for PDF.
Source details, SHA-256 checksums and references: `media/jets/SOURCES.md`.
Stable anchors `cosmic-messengers` and `acceleration-and-confinement` are retained.
The source remains `blocks/_04-sources.qmd`.

## Pion decays and the photon budget

Pion/muon decays and characteristic parent-proton energies precede the data.
The photon-flux relation is an optional pp benchmark. The gamma-ray budget
follows the measured diffuse spectrum, with the p-gamma assumptions of the
published comparison stated separately. A compact-source diagram introduces
photon conversion and reprocessing before NGC 1068. The `pion-production`,
`parent-particle-energy` and `hidden-sources` anchors are retained.
Sources: `blocks/_04a-pion-production.qmd`, `blocks/_05a-gamma-budget.qmd`,
`media/multimessenger/SOURCES.md` and `media/response/SOURCES.md`.

## Closing and observatory programme

The source-sensitivity scaling precedes the global sky and instrument designs.
Its first tab plays "A source emerges" (57.4 s, from `dvnanima/source_emerges`;
media in `media/sensitivity/`): events arriving one by one, three angular
resolutions (cascade in ice 10°, cascade in water 2.5°, track 0.4°) and
1 → 30 km³. The source is invented at NGC 1068's strength on a uniform background;
significance is a one-sided Poisson likelihood ratio at the known position with
Asimov expectations. It is an illustration, not a forecast for any detector.
The observatory tabs retain official configuration figures, design/operating
status and explicitly stated scientific goals; the KM3NeT tab shows an artist's
impression (Edward Berbee/Nikhef). The GVD effective-volume label is not equated
to the geometric volumes of other arrays. The Baikal option of HUNT is called
B-HUNT and has its own slide (`b-hunt`), Baikal-GVD → B-HUNT (Russia + China).

The prospects close with "What we want to discover" (questions placed on the
energy axis), "What we lack" (instruments, analysis and people: the ФНАФЧ
programme, «Физика нейтрино и астрофизика частиц», on teach-in.ru) and
"Where are the sources?", which answers the opening question.
Sources: `blocks/_07-outlook.qmd`, `assets/prospects/`, `media/prospects/`. Limits of the Gaussian background-dominated
point-source scaling remain in `blocks/_06b-source-sensitivity.qmd`.

## Existing DN material

- `sciencepop/neutrino-telescope-astrofest-2026/NeutrinoTelescopes.key`:
  accessible original Keynote package, with embedded media under `Data/`.
  It is a source, not a file to modify or publish wholesale.
- The PDF beside it provides the slide sequence and existing author credits,
  including M. Mishchenko, S. Gursky, B. Shaybonov and M. Zhukov.
- `talks/georgia-2026/media/baikal_short-1770.mp4`: existing 26.8-second clip.
- `talks/protvino-2026/dnaumov.qmd`: existing Baikal-GVD and HUNT context.
- `ntsim/README.md`: HDF5 schema and particle propagation viewer.
- `lighthit/README.md`, `lighthit/src/lighthit/assets/event_viewer.*`:
  transport response and browser viewer, inspected read-only.

Before importing an asset, record its original filename, creator, scientific
meaning, permission/public status and any processing. Select the correct
Keynote media by visual inspection, not by filename alone.

## Speaking route

The route below predates the October 2026 rework and will be replaced when the
lecture is recomposed into a main route and a backup section.

The time budget is 60 minutes of speaking, including videos. It is a rehearsal
allocation, not a measured performance duration. Use the following route;
additional tabs remain available for discussion.

| Part | Main route | Reserve |
| --- | --- | --- |
| Opening/history | Recognition; Markov idea; DUMAND photograph; Baikal site and three-string episode; IceCube construction | Portrait pairs and detailed chronology |
| Detection | Cosmic/Earth contrast; muon source; Cherenkov movie; PMT movie; pattern comparison; reconstruction movie; both background tabs; Effective area | Electron source; event compilations; viewer captures; interactive fit; detailed response tabs |
| Source physics | Complete jet films; Pion decays and Parent proton energy; Production environments | Alternative engines and targets; photon-flux coefficient |
| Diffuse results | IceCube The excess; GVD Cascade energies and Spectrum; IceCube Measured spectrum | Veto diagram; zenith plots; parameter and index contours; event-proxy distributions |
| Interpretation | Transparent sources; compact-region diagram; Milky Way IceCube, Animation, then IceCube again | Photon threshold; Galactic toy sky |
| Sources | TXS alert and archival flare; NGC directional excess, photon comparison and X-ray population; KM3 event and energy inference; GVD source limits | TXS reprocessing and GVD candidate; AGN spectra; alternative limit spectra |
| Prospects | Source-sensitivity scaling; sky coverage and joint analysis; IceCube, KM3NeT, Baikal-GVD | Four proposed arrays and extended project comparisons |
| Closing | Questions and measurements; Measurements and remaining uncertainties | Cross-section and flavour programme during questions |

The two jet films last 195.8 s together. Other main films: muon 20 s,
Cherenkov 40 s, PMT 40 s, reconstruction 48 s, Milky Way 72.4 s,
IceCube-170922A 11.776 s, KM3-230213A 30 s and A source emerges 57.4 s. Full video time is
about 8 min 36 s, before discussion; the Milky Way film now comes from
`dvnanima/milky_way_neutrinos` (the lecture-local `assets/galactic` generator is superseded). The interactive is an optional demonstration;
if used, exchange time with a reserve result rather than extending the hour.

## Diffuse evidence and response

Redrawn figures (`*-dark.svg/png`), their generators, data and tests:
`assets/diffuse-figures/`, `assets/source-figures/`, `assets/gvd-galactic/`,
`assets/gamma-partner/`, `assets/theory/`, `assets/response/`,
`assets/joint-search/`, `assets/prospects/`, `assets/earth-transmission/`
(slide 7: CC-only Earth transmission computed with PREM and CSMS),
`assets/km3-energy/` (KM3-230213A energy intervals from the paper's text). Originals, exact versions and
conventions: `media/diffuse/SOURCES.md`, `media/response/SOURCES.md`,
`media/source-results/SOURCES.md`, `media/multimessenger/SOURCES.md`,
`media/galactic/SOURCES.md`, `media/theory/SOURCES.md`,
`media/joint-search/SOURCES.md`, `media/prospects/SOURCES.md`. Source identities and checksums:
`assets/evidence/figures.json`; regeneration: `assets/evidence/README.md`.
The NGC 1068 photon comparison is dated 2022 and remains separate from the
2026 neutrino fit. The published GVD spectrum comparison retains preliminary
IceCube points with an explicit label; the next slide uses finalized IceCube
spectral-feature results. No fit or calibration is inferred from the teaching
diagrams or movie counts.

## Focused checks

```sh
python neutrino-telescopes-2026/assets/check_lecture.py
```

This checks slide order and stable IDs, local media, video posters, exact
publication-artwork checksums, comparison conventions and removed placeholder
text. The relevant Quarto render and browser inspection verify layout separately.
