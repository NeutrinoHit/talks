"""Directions of GVD210418CA, IceCube-170922A and TXS 0506+056, lecture style.

Redraw of Fig. 3 of Baikal-GVD, ICRC 2023, arXiv:2308.13686v1 (skymapTXS.png).

    python build_txs_directions.py /path/to/2308.13686v1   # unpacked arXiv source

- Baikal-GVD cascade: direction and the 50% / 90% containment radii are read at
  build time from the paper's text (by agreement, Baikal event coordinates are
  shown only graphically and are not stored in this repository).
- IceCube-170922A 90% contour: digitized from the original raster (Fig. 3) by
  radial scans from the best-fit marker; calibrated on the drawn grid lines.
  Stored in data/ic170922a-contour-digitized.csv.
- TXS 0506+056: catalogue position quoted in IceCube et al., Science 361 (2018).
"""
import csv
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE.parents[1] / "media/source-results"
TXS = (77.3582, 5.6931)                      # deg, J2000
CONTOUR = DATA / "ic170922a-contour-digitized.csv"


def gvd_event(tex):
    text = Path(tex).read_text()
    m = re.search(r"RA\$= ([\d.]+)\^\\circ\$ and DEC\$= \+?([-\d.]+)\^\\circ\$", text)
    r50 = float(re.search(r"50\\,\\% mismatch angle is \$([\d.]+)\^\\circ\$", text).group(1))
    r90 = float(re.search(r"for 90\\,\\% we found \$([\d.]+)\^\\circ\$", text).group(1))
    return float(m.group(1)), float(m.group(2)), r50, r90


def digitize_contour(png):
    """IceCube 90% contour from the original raster; grid lines: RA 88..74, Dec 2..14 deg."""
    import matplotlib.image as mpimg
    im = mpimg.imread(png)[..., :3] * 255
    ra = lambda x: 88 - (x - 166) / 52.55             # grid columns at 166 (88 deg) ... 901.5 (74 deg)
    dec = lambda y: 14 - (y - 10.5) / 52.75           # grid rows at 10.5 (14 deg) ... 643.5 (2 deg)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    green = (g > r + 50) & (g > b + 50)
    c = np.array([719.5, 446.5])                      # IceCube best-fit marker (pixels)
    pts = []
    for th in np.linspace(0, 2 * np.pi, 180, endpoint=False):
        left_marker = False                           # leave the filled star marker first,
        for rr in np.arange(11, 70, 0.5):             # (arms reach ~8 px; the contour is >= 14 px away),
                                                      # then take the first green pixel (the contour);
            x, y = int(round(c[0] + rr * np.cos(th))), int(round(c[1] - rr * np.sin(th)))
            if not green[y, x]:                       # the "90%" label lies outside the contour
                left_marker = True
            elif left_marker:
                pts.append((ra(x), dec(y)))
                break
    with CONTOUR.open("w", newline="") as stream:
        w = csv.writer(stream)
        w.writerow(["ra_deg", "dec_deg"])
        w.writerows([[f"{a:.3f}", f"{d:.3f}"] for a, d in pts])
    return np.array(pts)


def build(src):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(HERE))
    from build import figure, save, BLUE, ORANGE, FG, GRID, MUTED
    ra0, dec0, r50, r90 = gvd_event(Path(src) / "earxivTXS0506_icrc2023_nolines.tex")
    contour = digitize_contour(Path(src) / "skymapTXS.png")
    plt, fig, ax = figure((8.6, 7.6))
    t = np.linspace(0, 2 * np.pi, 361)
    for r, a in ((r90, 0.18), (r50, 0.28)):
        ax.fill(ra0 + r * np.cos(t), dec0 + r * np.sin(t), color=BLUE, alpha=a, lw=0)
        ax.plot(ra0 + r * np.cos(t), dec0 + r * np.sin(t), color=BLUE, lw=2)
    ax.text(ra0 + r50 * 0.62, dec0 - r50 * 0.86, "50%", color=BLUE, fontsize=15, rotation=-35)
    ax.text(ra0 + r90 * 0.6, dec0 - r90 * 0.9, "90%", color=BLUE, fontsize=15, rotation=-35)
    ax.plot(ra0, dec0, "*", ms=15, color=BLUE)
    ax.text(ra0, dec0 + 0.55, "Baikal-GVD cascade\n18 April 2021", color=BLUE, ha="center", fontsize=16)
    cc = np.vstack([contour, contour[:1]])
    ax.fill(cc[:, 0], cc[:, 1], color=ORANGE, alpha=0.3, lw=0)
    ax.plot(cc[:, 0], cc[:, 1], color=ORANGE, lw=2.2)
    ax.text(77.6, 6.6, "IceCube track\n22 Sept 2017 (90%)", color=ORANGE, ha="center", fontsize=15)
    ax.plot(*TXS, "o", ms=8, color=FG, mec="#000000", zorder=5)
    ax.annotate("TXS 0506+056", TXS, xytext=(76.3, 4.3), color=FG, fontsize=16,
                arrowprops={"arrowstyle": "-", "color": FG, "lw": 1})
    ax.set_xlim(89.5, 72.8); ax.set_ylim(0, 14.2)
    ax.set_aspect(1 / np.cos(np.deg2rad(dec0)))
    ax.set_xlabel("Right ascension [deg]"); ax.set_ylabel("Declination [deg]")
    ax.grid(color=GRID, lw=0.7, alpha=0.7)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.98, bottom=0.1)
    save(plt, fig, "txs-baikal-directions-dark")


if __name__ == "__main__":
    build(sys.argv[1])
