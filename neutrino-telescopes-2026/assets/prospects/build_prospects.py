"""Lecture-style figures for the prospects and closing slides.

gvd-to-bhunt.svg      milestones Baikal-GVD -> B-HUNT and two cubes drawn to volume scale
discovery-map.svg     open questions placed on the neutrino-energy axis over the measured IceCube spectrum
people-chain.svg      programme -> people -> results -> B-HUNT
sources-sky.svg       what is found so far on an equatorial sky map

Every number and position is taken from the sources listed in MILESTONES, QUESTIONS and SKY
(see README.md); nothing is fitted or forecast. Cube sizes encode only the stated volumes.
"""
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "media/prospects"
sys.path.insert(0, str(ROOT / "assets/theory"))

C = {"bg": "#070d16", "fg": "#eeeeee", "muted": "#a0b5ca", "grid": "#344250", "gvd": "#73c7ff",
     "hunt": "#ffd477", "nu": "#67ddf7", "cr": "#ffb052", "wb": "#aa9bef", "frame": "#506a84"}
FONT = "Arial, sans-serif"

# (year label, text lines, colour key, source)
MILESTONES = [
    ("2024", ["First HUNT prototype string in Lake Baikal", "12 modules with 20-inch photomultipliers"], "hunt",
     "PoS(ICRC2025)1101; Science and Technology Daily, 5 Feb 2025"),
    ("2025", ["Lake Baikal: full-scale string with 20-inch modules", "South China Sea: 4 prototype detector units",
              "+ LED calibration unit, 1600 m"], "hunt",
     "JINR, 1 Apr 2025; Science and Technology Daily, 5 Feb 2025"),
    ("2026", ["Baikal-GVD: 16 clusters", "effective volume ≈ 0.8 km³"], "gvd", "baikal-gvd.jinr.ru/telescope"),
    ("≈2028", ["Baikal-GVD: ≈ 1 km³"], "gvd", "JINR, 3 Mar 2026"),
    ("≈2040", ["B-HUNT: ≈ 30 km³ in Lake Baikal", "Baikal-GVD Collaboration with IHEP (Beijing)"], "hunt",
     "JINR, 3 Mar 2026; IHEP, 11 Oct 2025"),
]
VOLUMES_KM3 = {"gvd": 1.0, "hunt": 30.0}


def _text(parts, x, y, t, color, size=28, anchor="start", weight="normal"):
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="{FONT}" font-size="{size}" '
                 f'font-weight="{weight}" text-anchor="{anchor}">{t}</text>')


def cube_side_ratio():
    return (VOLUMES_KM3["hunt"] / VOLUMES_KM3["gvd"]) ** (1 / 3)


def _cube(parts, x0, y0, side, color, label, sub):
    """Isometric cube with its front-bottom-left corner at (x0, y0)."""
    d = 0.45 * side
    front = f"M{x0} {y0}h{side}v{-side}h{-side}Z"
    top = f"M{x0} {y0 - side}l{d} {-d * 0.6}h{side}l{-d} {d * 0.6}Z"
    right = f"M{x0 + side} {y0}l{d} {-d * 0.6}v{-side}l{-d} {d * 0.6}Z"
    for path, alpha in ((front, 0.30), (top, 0.45), (right, 0.18)):
        parts.append(f'<path d="{path}" fill="{color}" fill-opacity="{alpha}" stroke="{color}" stroke-width="2"/>')
    _text(parts, x0 + side / 2, y0 + 42, label, color, 30, "middle", "bold")
    _text(parts, x0 + side / 2, y0 + 78, sub, C["muted"], 24, "middle")


