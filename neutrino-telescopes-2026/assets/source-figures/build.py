"""Lecture-style redraws of point-source figures from the tables in data/.

    MPLCONFIGDIR=/private/tmp/nt-mpl pyenv exec python build.py [name ...]

Published quantities, conventions and confidence levels are unchanged; only
colours, fonts and layout differ. Provenance: README.md.
"""
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE.parents[1] / "media/source-results"

BG, FG, GRID, MUTED = "#000000", "#eeeeee", "#344250", "#9aa7b4"
BLUE, VIOLET, ORANGE, GREEN, RED = "#73c7ff", "#ca9cff", "#ffbd70", "#8fe388", "#ff8a80"


def rows(name):
    with (DATA / name).open() as stream:
        return list(csv.DictReader(stream))


def column(rs, key, cast=float):
    return np.array([cast(r[key]) for r in rs])


def figure(size, **kw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 19, "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
                         "ytick.color": FG, "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=size, facecolor=BG, **kw)
    for a in np.atleast_1d(ax):
        a.set_facecolor(BG)
        for spine in a.spines.values():
            spine.set_color(GRID)
    return plt, fig, ax


def save(plt, fig, name):
    fig.savefig(OUT / f"{name}.svg")
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)


def lecture_cmap():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("nh", [BLUE, VIOLET, ORANGE])


def txs_flare():
    from matplotlib.colors import LogNorm
    ev = rows("txs-flare-events.csv")
    fits = rows("txs-flare-fits.csv")
    t, w, e = column(ev, "mjd"), column(ev, "log10_weight"), column(ev, "muon_energy_proxy_tev_approx")
    plt, fig, ax = figure((13, 4.6))
    norm, cmap = LogNorm(0.1, 20), lecture_cmap()
    for ti, wi, ei in sorted(zip(t, w, e), key=lambda z: z[1]):
        ax.plot([ti, ti], [1, wi], color=cmap(norm(ei)), lw=2.4, solid_capstyle="butt")
    box = [(float(r["mjd"]), float(r["log10_weight_axis"])) for r in fits if r["curve"] == "box"]
    bx = sorted({b[0] for b in box}); by = max(b[1] for b in box); bl = min(b[1] for b in box)
    ax.plot([bx[0], bx[0], bx[1], bx[1]], [bl, by, by, bl], color=FG, lw=2, label="Best fit: box")
    g = np.array([(float(r["mjd"]), float(r["log10_weight_axis"])) for r in fits if r["curve"] == "gaussian"])
    ax.plot(g[:, 0], g[:, 1], color=FG, lw=2, ls=(0, (4, 3)), label="Best fit: Gaussian")
    ax.set_xlim(56043, 57160); ax.set_ylim(1, 4.5)   # frame of the original
    ax.set_xlabel("MJD"); ax.set_ylabel(r"$\log_{10}$ event weight")
    ax.grid(color=GRID, lw=0.7, alpha=0.7)
    top = ax.secondary_xaxis("top", functions=(lambda m: 2000 + (m - 51544.5) / 365.25,
                                               lambda y: 51544.5 + (y - 2000) * 365.25))
    top.set_xticks([2012.5, 2013, 2013.5, 2014, 2014.5, 2015])
    top.tick_params(colors=MUTED, labelsize=15)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, ax=ax, pad=0.015, fraction=0.03)
    cb.set_label("Muon energy proxy [TeV]", fontsize=15)
    cb.set_ticks([0.1, 0.5, 1, 5, 10, 20]); cb.set_ticklabels(["0.1", "0.5", "1", "5", "10", "20"])
    cb.ax.tick_params(labelsize=14); cb.outline.set_edgecolor(GRID)
    ax.legend(loc="upper left", frameon=False, fontsize=15)
    fig.subplots_adjust(left=0.08, right=0.93, top=0.86, bottom=0.17)
    save(plt, fig, "txs-archival-flare-2018-dark")


