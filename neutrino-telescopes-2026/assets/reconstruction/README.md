# Slide 12: reconstructing a hidden track

The slide presents the explanatory movie first, then this exercise, then the
equations and assumptions. The default public event is exactly the synthetic
event generated for `dvnanima/neutrino_reconstruction` with its default settings.
No private detector responses, experimental events or calibration data are read.

## Rebuild and test

From `talks`, using the configured Python and installed Node:

```sh
python neutrino-telescopes-2026/assets/reconstruction/export_assets.py
python -m unittest discover -s neutrino-telescopes-2026/assets/reconstruction -p test_parity.py
python -m unittest discover -s neutrino-telescopes-2026/assets/reconstruction -p test_controls.py
node --check neutrino-telescopes-2026/assets/reconstruction/interactive.js
```

`ui.toml`, `model.js`, `interactive.js`, and `export_assets.py` are authored
sources. `interactive.html` and `data.json` are intentionally shipped generated
assets, rebuilt by the exporter. Include the HTML fragment from the QMD; its
scripts and input JSON are relative to the rendered lecture. The public bundle
contains physical settings, the synthetic observation, browser preferences,
theme and colour tables. No sibling repository is required by the published
exercise. Source regeneration and parity tests use the sibling animation model.

## Controls

- Trial polar/azimuth sliders and a click on the likelihood panel select a
  hypothesis. The measured sensor pattern never moves.
- **Fit** performs a real full-sphere grid search with multiple refinements,
  profiles the global time offset, and replays actual accepted hypotheses.
  The fitter does not read `truth` or a precomputed Python fit result.
- **Reveal truth** displays the separately generated direction. The angular
  separation is a comparison for this toy event, not experimental resolution.
- Expected photoelectrons and timing jitter apply to the **next New event**.
  Each event contains actual sampled Poisson counts and individual Gaussian
  hit times, not mean responses presented as detections.
- Assumed group index changes the fitting medium, **not** the observed times
  or the medium that generated them. Wrong assumptions can bias a fit and
  increase its score.
- **Reset** restores the exact movie event and correct medium.

Filled circles encode observed mean hit time; size is a pictorial count scale.
Rings encode predicted times. Histogram height counts individual photoelectrons
per bin. Its count scale is anchored to the event/model's best-fit histogram
with a configured minimum; it stays fixed while a trial direction changes.
Any bars exceeding that count scale are explicitly counted, not silently
clipped. The horizontal timing window also stays fixed, with explicit overflow.
The angular panel is a relative
likelihood landscape, **not calibrated confidence**. Phase index controls the
Cherenkov angle and group index controls photon travel time. A known crossing
point is held fixed; only direction and time offset are reconstructed. The arrow
follows the muon's travel; celestial source direction is opposite.

See `dvnanima/neutrino_reconstruction/MODEL.md` for the equations, assumptions,
provenance and Python tests. Browser and Python likelihood/predictions agree
numerically; the two deterministic optimizers are different but agree at the
minimum. NumPy and browser PRNGs are different; browser events reproduce within
the browser, while the initial event is exported from Python exactly.

All preferences/copy/formulas are external TOML. Mathematical controls, plot
labels and result readouts use the lecture's MathJax engine; ordinary numeric
ticks are canvas text. No lecture-specific CSS classes or stylesheet is added.
Native ranges inherit the larger control font, reserve fixed label widths and
coalesce input redraws into one update per display frame. Dynamic formulas are
typeset off-screen, then swapped atomically; raw TeX never changes the slider
layout. Pointer/touch events on ranges do not trigger Reveal navigation.
`test_controls.py` checks fixed geometry and non-destructive math enqueueing;
real mouse drags and the unchanged numerical fit are also checked in the browser.
The installed Reveal template requires a MathJax 2 engine URL; the scoped
lecture metadata matches it. The interactive also supports MathJax 3 if the
presentation's loader is later migrated coherently.
