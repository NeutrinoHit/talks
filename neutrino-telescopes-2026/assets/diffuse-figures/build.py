"""Lecture-style redraws of diffuse-flux figures from the tables in data/.

    MPLCONFIGDIR=/private/tmp/nt-mpl pyenv exec python build.py [name ...]

Every figure keeps the published quantities, conventions and confidence levels;
only colours, fonts and layout change. Provenance: README.md.
"""
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE.parents[1] / "media/diffuse"

BG, FG, GRID, MUTED = "#000000", "#eeeeee", "#344250", "#9aa7b4"
BLUE, VIOLET, ORANGE, GREEN, RED = "#73c7ff", "#ca9cff", "#ffbd70", "#8fe388", "#ff8a80"


def table(name):
    with (DATA / name).open() as stream:
        rows = list(csv.DictReader(stream))
    return {k: np.array([float(r[k]) if r[k] not in ("", "nan") else np.nan for r in rows])
            if k not in ("label", "sample", "kind") else np.array([r[k] for r in rows]) for k in rows[0]}


def figure(size):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 19, "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
                         "ytick.color": FG, "svg.fonttype": "path", "mathtext.fontset": "stix",
                         "hatch.color": "#c9d1d9", "hatch.linewidth": 0.8})
    fig, ax = plt.subplots(figsize=size, facecolor=BG)
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(color=GRID, lw=0.7, alpha=0.7, which="major")
    return plt, fig, ax


def save(plt, fig, name):
    fig.savefig(OUT / f"{name}.svg")
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)


def steps(ax, lo, hi, y, **kw):
    x = np.r_[lo, hi[-1]]
    ax.stairs(y, x, **kw)


def icecube2013(which="energy"):
    h = table(f"icecube2013-{which}-histograms.csv")
    d = table(f"icecube2013-{which}-data.csv")
    plt, fig, ax = figure((10.5, 7.2))
    lo_k, hi_k, x_k = ("e_lo_tev", "e_hi_tev", "e_tev") if which == "energy" else ("sindec_lo", "sindec_hi", "sindec")
    edges = np.r_[h[lo_k], h[hi_k][-1]]
    base = 1e-3 if which == "energy" else 0.0
    ax.stairs(h["atm_nu"], edges, baseline=base, fill=True, color=BLUE, alpha=0.55, lw=0,
              label=r"Atmospheric neutrinos ($\pi$/K)")
    ax.stairs(h["atm_nu"] + h["atm_mu"], edges, baseline=h["atm_nu"], fill=True, color=RED, alpha=0.6, lw=0,
              label="Atmospheric muons")
    ok = np.isfinite(h["bkg_unc_lo"])
    first = True
    for i in np.where(ok)[0]:
        ax.fill_between([edges[i], edges[i + 1]], h["bkg_unc_lo"][i], h["bkg_unc_hi"][i], facecolor="none",
                        hatch="////", edgecolor="#c9d1d9", lw=0, label="Background uncertainty" if first else None)
        first = False
    ax.stairs(h["charm_benchmark"], edges, color=GREEN, lw=2.2, label="Benchmark charm")
    ax.stairs(h["charm_90cl_limit"], edges, color=VIOLET, lw=2.2, label="90% CL charm limit")
    ax.stairs(h["signal_plus_background"], edges, color=ORANGE, lw=2.6, label=r"Signal + background ($E^{-2}$ fit)")
    has = d["events"] > 0
    x = d[x_k]
    ax.errorbar(x[has], d["events"][has], xerr=[x[has] - d["x_bin_lo"][has], d["x_bin_hi"][has] - x[has]],
                yerr=[d["events"][has] - d["err_lo"][has], d["err_hi"][has] - d["events"][has]],
                fmt="o", ms=8, color=FG, elinewidth=1.8, capsize=0, label="Data (28 events)", zorder=5)
    for xi, top in zip(x[~has], d["err_hi"][~has]):
        ax.plot([xi, xi], [base if base > 0 else 0, top], color=FG, lw=1.8, zorder=5)
    if which == "energy":
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(edges[0], 2000); ax.set_ylim(0.02, 200)
        ax.set_xlabel("Deposited EM-equivalent energy [TeV]")
    else:
        ax.set_xlim(-1, 1); ax.set_ylim(0, 11)
        ax.set_xlabel(r"$\sin(\mathrm{declination})$")
        ax.text(-0.97, 10.5, "Southern sky (downgoing)", color=MUTED, fontsize=14, va="top")
        ax.text(0.97, 10.5, "Northern sky (upgoing)", color=MUTED, fontsize=14, va="top", ha="right")
    ax.set_ylabel("Events per 662 days")
    ax.legend(loc="upper right", frameon=False, fontsize=13.5, labelspacing=0.3,
              bbox_to_anchor=(1, 0.93 if which == "zenith" else 1))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.97, bottom=0.12)
    save(plt, fig, f"icecube-2013-{which}-dark")

