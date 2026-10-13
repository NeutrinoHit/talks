# Global observatory geometry

`build_figures.py` produces the map and below-horizon fraction on the
`global-observatories` slide.
Site coordinates, labels and plot styling are in `config.toml`.

```sh
MPLCONFIGDIR=/private/tmp/neutrino-global-sky-mpl pyenv exec python neutrino-telescopes-2026/assets/global-sky/build_figures.py
pyenv exec python -m unittest discover -s neutrino-telescopes-2026/assets/global-sky -p 'test_*.py'
```

NumPy and Matplotlib are available in the configured NeutrinoHit environment.
Outputs: SVG and PNG in `media/source-results/`.

## Model

The zenith cosine is sin(phi)sin(delta)+cos(phi)cos(delta)cos(H).
The below-horizon fraction integrates cos(zenith)<0 over one full sidereal
rotation. This is geometry, not event rate, effective area or sensitivity.
No energy weighting, attenuation, veto, reconstruction cuts or detector-depth
horizon shift is included. IceCube also accesses southern directions using
starting and contained event selections.

Five tests cover pole/equator behaviour, complementary declinations, direct
sampling of Earth rotation and the Galactic Centre values. The fraction for
a source exactly on the horizon at a polar site is represented by 0.5 as the
symmetry convention; that measure-zero case is not connected by a spurious
vertical line in the IceCube curve.

## Coordinates and map

- IceCube: South Pole; longitude immaterial at the pole.
- ARCA: 36.27°N,16.10°E; ORCA:42.80°N,6.03°E.
  [KM3NeT design](https://arxiv.org/abs/1601.07459).
- Baikal-GVD:51°46′N,104°24′E, the actual detector site, not the centre of
  Lake Baikal. [Collaboration site record](https://indico.cern.ch/event/378423/contributions/900413/attachments/1155595/1660951/3_zhan_Baikal_VLVnT_status.pdf).
- P-ONE:47.74°N,127.73°W represents the Cascadia region of ONC infrastructure,
  not an exact final-array layout. [ONC update](https://www.oceannetworks.ca/news-and-stories/stories/onc-coengineers-key-infrastructure-for-pacific-deep-sea-neutrino-telescope/).
- TRIDENT:17.4°N,114.0°E, published design location.
  [Design paper](https://doi.org/10.1038/s41550-023-02087-6).

Open symbols identify next-generation projects; filled symbols operating
arrays. They do not indicate equal volume, exposure or funding milestones.
HUNT/B-HUNT and NEON are discussed on later project slides rather than assigned
invented fixed sites or counted twice.

Land geometry: unmodified `ne_110m_land.geojson` from the
[Natural Earth vector repository](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson),
retrieved 12 October 2026. [Public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/).
The coastlines are approximate at 1:110million scale. Vertex projection avoids
unnecessary path densification; it does not change telescope coordinates.
