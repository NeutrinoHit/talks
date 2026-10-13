# Jet teaching films for slides `cosmic-messengers` and `acceleration-and-confinement`

English films supplied by DN and selected by DN for this lecture on
12 October 2026. The MP4 files are copied byte for byte from the workspace
sources below. No simulation or film rendering was rerun, and no Russian
version was imported. Lecture-local copies remove any runtime dependency
on the sibling `dvnanima` checkout. This records authorized lecture reuse,
not a new publication or an independent assessment of third-party licences.

| Local file | Original workspace file | Duration | Format | SHA-256 |
| --- | --- | --- | --- | --- |
| `jet_launch_en.mp4` | `dvnanima/jet_launch/media/jet_launch_en.mp4` | 98.4 s | H.264, 1920×1080, 30 fps, silent | `6e0fd24a29df8628203ed010b1872ca608fb91a3742c8c5dcfc68afc141a1839` |
| `jet_star_en.mp4` | `dvnanima/jet_star/media/jet_star_en.mp4` | 97.4 s | H.264, 1920×1080, 30 fps, silent | `5bfca727909455c5130b116563be3718b9850223ad8a2159fd153cb15318602b` |

Durations, resolution, codec and frame rate were checked with `ffprobe`.
Posters are single frames extracted with `ffmpeg`, with no cropping or
retouching: `jet_launch_en.jpg` at 75 s and `jet_star_en.jpg` at 56 s.
They supply the initial HTML view and a static counterpart for PDF.
Videos retain their original on-frame credits and reference end cards.

## From a star to a jet

Source: `dvnanima/jet_launch/jet_launch.py`, `tde_sim.py`, `jet_physics.py`,
`config.toml`, `texts.toml`, `README.md` and `CARD.md`.

The film follows a jetted tidal disruption, returning debris and a magnetic
engine. Debris trajectories are computed test-particle orbits in the frozen-in
approximation with an apsidal-precession prescription. Disc formation,
magnetic geometry, Poynting-flux pulses and bulk acceleration are schematic.
This is not a GRMHD calculation or a non-thermal particle-acceleration model.
The Swift J1644+57 curve is a schematic X-ray trend rather than observational
data points. It is not a claim that every disrupted star produces a jet.

References retained from the film:

- Lacy, Townes and Hollenbach, ApJ 262 (1982) 120.
- Burrows et al., Nature 476 (2011) 421.
- Levan et al., Science 333 (2011) 199.
- Zauderer et al., ApJ 767 (2013) 152.
- Blandford and Znajek, MNRAS 179 (1977) 433.
- Bardeen, Press and Teukolsky, ApJ 178 (1972) 347.

## A star in the jet

Source: `dvnanima/jet_star/jet_star.py`, `hydro2d.py`, `run_hydro.py`,
`star_physics.py`, `tracers.py`, `jet_context.py`, `config.toml` and `texts.toml`.

This is a different scenario: a star enters an already existing jet. It is not
the next stage in the same tidal disruption. Gas images consume DN's actual
axisymmetric, non-relativistic hydrodynamic calculation of a dense sphere
and wind in a supersonic flow (density contrast 100). The model lacks
self-gravity and stellar structure and is not a relativistic AGN-jet model.
The displayed remaining percentage describes dense tracer material.

Protons, shock-crossing cycles, collisions, pion products, gamma attenuation
and neutrino rays are schematic overlays. The numbers of drawn particles and
absorbed gamma rays are not flux or opacity predictions. The one-crossing
cloud estimates use `n = 1e10 cm^-3`, `R = 1e14 cm`, `sigma_pp = 50 mb`,
`kappa = 0.5`: `tau_pp = 0.05` and approximately 2.5% of proton energy into
pions, not all into neutrinos. Photomeson efficiency is not computed.
The final Earth image is credited in the film to NASA Blue Marble, July 2004.

The producer's older `README.md` opening and `CARD.md` describe a shorter,
purely schematic-gas version. For this 97.4-second export, the current code,
TOML files and visible credits establish the hydro/schematic distinction.
The 56 s poster shows the cloud, the particle paths and the neutrino label.

Attribution on the slide (13 October 2026): the red-giant/jet scenario and its
calculation belong to [Barkov, Aharonian and Bosch-Ramon, ApJ 724 (2010) 1517,
arXiv:1005.5252](https://arxiv.org/abs/1005.5252), who solved the hydrodynamics
of a stellar envelope blown by an AGN jet and proposed pp collisions as the origin
of TeV flares from M87. This film illustrates the idea; it does not reproduce
their calculation. Barkov's own calculation movies are not used in the lecture.

Scenario references retained from the film:

- Barkov, Aharonian and Bosch-Ramon, ApJ 724 (2010) 1517.
- [Wang et al., Jet-cloud/star interaction as an interpretation of neutrino
  outburst from the blazar TXS 0506+056](https://arxiv.org/abs/1809.00601),
  first submitted in 2018, revised in 2022. This is a proposed interpretation.
- Fichet de Clairfontaine et al., A&A 693 (2025) A270.

The lecture exposes no raw hydro caches or private event data.