def icecube2026():
    seg = table("icecube2026-segments.csv")
    with (DATA / "icecube2026-curves.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    curves = {}
    for r in rows:
        curves.setdefault(r["curve"], []).append((float(r["e_gev"]), float(r["e2flux"])))
    c = {k: np.array(v) for k, v in curves.items()}
    plt, fig, ax = figure((10.5, 8.2))
    grey = "#8b98a5"
    ax.fill(*c["Galactic_band_0"].T, color="#c9d1d9", alpha=0.25, lw=0)
    ax.plot(*c["Galactic_line_0"].T, color="#c9d1d9", lw=1.6, ls=(0, (5, 2.4)),
            label=r"Galactic $\nu$ (Fermi $\pi^0$), $4\pi$ av.")
    ax.fill(*c["NGC1068_band_0"].T, color=grey, alpha=0.35, lw=0)
    ax.plot(*c["NGC1068_line_0"].T, color=grey, lw=1.6, ls="-.", label=r"NGC 1068, $4\pi$ av.")
    for name, col, lab in (("CF", ORANGE, "Combined Fit"), ("MESE", BLUE, "MESE")):
        ax.fill(*c[f"{name}_band_0"].T, facecolor=col, alpha=0.22, lw=0)
        ax.fill(*c[f"{name}_band_0"].T, facecolor="none", edgecolor=col, lw=0.8, alpha=0.8)
        ax.plot(*c[f"{name}_bpl_0"].T, color=col, lw=2, label=f"{lab} BPL")
        for k in (0, 1):
            ax.plot(*c[f"{name}_extrapolation_{k}"].T, color=col, lw=2, ls=":", alpha=0.7)
        m = seg["sample"] == name
        lo, hi, y = seg["e_lo_gev"][m], seg["e_hi_gev"][m], seg["e2flux"][m]
        ylo, yhi, ul = seg["e2flux_lo"][m], seg["e2flux_hi"][m], seg["upper_limit"][m] > 0
        x = np.sqrt(lo * hi) * (1.0 if name == "CF" else 1.06)
        meas = ~ul
        ax.errorbar(x[meas], y[meas], xerr=[x[meas] - lo[meas], hi[meas] - x[meas]],
                    yerr=[y[meas] - np.where(ylo[meas] > 0, ylo[meas], 1e-12), yhi[meas] - y[meas]],
                    fmt="none", ecolor=col, elinewidth=3 if name == "CF" else 1.8, capsize=0,
                    label=f"Segmented flux, {lab}")
        ax.errorbar(x[ul], y[ul], xerr=[x[ul] - lo[ul], hi[ul] - x[ul]], yerr=0.35 * y[ul], uplims=True,
                    fmt="none", ecolor=col, elinewidth=3 if name == "CF" else 1.8, capsize=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(10 ** 2.78, 10 ** 8.18); ax.set_ylim(1e-10, 1e-6)
    ax.set_xlabel("Neutrino energy [GeV]")
    ax.set_ylabel(r"$E_\nu^2\,\Phi$ per flavour, $\nu+\bar\nu$  [GeV cm$^{-2}$ s$^{-1}$ sr$^{-1}$]")
    ax.legend(loc="upper right", frameon=False, fontsize=13.5, labelspacing=0.3, ncol=1)
    fig.subplots_adjust(left=0.15, right=0.98, top=0.98, bottom=0.1)
    save(plt, fig, "icecube-spectrum-2026-dark")


def gvd2025_energy(which="energy"):
    h = table(f"gvd2025-{which}-stack.csv")
    d = table(f"gvd2025-{which}-data.csv")
    xl = "log10e" if which == "energy" else "costheta"
    plt, fig, ax = figure((10.5, 7.2))
    edges = np.r_[h[f"{xl}_lo"], h[f"{xl}_hi"][-1]]
    width = edges[1] - edges[0]
    b1 = h["atm_nu"]; b2 = b1 + h["atm_mu"]; b3 = b2 + h["astro"]
    ax.stairs(b3, edges, baseline=b2, fill=True, color=ORANGE, alpha=0.85, lw=0, label="Astrophysical (fit)")
    ax.stairs(b2, edges, baseline=b1, fill=True, color=VIOLET, alpha=0.85, lw=0, label="Atmospheric muons")
    ax.stairs(b1, edges, baseline=1e-3, fill=True, color=BLUE, alpha=0.6, lw=0, label="Atmospheric neutrinos")
    x = d[f"{xl}_centre"]; n = d["events"]
    ax.errorbar(x, n, xerr=width / 2, yerr=[n - np.maximum(d["err_lo"], 1.01e-3), d["err_hi"] - n], fmt="o", ms=9,
                color=FG, elinewidth=2, capsize=5, label="Data (18 cascades)", zorder=5)
    ax.set_yscale("log"); ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(1e-3 if which == "energy" else 1e-2, 1e2)
    ax.set_xlabel(r"$\log_{10}(E_{\rm sh}/{\rm TeV})$" if which == "energy" else r"$\cos\theta$ (reconstructed)")
    ax.set_ylabel("Events per bin")
    ax.legend(loc="upper right", frameon=False, fontsize=15, labelspacing=0.3)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.97, bottom=0.12)
    save(plt, fig, f"gvd-2018-2024-{which}-dark")

def gvd2025_spectrum():
    import csv as _csv
    with (DATA / "gvd2025-spectrum-points.csv").open() as stream:
        pts = list(_csv.DictReader(stream))
    b = table("gvd2025-spectrum-band.csv")
    plt, fig, ax = figure((10.5, 8.2))
    ax.fill_between(b["e_tev"], b["e2flux_lo"], b["e2flux_hi"], color=GREEN, alpha=0.45, lw=0)
    ax.plot(b["e_tev"], b["e2flux_fit"], color=GREEN, lw=3, label="Baikal-GVD upgoing cascades")
    for name, col, mk, lab in (("IceCube starting tracks", ORANGE, "o", "IceCube starting tracks"),
                               ("IceCube combined (preliminary)", BLUE, "s", "IceCube combined (preliminary)")):
        sel = [r for r in pts if r["sample"] == name]
        for kind in ("point", "upper_limit"):
            q = [r for r in sel if r["kind"] == kind]
            e = np.array([float(r["e_tev"]) for r in q]); y = np.array([float(r["e2flux"]) for r in q])
            xe = [e - np.array([float(r["e_lo_tev"]) for r in q]), np.array([float(r["e_hi_tev"]) for r in q]) - e]
            if kind == "point":
                lo = np.array([max(float(r["e2flux_lo"]), 1.01e-11) for r in q])
                hi = np.array([float(r["e2flux_hi"]) for r in q])
                ax.errorbar(e, y, xerr=xe, yerr=[y - lo, hi - y], fmt=mk, ms=9, color=col, elinewidth=1.6,
                            capsize=4, label=lab)
            else:
                ax.errorbar(e, y, xerr=xe, yerr=0.45 * y, uplims=True, fmt=mk, ms=9, color=col,
                            elinewidth=1.6, capsize=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1, 1e5); ax.set_ylim(1e-11, 1e-6)
    ax.set_xlabel("Neutrino energy [TeV]")
    ax.set_ylabel(r"$E^2\Phi$ per flavour  [GeV cm$^{-2}$ s$^{-1}$ sr$^{-1}$]")
    ax.legend(loc="lower left", frameon=False, fontsize=15, labelspacing=0.35)
    fig.subplots_adjust(left=0.14, right=0.98, top=0.98, bottom=0.1)
    save(plt, fig, "gvd-spectrum-2025-dark")


def zathul():
    """Zathul et al. (2026) Fig. 2; IceCube points: CF segmented flux of PRL 136 (2026) Fig. 3 x 3 (all flavours).

    Colour = spectral model (SPL, BPL, LP); line style = what is drawn (dashed: neutrino
    fit, solid: gamma-ray cascade). The y range stops at 7e-10, the lowest flux at
    which the band edges could be recovered from the original (its legend hides the rest).
    """
    import csv as _csv
    from matplotlib.lines import Line2D
    def load(name):
        with (DATA / name).open() as stream:
            return list(_csv.DictReader(stream))
    bands, lines = load("zathul-bands.csv"), load("zathul-lines.csv")
    col = {"SPL": "#e8edf2", "BPL": ORANGE, "LogP": BLUE}
    alpha = {("gamma", "SPL"): 0.08, ("gamma", "BPL"): 0.24, ("gamma", "LogP"): 0.24,
             ("neutrino", "SPL"): 0.18, ("neutrino", "BPL"): 0.32, ("neutrino", "LogP"): 0.32}
    sample = "#8b98a5"
    plt, fig, ax = figure((12, 8.4))
    for family in ("gamma", "neutrino"):
        for model in ("SPL", "BPL", "LogP"):
            r = [x for x in bands if x["family"] == family and x["model"] == model]
            e = np.array([float(x["e_gev"]) for x in r])
            lo = np.array([float(x["e2flux_lo"]) if x["e2flux_lo"] not in ("nan", "") else 1e-10 for x in r])
            hi = np.array([float(x["e2flux_hi"]) for x in r])
            ax.fill_between(e, lo, hi, color=col[model], alpha=alpha[(family, model)], lw=0)
            q = np.array(sorted((float(x["e_gev"]), float(x["e2flux"])) for x in lines
                                if x["family"] == family and x["model"] == model))
            ax.plot(q[:, 0], q[:, 1], color=col[model], lw=2.6, ls="-" if family == "gamma" else (0, (4, 2.5)))
    f = load("zathul-fermi-igrb.csv")
    e = np.array([float(x["e_gev"]) for x in f]); y = np.array([float(x["e2flux"]) for x in f])
    ax.errorbar(e, y, xerr=[e - [float(x["e_lo_gev"]) for x in f], [float(x["e_hi_gev"]) for x in f] - e],
                yerr=[y - [float(x["e2flux_lo"]) for x in f], [float(x["e2flux_hi"]) for x in f] - y],
                fmt="o", ms=6, color=VIOLET, elinewidth=1.6, capsize=0)
    seg = table("icecube2026-segments.csv"); m = seg["sample"] == "CF"
    lo_e, hi_e = seg["e_lo_gev"][m], seg["e_hi_gev"][m]; v = 3 * seg["e2flux"][m]
    vlo, vhi, ul = 3 * seg["e2flux_lo"][m], 3 * seg["e2flux_hi"][m], seg["upper_limit"][m] > 0
    xc = np.sqrt(lo_e * hi_e)
    ic = "#9aa7b4"
    ax.errorbar(xc[~ul], v[~ul], xerr=[xc[~ul] - lo_e[~ul], hi_e[~ul] - xc[~ul]],
                yerr=[v[~ul] - np.maximum(vlo[~ul], 1.01e-10), vhi[~ul] - v[~ul]], fmt="none", ecolor=ic,
                color=ic, elinewidth=1.6)
    ax.errorbar(xc[ul], v[ul], xerr=[xc[ul] - lo_e[ul], hi_e[ul] - xc[ul]], yerr=0.4 * v[ul], uplims=True,
                fmt="none", ecolor=ic, color=ic, elinewidth=1.6, capsize=3)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1, 1e8); ax.set_ylim(7e-10, 1e-6)
    models = [Line2D([], [], color=col["SPL"], lw=4, label="single power law"),
              Line2D([], [], color=col["BPL"], lw=4, label="broken power law"),
              Line2D([], [], color=col["LogP"], lw=4, label="log parabola")]
    kinds = [Line2D([], [], color=sample, lw=2.6, ls=(0, (4, 2.5)), label="dashed: neutrinos"),
             Line2D([], [], color=sample, lw=2.6, label="solid: cascade photons"),
             Line2D([], [], color=VIOLET, lw=0, marker="o", label="Fermi IGRB"),
             Line2D([], [], color=ic, lw=0, marker="+", ms=14, mew=1.8, label="IceCube (all flavours)")]
    l1 = fig.legend(handles=models, loc="upper left", bbox_to_anchor=(0.1, 0.995), ncol=3, frameon=False,
                    fontsize=15, title="model:", title_fontsize=15, alignment="left", handlelength=1.8)
    l1.get_title().set_color(MUTED)
    fig.legend(handles=kinds, loc="upper left", bbox_to_anchor=(0.1, 0.905), ncol=4, frameon=False,
               fontsize=14, handlelength=1.8, columnspacing=1.2)
    ax.set_xlabel("Energy [GeV]"); ax.set_ylabel(r"$E^2\,dN/dE$  [GeV cm$^{-2}$ s$^{-1}$ sr$^{-1}$]")
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.84, bottom=0.09)
    out = HERE.parents[1] / "media/multimessenger"
    fig.savefig(out / "diffuse-gamma-neutrino-2026-dark.svg"); fig.savefig(out / "diffuse-gamma-neutrino-2026-dark.png", dpi=150)
    plt.close(fig)

