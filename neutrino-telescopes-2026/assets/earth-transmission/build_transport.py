"""Earth transmission with neutral-current regeneration: redraw of V. A. Allakhverdyan's transport calculation.

The colour is the ratio of the differential flux at a detector 1 km deep to the flux entering the Earth,
Phi_full / Phi_surf, on his grid (E = 10 GeV - 100 PeV, zenith 90 - 180 deg; CT10nlo cross sections, PREM).
Neutral currents do not remove a neutrino but move it to lower energy, so the ratio depends on the incident
spectrum. The dashed contour is the same calculation without regeneration, Phi_cc / Phi_surf: the probability to
cross without any interaction, exp(-N_A sigma_tot X). Source: dissertation 2026, Fig. 4.20; Allakhverdyan,
Zavyalov and Naumov, Phys. Part. Nucl. Lett. 23 (2026), Fig. 9. The input table is not redistributed.
"""
from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CFG = tomllib.loads((HERE / "config.toml").read_text())
OUT = HERE.parents[1] / "media" / "propagation"
DATA = (HERE / CFG["transport"]["data"]).resolve()


def load(path=DATA):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CFG["transport"]["sha256"]:
        raise ValueError(f"{path}: not the checked version of the transport table")
    d = np.load(path, allow_pickle=False)
    surf = d["flux_surf"]
    return d["E"], d["theta_deg"], d["flux_full"] / surf, d["flux_cc"] / surf


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.lines import Line2D
    P, T = CFG["plot"], CFG["transport"]
    plt.rcParams.update({"font.size": P["font_size"], "text.color": P["foreground"], "axes.labelcolor": P["foreground"],
                         "xtick.color": P["foreground"], "ytick.color": P["foreground"], "svg.fonttype": "path", "mathtext.fontset": "stix"})
    e, z, full, bare = load()
    le = np.log10(e)
    cmap = LinearSegmentedColormap.from_list("lecture", P["colours"])
    fig = plt.figure(figsize=(P["width_in"], P["height_in"]), facecolor=P["background"])
    ax = fig.add_axes([0.10, 0.14, 0.72, 0.80], facecolor=P["background"])
    im = ax.pcolormesh(z, le, full, cmap=cmap, vmin=0, vmax=1, shading="gouraud", rasterized=True)
    cs = ax.contour(z, le, full, levels=T["contours"], colors=P["contour_colour"], linewidths=1.4)
    ax.clabel(cs, fmt=lambda v: f"{v:.0%}".replace("%", " %"), fontsize=P["font_size"] - 3)
    ax.contour(z, le, bare, levels=T["no_regeneration_contours"], colors=T["no_regeneration_colour"],
               linewidths=1.4, linestyles=[(0, (5, 4))])
    ax.legend(handles=[Line2D([], [], color=P["contour_colour"], lw=1.4, label="with NC regeneration"),
                       Line2D([], [], color=T["no_regeneration_colour"], lw=1.4, ls=(0, (5, 4)),
                              label="same levels without regeneration")],
              loc="lower left", fontsize=P["font_size"] - 4, frameon=True, facecolor=P["background"], framealpha=0.9,
              edgecolor=P["grid"], labelcolor=P["foreground"])
    ax.set_xlabel("Zenith angle [deg]   (90°: horizon, 180°: through the centre)")
    ax.set_ylabel(r"$\log_{10}(E_\nu/\mathrm{GeV})$")
    ax.axhline(6.0, color=P["foreground"], lw=0.8, ls=(0, (4, 4)), alpha=0.7)
    ax.text(178.5, 6.08, "1 PeV", color=P["foreground"], fontsize=P["font_size"] - 3, va="bottom", ha="right")
    core = 180.0 - np.degrees(np.arcsin(3480.0 / (CFG["earth"]["radius_km"] - CFG["earth"]["detector_depth_km"])))
    ax.axvline(core, color=P["foreground"], lw=0.8, ls=(0, (1, 3)), alpha=0.6)
    ax.text(core + 0.8, 7.75, "paths through\nthe core", color=P["foreground"], fontsize=P["font_size"] - 4, va="top", ha="left")
    for sp in ax.spines.values():
        sp.set_color(P["grid"])
    cax = fig.add_axes([0.85, 0.14, 0.025, 0.80])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r"Flux at detector / flux entering the Earth")
    cb.outline.set_edgecolor(P["grid"])
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"earth-transport-full-dark.{ext}", facecolor=P["background"], dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plot()
    e, z, full, bare = load()
    i = int(np.argmin(abs(np.log10(e) - 6.0)))
    print(f"1 PeV through the centre: with regeneration {full[i, -1]:.3f}, without {bare[i, -1]:.4f}")
