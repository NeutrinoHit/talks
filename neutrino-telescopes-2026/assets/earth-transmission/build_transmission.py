"""Earth transmission map, charged-current absorption only: T(E, theta) = exp(-N_A sigma_CC(E) X(theta)).

X(theta) is the PREM column depth (Dziewonski & Anderson 1981) from a detector 1 km below the surface along the
up-going direction with zenith angle theta (180 deg: through the centre). sigma_CC: CSMS (arXiv:1106.3723).
Neutral currents are ignored: they do not remove a neutrino but move it to lower energy, and that regeneration
(and tau regeneration) is not computed. T is the averaged survival probability of nu and anti-nu at fixed energy,
not a flux ratio for a source spectrum.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CFG = tomllib.loads((HERE / "config.toml").read_text())
OUT = HERE.parents[1] / "media" / "propagation"

# PREM density, g/cm^3, as polynomials in x = r / 6371 km: (outer radius km, coefficients a0 + a1 x + a2 x^2 + a3 x^3)
PREM = [(1221.5, (13.0885, 0.0, -8.8381, 0.0)),
        (3480.0, (12.5815, -1.2638, -3.6426, -5.5281)),
        (5701.0, (7.9565, -6.4761, 5.5283, -3.0807)),
        (5771.0, (5.3197, -1.4836, 0.0, 0.0)),
        (5971.0, (11.2494, -8.0298, 0.0, 0.0)),
        (6151.0, (7.1089, -3.8045, 0.0, 0.0)),
        (6346.6, (2.6910, 0.6924, 0.0, 0.0)),
        (6356.0, (2.900, 0.0, 0.0, 0.0)),
        (6368.0, (2.600, 0.0, 0.0, 0.0)),
        (6371.0, (1.020, 0.0, 0.0, 0.0))]


def density(r_km):
    r = np.asarray(r_km, dtype=float)
    x = r / 6371.0
    rho = np.zeros_like(r)
    inner = 0.0
    for outer, (a0, a1, a2, a3) in PREM:
        m = (r >= inner) & (r < outer) if outer < 6371.0 else (r >= inner) & (r <= outer)
        rho = np.where(m, a0 + a1 * x + a2 * x ** 2 + a3 * x ** 3, rho)
        inner = outer
    return rho


def column(zenith_deg, depth_km=None, steps=None):
    """Column depth (g/cm^2) from the detector to the surface along the up-going direction."""
    E = CFG["earth"]
    R = E["radius_km"]
    d = E["detector_depth_km"] if depth_km is None else depth_km
    n = E["path_steps"] if steps is None else steps
    rd = R - d
    c = np.cos(np.radians(zenith_deg))                     # direction of arrival: the neutrino comes from below for c < 0
    # points towards the arrival direction u (zenith angle theta): p = rd z + s u, so r(s)^2 = rd^2 + s^2 + 2 rd s c
    L = rd * (-c) + np.sqrt((rd * c) ** 2 + R ** 2 - rd ** 2)   # distance to the surface
    s = (np.arange(n) + 0.5) / n * L
    r = np.sqrt(np.maximum(rd ** 2 + s ** 2 + 2 * rd * s * c, 0.0))
    return float(np.sum(density(r)) * (L / n) * 1e5)


def sigma_cc(e_gev, anti=False):
    X = CFG["cross_sections"]
    tab = X["antinu_cc_pb"] if anti else X["nu_cc_pb"]
    return np.exp(np.interp(np.log(e_gev), np.log(X["energy_gev"]), np.log(tab))) * X["cm2_per_pb"]


def transmission(e_gev, x_gcm2):
    NA = CFG["cross_sections"]["nucleons_per_gram"]
    e = np.asarray(e_gev, dtype=float)[:, None]
    x = np.asarray(x_gcm2, dtype=float)[None, :]
    return 0.5 * (np.exp(-NA * sigma_cc(e) * x) + np.exp(-NA * sigma_cc(e, anti=True) * x))


def grid():
    G = CFG["grid"]
    e = np.logspace(G["log10_e_min"], G["log10_e_max"], G["energies"])
    z = np.linspace(G["zenith_min_deg"], G["zenith_max_deg"], G["zeniths"])
    x = np.array([column(t) for t in z])
    return e, z, x, transmission(e, x)


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    P = CFG["plot"]
    plt.rcParams.update({"font.size": P["font_size"], "text.color": P["foreground"], "axes.labelcolor": P["foreground"],
                         "xtick.color": P["foreground"], "ytick.color": P["foreground"], "svg.fonttype": "path", "mathtext.fontset": "stix"})
    e, z, x, T = grid()
    cmap = LinearSegmentedColormap.from_list("lecture", P["colours"])
    fig = plt.figure(figsize=(P["width_in"], P["height_in"]), facecolor=P["background"])
    ax = fig.add_axes([0.10, 0.14, 0.72, 0.80], facecolor=P["background"])
    im = ax.pcolormesh(z, np.log10(e), T, cmap=cmap, vmin=0, vmax=1, shading="auto", rasterized=True)
    cs = ax.contour(z, np.log10(e), T, levels=CFG["grid"]["contours"], colors=P["contour_colour"], linewidths=1.4)
    ax.clabel(cs, fmt=lambda v: f"{v:.0%}".replace("%", " %"), fontsize=P["font_size"] - 3)
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
    cb.set_label("Survival probability, CC absorption")
    cb.outline.set_edgecolor(P["grid"])
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"earth-transmission-cc-dark.{ext}", facecolor=P["background"], dpi=150)
    plt.close(fig)
    np.savetxt(OUT / "earth-transmission-cc-dark.csv", np.column_stack([np.repeat(np.log10(e), len(z)), np.tile(z, len(e)), T.ravel()]),
               delimiter=",", header="log10_E_GeV,zenith_deg,survival_probability_cc_only", comments="", fmt="%.4f")


if __name__ == "__main__":
    plot()
    print("diameter column g/cm2:", f"{column(180.0, depth_km=0.0):.3e}")