def icecube2026_indices():
    import csv as _csv
    from matplotlib.lines import Line2D
    r = list(_csv.DictReader((DATA / "icecube2026-indices-contours.csv").open()))
    plt, fig, ax = figure((8.4, 7.6))
    ax.plot([2.6, 3.4], [2.6, 3.4], color=MUTED, lw=2, ls=":")
    ax.text(2.55, 2.93, r"$\gamma_1=\gamma_2$", color=MUTED, fontsize=15, ha="right")
    for sample, col in (("CF", ORANGE), ("MESE", BLUE)):
        for level, ls in (("68%", (0, (6, 2, 1.5, 2))), ("95%", "-")):
            q = np.array([(float(x["gamma1"]), float(x["gamma2"])) for x in r if x["sample"] == sample and x["level"] == level])
            ax.plot(q[:, 0], q[:, 1], color=col, lw=3, ls=ls)
        bf = next(x for x in r if x["sample"] == sample and x["level"] == "best_fit")
        ax.plot(float(bf["gamma1"]), float(bf["gamma2"]), "*", ms=16, color=col, mec="#000000")
    handles = [Line2D([], [], color=ORANGE, lw=3, label="Combined Fit"), Line2D([], [], color=BLUE, lw=3, label="MESE"),
               Line2D([], [], color=FG, lw=2, ls=(0, (6, 2, 1.5, 2)), label="68%"), Line2D([], [], color=FG, lw=2, label="95%")]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=15, ncol=2)
    ax.set_xlim(0, 3); ax.set_ylim(2.6 - 0.15, 3.4)
    ax.set_xlabel(r"$\gamma_1$ (below the break)"); ax.set_ylabel(r"$\gamma_2$ (above the break)")
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.12)
    save(plt, fig, "icecube-spectral-indices-2026-dark")


