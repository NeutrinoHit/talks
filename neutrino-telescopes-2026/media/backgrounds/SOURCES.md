# Slide 13: Earth filtering and radioactive light

Explanatory material used in DN's lecture. The Earth film is imported from
`dvnanima/earth_shield`; the independent seawater companion remains from
`dvnanima/earth_filter`. Both are English, silent, 1920×1080 at 30 fps.
No measured telescope events or private response arrays are included.

## Earth film

`earth_shield_en.mp4`: 97.9 s, copied unchanged from
`dvnanima/earth_shield/media/earth_shield_en.mp4` on 10 October 2026.
Poster `earth_shield_en.jpg`: frame at 20 s, extracted with ffmpeg.
This replaces the earlier Earth filter in the slide; the old local media
are retained as unused files.

Surface texture: [NASA Blue Marble Next Generation Base Map](https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-map/),
July 2004 global 5400×2700 JPEG, NASA Earth Observatory/MODIS composite.
Original file downloaded on 10 October 2026 from the page's official
[JPEG asset](https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-base/july/world.200407.3x5400x2700.jpg).
NASA's [Earth imagery guidance](https://science.nasa.gov/earth/faq/) permits
reuse except where otherwise credited; NASA attribution is retained in the
film and this record. No endorsement or NASA-logo permission is implied.
This is real satellite-composite geography, not a live image or an invented
map. Lighting, atmosphere halo and interior colours are synthetic artwork.

The cutaway exposes a half-globe. Particle trajectories use a **complete
single physical plane** through the detector, without folded paths. PREM
core/mantle/crust radii are preserved; boundary strokes are annotations, not
artificially enlarged geological layers. Atmosphere/shower/detector/particle
glyphs are explicitly illustrative and enlarged for visibility.

Density: [Dziewonski & Anderson, PREM (1981)](https://doi.org/10.1016/0031-9201(81)90046-7),
original Table I, with discontinuity-aware integration and its spherical
average ocean shell. Texture does not imply local bathymetry in the model.
Neutrino cross sections: [CSMS, arXiv:1106.3723, Table I](https://arxiv.org/abs/1106.3723),
HERAPDF1.5 central neutrino CC+NC values, interpolated log–log within the
50 GeV–10 EeV table; the film shows 1 TeV, 100 TeV and 1 PeV. The model gives
**zero-interaction probability**, not regenerated flux or detector efficiency.
First-interaction positions and CC/NC types are genuinely sampled; an NC mark
is not destruction, and its lower-energy continuation is not propagated.
Surface-to-surface chords neglect burial depth and do not represent a named
detector's exact acceptance. There is no sharp energy cutoff.

Muon illustration: interpolated CSDA ranges from
[PDG standard-rock tables](https://pdg.lbl.gov/2024/AtomicNuclearProperties/MUE/muE_standard_rock.txt)
and liquid-water tables. A 1 TeV muon travels about 0.93 km in standard rock
(2.43 km in liquid water); the 1 PeV rock range is about 6.4 km. Rock stopping
is shown in a labelled enlarged inset because it is unresolved on the planet.
Stochastic losses and decay are not propagated. Atmospheric showers reuse
the Monte Carlo library from `dvnanima/air_shower_cascade`; atmosphere and
lateral scales are enlarged for visibility. Full model/provenance/tests:
`dvnanima/earth_shield/README.md`, `earth_physics.py` and `test_earth_shield.py`.

## Seawater companion

`water_radioactivity_en.mp4`: 32 s. Poster `water_radioactivity_en.jpg`: 21.5 s.

Mechanism and coincidence context:
[D. Zaborov for ANTARES, arXiv:0812.4886](https://arxiv.org/abs/0812.4886),
pp. 1–2; [KM3NeT sensor validation](https://www.km3net.org/research/detector/sensors/).
One K-40 beta-minus branch is illustrated with a chosen 0.8 MeV electron,
not a sampled beta spectrum. Its short path is enlarged only in an inset.
Electron/antineutrino glyphs are schematic, not a decay-kinematics solver.
The electron supplies optical light, not the decay antineutrino.

The three-line teaching array borrows ANTARES's 1 m module-triplet and
14.5 m storey spacing; it is not the full detector. Selected direct-ray times
are calculated with group speed, then shown in slow motion. Local flashes
are not simulated accepted hits. No activity, photon yield, optical acceptance,
counts/rates or selection efficiency is claimed. Nearby PMTs may share a
flash; coincidences can calibrate timing/response. This is **seawater**, not
a background prediction for freshwater Baikal; bioluminescence is separate
and is not modelled. Details: `dvnanima/earth_filter/RADIOACTIVITY.md`,
`water.toml`, `water.py` and `test_water.py`.
