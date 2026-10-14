"""Earth tomography with neutrino absorption: how much the density profile matters.

Compares the charged-current survival probability through the PREM Earth with that through a homogeneous Earth of the
same mass (same radius, mean density from the PREM integral), from a detector 1 km deep. Absorption only, as in
build_transmission.py: neutral-current and tau regeneration are not included, and no detector response or flux
model enters. The contrast shows where in energy and zenith angle up-going neutrinos are sensitive to the dense core;
a measurement (Donini, Palomares-Ruiz & Salvado, Nature Physics 15 (2019) 37) fits such absorption to IceCube data.
"""
from __future__ import annotations

import numpy as np

import build_transmission as bt

CFG = bt.CFG
T = CFG["tomography"]


def mean_density() -> float:
    R = CFG["earth"]["radius_km"]
    r = np.linspace(0.0, R, 200001)
    mass = np.trapezoid(4 * np.pi * r ** 2 * bt.density(r), r)
    return float(mass / (4 / 3 * np.pi * R ** 3))


def column_with(density, zenith_deg):
    """Column depth (g/cm^2) along the same path as bt.column, for any density function of r (km)."""
    E = CFG["earth"]
    R, d, n = E["radius_km"], E["detector_depth_km"], E["path_steps"]
    rd = R - d
    c = np.cos(np.radians(zenith_deg))
    L = rd * (-c) + np.sqrt((rd * c) ** 2 + R ** 2 - rd ** 2)
    s = (np.arange(n) + 0.5) / n * L
    r = np.sqrt(np.maximum(rd ** 2 + s ** 2 + 2 * rd * s * c, 0.0))
    return float(np.sum(density(r)) * (L / n) * 1e5)


def grids():
    rho = mean_density()
    hom = lambda r: np.full_like(np.asarray(r, dtype=float), rho)
    z = np.linspace(90.0, 180.0, T["zeniths"])
    xp = np.array([bt.column(t) for t in z])
    xh = np.array([column_with(hom, t) for t in z])
    e = np.logspace(T["log10_e_min"], T["log10_e_max"], T["energies"])
    return rho, e, z, xp, xh, bt.transmission(e, xp), bt.transmission(e, xh)


LABELS = {
    "energy": "{e:g} TeV · PREM",
    "homogeneous": "homogeneous, {rho:.2f} g/cm³",
    "core": "paths through\nthe core",
    "zenith": "Zenith angle [deg]",
    "survival": "Survival probability, CC absorption",
    "log_energy": r"$\log_{10}(E_\nu/\mathrm{GeV})$",
    "contrast": "(PREM − homogeneous) / homogeneous",
}


def plot(labels=None, out=None, name="earth-tomography-contrast-dark", decimal_comma=False):
    L = {**LABELS, **(labels or {})}
    comma = (lambda s: s.replace(".", ",")) if decimal_comma else (lambda s: s)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    P = CFG["plot"]
    plt.rcParams.update({"font.size": P["font_size"], "text.color": P["foreground"], "axes.labelcolor": P["foreground"],
                         "xtick.color": P["foreground"], "ytick.color": P["foreground"], "svg.fonttype": "path", "mathtext.fontset": "stix"})
    rho, e, z, xp, xh, tp, th = grids()
    core = 180.0 - np.degrees(np.arcsin(3480.0 / (CFG["earth"]["radius_km"] - CFG["earth"]["detector_depth_km"])))
    fig = plt.figure(figsize=(T["width_in"], T["height_in"]), facecolor=P["background"])
    # left: survival against zenith angle at a few energies
    a = fig.add_axes([0.06, 0.15, 0.38, 0.75], facecolor=P["background"])
    for E_tev, col in zip(T["profile_energies_tev"], T["profile_colours"]):
        e1 = np.array([E_tev * 1e3])
        a.plot(z, bt.transmission(e1, xp)[0], color=col, lw=2.4, label=comma(L["energy"].format(e=E_tev)))
        a.plot(z, bt.transmission(e1, xh)[0], color=col, lw=1.6, ls=(0, (5, 4)), alpha=0.85)
    a.plot([], [], color=P["foreground"], lw=1.6, ls=(0, (5, 4)), label=comma(L["homogeneous"].format(rho=rho)))
    a.axvline(core, color=P["foreground"], lw=0.8, ls=(0, (1, 3)), alpha=0.6)
    a.text(core + 0.8, 0.98, L["core"], color=P["foreground"], fontsize=P["font_size"] - 5, ha="left", va="top")
    a.set_xlim(90, 180); a.set_ylim(0, 1.02)
    a.set_xlabel(L["zenith"]); a.set_ylabel(L["survival"])
    a.legend(frameon=False, fontsize=P["font_size"] - 4, loc="lower left")
    # right: relative contrast map
    b = fig.add_axes([0.53, 0.15, 0.36, 0.75], facecolor=P["background"])
    ratio = (tp - th) / th
    cmap = LinearSegmentedColormap.from_list("contrast", T["diverging"])
    lim = T["contrast_limit"]
    im = b.pcolormesh(z, np.log10(e), np.clip(ratio, -lim, lim), cmap=cmap, vmin=-lim, vmax=lim, shading="auto", rasterized=True)
    cs = b.contour(z, np.log10(e), ratio, levels=T["contrast_contours"], colors=P["contour_colour"], linewidths=1.3)
    b.clabel(cs, fmt=lambda v: f"{v:+.0%}".replace("%", " %"), fontsize=P["font_size"] - 4)
    b.axvline(core, color=P["foreground"], lw=0.8, ls=(0, (1, 3)), alpha=0.6)
    b.set_xlabel(L["zenith"]); b.set_ylabel(L["log_energy"])
    cax = fig.add_axes([0.905, 0.15, 0.015, 0.75])
    cb = fig.colorbar(im, cax=cax); cb.set_label(L["contrast"])
    if decimal_comma:
        from matplotlib.ticker import FuncFormatter
        fmt = FuncFormatter(lambda v, _: comma(f"{v:g}").replace("-", "−"))
        for axis in (a.yaxis, b.yaxis, cb.ax.yaxis):
            axis.set_major_formatter(fmt)
    for ax in (a, b, cax):
        for sp in ax.spines.values():
            sp.set_color(P["grid"])
    out = bt.OUT if out is None else out
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(out / f"{name}.{ext}", facecolor=P["background"], dpi=150)
    plt.close(fig)
    i = np.argmin(abs(e - 30e3))
    print(f"mean density {rho:.3f} g/cm3; diameter columns PREM {xp[-1]:.3e}, homogeneous {xh[-1]:.3e} g/cm2;"
          f" contrast at 30 TeV through the centre {ratio[i, -1]:+.2f}")


if __name__ == "__main__":
    plot()