def gvd2025_contours():
    import csv as _csv
    from matplotlib.lines import Line2D
    r = list(_csv.DictReader((DATA / "gvd2025-contours.csv").open()))
    plt, fig, ax = figure((10.5, 8))
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    style = {"Baikal-GVD 6y cascades": (RED, "*", 18), "IceCube 7.5y HESE": (BLUE, "s", 9),
             "IceCube 6y cascades": (ORANGE, "o", 10), "IceCube 9.5y tracks": (GREEN, "^", 11)}
    handles = []
    for name, (col, mk, ms) in style.items():
        for level in ("68%", "90%", "95%"):
            q = np.array([(float(x["gamma"]), float(x["phi_1e-18"])) for x in r if x["sample"] == name and x["level"] == level])
            if len(q):
                q = np.vstack([q, q[:1]])
                ax.plot(q[:, 0], q[:, 1], color=col, lw=2.6, ls="-" if level == "68%" else (0, (6, 3)))
        bf = next(x for x in r if x["sample"] == name and x["level"] == "best_fit")
        ax.plot(float(bf["gamma"]), float(bf["phi_1e-18"]), mk, ms=ms, color=col)
        handles.append(Line2D([], [], color=col, marker=mk, ms=ms * 0.8, lw=0, label=name))
    handles += [Line2D([], [], color=MUTED, lw=2.6, label="68%"),
                Line2D([], [], color=MUTED, lw=2.6, ls=(0, (6, 3)), label="GVD 90%, IceCube 95%")]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=14, labelspacing=0.35)
    ax.set_xlim(2.0, 3.4); ax.set_ylim(0, 9)
    ax.set_xlabel(r"$\gamma_{\rm astro}$")
    ax.set_ylabel(r"$\phi_{\rm astro}$  [$10^{-18}$ GeV$^{-1}$ cm$^{-2}$ s$^{-1}$ sr$^{-1}$]")
    fig.subplots_adjust(left=0.12, right=0.98, top=0.97, bottom=0.1)
    save(plt, fig, "gvd-2018-2024-contours-dark")