def ngc_scan():
    from matplotlib.colors import LinearSegmentedColormap
    g = np.load(DATA / "ngc1068-scan-grid.npz")
    c = rows("ngc1068-scan-contours.csv")
    plt, fig, ax = figure((7.4, 7.6))
    cmap = LinearSegmentedColormap.from_list("sig", ["#05080c", "#1d3557", BLUE, "#eef6ff"])
    ra, dec = g["ra_deg"], g["dec_deg"]
    im = ax.imshow(g["neg_log10_p_local"], extent=[ra[0], ra[-1], dec[-1], dec[0]], cmap=cmap,
                   vmin=0.27, vmax=6.6, aspect="auto", interpolation="bilinear")
    for name, ls in (("68%", "-"), ("95%", (0, (4, 2)))):
        pts = np.array([(float(r["ra_deg"]), float(r["dec_deg"])) for r in c if r["item"] == name])
        pts = np.vstack([pts, pts[:1]]) if name == "68%" else pts
        ax.plot(pts[:, 0], pts[:, 1], color="#0d1b2e", lw=2.4, ls=ls)
    lab = {"68%": (40.74, 0.08), "95%": (40.84, -0.26)}
    for k, (x, y) in lab.items():
        ax.text(x, y, k, color="#0d1b2e", fontsize=16, ha="center")
    pos = {r["item"]: (float(r["ra_deg"]), float(r["dec_deg"])) for r in c if r["item"] in ("NGC 1068", "best fit")}
    ax.plot(*pos["NGC 1068"], "o", ms=14, mfc="none", mec=ORANGE, mew=3, label="NGC 1068")
    ax.plot(*pos["best fit"], "x", ms=11, color="#0d1b2e", mew=3, label="Best fit")
    ax.set_xlim(ra[0], ra[-1]); ax.set_ylim(dec[-1], dec[0])
    ax.set_xticks([41.0, 40.7, 40.4]); ax.set_yticks([-0.4, -0.2, 0, 0.2, 0.4])
    ax.set_xlabel("Right ascension [deg]"); ax.set_ylabel("Declination [deg]")
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", location="top", pad=0.03, fraction=0.05)
    cb.set_label(r"$-\log_{10}\,p_{\rm local}$", fontsize=17); cb.ax.tick_params(labelsize=15)
    cb.outline.set_edgecolor(GRID)
    leg = ax.legend(loc="lower right", frameon=True, fontsize=15, facecolor="#0d1b2e", edgecolor=GRID)
    leg.get_texts()[1].set_color(FG); leg.legend_handles[1].set_color(FG)
    fig.subplots_adjust(left=0.18, right=0.96, top=0.86, bottom=0.11)
    save(plt, fig, "ngc1068-neutrino-scan-2026-dark")


def ngc_sed():
    pts = rows("ngc1068-sed-points.csv")
    cur = {}
    for r in rows("ngc1068-sed-curves.csv"):
        cur.setdefault(r["curve"], []).append((float(r["e_gev"]), float(r["e2flux"])))
    cur = {k: np.array(v) for k, v in cur.items()}
    plt, fig, ax = figure((12, 6.6))
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    ax.fill(*cur["inoue_band"].T, color=VIOLET, alpha=0.22, lw=0)
    ax.plot(*cur["murase"].T, color=VIOLET, lw=2.2, label="Core models")
    ax.fill(*cur["icecube_band"].T, color=BLUE, alpha=0.45, lw=0)
    ax.plot(*cur["icecube_best"].T, color=BLUE, lw=2.6, label=r"IceCube 2022 neutrino fit ($\nu_\mu+\bar\nu_\mu$)")

    def draw(name, colour, label, ms=6):
        sel = [r for r in pts if r["dataset"] == name]
        P = [r for r in sel if r["kind"] == "point"]
        U = [r for r in sel if r["kind"] == "upper_limit"]
        if P:
            e = column(P, "e_gev"); y = column(P, "e2flux")
            ax.errorbar(e, y, xerr=[e - column(P, "e_lo_gev"), column(P, "e_hi_gev") - e],
                        yerr=[y - column(P, "e2flux_lo"), column(P, "e2flux_hi") - y],
                        fmt="o", ms=ms, color=colour, elinewidth=1.4, capsize=0, label=label)
            label = None
        if U:
            e = column(U, "e_gev"); y = column(U, "e2flux")
            ax.errorbar(e, y, xerr=[e - column(U, "e_lo_gev"), column(U, "e_hi_gev") - e], yerr=0.4 * y,
                        uplims=True, fmt="none", ecolor=colour, elinewidth=1.6, capsize=3, label=label)

    draw("archival", "#9aa7b4", "Archival photons", ms=4)
    draw("4FGL-DR2", ORANGE, "Gamma rays (Fermi, MAGIC)", ms=7)
    draw("MAGIC", ORANGE, None)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(10 ** -16.6, 10 ** 7.6); ax.set_ylim(1e-14, 2e-9)
    ax.set_xlabel("Energy [GeV]"); ax.set_ylabel(r"$E^2\phi$ [TeV cm$^{-2}$ s$^{-1}$]")
    ax.set_xticks([1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1, 1e3, 1e6])
    ax.legend(loc="lower left", bbox_to_anchor=(0.2, 0.0), frameon=False, fontsize=14.5, labelspacing=0.35)
    fig.subplots_adjust(left=0.11, right=0.98, top=0.97, bottom=0.13)
    save(plt, fig, "ngc1068-multimessenger-2022-dark")


