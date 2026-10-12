# Neutrino Telescopes: Principles, Results, and Prospects

Dmitry Naumov. English. 60 minutes of speaking time, including animations.

## Current stage: opening, history and detection animations

The opening and history use photographs and thematic tabsets. Slide 7 now
compares the 1 PeV interaction length in cosmic baryonic matter with Earth's
opacity, using Allakhverdyan's dissertation figure 4.20. Slide 2 also includes
the Big Three IceCube event displays. Slide 8 has Manim/NTSim muon and electron
films, with one large English lecture video per particle tab. Shorts are
separate exports for YouTube, not embedded in the slides.
The remaining physics slides remain an editable scaffold. The deck contains 35 slides including the automatic
title slide. A separate Baikal history slide adds one slide without extending
the 3–8 minute history allocation. Portrait tabs are optional detours, not an
instruction to narrate every panel. Speaker notes contain context and citations.
Raw event data remain local; the lecture consumes only exported films and posters.
The propagation map is an attributed
figure extracted from a public dissertation, not a new transport simulation.
No public deployment is implied.

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
IDs so links remain stable. All mathematics uses LaTeX/MathJax. Styling comes
from the canonical NeutrinoHit Reveal assets; there is no lecture-specific CSS
or JavaScript. Keep future substantial code in `assets/` and consumed public
media in `media/`, with a static poster for each video.

| Block | Time | Slides | Source | First slide ID |
| --- | --- | --- | --- | --- |
| Opening | 0–3 min | 1–2 | `blocks/_01-opening.qmd` plus title | `a-new-window` |
| History | 3–8 min | 3–6 | `blocks/_02-history.qmd` | `markovs-idea` |
| Detection principles | 8–20 min | 7–13 | `blocks/_03-principles.qmd` | `interaction-probability` |
| Source physics | 20–30 min | 14–19 | `blocks/_04-sources.qmd` | `cosmic-messengers` |
| Results | 30–44 min | 20–27 | `blocks/_05-results.qmd` | `icecube-diffuse-flux` |
| Observatories | 44–56 min | 28–33 | `blocks/_06-observatories.qmd` | `global-observatories` |
| Outlook | 56–60 min | 34–35 | `blocks/_07-outlook.qmd` | `next-questions` |

If the session includes five minutes of questions, reduce principles by two
minutes, sources by one and observatories by two. No extra slide is required.

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
checkouts. No package changes or expensive reruns belong to Stage 1.

| ID | Sequence | Existing material | Remaining work |
| --- | --- | --- | --- |
| A01 | Cherenkov threshold and cone | Existing English `cherenkov_radiation_en.mp4`, 40 s, copied with poster into `media/principles` | Connected on slide 9; preserve phase/group distinction |
| A02 | Photoelectron multiplication | Existing English `pmt_multiplication_en.mp4`, 40 s; four real OM photos | Connected on slide 10, with Optical modules tab; TRIDENT is a prototype |
| A03 | Tracks, photon births and time–angle production | `dvnanima/neutrino_telescope`; muon 20 s (1 TeV / 1 PeV, fixed view, 2 m transverse extent only), electron 20 s (100 GeV / 1 TeV, unchanged); portrait exports separately for YouTube | Genuine electron PeV event pending; propagation and module hits belong to the next stage |
| A04 | Direct and scattered light | LightHit viewer now records actual WebGL MP4/WebM, with static camera and optional local saving; two 15 s direct-light demonstrations | Slide 11 compares measured KM3NeT/IceCube displays and calculated means. Scattered-light movies remain a later step |
| A05 | Reconstructing a hidden track | New 48 s English film + interactive, same sampled synthetic event and validated direct-light timing model | Connected on slide 12; known crossing point, direction/time fit only, not calibrated angular uncertainty |
| A06 | Earth filtering and local optical background | New 58 s Earth film with NASA geography, PREM layers and sampled CC/NC interactions; separate 32 s seawater K-40 companion | Connected on slide 13; no regenerated-flux, detector-efficiency or freshwater-background claims |
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
`texts.toml`. The former angle-and-ring movie has been removed from the lecture
and producer media; the four-step version is now the canonical animation.
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
may be older. The preparation script selects it explicitly and preserves
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

## Slide 13: Earth filtering and radioactive light

Default **Earth shield** tab: 97.9-second English film from
`dvnanima/earth_shield/media/earth_shield_en.mp4`, with actual NASA surface
geography, Monte Carlo atmospheric showers, a true-radius PREM half-globe
cutaway, PDG CSDA muon ranges and sampled neutrino first interactions from
1 TeV to 1 PeV. A single complete planar section is used for straight paths.
The same PeV energy is compared on a diameter and several shorter chords.
Displayed P0 means zero CC/NC interactions; no sharp energy cutoff is imposed.

**Radioactivity** is a separate 32-second seawater K-40 explanation: beta electron,
optical light and selected nearby-module coincidence paths. Its group-speed
times are calculated, but rates, acceptance and accepted hits are not modelled.
No radioactive-background forecast for freshwater Baikal is made.

Other tabs explain background classes, energy/direction and the existing
effective-area formula. All formulas are LaTeX and styling stays canonical.
The slide remains number 13 with its stable `backgrounds-and-earth` anchor;
the deck still has 35 slides. Authoring block: `blocks/_03b-backgrounds.qmd`.
Earth model/movie controls: `dvnanima/earth_shield/README.md`, `config.toml`,
`texts.toml` and `test_earth_shield.py`. The independent seawater companion
remains in `dvnanima/earth_filter/RADIOACTIVITY.md`. Reuse/source record:
`media/backgrounds/SOURCES.md`. No publication has been performed.

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

## Block completion criteria

For each later block: agree the scientific message, choose approved assets,
implement the visual sequence, check notation and units, render and inspect
the slides, then rehearse the allotted time. Keep measured results, simulations
and conceptual illustrations visibly distinct. Recheck time-sensitive claims
before the final talk. Full references remain in notes with concise visible
attribution where needed.
