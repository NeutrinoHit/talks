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

## IceCube: recorded cascades

- The first tab reuses the existing credited Big Bird event image from
  `media/icecube/big-bird.jpg`; the IceCube tab shows `media/icecube/bert-ernie.png`.
  Their provenance remains in that folder. Every tab works offline; no online
  video is embedded.
- Credit: IceCube Collaboration / IceCube–NSF.

## DN's LightHit/NTSim-source demonstrations

- `simulated_muon_response_en.mp4` / `.jpg`: rendered frame by frame (WebCodecs H.264)
  by the LightHit WebGL event viewer ("studio", development version on top of
  LightHit commit 5fcaad8) from the same local viewer payload as before
  (`lighthit/.build/neutrino-telescope-recording/muon.json`, ready `ntsim3000-all`
  result): 17.5 s, 1920 × 1080 at 30 FPS, opening hold, detector-clock event with
  pacing where light arrives (the on-screen clock shows true detector time), closing
  orbit. The viewer draws the Cherenkov front for n = 1.34 travelling at c/n_g as an
  illustration. Poster: the last frame. The existing timed track source uses the detector
  clock. Source line is a straight display representation, not a measured
  reconstruction or a complete broken charged trajectory.
- `simulated_cascade_response_en.mp4` / `.jpg`: the existing 1 TeV electron event-5
  response in an illustrative three-cluster array, rendered by the same viewer from
  `lighthit/.build/neutrino-telescope-recording/cascade.json`: 17.5 s, 1920 × 1080 at
  30 FPS; the expanding light sphere is illustrative. Poster: the last frame. The older result had
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

## LightHit inside NTSim: neutrino-interaction models (current "Model" tabs, 14 October 2026)

- `lighthit_numu_cc_en.mp4` / `.jpg`: ν_μ CC-like event at one vertex, 800 GeV μ⁻ + 150 GeV π⁺ + 50 GeV p
  (1 TeV in total), `run_lighthit.py` hybrid route `lighthit.event` (orders 0, 1, ≥2), 5 Baikal-GVD clusters
  (1440 OMs, 30 active, threshold 0.01 pe). SHA-256 `e85f565b3d8ba0a886a99e03903e5466113b7f6cbb98fdfdaed9d31e4c61487d`.
- `lighthit_nue_cc_en.mp4` / `.jpg`: ν_e CC-like event, 70 GeV e⁻ + 25 GeV π⁺ + 5 GeV p (100 GeV), shower route,
  same array (26 active OMs). SHA-256 `1a6e48430a095808570f3f702e139a1f3cda1bc8c0d33e92f2d343b11526a23e`.
- Source: DN's notebook run `LightHit/.build/notebook-run/ntsim/lighthit-demo-output/{numu-cc,nue-cc}`
  (LightHit 0.3.0a3, NTSim/Geant4 11.4.1; inputs and viewers stay in LightHit's ignored `.build`).
- Rendered frame by frame by the viewer's own Movie export (WebCodecs H.264): 1920 × 1080, 30 FPS, 17.5 s
  (1.5 s hold, 12 s event with pacing on light, 4 s orbit), light component Total, colour = first-light time,
  on-screen detector clock, colour scale, scale bar and the viewer's honesty note. Only title and subtitle were typed.
  Re-encoded with ffmpeg (libx264, CRF 20, faststart), no other change; poster = last frame.
- Russian versions (`neutrino-telescopes-ru-2026/media/films/lighthit_{numu,nue}_cc_ru.*`) come from a local copy of
  the same viewer with the eight on-screen overlay strings translated; data, camera and settings identical.
- The glow is the expected photoelectron response, not Poisson-sampled hits or observed data; the light front is illustrative.
- The previous `simulated_muon_response_en.*` and `simulated_cascade_response_en.*` remain in this folder (documented above)
  but are no longer referenced by the slides.