def radio_sky():
    """Recoloured composite in the original page coordinates (points, y down)."""
    import matplotlib.image as mpimg
    from matplotlib.colors import LogNorm
    W, H = 593.6, 300.0
    plt, fig, ax = figure((12.4, 7.2))
    ax.set_position([0.01, 0.2, 0.98, 0.79]); ax.set_xlim(0, W); ax.set_ylim(H, 0)
    ax.set_aspect("equal"); ax.axis("off")
    grid = {}
    for r in rows("radio-sky-graticule.csv"):
        grid.setdefault(r["line"], []).append((float(r["x_pt"]), float(r["y_pt"])))
    outline = max(grid.values(), key=lambda v: (np.ptp([q[0] for q in v]), len(v)))
    ax.fill(*np.array(outline).T, color="#05080c", lw=0)
    for v in grid.values():
        ax.plot(*np.array(v).T, color=GRID, lw=0.7)
    layer_style = {"vlbi_sample": ("#4a5562", 1.0), "galactic_plane": (VIOLET, 0.6),
                   "ellipses_enlarged": (BLUE, 0.35), "ellipses_original": (BLUE, 1.0)}
    for r in rows("radio-sky-layers.csv"):
        mask = mpimg.imread(DATA / f"radio-sky-{r['layer']}.png")[..., 0] < 0.5
        col, alpha = layer_style[r["layer"]]
        rgba = np.zeros(mask.shape + (4,))
        from matplotlib.colors import to_rgb
        rgba[..., :3] = to_rgb(col); rgba[..., 3] = mask * alpha
        ax.imshow(rgba, extent=[float(r["x0_pt"]), float(r["x1_pt"]), float(r["y1_pt"]), float(r["y0_pt"])],
                  interpolation="nearest", zorder=2)
    norm, cmap = LogNorm(0.15, 15), lecture_cmap()
    stars = {}
    for r in rows("radio-sky-stars.csv"):
        stars.setdefault(r["star"], [float(r["vlbi_flux_jy"]), []])[1].append((float(r["x_pt"]), float(r["y_pt"])))
    for f, pts in stars.values():
        pts = np.array(pts); c = pts.mean(axis=0)
        ax.fill(*(c + 1.5 * (pts - c)).T, facecolor=cmap(norm(f)), edgecolor=BG, lw=0.4, zorder=4)
    for r in rows("radio-sky-labels.csv"):
        name = r["text"]
        named = not (name.endswith("°") or name.endswith("h"))
        ax.text(float(r["x_pt"]), float(r["y_baseline_pt"]) - 4, name, zorder=5,
                fontsize=13 if named else 11, color=FG if named else MUTED,
                fontweight="bold" if named else None)
    cax = fig.add_axes([0.15, 0.1, 0.7, 0.035])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal")
    cb.set_ticks([0.15, 0.2, 0.5, 1, 2, 5, 10, 15]); cb.set_ticklabels(["0.15", "0.2", "0.5", "1", "2", "5", "10", "15"])
    cb.ax.tick_params(labelsize=14); cb.outline.set_edgecolor(GRID)
    cb.set_label("VLBI flux density at 8 GHz [Jy]", fontsize=15)
    save(plt, fig, "radio-blazars-sky-2020-dark")


