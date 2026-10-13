"""Lecture-style (dark) redraws of the two effective-area figures from data/*.csv.

Same quantities, binning and axis ranges as the originals; only colours and typography change.
Inputs come from digitize_effective_areas.py. Outputs: media/response/*-dark.svg and .png.
"""
from pathlib import Path
import csv
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE.parents[1] / "media/response"
C = {"fg": "#eeeeee", "muted": "#a0b5ca", "grid": "#344250", "bg": "#000000",
     "gold": "#ffd477", "cyan": "#67ddf7", "lavender": "#aa9bef"}


def _style(plt):
    plt.rcParams.update({"font.size": 18, "text.color": C["fg"], "axes.labelcolor": C["fg"], "xtick.color": C["fg"],
                         "ytick.color": C["fg"], "svg.fonttype": "path", "mathtext.fontset": "stix"})


def _frame(ax):
    ax.set_facecolor(C["bg"])
    ax.grid(which="major", color=C["grid"], lw=0.7, alpha=0.7)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_color(C["grid"])


def spiering_curves():
    curves = {}
    with (DATA / "spiering2026-fig6-digitized.csv").open() as f:
        for row in csv.DictReader(f):
            curves.setdefault(row["zenith_band_deg"], []).append((float(row["log10_E_GeV"]), float(row["log10_A_eff_m2"])))
    return {k: np.array(v).T for k, v in curves.items()}


def hese_steps():
    steps = {}
    with (DATA / "hese2013-effective-area-digitized.csv").open() as f:
        for row in csv.DictReader(f):
            steps.setdefault(row["flavour"], []).append(
                (float(row["log10_E_lo_TeV"]), float(row["log10_E_hi_TeV"]), float(row["A_eff_m2"])))
    return steps


def directional_area():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _style(plt)
    fig, ax = plt.subplots(figsize=(8.4, 6.8), facecolor=C["bg"])
    _frame(ax)
    styles = {"90-120": (C["gold"], r"$90^\circ<\theta<120^\circ$", "just below horizon", (3.05, 3.55)),
              "150-180": (C["cyan"], r"$150^\circ<\theta<180^\circ$", "upward", (6.75, 1.0)),
              "0-30": (C["lavender"], r"$0^\circ<\theta<30^\circ$", "downward", (5.05, -1.95))}
    for key, (x, y) in spiering_curves().items():
        colour, band, words, (tx, ty) = styles[key]
        ax.plot(10**x, 10**y, color=colour, lw=3.2)
        ax.text(10**tx, 10**ty, band, color=colour, fontsize=21, ha="left")
        ax.text(10**(tx + 0.25), 10**(ty - 0.42), f"({words})", color=colour, fontsize=17, ha="left")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1e2, 1e9); ax.set_ylim(1e-3, 1e4)
    ax.set_xticks([1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9])
    ax.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 1e2, 1e3, 1e4])
    ax.set_xlabel(r"Neutrino energy $E_\nu$ [GeV]")
    ax.set_ylabel(r"Effective area [m$^2$]")
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.13)
    fig.savefig(OUT / "icecube-directional-area-dark.svg", facecolor=C["bg"])
    fig.savefig(OUT / "icecube-directional-area-dark.png", dpi=120, facecolor=C["bg"])
    plt.close(fig)


def hese_area():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _style(plt)
    fig, ax = plt.subplots(figsize=(11, 6.3), facecolor=C["bg"])
    _frame(ax)
    styles = {"nu_e": (C["gold"], r"$\nu_e$"), "nu_mu": (C["cyan"], r"$\nu_\mu$"), "nu_tau": (C["lavender"], r"$\nu_\tau$")}
    for flavour, rows in hese_steps().items():
        colour, label = styles[flavour]
        edges = [10**rows[0][0]] + [10**r[1] for r in rows]
        values = [r[2] for r in rows]
        ax.stairs(values, edges, color=colour, lw=2.6, label=label, baseline=None)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(10, 1e4); ax.set_ylim(1e-3, 10**3.3)
    ax.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 1e2, 1e3])
    ax.set_xlabel("Neutrino energy [TeV]")
    ax.set_ylabel(r"Neutrino effective area [m$^2$]")
    ax.text(13, 10**2.75, r"$4\pi$ / all-sky", color=C["muted"], fontsize=19)
    ax.annotate("Glashow resonance", xy=(6.3e3, 600), xytext=(1.1e3, 900), color=C["gold"], fontsize=16,
                ha="right", va="center", arrowprops={"arrowstyle": "-", "color": C["gold"], "lw": 1})
    ax.legend(loc="lower right", frameon=False, labelcolor="linecolor", fontsize=22)
    fig.subplots_adjust(left=0.11, right=0.975, top=0.97, bottom=0.13)
    fig.savefig(OUT / "icecube-hese-2013-effective-area-dark.svg", facecolor=C["bg"])
    fig.savefig(OUT / "icecube-hese-2013-effective-area-dark.png", dpi=120, facecolor=C["bg"])
    plt.close(fig)


if __name__ == "__main__":
    directional_area()
    hese_area()
