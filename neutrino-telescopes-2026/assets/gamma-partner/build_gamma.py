"""Diffuse Galactic-plane gamma rays above 10 TeV: LHAASO-KM2A and Tibet ASgamma.

LHAASO points are transcribed from Tables S2 and S3 of arXiv:2305.05372v2
(PRL 131, 151001). Tibet points are digitized from the vector paths of Fig. 4
of arXiv:2104.05181v2 (PRL 126, 141101) by digitize_tibet.py. Both are drawn
as E^2.7 dN/dE in GeV^1.7 cm^-2 s^-1 sr^-1, the convention of the Tibet figure
and the LHAASO spectral figure. No fit, model curve or neutrino conversion.
"""
from pathlib import Path
import csv
import numpy as np

HERE = Path(__file__).resolve().parent
LHAASO = HERE / "data/lhaaso-km2a-diffuse-2305.05372v2.csv"
TIBET = HERE / "data/tibet-asgamma-fig4-2104.05181v2.csv"
OUT = HERE.parents[1] / "media/galactic"
INDEX = 2.7
TEV_TO_GEV = 1e3


def e27_gev(e_tev, flux_per_tev):
    """E^2.7 dN/dE with E in GeV and dN/dE per GeV."""
    return (e_tev * TEV_TO_GEV) ** INDEX * flux_per_tev / TEV_TO_GEV


def lhaaso_points():
    rows = []
    with LHAASO.open() as stream:
        for r in csv.DictReader(stream):
            e = float(r["mean_e_tev"])
            phi = float(r["flux_per_tev_cm2_s_sr"])
            up, down, sys = (float(r[k]) for k in ("stat_plus", "stat_minus", "sys"))
            rows.append({
                "region": r["region"], "e_tev": e, "y": e27_gev(e, phi),
                "stat": (e27_gev(e, phi - down), e27_gev(e, phi + up)),
                "total": (e27_gev(e, phi - np.hypot(down, sys)), e27_gev(e, phi + np.hypot(up, sys))),
            })
    return rows


def tibet_points():
    with TIBET.open() as stream:
        return [{k: (v if k in ("panel", "region") else float(v)) for k, v in r.items()}
                for r in csv.DictReader(stream)]


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 19, "text.color": "#eeeeee", "axes.labelcolor": "#eeeeee",
                         "xtick.color": "#eeeeee", "ytick.color": "#eeeeee", "svg.fonttype": "path",
                         "mathtext.fontset": "stix"})
    orange, violet = "#ffbd70", "#ca9cff"
    fig, ax = plt.subplots(figsize=(10.5, 6.6), facecolor="#000000")
    ax.set_facecolor("#000000")
    lh = lhaaso_points()
    for region, filled, label in (("inner", True, "LHAASO, inner Galaxy"),
                                  ("outer", False, "LHAASO, outer Galaxy")):
        pts = [p for p in lh if p["region"] == region]
        e = np.array([p["e_tev"] for p in pts]); y = np.array([p["y"] for p in pts])
        tot = np.array([[p["y"] - p["total"][0] for p in pts], [p["total"][1] - p["y"] for p in pts]])
        stat = np.array([[p["y"] - p["stat"][0] for p in pts], [p["stat"][1] - p["y"] for p in pts]])
        ax.errorbar(e, y, yerr=tot, fmt="none", ecolor=orange, elinewidth=1.0, alpha=0.55, capsize=0)
        ax.errorbar(e, y, yerr=stat, fmt="o", ms=9, color=orange, mfc=orange if filled else "#000000",
                    mew=2, elinewidth=2.4, capsize=0, label=label)
    tb = tibet_points()
    for panel, filled, label in (("a", True, r"Tibet AS$\gamma$, inner region"),
                                 ("b", False, r"Tibet AS$\gamma$, outer region")):
        pts = [p for p in tb if p["panel"] == panel]
        e = np.array([p["e_tev"] for p in pts]); y = np.array([p["e27_flux"] for p in pts])
        xerr = np.array([e - [p["e_min_tev"] for p in pts], [p["e_max_tev"] for p in pts] - e])
        yerr = np.array([y - [p["e27_flux_low"] for p in pts], [p["e27_flux_high"] for p in pts] - y])
        ax.errorbar(e * (1.0 if filled else 1.04), y, xerr=xerr, yerr=yerr, fmt="s", ms=9, color=violet,
                    mfc=violet if filled else "#000000", mew=2, elinewidth=1.6, capsize=0, label=label)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8, 1300); ax.set_ylim(6e-6, 5e-4)
    ax.set_xlabel(r"Gamma-ray energy $E$ [TeV]")
    ax.set_ylabel(r"$E^{2.7}\,dN/dE$  [GeV$^{1.7}$ cm$^{-2}$ s$^{-1}$ sr$^{-1}$]")
    ax.grid(color="#344250", lw=0.7, alpha=0.7, which="major")
    for spine in ax.spines.values():
        spine.set_color("#344250")
    ax.legend(loc="upper left", frameon=False, fontsize=15.5, handletextpad=0.4, labelspacing=0.35)
    fig.subplots_adjust(left=.14, bottom=.14, top=.97, right=.97)
    fig.savefig(OUT / "galactic-gamma-diffuse.svg")
    fig.savefig(OUT / "galactic-gamma-diffuse.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    build()