def radio_flux():
    r = rows("radio-flux-average.csv")
    ind = sorted(float(x["flux_jy"]) for x in r if x["item"] == "individual_neutrino_agn")
    nav = next(float(x["flux_jy"]) for x in r if x["item"] == "neutrino_agn_average")
    rnd = next(x for x in r if x["item"] == "random_average_68pct")
    plt, fig, ax = figure((8, 4.2))
    ax.vlines(ind, 0, 0.3, color=FG, lw=1.6, label="AGN near neutrinos")
    lo, mid, hi = (float(rnd[k]) for k in ("interval_lo_jy", "flux_jy", "interval_hi_jy"))
    ax.errorbar([mid], [0.48], xerr=[[mid - lo], [hi - mid]], fmt="|", ms=20, mew=2.5, color=BLUE,
                elinewidth=3.5, label="Average, random sky (68%)")
    ax.plot([nav], [0.48], "v", ms=17, color=ORANGE, label="Average, near neutrinos")
    labels = [(ind[-1], "3C 279", 0.62), (ind[-2], "PKS 2145+067", 0.78), (ind[-3], "NRAO 530,\nPKS 1741−038", 0.48)]
    for x, txt, y in labels:
        ax.annotate(txt, (x, 0.3), xytext=(x, y), ha="center", va="bottom", fontsize=15, color=MUTED,
                    arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    ax.set_xscale("log"); ax.set_xlim(0.12, 30); ax.set_ylim(0, 1.25); ax.set_yticks([])
    ax.set_xticks([0.2, 0.5, 1, 2, 5, 10, 20]); ax.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10", "20"])
    ax.set_xlabel("8 GHz VLBI flux density [Jy]")
    ax.legend(loc="upper left", frameon=False, fontsize=15, labelspacing=0.3)
    fig.subplots_adjust(left=0.03, right=0.98, top=0.98, bottom=0.2)
    save(plt, fig, "radio-blazars-vlbi-flux-2020-dark")

def txs_radio():
    fe = rows("txs-lightcurve-fermi.csv"); ra = rows("txs-lightcurve-ratan.csv")
    fl = rows("txs-lightcurve-flares.csv"); mk = rows("txs-lightcurve-marks.csv")
    plt, fig, ax = figure((13, 6.2))
    ax2 = ax.twinx()
    band = next(r for r in mk if r["item"] == "icecube_2014_band")
    ax.axvspan(float(band["value"]), float(band["value2"]), color=BLUE, alpha=0.25, lw=0)
    ax.text(float(band["value2"]) + 0.08, 7.6, "IceCube 2014–15\nexcess", color=BLUE, fontsize=14, va="top")
    names = ["IceCube 2017", "Baikal-GVD 2021"]
    for r, name in zip([r for r in mk if r["item"] == "neutrino_line"], names):
        x = float(r["value"])
        ax.axvline(x, color=BLUE, lw=2, ls=(0, (5, 3)))
        ax.text(x - 0.07, 8.45, name, color=BLUE, fontsize=14, ha="right", va="top")
    med = float(next(r for r in mk if r["item"] == "fermi_median")["value"])
    ax.axhline(med, color="#6b7785", lw=1.5)
    t = column(fe, "epoch_yr"); f = column(fe, "flux_1e-7_ph_cm2_s")
    ax.errorbar(t, f, yerr=[f - column(fe, "lo"), column(fe, "hi") - f], fmt="o", ms=4.5, color=FG,
                elinewidth=1, capsize=0, label="Fermi-LAT gamma rays")
    rt = column(ra, "epoch_yr"); rf = column(ra, "flux_jy")
    ax2.errorbar(rt, rf, yerr=[rf - column(ra, "lo"), column(ra, "hi") - rf], fmt="D", ms=5.5, mfc="none",
                 mec=ORANGE, mew=1.3, ecolor=ORANGE, elinewidth=0.9, capsize=0, label="RATAN-600 radio, 11 GHz")
    for kind, style in (("component", dict(lw=1.4, ls=(0, (4, 3)), alpha=0.8)), ("sum", dict(lw=3.2))):
        q = sorted((float(r["epoch_yr"]), float(r["flux_jy"])) for r in fl if r["curve"] == kind)
        if kind == "sum":
            q = np.array(q)
            ax2.plot(q[:, 0], q[:, 1], color=ORANGE, label="Radio flares (fit)", **style)
        else:
            q = np.array(q)
            ax2.plot(q[:, 0], q[:, 1], ".", ms=2.2, color=ORANGE, alpha=0.7)
    ax.set_xlim(2010, 2022.8); ax.set_ylim(-0.25, 8.6)
    ax2.set_ylim(F_to_R(-0.25), F_to_R(8.6))
    ax.set_xlabel("Year"); ax.set_ylabel(r"$F_\gamma$ [$10^{-7}$ ph cm$^{-2}$ s$^{-1}$]")
    ax2.set_ylabel("Radio flux density [Jy]", color=ORANGE); ax2.tick_params(axis="y", colors=ORANGE)
    for sp in ax2.spines.values():
        sp.set_color(GRID)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=14, bbox_to_anchor=(0.0, 0.88))
    fig.subplots_adjust(left=0.08, right=0.92, top=0.97, bottom=0.12)
    save(plt, fig, "txs-radio-gamma-2023-dark")


