# Galactic neutrino emission (superseded)

Superseded on 13 October 2026 by the film from `dvnanima/milky_way_neutrinos`,
which now owns `media/galactic/milky_way_neutrinos_en.{mp4,jpg}` and
`milky_way_neutrinos_sky.jpg`. This generator now writes to `media/galactic/legacy/`
by default so that a rerun cannot overwrite the lecture film.

Source for the 48-second English film on slide 23. Parameters, colour palette,
timing, camera and labels are in `config.toml`. Requires the configured
NeutrinoHit Python with NumPy, SciPy and Pillow, plus ffmpeg. No sibling code
or data is required to render the film.

From the talks checkout:

```sh
python neutrino-telescopes-2026/assets/galactic/render.py
python -m unittest discover -s neutrino-telescopes-2026/assets/galactic -p 'test_model.py'
```

`--stills --out /tmp/galactic/movie.mp4` exports teaching frames for inspection.
`--width 960 --fps 15 --out /tmp/galactic/movie.mp4` makes a smaller preview.
The default outputs are in `media/galactic/`: H.264 MP4 and a JPEG poster.

The first 32 seconds use a fixed camera. Gold paths illustrate deflection
of cosmic-ray protons. A flash marks a collision and the pion-decay chain
is compressed into that flash. Cyan paths illustrate the conditional subset
of neutrinos heading to the Solar System. Travel time is uniformly rescaled
per displayed path for readability. The particles are schematic and do not
represent event counts, a propagated cosmic-ray sample or a calculated flux.

The final sky strip is a numerical line-of-sight integral in Galactic
coordinates, longitude +180 to -180 degrees and latitude +30 to -30 degrees.
The observer is at (8.2, 0, 0) kpc. Zero longitude points towards the centre,
positive longitude towards +y. The gas density is an exponential disk with
a positive four-arm modulation. Cosmic-ray density is a radial exponential.
Emissivity is their product. Gas particles sample the gas density and collision
locations add the cosmic-ray weighting. The star cloud is a separate visual
context. All parameters are illustrative, with no fit to Galactic gas surveys.

Specific intensity is proportional to the integral of emissivity over path
length. No additional inverse-square factor belongs in this integral.
The sky uses a fixed asinh stretch in arbitrary relative intensity units.
It contains no energy dependence, telescope acceptance, angular smearing,
background or event-count prediction. The original IceCube figure appears
on a separate slide tab. Scientific sources and image credit:
`../../media/galactic/SOURCES.md`.
