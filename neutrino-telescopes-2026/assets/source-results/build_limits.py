"""Baikal-GVD E^-2 limits from published Table 1; no new fit or sensitivity."""
from pathlib import Path
import re
import csv
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data/baikal-source-list-2603.21261v2.tex"
OUT = HERE.parents[1] / "media/source-results"
TABLE_SCALE = 1e-8  # Table 1: cm^-2 s^-1 GeV^-1 at E0=1 GeV, gamma=2.


def source_limits():
    result = []
    for line in DATA.read_text().splitlines():
        fields = [x.strip() for x in line.split("&")]
        if len(fields) != 8 or fields[0] == "Name":
            continue
        name = fields[0].replace(r"{\bf ", "").replace("}", "")
        number = lambda x: float(re.search(r"[-+]?\d+(?:\.\d+)?", x).group(0))
        result.append((name, number(fields[1]), number(fields[5]) * TABLE_SCALE))
    if len(result) != 92:
        raise ValueError(f"Expected 92 source rows, got {len(result)}")
    return result


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import LogFormatterMathtext
    rows = source_limits()
    x = np.sin(np.deg2rad([row[1] for row in rows]))
    # For E^-2, this table normalization times (1 GeV)^2 is E^2 Phi.
    y = np.array([row[2] for row in rows])
    plt.rcParams.update({"font.size": 18, "text.color": "#eeeeee", "axes.labelcolor": "#eeeeee",
                        "xtick.color": "#eeeeee", "ytick.color": "#eeeeee", "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=(14, 5.1), facecolor="#000000")
    ax.set_facecolor("#000000")
    ax.scatter(x, y, marker="v", s=38, color="#73c7ff", alpha=0.9, label="92 source upper limits")
    annotations = {"NGC 1068": (0.13, 3.4e-8), "TXS 0506+056": (0.25, 5.0e-9), "KM3-230213A": (-0.43, 1.9e-8)}
    for name, position in annotations.items():
        i = next(i for i, row in enumerate(rows) if row[0] == name)
        ax.scatter(x[i], y[i], marker="v", s=65, color="#ffbd70", zorder=4)
        label = "KM3-230213A direction" if name == "KM3-230213A" else name
        ax.annotate(label, (x[i], y[i]), xytext=position, ha="center", color="#ffbd70", fontsize=16,
                    arrowprops={"arrowstyle": "-", "color": "#ffbd70", "lw": 1})
    ax.set_yscale("log")
    ax.set_xlim(-1, 0.65); ax.set_ylim(1e-9, 1e-7)
    ax.set_xticks([-1, -.75, -.5, -.25, 0, .25, .5])
    ax.set_yticks([1e-9, 1e-8, 1e-7])
    ax.yaxis.set_major_formatter(LogFormatterMathtext(labelOnlyBase=False))
    ax.tick_params(which="minor", length=0)
    ax.set_xlabel(r"Source declination $\sin\delta$")
    ax.set_ylabel(r"$E_\nu^2\Phi_{\nu_\mu+\bar\nu_\mu}^{90\%}$ [GeV cm$^{-2}$ s$^{-1}$]")
    ax.grid(color="#344250", lw=0.7, alpha=0.7)
    for spine in ax.spines.values(): spine.set_color("#344250")
    ax.legend(loc="upper left", frameon=False, labelcolor="#73c7ff", fontsize=16)
    fig.subplots_adjust(left=.13, bottom=.18, top=.95, right=.975)
    fig.savefig(OUT / "baikal-source-limits-e2.svg")
    fig.savefig(OUT / "baikal-source-limits-e2.png", dpi=150)
    plt.close(fig)
    with (OUT / "baikal-source-limits-e2.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source", "declination_deg", "e2_muon_neutrino_flux_limit_gev_cm2_s"])
        writer.writerows(rows)


if __name__ == "__main__":
    build()