def F_to_R(f):
    """Map a left-axis value to the right axis exactly as in the original (shared pixel frame)."""
    y = 654.0 + (51.5 - 654.0) * f / 8.0
    return (656.0 - y) * 2.0 / (656.0 - 177.5)


def baikal_limits():
    t = rows("baikal-limits-table1.csv"); sens = rows("baikal-limits-sensitivity.csv")
    highlight = {"Westerlund 1": (-0.72, 3e-4), "NGC 1068": (0.08, 3e-4), "KM3-230213A": (-0.33, 1.5e-7),
                 "TXS 0506+056": (0.28, 1.5e-7)}
    plt, fig, ax = figure((12, 7.6))
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    style = {"2.0": (FG, "s"), "2.5": (BLUE, "^"), "3.2": (GREEN, "v")}
    for gamma, (col, mk) in style.items():
        r = [x for x in t if x["gamma"] == gamma]
        x = np.sin(np.deg2rad([float(v["dec_deg"]) for v in r])); y = [float(v["limit_gev_gamma_minus_1_cm2_s"]) for v in r]
        hi = np.array([v["source"] in highlight for v in r])
        ax.plot(x[~hi], np.array(y)[~hi], mk, ms=6.5, color=col, ls="none")
        ax.plot(x[hi], np.array(y)[hi], mk, ms=8, color=ORANGE, ls="none")
        q = np.array(sorted((float(v["sin_dec"]), float(v["sensitivity"])) for v in sens if v["gamma"] == gamma))
        ax.plot(q[:, 0], q[:, 1], color=col, lw=2.2)
        ax.text(0.45, q[-1, 1] * 2.8, rf"$\gamma={gamma}$", color=col, fontsize=18)
    for name, (tx, ty) in highlight.items():
        v = next(x for x in t if x["gamma"] == "2.5" and x["source"] == name)
        ax.annotate(name, (np.sin(np.deg2rad(float(v["dec_deg"]))), float(v["limit_gev_gamma_minus_1_cm2_s"])),
                    xytext=(tx, ty), color=ORANGE, fontsize=14, ha="center",
                    arrowprops={"arrowstyle": "-", "color": ORANGE, "lw": 0.9})
    ax.set_yscale("log"); ax.set_xlim(-1, 0.6); ax.set_ylim(1e-9, 1)
    ax.set_xlabel(r"$\sin\delta$")
    ax.set_ylabel(r"$\Phi\cdot(E/\mathrm{GeV})^{\gamma}$  [cm$^{-2}$ s$^{-1}$ GeV$^{-1}$]")
    ax.text(-0.97, 0.4, "90% CL upper limits (points) and median sensitivity (lines)", color=MUTED, fontsize=15, va="top")
    fig.subplots_adjust(left=0.12, right=0.98, top=0.97, bottom=0.11)
    save(plt, fig, "baikal-source-limits-dark")


def baikal_antares():
    t = rows("baikal-limits-table1.csv"); a = rows("antares-limits-fig3.csv"); sens = rows("baikal-antares-sensitivity.csv")
    plt, fig, ax = figure((12, 7.6))
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    for gamma, col, mk, acol, amk in (("2.5", BLUE, "^", ORANGE, "D"), ("2.0", FG, "s", GREEN, "o")):
        q = [x for x in a if x["gamma"] == gamma]
        ax.plot([float(x["sin_dec"]) for x in q], [float(x["limit_gev_gamma_minus_1_cm2_s"]) for x in q], amk,
                ms=5.5, mfc="none", mec=acol, mew=1.1, ls="none", label=rf"ANTARES, $\gamma={gamma}$")
        r = [x for x in t if x["gamma"] == gamma]
        ax.plot(np.sin(np.deg2rad([float(v["dec_deg"]) for v in r])), [float(v["limit_gev_gamma_minus_1_cm2_s"]) for v in r],
                mk, ms=6.5, color=col, ls="none", label=rf"Baikal-GVD, $\gamma={gamma}$")
        c = np.array(sorted((float(v["sin_dec"]), float(v["sensitivity"])) for v in sens if v["gamma"] == gamma))
        ax.plot(c[:, 0], c[:, 1], color=col, lw=2.2)
    ax.set_yscale("log"); ax.set_xlim(-1.034, 0.68); ax.set_ylim(1e-9, 2e-4)
    ax.set_xlabel(r"$\sin\delta$")
    ax.set_ylabel(r"$\Phi\cdot(E/\mathrm{GeV})^{\gamma}$  [cm$^{-2}$ s$^{-1}$ GeV$^{-1}$]")
    ax.legend(loc="upper left", ncol=2, frameon=False, fontsize=14)
    ax.text(0.66, 1.4e-9, "90% CL upper limits; lines: Baikal-GVD sensitivity", color=MUTED, fontsize=14, ha="right")
    fig.subplots_adjust(left=0.12, right=0.98, top=0.97, bottom=0.11)
    save(plt, fig, "baikal-antares-limits-dark")


