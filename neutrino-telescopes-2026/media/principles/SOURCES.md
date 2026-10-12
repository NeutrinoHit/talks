# Detection-principle animations

- `cherenkov_steps_en.mp4`: simplified lecture version for DN from
  `dvnanima/cherenkov_radiation/media/cherenkov_radiation_en.mp4`, 40 s,
  1920x1080, 30 fps, silent. Four geometrical wavefronts; two separate
  constant-speed trials; paused common-tangent construction; normal light
  directions. No graph or detector ring. The physical clock freezes together
  with the charge during teaching pauses; a short fade separates the trials.
  Source/parameters/texts: `cherenkov_radiation.py`, `config.toml`, `texts.toml`.
  Phase index 1.33, beta=0.55/0.99; photon direction 40.6 degrees in the fast
  example, rounded to about 41 degrees. No photon yield or interference
  amplitude is computed. Poster extracted at 36 s. Geometry and both-language
  text layout checked with `test_cherenkov_radiation.py`.
  Carries the standard small dvnanima footer. The previous angle/ring movie
  and its lecture poster have been removed; published gallery and printed
  QR addresses reuse the same stable asset URLs for the replacement.
- `pmt_multiplication_en.mp4`: DN's existing English animation from
  `dvnanima/pmt_multiplication/media/pmt_multiplication_en.mp4`, 40 s.
  Copied without editing. Stochastic dynode branching and anode pulses;
  a teaching model, not a detector-specific gain calibration.
  Poster extracted at 12 s.

## Slide 9: explanatory vector diagrams

`cherenkov-slow-fast.svg` and `cherenkov-light-direction.svg` are original
lecture-local diagrams for DN's talk. They illustrate the animation's Huygens
geometry, not measured data, simulated photon yield or an interference field.
English labels are deliberately limited to positions, the common front and
the light direction; equations remain LaTeX in the slide.

The comparison uses the film's constant phase index 1.33 and constant particle
speeds beta=0.55/0.99. Both panels use the same four wavelet ages, hence identical
radii. The slow panel has nested fronts; the fast panel has two common tangent
lines, not lines through circle intersections. Small gold dots mark earlier
particle positions; the large dot is the present position.
The angle diagram uses the beta=1 limit, with light normal to the tangent and
an emission angle of 41.2465 degrees. Geometry is non-dispersive and schematic.
For the physical phase-velocity condition and angle:
[PDG, passage of particles through matter, Cherenkov radiation](https://pdg.lbl.gov/2012/reviews/rpp2012-rev-passage-particles-matter.pdf).

The source animations' README/config/texts describe their physics and
configuration. The PMT copy remains unchanged; the four-step Cherenkov movie
is used on slide 9 and replaces the earlier movie in the site gallery.
