# Event displays and recorded viewer demonstrations

## KM3NeT: measured track

- `km3-230213a.mp4` / `.jpg`: official style-1 event display of KM3-230213A,
  recorded by ARCA on 13 February 2023. Original movie retained, approximately
  30 s, 960 × 544. Poster extracted at 10 s.
- [Official event-display page](https://www.km3net.org/km3-230213a/displays-of-the-event/).
- Original: <https://www.km3net.org/wp-content/uploads/2025/02/a2271402-78f7-44ce-8098-1c5ac6c7de27.mp4>.
- Credit: © KM3NeT Collaboration. Follow its
  [media-use policy](https://www.km3net.org/pictures-and-videos/copyright/).
- Red line: reconstructed muon trajectory. PMT markers: recorded signals,
  with relative hit time encoded in colour and detected light in size.
  The cone is an artistic illustration, not a measured photon trajectory.

## IceCube: recorded cascades and online compilation

- The first tab reuses the existing credited Big Bird event image from
  `media/icecube/big-bird.jpg`; its provenance remains in that folder.
- [Official research highlights](https://icecube.wisc.edu/science/research/)
  links the [event compilation](https://www.youtube.com/watch?v=2DDQYHIbL3Q),
  embedded in the IceCube tab. It contains recorded high-energy events and
  one simulated event with a Cherenkov cone. Do not describe every frame as
  measured data. The embed requires Internet; the local images and other
  movie tabs do not. No YouTube download or restriction bypass was used.
- Credit: IceCube Collaboration / IceCube–NSF.

## DN's LightHit/NTSim-source demonstrations

- `simulated_muon_response_en.mp4` / `.jpg`: actual browser-canvas recording
  from the ready `ntsim3000-all` viewer result. Approximately 15 s, encoded
  1280 × 720 at 30 FPS. The existing timed track source uses the detector
  clock. Source line is a straight display representation, not a measured
  reconstruction or a complete broken charged trajectory.
- `simulated_cascade_response_en.mp4` / `.jpg`: actual recording of the
  existing 1 TeV electron event-5 response in an illustrative three-cluster
  array, approximately 15 s, same output dimensions. The older result had
  no source timing block. The exact recorded G4 event and stored rigid pose
  were recovered; element count, source-contract photon yield and centroid
  were verified against the result. The existing package axial timing fit
  then supplied display-only source timing, enabling a detector-clock replay
  without recalculating or altering any OM bins, charges or reference times.
  The source head is a fitted axial illustration, not a detailed trajectory
  integration or an observed event reconstruction.
- Both recordings select the unscattered/direct-light component and
  cumulative mode. Those input bins were checked to be nonnegative. Stored
  spectra, other signed components, source coordinates and array values
  were not clipped, rescaled or replaced. Only display labels and the
  verified display-only source-clock metadata were adapted.
- Marker size is a display-scaled calculated mean photoelectron response,
  not Poisson-sampled PMT hits or observed Baikal-GVD data. The two detector
  configurations are not a matched geometry/energy comparison.
- The camera is fixed; detector framing and 10% view padding were selected
  through the viewer UI. Clipping the display axis at the frame boundary
  does not stop the physical source.
- Only captured movies and poster frames are public assets. Input result
  arrays, private model/calibration outputs and local recordable HTML/JSON
  stay under LightHit's ignored `.build/` directory, never under this site.
  Local provenance records retain source SHA256 checksums.
- Refresh recipe: `assets/prepare_recordable_viewers.py` and
  `assets/viewer_recording.toml`. Local-only saving server:
  `assets/serve_recordable_viewers.py`. Movie encoding:
  `assets/encode_viewer_movie.py` and `assets/event_movie_layout.toml`.
  The encoding keeps the scene aspect ratio, adds honest clock/component
  labels, and does not perform transport or invent interpolated physics.
- Viewer capture tests: native H.264 smoke clip, 2.017 s, 46 evolving,
  nonblank frames; production clips decoded completely and showed changing
  frames. Source Python viewer generator and its pre-existing tests were
  verified unchanged by SHA256. Posters extracted at 7.5 s.

## DN archive material inspected but not presented as observed data

The 2021 Keynote contains beautiful Baikal-GVD explanatory 3D clips of an
exploded OM, electronics, string arrangement and detection. Those are
illustrations, not demonstrated measured event displays. They have not been
added as a substitute for real events in slide 11. Original Keynotes were
not modified; temporary inspection copies remain outside the public site.