def xray_spectra():
    r = rows("xray-agn-spectra-bands.csv")
    plt, fig, ax = figure((11, 6.4))
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    cols = {"Diffuse astrophysical": ("#d0d7de", "Diffuse flux (all sky)"), "NGC 1068": (BLUE, "NGC 1068"),
            "NGC 7469": (VIOLET, "NGC 7469"), "CGCG 420-015": (RED, "CGCG 420-015"), "NGC 4151": (ORANGE, "NGC 4151")}
    for name, (col, lab) in cols.items():
        q = np.array([(float(x["e_gev"]), float(x["e2flux_tev_cm2_s"])) for x in r if x["source"] == name])
        ax.fill(q[:, 0], q[:, 1], facecolor=col, alpha=0.45, edgecolor=col, lw=1.6, label=lab)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e2, 1e7); ax.set_ylim(1e-15, 1e-7)
    ax.set_xlabel(r"$E_\nu$ [GeV]"); ax.set_ylabel(r"$E^2\phi(E)$ [TeV cm$^{-2}$ s$^{-1}$]")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=15)
    fig.subplots_adjust(left=0.11, right=0.7, top=0.97, bottom=0.12)
    save(plt, fig, "xray-agn-spectra-dark")


def txs_dirs(name, title, out):
    from matplotlib.colors import Normalize
    r = rows(name)
    plt, fig, ax = figure((6.4, 5.6))
    ax.grid(color=GRID, lw=0.7, alpha=0.6)
    norm, cmap = Normalize(1, 5), lecture_cmap()
    t = np.linspace(0, 2 * np.pi, 181)
    for x in r:
        if x["kind"] == "circle":
            ra, dec, sg, e = (float(x[k]) for k in ("ra_deg", "dec_deg", "sigma_deg", "log10_energy_proxy_approx"))
            ls = (0, (5, 2.5)) if x["dashed"] == "1" else "-"
            ax.plot(ra + sg * np.cos(t), dec + sg * np.sin(t), color=cmap(norm(e)), lw=2, ls=ls)
            ax.plot(ra, dec, "o", ms=3.5, color=cmap(norm(e)))
        elif x["kind"] == "event":
            ax.plot(float(x["ra_deg"]), float(x["dec_deg"]), "o", ms=3.2,
                    color=cmap(norm(float(x["log10_energy_proxy_approx"]))))
        elif x["kind"].startswith("label"):
            ax.text(float(x["ra_deg"]), float(x["dec_deg"]), x["kind"][6:], color=MUTED, fontsize=11)
    txs = next(x for x in r if x["kind"] == "TXS 0506+056")
    ax.plot(float(txs["ra_deg"]), float(txs["dec_deg"]), "X", ms=11, color=FG, mec="#000000", label="TXS 0506+056")
    ax.set_xlim(74, 81); ax.set_ylim(3, 10); ax.set_aspect("equal")
    ax.set_xlabel("RA [deg]"); ax.set_ylabel("Dec [deg]")
    ax.text(74.2, 3.3, title, color=MUTED, fontsize=13)
    ax.legend(loc="upper right", frameon=False, fontsize=13)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.045, pad=0.03)
    cb.set_label(r"$\log_{10}$(energy proxy)", fontsize=13); cb.ax.tick_params(labelsize=12); cb.outline.set_edgecolor(GRID)
    fig.subplots_adjust(left=0.13, right=0.9, top=0.97, bottom=0.12)
    save(plt, fig, out)


