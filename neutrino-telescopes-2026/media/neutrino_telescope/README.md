# Charged tracks and Cherenkov photon production

Exported from `dvnanima/neutrino_telescope` for slide 8. English, no visible
credits, framework names or QR codes. Formula artwork is LaTeX; all values,
layouts and inputs are configured in the source animation folder.

- `muon_lecture_en.mp4`: 1280 × 720, 60 FPS, 20 s.
- `electron_lecture_en.mp4`: 1280 × 720, 60 FPS, 20 s.

Portrait exports remain in the source animation's media directory for YouTube;
they are not embedded or shipped as lecture resources.

Each independent event occupies 10 seconds. Muons: 1 TeV and 1 PeV.
Electrons: 100 GeV and 1 TeV; no genuine electron PeV input yet.
The two new PeV files both contain muon primaries. No substituted event
or scaled lower-energy shower is used.

Charged trajectories are existing NTSim/Geant4 data supplied by DN.
Photon births follow the nondispersive resolved-segment Frank–Tamm model,
index 1.34, band 350–610 nm. Markers are a weighted sample of 9000 births,
not every photon. They stay at their birth coordinates. There is no photon
transport, scattering, absorption, detector geometry or hit simulation.

The growing graph shows expected photons per physical time–cosine bin,
estimated by the weighted birth sample; cosine is relative to the initial
primary direction. Its explicit logarithmic colour scale is event-specific.
The 96 × 120 bins use bilinear colour interpolation for display only; the
final bin sum equals the integrated model source yield. Spatial windows
and bins vary by event. The landscape muon view is fixed: its original
longitudinal scale is preserved and only the perpendicular coordinate is
expanded to a 2 m-high window. Separate axis bars make this unequal aspect
ratio explicit. There is no camera tracking, panning or animated zoom.
The graph remains a complete-event distribution, including births outside
the transverse crop; the electron film is unchanged. Some
rare outliers fall outside the quantile-fitted viewport. Source trajectories
are retained representative real vertices, not an exhaustive particle display.

The low-energy muon recordings end at 100 m; the PeV water window is 10 km.
Neither a recording boundary nor the end of an animation means the particle
has stopped. Portrait and landscape exports use identical source samples.
Posters are extracted from the corresponding finished films. Raw HDF5 files
remain local and are not needed to play these public exports.
