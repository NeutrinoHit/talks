"""Three messengers on one E^2*flux axis: Fermi-LAT IGRB, IceCube neutrinos, Auger UHECR, Waxman-Bahcall bound.

All values come from published tables (LaTeX excerpts in data/), except the IceCube 68% band,
digitized from the vector Fig. 3 of arXiv:2507.22233v3 (digitize_icecube_band.py).
No fit, flux or bound is recomputed; only units and the per-flavour WB convention are converted.
"""
from pathlib import Path
import csv
import re
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE.parents[1] / "media/theory"
YEAR_S = 365.25 * 86400.0

# Fermi-LAT IGRB, foreground model A: Ackermann et al., ApJ 799, 86 (2015), Tables 3 and 4.
IGRB_INDEX = 2.32          # Table 4, model A; used only to place each bin integral at its geometric centre
IGRB_FIT = dict(i100_per_mev=0.95e-7, gamma=2.32, ecut_gev=279.0, i_above_100mev=7.2e-6)

# IceCube Combined Fit (CF) broken power law, per flavour nu+nubar: PRL 136, 121002 (2026), Table III.
CF_BPL = dict(phi0=1.77, gamma1=1.31, gamma2=2.74, log_ebreak=4.39)

# Waxman & Bahcall, PRD 59, 023002 (1999), Eq. (2): I_max ~ 1.5e-8 xi_Z GeV cm^-2 s^-1 sr^-1
# for nu_mu + anti-nu_mu at the source, xi_Z ~ 0.6 (no evolution) ... 3 (QSO/SFR-like evolution).
WB_IMAX = 1.5e-8
WB_XI = (0.6, 3.0)
# Source pion decay gives nu_mu+anti-nu_mu = I_max and nu_e+anti-nu_e = I_max/2 (Eq. 3);
# after oscillations the 1.5 I_max total is shared equally: per flavour (nu+nubar) = I_max/2.
WB_PER_FLAVOUR = 0.5
WB_RANGE_GEV = (1e4, 1e11)

COLORS = dict(gamma="#ffd477", nu="#67ddf7", cr="#ffb052", wb="#aa9bef",
              fg="#eeeeee", muted="#a0b5ca", grid="#344250", bg="#000000")


def _sci(mantissa, exponent):
    return float(mantissa) * 10.0 ** int(exponent)


def igrb_bins():
    """Rows (E_lo, E_hi [GeV], I, -err, +err, fg_minus, fg_plus [cm^-2 s^-1 sr^-1], upper_limit)."""
    text = (DATA / "ackermann2015-igrb-table3.tex").read_text()
    body = text.split(r"\startdata")[1].split(r"\enddata")[0]
    rows = []
    for raw in body.split(r"\\"):
        cells = [c.strip() for c in raw.replace("\n", " ").split("&")]
        if len(cells) < 6:
            continue
        lo, hi = map(float, re.findall(r"[\d.]+", cells[0]))
        cell, fg = cells[1], cells[2]
        if "<" in cell:
            m = re.search(r"([\d.]+)\s*\\times\s*10\^\{(-?\d+)\}", cell)
            rows.append((lo, hi, _sci(*m.groups()), 0.0, 0.0, 0.0, 0.0, True))
            continue
        exp = re.search(r"10\^\{(-?\d+)\}", cell).group(1)
        value = re.search(r"\(\s*([\d.]+)", cell).group(1)
        sym = re.search(r"\\pm\s*([\d.]+)", cell)
        if sym:
            err_lo = err_hi = sym.group(1)
        else:
            err_hi, err_lo = re.search(r"\\tvect\{\+([\d.]+)\}\{-([\d.]+)\}", cell).groups()
        fexp = re.search(r"10\^\{(-?\d+)\}", fg).group(1)
        fsym = re.search(r"\\pm\s*([\d.]+)", fg)
        if fsym:
            fg_lo = fg_hi = fsym.group(1)
        else:
            fg_hi, fg_lo = re.search(r"\\tvect\{\+([\d.]+)\}\{-([\d.]+)\}", fg).groups()
        rows.append((lo, hi, _sci(value, exp), _sci(err_lo, exp), _sci(err_hi, exp),
                     _sci(fg_lo, fexp), _sci(fg_hi, fexp), False))
    return rows