def xray_population():
    from matplotlib.lines import Line2D
    r = rows("xray-agn-population.csv")
    get = lambda item: np.array([(float(x["n_sources"]), float(x["p"])) for x in r if x["item"] == item])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 17, "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
                         "ytick.color": FG, "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig = plt.figure(figsize=(10, 7.4), facecolor=BG)
    gs = fig.add_gridspec(2, 2, width_ratios=[7, 1], height_ratios=[2, 1], wspace=0.05, hspace=0.05)
    axes = [[fig.add_subplot(gs[i, j]) for j in range(2)] for i in range(2)]
    shades = {"3sigma": "#1d3557", "2sigma": "#2f5d8a", "1sigma": "#4f8fc4"}
    for j, part, xl in ((0, "main", (-0.5, 35.5)), (1, "right", (44.5, 47.8))):
        top, bot = axes[0][j], axes[1][j]
        for ax in (top, bot):
            ax.set_facecolor(BG); ax.set_xlim(*xl)
            for sp in ax.spines.values():
                sp.set_color(GRID)
            ax.grid(color=GRID, lw=0.6, alpha=0.6)
        for shade, col in shades.items():
            q = get(f"band_{shade}_{part}")
            top.fill(q[:, 0], q[:, 1], color=col, lw=0)
        bk = get("bkg_expectation"); ob = get("observed"); pb = get("p_binom")
        sel = (bk[:, 0] < 40) if part == "main" else (bk[:, 0] > 40)
        top.plot(bk[sel, 0], bk[sel, 1], color=FG, lw=1.8, ls=(0, (5, 3)))
        so = (ob[:, 0] < 40) if part == "main" else (ob[:, 0] > 40)
        top.plot(ob[so, 0], ob[so, 1], "o", ms=4.5, color=ORANGE)
        sb = (pb[:, 0] < 40) if part == "main" else (pb[:, 0] > 40)
        bot.plot(pb[sb, 0], pb[sb, 1], color=FG, lw=2.2)
        top.set_yscale("log"); bot.set_yscale("log")
        top.set_ylim(1.7, 5e-8); bot.set_ylim(3e-6, 3.0)        # frames of the original; p_local inverted
        top.set_xticklabels([])
        if part == "main":
            md = get("max_deviation")[0]
            top.plot([0, md[0]], [md[1], md[1]], color=RED, lw=2, ls=":")
            top.axvline(md[0], color=RED, lw=2, ls=":"); bot.axvline(md[0], color=RED, lw=2, ls=":")
            st = get("ngc1068_excluded")[0]
            top.plot(st[0], st[1], "*", ms=13, color=VIOLET)
            top.text(1.0, st[1], "NGC 1068 (excluded)", color=VIOLET, fontsize=14, va="center")
            bot.set_xticks([0, 11, 22, 33]); top.set_xticks([0, 11, 22, 33])
            top.set_ylabel(r"$p_{\rm local}$"); bot.set_ylabel(r"$p_{\rm binom}$")
        else:
            for ax in (top, bot):
                ax.set_yticklabels([]); ax.tick_params(axis="y", length=0)
            bot.set_xticks([47]); top.set_xticks([47])
    fig.text(0.5, 0.02, "Number of sources $N$ (ordered by local p-value)", ha="center", fontsize=17, color=FG)
    handles = [Line2D([], [], color=FG, lw=1.8, ls=(0, (5, 3)), label="background expectation (bands: 1, 2, 3 sigma)"),
               Line2D([], [], color=ORANGE, lw=0, marker="o", label="observation"),
               Line2D([], [], color=RED, lw=2, ls=":", label="max. deviation (11 sources)")]
    axes[0][0].legend(handles=handles, loc="upper right", frameon=False, fontsize=13)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.97, bottom=0.11)
    save(plt, fig, "xray-agn-population-dark")


FIGURES = {"xray_population": xray_population, "txs_original": lambda: txs_dirs("txs-original-directions.csv", "PSTracks v2", "txs-original-directions-dark"), "txs_updated": lambda: txs_dirs("txs-updated-directions.csv", "Northern Tracks v5 (preliminary)", "txs-updated-directions-dark"), "xray_spectra": xray_spectra, "baikal_antares": baikal_antares, "baikal_limits": baikal_limits, "txs_radio": txs_radio, "radio_flux": radio_flux, "txs_flare": txs_flare, "ngc_scan": ngc_scan, "ngc_sed": ngc_sed, "radio_sky": radio_sky}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()
