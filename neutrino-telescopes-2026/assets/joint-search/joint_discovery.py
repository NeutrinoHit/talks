"""ANTARES + IceCube joint southern-sky search: 5-sigma discovery flux for an E^-2 spectrum.

digitize(): reads the Poppler vector conversion of DiscoveryX20.pdf (ANTARES & IceCube,
ApJ 892, 92 (2020), arXiv:2001.04412, Fig. 2 left), media/source-results/joint-discovery-flux.svg,
and writes data/joint-discovery-flux-e2-digitized.csv. The three curves are polylines with
9 vertices each; x is calibrated on the frame (sin dec = -1 ... 0), y on the dotted ROOT grid:
the lines that follow the smallest gaps (9 -> 10) are the decades 1e-9, 1e-8, 1e-7.
build(): lecture-style redraw to media/joint-search/.
"""
from pathlib import Path
import csv
import re
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_SVG = ROOT / "media/source-results/joint-discovery-flux.svg"
DATA = HERE / "data/joint-discovery-flux-e2-digitized.csv"
OUT = ROOT / "media/joint-search"
SERIES = {"rgb(0%, 0%, 100%)": "IceCube 7 years", "rgb(100%, 0%, 0%)": "ANTARES 9 years",
          "rgb(0%, 39.99939%, 0%)": "IceCube+ANTARES"}


def _paths(svg):
    for m in re.finditer(r'<path ([^>]*?)d="([^"]*)"([^>]*)/>', svg):
        attrs = m.group(1) + m.group(3)
        n = np.array(list(map(float, re.findall(r"-?\d+\.?\d*", m.group(2)))))
        yield attrs, n[0::2], n[1::2]


def calibration(svg):
    frame = [(x, y) for a, x, y in _paths(svg)
             if 'stroke-width="0.75"' in a and "rgb(0%, 0%, 0%)" in a and "dasharray" not in a and len(x) == 5]
    x_left, x_right = frame[0][0].min(), frame[0][0].max()
    rows = sorted({round(float(y[0]), 4) for a, x, y in _paths(svg)
                   if 'stroke-dasharray="1 2"' in a and 'stroke-width="0.75"' in a and len(y) == 2 and abs(y[0] - y[1]) < 1e-6})
    gaps = np.diff(rows)
    decades = [rows[i + 1] for i in range(len(gaps)) if gaps[i] < 0.06 * (rows[-1] - rows[0]) / 3
               and (i + 1 == len(gaps) or gaps[i + 1] > 2 * gaps[i])]
    if len(decades) != 3:
        raise ValueError(f"expected three decade grid lines, found {decades}")
    k = np.polyfit([-9, -8, -7], decades, 1)
    return (x_left, x_right), k, decades


def digitize(svg_path=SOURCE_SVG):
    svg = Path(svg_path).read_text()
    (x_left, x_right), k, _ = calibration(svg)
    out = {}
    for a, x, y in _paths(svg):
        colour = re.search(r'stroke="([^"]*)"', a)
        if colour and colour.group(1) in SERIES and 'stroke-width="3"' in a and len(x) > 2:
            sin_dec = -1 + (x - x_left) / (x_right - x_left)
            out[SERIES[colour.group(1)]] = (sin_dec, 10 ** ((y - k[1]) / k[0]))
    return out


def write_data():
    DATA.parent.mkdir(exist_ok=True)
    with DATA.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["series", "sin_dec", "dec_deg", "E2_Phi0_5sigma_GeV_cm2_s"])
        for name, (s, v) in digitize().items():
            for si, vi in zip(s, v):
                w.writerow([name, f"{si:.4f}", f"{np.degrees(np.arcsin(si)):.2f}", f"{vi:.4g}"])


def read_data():
    series = {}
    with DATA.open() as f:
        for r in csv.DictReader(f):
            series.setdefault(r["series"], []).append((float(r["sin_dec"]), float(r["E2_Phi0_5sigma_GeV_cm2_s"])))
    return {k: np.array(v).T for k, v in series.items()}


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 18, "text.color": "#eeeeee", "axes.labelcolor": "#eeeeee",
                         "xtick.color": "#eeeeee", "ytick.color": "#eeeeee", "svg.fonttype": "path",
                         "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=(10.5, 6.6), facecolor="#000000")
    ax.set_facecolor("#000000")
    styles = {"IceCube 7 years": ("#73c7ff", (0, (1.2, 1.6)), 3.0),
              "ANTARES 9 years": ("#aa9bef", (0, (4, 3)), 3.0),
              "IceCube+ANTARES": ("#ffd477", "-", 4.0)}
    data = read_data()
    for name in ("IceCube 7 years", "ANTARES 9 years", "IceCube+ANTARES"):
        s, v = data[name]
        colour, ls, lw = styles[name]
        ax.plot(s, v, color=colour, ls=ls, lw=lw, label=name)
    ax.set_yscale("log")
    ax.set_xlim(-1, 0); ax.set_ylim(10**-9.301, 10**-6.301)
    ax.set_yticks([1e-9, 1e-8, 1e-7])
    ax.set_xlabel(r"Source declination $\sin\delta$")
    ax.set_ylabel(r"$E_\nu^2\,\Phi_0^{5\sigma}$ [GeV cm$^{-2}$ s$^{-1}$]")
    ax.set_title(r"$5\sigma$ discovery flux for $\gamma=2.0$", color="#eeeeee", fontsize=19)
    ax.grid(which="major", color="#344250", lw=0.7, alpha=0.7)
    ax.tick_params(which="minor", length=0)
    for sp in ax.spines.values():
        sp.set_color("#344250")
    ax.legend(loc="upper right", frameon=False, labelcolor="linecolor", fontsize=18, handlelength=3)
    fig.subplots_adjust(left=0.15, right=0.975, top=0.91, bottom=0.13)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "joint-discovery-flux-dark.svg", facecolor="#000000")
    fig.savefig(OUT / "joint-discovery-flux-dark.png", dpi=120, facecolor="#000000")
    plt.close(fig)


if __name__ == "__main__":
    if "--digitize" in sys.argv:
        write_data()
    build()