def igrb_e2flux(row, index=IGRB_INDEX):
    """E_c, factor: E^2 dN/dE at the geometric bin centre per unit bin integral, for dN/dE ~ E^-index."""
    lo, hi = row[0], row[1]
    ec = np.sqrt(lo * hi)
    factor = (index - 1) * ec ** (2 - index) / (lo ** (1 - index) - hi ** (1 - index))
    return ec, factor


def auger_points():
    """Rows (log10 E/eV, J, -err, +err [km^-2 yr^-1 sr^-1 eV^-1], upper_limit)."""
    rows = []
    for line in (DATA / "auger2020-spectrum-table6.tex").read_text().splitlines():
        m = re.match(r"\s*(\d+\.\d+)\s*&\s*\d+\s*&\s*\d+\s*&(.*)", line)
        if not m:
            continue
        log_e, cell = float(m.group(1)), m.group(2)
        exp = re.search(r"10\^\{(-?\d+)\}", cell).group(1)
        if "<" in cell:
            rows.append((log_e, _sci(re.search(r"<\s*([\d.]+)", cell).group(1), exp), 0.0, 0.0, True))
            continue
        value, err_hi, err_lo = re.search(r"\(\s*([\d.]+)\s*~\^\{\+([\d.]+)\}_\{-([\d.]+)\}", cell).groups()
        rows.append((log_e, _sci(value, exp), _sci(err_lo, exp), _sci(err_hi, exp), False))
    return rows


def auger_e2flux(log_e_ev, j):
    """E^2 J in GeV cm^-2 s^-1 sr^-1 from J in km^-2 yr^-1 sr^-1 eV^-1."""
    return (10.0 ** log_e_ev) ** 2 * j * 1e-10 / YEAR_S * 1e-9


def bpl_e2flux(e_gev, phi0, gamma1, gamma2, log_ebreak):
    """IceCube Table III BPL (E_break < 100 TeV branch), returned as E^2 Phi per flavour."""
    e, eb = np.asarray(e_gev, float), 10.0 ** log_ebreak
    norm = phi0 * (eb / 1e5) ** (-(gamma1 if eb > 1e5 else gamma2))
    gamma = np.where(e < eb, gamma1, gamma2)
    return 1e-18 * norm * (e / eb) ** (-gamma) * e**2


def icecube_band():
    log_e, log_f = np.loadtxt(DATA / "icecube2026-cf-bpl-band-digitized.txt", unpack=True)
    return 10.0**log_e, 10.0**log_f


def wb_per_flavour():
    return tuple(WB_PER_FLAVOUR * WB_IMAX * xi for xi in WB_XI)


