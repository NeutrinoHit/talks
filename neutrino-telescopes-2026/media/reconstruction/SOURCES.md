# Reconstruction teaching film

`reconstruction_en.mp4`: 48 s, 1920×1080, 30 fps, silent, produced from
`dvnanima/neutrino_reconstruction/render.py` with its default TOML files.
`reconstruction_en.jpg`: static counterpart/poster at 38 s.

Original synthetic teaching material produced for DN's lecture. It is not an
experimental event display, recorded telescope data or a detector-resolution
prediction. All observations are actual sampled Poisson photoelectrons with
individual Gaussian-jittered times. Their illumination is schematic. The known
crossing point is fixed; only direction and global time offset are fitted.

The movie's full-sphere map and accepted refinement hypotheses are outputs of a
genuine conditional timing fit, independent of the generated truth. The phase
index defines the Cherenkov cone and the group index defines photon flight time.
Map colour is a relative fit score, not confidence. The muon-travel arrow points
opposite to a possible celestial source direction. The camera is fixed.

Reproducible model, equations, physical constants, assumptions and tests:
`dvnanima/neutrino_reconstruction/MODEL.md`, `physics.toml`, `test_model.py`.
Camera/layout/timing and all English copy/LaTeX artwork are external configuration.
No raw private simulation or detector-response arrays are included.

Source context (not a claim of reproducing their algorithms):

- [AMANDA muon reconstruction methods](https://arxiv.org/abs/astro-ph/0407044).
- [KM3NeT: KM3-230213A data analysis](https://www.km3net.org/km3-230213a/the-data-analysis/).