def gvd_to_bhunt():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="640" viewBox="0 0 1600 640">',
             "<title>From Baikal-GVD to B-HUNT</title>",
             "<desc>Published milestones and two cubes whose volumes are 1 and 30 cubic kilometres. Not a detector layout.</desc>",
             f'<rect width="1600" height="640" fill="{C["bg"]}"/>']
    x_line, y0, dy = 150, 56, 126
    parts.append(f'<path d="M{x_line} {y0 - 10}V{y0 + dy * (len(MILESTONES) - 1) + 10}" stroke="{C["frame"]}" stroke-width="3"/>')
    for i, (year, lines, key, _src) in enumerate(MILESTONES):
        y = y0 + i * dy
        parts.append(f'<circle cx="{x_line}" cy="{y}" r="11" fill="{C[key]}"/>')
        _text(parts, x_line - 26, y + 10, year, C[key], 30, "end", "bold")
        for j, line in enumerate(lines):
            _text(parts, x_line + 32, y + 10 + 36 * j, line, C["fg"] if j == 0 else C["muted"], 28 if j == 0 else 24)
    base = 70  # pixels per km of cube side
    small, big = base, base * cube_side_ratio()
    _cube(parts, 960, 470, small, C["gvd"], "1 km³", "Baikal-GVD goal")
    _cube(parts, 1180, 470, big, C["hunt"], "30 km³", "B-HUNT · Russia + China")
    _text(parts, 1250, 600, "Cubes drawn to volume scale", C["muted"], 22, "middle")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


PEOPLE = [
    ("Programme", "hunt", ["ФНАФЧ: neutrino physics", "and particle astrophysics", "courses · seminars", "Baikal school"]),
    ("People", "gvd", ["students become", "researchers", "and lecturers"]),
    ("Results", "nu", ["data analysis", "e.g. the Milky Way", "in Baikal-GVD data;", "first author: a graduate", "of the programme"]),
    ("Next experiment", "cr", ["B-HUNT", "next-generation", "telescope", "Russia + China"]),
]


