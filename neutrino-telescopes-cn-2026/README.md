# Neutrino Telescopes (student lecture, English version for Chinese students)

D. V. Naumov. English. Audience: students without a background in neutrino physics. About 60 minutes.
English version of the Russian student lecture `../neutrino-telescopes-ru-2026`, which is itself a shortened
and simplified version of `../neutrino-telescopes-2026`. Differences from the Russian lecture:

- the opening slide shows the Nobel Prize news without the correspondence with F. Halzen;
- TRIDENT, HUNT and NEON are tabs of the main slide "Neutrino telescopes of the world"; the appendix keeps P-ONE;
- the last slide "Who will do it?" has no link to a course catalogue, and its chain names the programme by subject.

## Structure

`lecture.qmd` assembles the blocks:

| block | content |
|---|---|
| `_01-opening.qmd` | the prize, "So what?" (1 PeV), quiz on solar neutrinos, what a neutrino is |
| `_02-history.qmd` | Markov, DUMAND (1979 and 1993), Baikal, the path to a cubic kilometre; one photograph per epoch |
| `_03-principles.qmd` | quiz on depth, how to catch a neutrino, Cherenkov light (film with the dipoles of the medium), the photomultiplier (film of the JUNO PMT R12860), tracks and showers (own LightHit films), quiz on upward muons, how the direction is reconstructed (film only), quiz on tracks and showers |
| `_04-sources.qmd` | cosmic accelerators (film of a black hole tearing a star apart, AGN, GRB), how a jet produces neutrinos (film and the chain, which answers "So what?") |
| `_05-results.qmd` | the flux from space, the Milky Way, the first sources, KM3-230213A; each tab opens with a one-line conclusion |
| `_06-future.qmd` | how to see more, telescopes of the world (with TRIDENT, NEON, HUNT), questions, "Where are the sources?" with the answer to "Then what? And where?", people and the telescopes built nearby |
| `_09-appendix.qmd` | appendix: transparent Universe and opaque Earth, the reconstruction model, the Waxman–Bahcall bound, neutrinos → gamma rays, and the technical slides from the plenary lecture |

Each block starts with a title slide. Formulae are in the appendix; the main part has only $\cos\theta_C=1/(n\beta)$ on "Cherenkov light". Texts are bullet lists.
The quizzes use the shared quiz classes (`.quiz-slide`, `.quiz-option`, `.quiz-note`): a question slide, then the same slide
with the answer marked.
There are no speaker notes.

## Media

- Photographs, plots, official videos and the English posters of the films are taken from
  `../neutrino-telescopes-2026/media` (sources and rights in the `SOURCES.md` files there); the photographs
  of B. Shaybonov from `../neutrino-telescopes-ru-2026/media/photos`.
- The title background is `../neutrino-telescopes-2026/media/galactic/title-galaxy.jpg`, the same picture as
  in the Russian lecture with the credit line in English (`../neutrino-telescopes-ru-2026/assets/build_title_galaxy.py en`).
- The figures of the map, the milestones to B-HUNT, the questions on the energy axis, the source map,
  the energy budget and the tomography contrast are the English originals in `../neutrino-telescopes-2026/media`.
- `media/figures/` holds the figures that exist only here. `assets/cn_figures.py` makes them from the original
  generators, replacing only the visible labels; if a label is not found where expected, it stops:
  - `people-chain.svg`: the chain of `../neutrino-telescopes-2026/assets/prospects/build_prospects.py`, with the
    programme named by its subject (neutrino physics and particle astrophysics) instead of the course label;
  - `nt36-side.svg`: the NT-36 side view of `../neutrino-telescopes-ru-2026/assets/build_nt36.py`
    (astro-ph/9601161, section 2, Fig. 1) with English labels;
  - `solar-neutrinos.png`: the Sun and the Earth of `../neutrino-telescopes-ru-2026/assets/build_intro.py`
    (solar neutrino flux about 6.5·10¹⁰ cm⁻² s⁻¹, rounded to "about 60 billion") with English labels.
- `media/films/` holds five posters cut from the English films; three at the moments of the Russian posters:
  `humanity_cube_en.jpg` (humanity-cube web-en, 13.6 s), `icecube_build_en.jpg` (icecube-first-pev web-en v3,
  48.0 s, the 5160 modules) and `gvd_cascades_sky_en.jpg` (milky-way-neutrinos film-en, 50.0 s, the 8 Baikal-GVD
  cascades, also used as a picture on the slide "Baikal above 200 TeV"); `pmt_juno_en.jpg` is the frame at 1 s of
  pmt-juno web-en v1 (`dvnanima/pmt_juno/media/pmt_short_v4_en_score_A.mp4`, the same SHA-256).
  `cherenkov_dipoles_en.jpg` is the frame at 45 s of cherenkov-radiation film-dipoles-en v1 (the triangle βct, (c/n)t).

```bash
python3 -I assets/cn_figures.py
```

Films are inserted with the shortcode `nh-video` from the shared media library; versions and SHA-256 are pinned in
`../media.lock.json`. "How to catch a neutrino?" plays the whole icecube-first-pev film (v3: the detector, then the
events); it is the only place the film is shown. "Tracks and showers" shows only the two LightHit films; the films of the muon and the shower (Geant4) are in
the appendix.

## Nerpa

The pet for breathers: `media/nerpa/nerpa.js` (a copy of the build `dvnanima/nerpa/web/nerpa.js`, the same file as in
the Russian lecture; after changes there, rebuild with `build_web.py` and copy the file). It is included in `_metadata.yml`.
On a slide the nerpa is set by `<div data-nerpa="…">` in a `{=html}` block; the position is relative to the whole slide.
Three spots, no more:

| slide | moment | trick |
|---|---|---|
| "Lake Baikal: the ice becomes a platform", tab "Romance" | after the DUMAND story | on click peeks from the bottom right, waves a flipper, dives (`peek`, `data-gesture="wave"`) |
| "Cherenkov light", tab "Why a cone?" | after the formula for the angle | on click dashes along the bottom with a wedge of waves behind, like a boat (`dash`) |
| section title "What We Already Know" | after the sources block | naps at the bottom, a bubble grows from its nose and pops (`nap`) |

The key **Y** sends the nerpa across the current slide, **Shift+Y** makes it peek from the corner;
there is no nerpa in the PDF version. In a hidden browser tab the nerpa does not start.
