"""KM3-230213A: from light to energy, drawn from the numbers published in the text of
Aiello et al. (KM3NeT), Nature 638 (2025) 376 — not from its figures (CC BY-NC-ND).

Muon energy at the detector: 120 (+110, -60) PeV (68 %), 35-380 PeV (90 %).
Parent neutrino, assuming an E^-2 spectrum: median 220 PeV, 110-790 PeV (68 %), 72 PeV-2.6 EeV (90 %).
Triggered PMTs: 3672, about 35 % of the active PMTs.
"""
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[2] / "media" / "source-results"
ROWS = [  # label, sub-label, central, 68 %, 90 %, colour
    ("Muon at the detector", "measured from the light: 3672 PMTs fired", 120.0, (60.0, 230.0), (35.0, 380.0), "#59dcff"),
    ("Parent neutrino", r"inferred, assuming $\Phi_\nu\propto E^{-2}$", 220.0, (110.0, 790.0), (72.0, 2600.0), "#ffd166"),
]
BG, FG, GRID, DIM = "#000000", "#eeeeee", "#344250", "#9fb0c8"


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 17, "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG,
                         "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig = plt.figure(figsize=(11.5, 5.6), facecolor=BG)
    ax = fig.add_axes([0.05, 0.17, 0.90, 0.78], facecolor=BG)
    ax.set_xscale("log")
    ax.set_xlim(10, 5000)
    ax.set_ylim(-0.6, 2.25)
    ax.set_yticks([])
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="x", which="major", color=GRID, lw=0.8)
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(["10 PeV", "100 PeV", "1 EeV"])
    ax.set_xlabel("Energy")
    ys = [1.45, 0.25]
    for (lab, sub, c, s68, s90, col), y in zip(ROWS, ys):
        ax.plot(s90, [y, y], color=col, lw=2.0, alpha=0.8)
        for x in s90:
            ax.plot([x, x], [y - 0.09, y + 0.09], color=col, lw=2.0, alpha=0.8)
        ax.add_patch(plt.Rectangle((s68[0], y - 0.17), s68[1] - s68[0], 0.34, fc=col, alpha=0.35, ec=col, lw=1.5))
        ax.plot([c], [y], "o", ms=11, color=col, mec=BG, mew=1.5, zorder=5)
        ax.text(11.5, y + 0.58, lab, color=col, fontsize=19, fontweight="bold", va="bottom")
        ax.text(11.5, y + 0.47, sub, color=DIM, fontsize=15, va="top")
    ax.annotate("", xy=(220, ys[1] + 0.22), xytext=(120, ys[0] - 0.22),
                arrowprops=dict(arrowstyle="-|>", color=FG, lw=1.4, alpha=0.8))
    ax.text(430, 0.86, "the neutrino gave only part of its energy\nto the muon, which also lost energy\nbefore it reached the detector",
            color=DIM, fontsize=13.5, va="center", ha="left")
    ax.text(4800, -0.45, "box: 68 %   ·   whiskers: 90 %", color=DIM, fontsize=13.5, ha="right")
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"km3-energy-intervals-dark.{ext}", facecolor=BG, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plot()