def people_chain():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="420" viewBox="0 0 1600 420">',
             "<title>Programme, people, results, next experiment</title>",
             f'<rect width="1600" height="420" fill="{C["bg"]}"/>',
             "<defs>" + "".join(
                 f'<marker id="m{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                 f'<path d="M0 0L10 5L0 10" fill="{C[k]}"/></marker>' for k in ("muted",)) + "</defs>"]
    w, h, gap, x0, y0 = 340, 270, 60, 30, 90
    for i, (title, key, lines) in enumerate(PEOPLE):
        x = x0 + i * (w + gap)
        parts.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{h}" rx="18" fill="{C[key]}" fill-opacity="0.10" '
                     f'stroke="{C[key]}" stroke-width="2.5"/>')
        _text(parts, x + w / 2, y0 - 22, title, C[key], 30, "middle", "bold")
        for j, line in enumerate(lines):
            _text(parts, x + w / 2, y0 + 62 + 46 * j, line, C["fg"], 27, "middle")
        if i < len(PEOPLE) - 1:
            parts.append(f'<path d="M{x + w + 8} {y0 + h / 2}H{x + w + gap - 8}" stroke="{C["muted"]}" '
                         f'stroke-width="4" marker-end="url(#mmuted)"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# Positions on the neutrino-energy axis [GeV] with their published origin.
QUESTIONS = {
    "seyfert": dict(span=(1.5e3, 1.5e4), source="IceCube NGC 1068, well-constrained range 1.5-15 TeV (arXiv:2510.13403)"),
    "break": dict(at=10**4.39, source="IceCube CF broken power law, E_break = 10^4.39 GeV (arXiv:2507.22233, Table III)"),
    "earth": dict(start=4e4, source="Earth absorbs neutrinos above ~40 TeV (IceCube, Nature 551, 596 (2017))"),
    "galaxy": dict(start=2e5, source="Baikal-GVD cascades above 200 TeV (ApJ 982, 73 (2025)); LHAASO UHE sources"),
    "glashow": dict(at=6.3e6, source="Glashow resonance, E = m_W^2/(2 m_e) = 6.3 PeV (IceCube, Nature 591, 220 (2021))"),
    "km3": dict(at=2.2e8, source="KM3-230213A median 220 PeV (KM3NeT, Nature 638, 376 (2025))"),
}


def _setup_axes(plt, figsize):
    plt.rcParams.update({"font.size": 18, "text.color": C["fg"], "axes.labelcolor": C["fg"], "xtick.color": C["fg"],
                         "ytick.color": C["fg"], "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=figsize, facecolor="#000000")
    ax.set_facecolor("#000000")
    return fig, ax


def discovery_map():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    import build_energy_budget as eb

    q = QUESTIONS
    fig, ax = _setup_axes(plt, (14, 6.6))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(7e2, 2e9); ax.set_ylim(3e-12, 3e-6)
    be, bf = eb.icecube_band()
    ax.add_patch(Polygon(np.c_[be, bf], closed=True, facecolor=C["nu"], alpha=0.22, edgecolor="none"))
    e = np.logspace(np.log10(be.min()), np.log10(be.max()), 200)
    ax.plot(e, eb.bpl_e2flux(e, **eb.CF_BPL), color=C["nu"], lw=2.4)
    ax.text(2.5e4, 1.2e-9, "Measured cosmic\nneutrino spectrum", color=C["nu"], fontsize=16, va="center")

    def span(x0, x1, y, color, label, arrow=False):
        ax.annotate("", xy=(x1, y), xytext=(x0, y),
                    arrowprops={"arrowstyle": "-|>" if arrow else "|-|", "color": color, "lw": 2.4, "mutation_scale": 16})
        ax.text(x0, y * 1.9, label, color=color, fontsize=19, ha="left", va="bottom")

    def mark(x, y, color, label, ha="center", va="top", dx=1.0, dy=1 / 2.2):
        if be.min() <= x <= be.max():
            ax.plot([x, x], [y, float(eb.bpl_e2flux(x, **eb.CF_BPL))], color=color, lw=1.3, ls=(0, (4, 4)))
        ax.plot(x, y, "o", ms=11, color=color)
        ax.text(x * dx, y * dy, label, color=color, fontsize=19, ha=ha, va=va)

    span(*q["seyfert"]["span"], 6e-7, C["cr"], "Seyfert galaxies beyond NGC 1068")
    mark(q["break"]["at"], 1.6e-7, C["hunt"], "Break: pp or pγ?", ha="right", va="center", dx=0.8, dy=1.0)
    span(q["galaxy"]["start"], 6e6, 1.0e-7, C["hunt"], "Milky Way and PeVatrons", arrow=True)
    mark(q["glashow"]["at"], 6e-10, C["nu"], "Glashow resonance:\nflavour and pp/pγ", ha="left", va="center", dx=1.35, dy=1.0)
    span(q["earth"]["start"], 2e6, 1.0e-11, C["wb"], "Cross section from Earth absorption", arrow=True)
    mark(q["km3"]["at"], 1.2e-8, C["wb"], "KM3-230213A:\nsource or cosmogenic?")
    ax.text(0.985, 0.97, "Any energy: transients through alerts · new physics", transform=ax.transAxes,
            color=C["muted"], fontsize=17, ha="right", va="top")

    ax.set_xticks([1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9])
    ax.set_xticklabels(["1 TeV", "10 TeV", "100 TeV", "1 PeV", "10 PeV", "100 PeV", "1 EeV"])
    ax.set_yticks([]); ax.tick_params(which="minor", length=0)
    ax.set_xlabel("Neutrino energy")
    ax.grid(axis="x", color=C["grid"], lw=0.7, alpha=0.7)
    for s in ax.spines.values():
        s.set_color(C["grid"])
    fig.subplots_adjust(left=0.02, right=0.985, top=0.98, bottom=0.12)
    fig.savefig(OUT / "discovery-map.svg", facecolor="#000000")
    fig.savefig(OUT / "discovery-map.png", dpi=120, facecolor="#000000")
    plt.close(fig)


# Equatorial J2000 positions: Baikal-GVD source list, arXiv:2603.21261v2, Table 1.
SKY = {"NGC 1068": (40.67, -0.01), "TXS 0506+056": (77.36, 5.69), "KM3-230213A": (94.30, -7.80)}
NGP_RA, NGP_DEC, L_NCP = 192.85948, 27.12825, 122.93192  # IAU J2000 Galactic pole


def galactic_to_equatorial(l_deg, b_deg):
    l, b = np.deg2rad(l_deg), np.deg2rad(b_deg)
    ra_p, dec_p, l_ncp = map(np.deg2rad, (NGP_RA, NGP_DEC, L_NCP))
    sin_dec = np.sin(dec_p) * np.sin(b) + np.cos(dec_p) * np.cos(b) * np.cos(l_ncp - l)
    dec = np.arcsin(sin_dec)
    y = np.cos(b) * np.sin(l_ncp - l)
    x = np.cos(dec_p) * np.sin(b) - np.sin(dec_p) * np.cos(b) * np.cos(l_ncp - l)
    ra = (ra_p + np.arctan2(y, x)) % (2 * np.pi)
    return np.rad2deg(ra), np.rad2deg(dec)


def _mollweide_x(ra_deg):
    """Astronomical orientation: RA increases to the left, 180 deg at the centre."""
    return np.deg2rad(180.0 - np.asarray(ra_deg))


def sources_sky():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 18, "text.color": C["fg"], "svg.fonttype": "path"})
    fig = plt.figure(figsize=(14, 7.2), facecolor="#000000")
    ax = fig.add_subplot(111, projection="mollweide", facecolor="#05080e")
    ax.grid(color=C["grid"], lw=0.6, alpha=0.8)
    ax.set_xticklabels([]); ax.set_yticklabels([])
    for s in ax.spines.values():
        s.set_color(C["frame"])
    # Galactic plane as a band |b| < 5 deg, with the Galactic Centre marked.
    l = np.linspace(0, 360, 721)
    for b, lw, alpha in ((0, 3.0, 0.9), (5, 1.0, 0.45), (-5, 1.0, 0.45)):
        ra, dec = galactic_to_equatorial(l, np.full_like(l, b))
        x = _mollweide_x(ra)
        cut = np.where(np.abs(np.diff(x)) > np.pi)[0] + 1
        for xs, ds in zip(np.split(x, cut), np.split(np.deg2rad(dec), cut)):
            ax.plot(xs, ds, color=C["hunt"], lw=lw, alpha=alpha)
    gc_ra, gc_dec = galactic_to_equatorial(0.0, 0.0)
    ax.plot(_mollweide_x(gc_ra), np.deg2rad(gc_dec), "o", ms=10, color=C["hunt"])
    ax.text(_mollweide_x(gc_ra) - 0.10, np.deg2rad(gc_dec) - 0.22, "Galactic Centre", color=C["hunt"], fontsize=17, ha="right")
    ax.text(0.0, np.deg2rad(42), "Milky Way:\ndiffuse neutrinos", color=C["hunt"], fontsize=20, ha="center")
    styles = {"NGC 1068": (C["cr"], "*", 26, "NGC 1068\nSeyfert galaxies", (0.10, -0.42)),
              "TXS 0506+056": (C["nu"], "D", 13, "TXS 0506+056\nblazars", (0.12, 0.20)),
              "KM3-230213A": (C["wb"], "o", 14, "KM3-230213A\norigin open", (0.06, -0.62))}
    for name, (ra, dec) in SKY.items():
        color, marker, ms, label, (dx, dy) = styles[name]
        x, y = _mollweide_x(ra), np.deg2rad(dec)
        ax.plot(x, y, marker, ms=ms, color=color, mfc=color if marker != "o" else "none", mew=2.4)
        ax.text(x + dx, y + dy, label, color=color, fontsize=18, ha="left" if dx > 0 else "right")
    ax.text(0.5, -0.06, "Most of the flux: many faint sources, not yet resolved", transform=ax.transAxes,
            color=C["nu"], fontsize=20, ha="center", va="top")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.10)
    fig.savefig(OUT / "sources-sky.svg", facecolor="#000000")
    fig.savefig(OUT / "sources-sky.png", dpi=120, facecolor="#000000")
    plt.close(fig)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gvd-to-bhunt.svg").write_text(gvd_to_bhunt())
    (OUT / "people-chain.svg").write_text(people_chain())
    discovery_map()
    sources_sky()


if __name__ == "__main__":
    build()