def upper_limit(ax, x, y, color):
    """Horizontal bar at the published limit with a downward arrow."""
    ax.plot([x / 1.12, x * 1.12], [y, y], color=color, lw=1.8, zorder=3)
    ax.annotate("", xy=(x, y / 2.6), xytext=(x, y), zorder=3,
                arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.6, "mutation_scale": 14})


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle

    c = COLORS
    plt.rcParams.update({"font.size": 18, "text.color": c["fg"], "axes.labelcolor": c["fg"],
                         "xtick.color": c["fg"], "ytick.color": c["fg"], "svg.fonttype": "path",
                         "mathtext.fontset": "stix", "hatch.linewidth": 0.8})
    fig, ax = plt.subplots(figsize=(14, 6.3), facecolor=c["bg"])
    ax.set_facecolor(c["bg"])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.05, 6e11); ax.set_ylim(3e-11, 3e-6)
    records = []

    # Waxman-Bahcall band, per flavour.
    wb_lo, wb_hi = wb_per_flavour()
    ax.add_patch(Rectangle((WB_RANGE_GEV[0], wb_lo), WB_RANGE_GEV[1] - WB_RANGE_GEV[0], wb_hi - wb_lo,
                           facecolor=c["wb"], alpha=0.16, edgecolor="none", zorder=1))
    for y in (wb_lo, wb_hi):
        ax.plot(WB_RANGE_GEV, [y, y], color=c["wb"], lw=1.6, ls=(0, (6, 4)), zorder=2)
    ax.text(2.5e8, wb_lo / 1.25, "Waxman–Bahcall bound", color=c["wb"], ha="center", va="top", fontsize=17)
    records += [("waxman_bahcall_bound", f"{WB_RANGE_GEV[0]:.0e}-{WB_RANGE_GEV[1]:.0e}", v, "", "",
                 f"per flavour nu+nubar, xi_Z={xi}") for v, xi in zip((wb_lo, wb_hi), WB_XI)]

    # Fermi-LAT IGRB.
    for row in igrb_bins():
        ec, k = igrb_e2flux(row)
        lo, hi, val, elo, ehi, flo, fhi, ul = row
        if ul:
            upper_limit(ax, ec, k * val, c["gamma"])
            records.append(("gamma_igrb_modelA", ec, k * val, "", "", "upper limit"))
            continue
        ax.add_patch(Rectangle((lo, k * (val - flo)), hi - lo, k * (flo + fhi),
                               facecolor=c["gamma"], alpha=0.18, edgecolor="none", zorder=2))
        ax.errorbar(ec, k * val, yerr=[[k * elo], [k * ehi]], fmt="o", ms=5, color=c["gamma"],
                    elinewidth=1.6, capsize=0, zorder=3)
        records.append(("gamma_igrb_modelA", ec, k * val, k * elo, k * ehi, f"foreground-model range -{k*flo:.3g}/+{k*fhi:.3g}"))
    ax.text(0.9, 1.6e-6, r"$\gamma$ rays", color=c["gamma"], fontsize=21, ha="left")
    ax.text(0.9, 0.95e-6, "Fermi-LAT, isotropic background", color=c["gamma"], fontsize=15, ha="left")

    # IceCube neutrinos, per flavour.
    be, bf = icecube_band()
    ax.add_patch(Polygon(np.c_[be, bf], closed=True, facecolor=c["nu"], alpha=0.30, edgecolor="none", zorder=3))
    e = np.logspace(np.log10(be.min()), np.log10(be.max()), 200)
    ax.plot(e, bpl_e2flux(e, **CF_BPL), color=c["nu"], lw=2.6, zorder=4)
    ax.text(2.2e5, 5.2e-8, r"$\nu$ per flavour", color=c["nu"], fontsize=21, ha="left")
    ax.text(2.2e5, 3.4e-8, "IceCube", color=c["nu"], fontsize=15, ha="left")
    records += [("neutrino_icecube_cf_bpl", float(x), float(bpl_e2flux(x, **CF_BPL)), "", "", "best fit, per flavour")
                for x in (be.min(), 10 ** CF_BPL["log_ebreak"], 1e5, 1e6, be.max())]

    # Auger UHECR.
    for log_e, j, elo, ehi, ul in auger_points():
        x = 10.0 ** (log_e - 9)
        y = auger_e2flux(log_e, j)
        if ul:
            upper_limit(ax, x, y, c["cr"])
            records.append(("cosmic_rays_auger", x, y, "", "", "90% upper limit"))
            continue
        ax.errorbar(x, y, yerr=[[auger_e2flux(log_e, elo)], [auger_e2flux(log_e, ehi)]], fmt="s", ms=5,
                    color=c["cr"], elinewidth=1.6, capsize=0, zorder=3)
        records.append(("cosmic_rays_auger", x, y, auger_e2flux(log_e, elo), auger_e2flux(log_e, ehi), "stat. only"))
    ax.text(2.2e9, 5.5e-10, "Cosmic rays", color=c["cr"], fontsize=21, ha="center")
    ax.text(2.2e9, 3.5e-10, "Pierre Auger Observatory", color=c["cr"], fontsize=15, ha="center")

    ax.set_xticks([1, 1e3, 1e6, 1e9])
    ax.set_xticklabels(["1 GeV", "1 TeV", "1 PeV", "1 EeV"])
    ax.set_yticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6])
    ax.tick_params(which="minor", length=0)
    ax.set_xlabel("Particle energy")
    ax.set_ylabel(r"$E^2\Phi$  [GeV cm$^{-2}$ s$^{-1}$ sr$^{-1}$]")
    ax.grid(which="major", color=c["grid"], lw=0.7, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_color(c["grid"])
    fig.subplots_adjust(left=0.115, right=0.985, top=0.97, bottom=0.135)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "energy-budget.svg", facecolor=c["bg"])
    fig.savefig(OUT / "energy-budget.png", dpi=150, facecolor=c["bg"])
    plt.close(fig)
    with (OUT / "energy-budget.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["series", "energy_gev", "e2flux_gev_cm2_s_sr", "err_minus", "err_plus", "note"])
        for r in records:
            writer.writerow([r[0]] + [f"{v:.4g}" if isinstance(v, float) else v for v in r[1:]])


if __name__ == "__main__":
    build()