def icecube2026_events():
    import csv as _csv
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    cur = {}
    for r in _csv.DictReader((DATA / "icecube2026-events-curves.csv").open()):
        cur.setdefault(r["curve"], []).append((float(r["e_proxy_gev"]), float(r["events"])))
    cur = {k: np.array(v) for k, v in cur.items()}
    pts = list(_csv.DictReader((DATA / "icecube2026-events-data.csv").open()))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 17, "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
                         "ytick.color": FG, "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig, (ax, axr) = plt.subplots(2, 1, figsize=(10, 8.6), facecolor=BG, sharex=True,
                                  gridspec_kw={"height_ratios": [4, 1], "hspace": 0.05})
    ax2 = ax.twinx()
    for a in (ax, axr, ax2):
        a.set_facecolor("none")
        for sp in a.spines.values():
            sp.set_color(GRID)
    ax.set_facecolor(BG); axr.set_facecolor(BG)
    ax.fill(*cur["tracks_total_mc"].T, color=ORANGE, alpha=0.35, lw=0)
    ax.plot(*cur["tracks_bkg"].T, color="#c9d1d9", lw=1.8, ls=(0, (6, 2, 1.5, 2)))
    ax.plot(*cur["tracks_astro"].T, color=ORANGE, lw=2.4, ls=":")
    ax2.fill(*cur["cascades_total_mc"].T, color=BLUE, alpha=0.55, lw=0)
    ax2.plot(*cur["cascades_bkg"].T, color=FG, lw=1.8, ls=(0, (6, 2, 1.5, 2)))
    ax2.plot(*cur["cascades_astro"].T, color="#d6f0ff", lw=2.4, ls=":")
    for sample, panel, a, mk, kw in (("tracks", "main", ax, "s", dict(mfc="none")), ("cascades", "main", ax2, "o", {}),
                                     ("tracks", "ratio", axr, "s", dict(mfc="none")), ("cascades", "ratio", axr, "o", {})):
        q = [r for r in pts if r["sample"] == sample and r["panel"] == panel]
        e = np.array([float(r["e_proxy_gev"]) for r in q]); v = np.array([float(r["value"]) for r in q])
        lo = np.array([float(r["lo"]) if r["lo"] != "nan" else float(r["value"]) for r in q])
        hi = np.array([float(r["hi"]) if r["hi"] != "nan" else float(r["value"]) for r in q])
        a.errorbar(e, v, yerr=[np.clip(v - lo, 0, None), np.clip(hi - v, 0, None)], fmt=mk, ms=6, color=FG,
                   mec=FG, elinewidth=1.3, capsize=0, **kw)
    ax.set_xscale("log"); ax.set_yscale("log"); ax2.set_yscale("log")
    ax.set_xlim(10 ** 2.5, 1e7); ax.set_ylim(1e-3, 1e6); ax2.set_ylim(1e-1, 1e8)
    ax.set_ylabel(r"$N_{\rm tracks}$", color=ORANGE); ax2.set_ylabel(r"$N_{\rm cascades}$", color=BLUE)
    ax.tick_params(axis="y", colors=ORANGE); ax2.tick_params(axis="y", colors=BLUE)
    axr.axhline(1, color=MUTED, lw=1.4, ls="--"); axr.set_ylim(0.5, 1.5)
    axr.set_ylabel("Data/MC"); axr.set_xlabel("Energy proxy [GeV]")
    for a in (ax, axr):
        a.grid(color=GRID, lw=0.6, alpha=0.6)
    handles = [Patch(color=ORANGE, alpha=0.5, label="tracks: total MC (left axis)"),
               Patch(color=BLUE, alpha=0.7, label="cascades: total MC (right axis)"),
               Line2D([], [], color=MUTED, lw=1.8, ls=(0, (6, 2, 1.5, 2)), label="background"),
               Line2D([], [], color=MUTED, lw=2.4, ls=":", label="astrophysical (BPL)"),
               Line2D([], [], color=FG, marker="s", mfc="none", lw=0, label="data tracks"),
               Line2D([], [], color=FG, marker="o", lw=0, label="data cascades")]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=13, labelspacing=0.3)
    fig.subplots_adjust(left=0.11, right=0.89, top=0.97, bottom=0.09)
    save(plt, fig, "icecube-combined-events-2026-dark")


FIGURES = {"icecube2026_events": icecube2026_events, "gvd2025_contours": gvd2025_contours, "gvd2025_zenith": lambda: gvd2025_energy("zenith"), "icecube2026_indices": icecube2026_indices, "zathul": zathul, "icecube2013_zenith": lambda: icecube2013("zenith"), "gvd2025_spectrum": gvd2025_spectrum, "gvd2025_energy": gvd2025_energy, "icecube2013": icecube2013, "icecube2026": icecube2026}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()
