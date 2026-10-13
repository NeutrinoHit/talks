"""Baikal-GVD cascades above 200 TeV and the Galactic-latitude test, lecture style.

Input: Table 1 of arXiv:2411.05608v2 (ApJ 982, 73), read directly from the
paper's source file GVD-Galactic.tex, whose path is passed as an argument.
Event coordinates are not stored in this repository: they appear only
graphically on the slide.

Outputs in media/galactic/:
- gvd-galactic-sky.svg/.png: the 8 cascades as 90% containment circles (r90)
  in Galactic coordinates, Mollweide projection, with the |b| < 10 deg band.
- gvd-galactic-test.svg/.png: median |b| for skies with randomized right
  ascensions (declinations fixed), the paper's data-driven null hypothesis,
  and the observed value.
"""
import argparse
import re
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "media/galactic"
N_SKIES = 100_000
SEED = 20241108

# ICRS (J2000) equatorial -> Galactic rotation (Hipparcos/ESA definition).
EQ_TO_GAL = np.array([[-0.0548755604162154, -0.8734370902348850, -0.4838350155487132],
                      [+0.4941094278755837, -0.4448296299600112, +0.7469822444972189],
                      [-0.8676661490190047, -0.1980763734312015, +0.4559837761750669]])


def unit(lon_deg, lat_deg):
    lon, lat = np.deg2rad(lon_deg), np.deg2rad(lat_deg)
    return np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], axis=-1)


def angles(v):
    lon = np.rad2deg(np.arctan2(v[..., 1], v[..., 0])) % 360
    lat = np.rad2deg(np.arcsin(np.clip(v[..., 2], -1, 1)))
    return lon, lat


def gal_to_eq(l, b):
    return angles(unit(l, b) @ EQ_TO_GAL)          # row vectors: v_eq = R^T v_gal


def eq_to_gal(ra, dec):
    return angles(unit(ra, dec) @ EQ_TO_GAL.T)


def read_table(tex):
    """Rows of Table 1: (event, E/TeV, l, b, r50, r90)."""
    text = Path(tex).read_text()
    block = text[text.index(r"\label{tab:events}"):]
    block = block[:block.index(r"\end{tabular}")]
    rows = []
    for line in block.splitlines():
        m = re.match(r"\s*\\text\{(GVD\d+CA)\}\s*&(.*)\\\\", line)
        if m:
            vals = [float(v.replace("$-$", "-").strip()) for v in m.group(2).split("&")]
            rows.append((m.group(1), *vals))
    if len(rows) != 8:
        raise ValueError(f"Expected 8 cascades in Table 1, found {len(rows)}")
    return rows


def scrambled_medians(l, b, n=N_SKIES, seed=SEED):
    _, dec = gal_to_eq(np.asarray(l), np.asarray(b))
    rng = np.random.default_rng(seed)
    ra = rng.uniform(0, 360, size=(n, len(dec)))
    _, bb = eq_to_gal(ra, np.broadcast_to(dec, ra.shape))
    return np.median(np.abs(bb), axis=1)


def circle(l0, b0, radius, n=181):
    """Small circle of angular radius around (l0, b0), as (l, b) in degrees."""
    c = unit(l0, b0)
    a = np.cross(c, [0, 0, 1.0]) if abs(b0) < 89 else np.array([1.0, 0, 0])
    a /= np.linalg.norm(a)
    d = np.cross(c, a)
    t = np.linspace(0, 2 * np.pi, n)[:, None]
    r = np.deg2rad(radius)
    return angles(np.cos(r) * c + np.sin(r) * (np.cos(t) * a + np.sin(t) * d))


def to_plot_x(l):
    """Galactic longitude to Mollweide x: l = 0 at the centre, increasing to the left."""
    return -np.deg2rad(((np.asarray(l) + 180) % 360) - 180)


def style(plt):
    plt.rcParams.update({"font.size": 18, "text.color": "#eeeeee", "axes.labelcolor": "#eeeeee",
                         "xtick.color": "#eeeeee", "ytick.color": "#eeeeee", "svg.fonttype": "path",
                         "mathtext.fontset": "stix"})


def mollweide(lon_rad, lat_rad):
    """Mollweide x, y (radius 1 sphere); lon in [-pi, pi]."""
    lat = np.asarray(lat_rad, dtype=float)
    theta = lat.copy()
    for _ in range(50):                       # Newton for 2t + sin 2t = pi sin(lat)
        f = 2 * theta + np.sin(2 * theta) - np.pi * np.sin(lat)
        d = 2 + 2 * np.cos(2 * theta)
        theta = np.where(d > 1e-12, theta - f / np.where(d > 1e-12, d, 1), theta)
    return 2 * np.sqrt(2) / np.pi * np.asarray(lon_rad) * np.cos(theta), np.sqrt(2) * np.sin(theta)


def sky(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    style(plt)
    orange, violet, grid = "#ffbd70", "#ca9cff", "#344250"
    fig, ax = plt.subplots(figsize=(12, 6.4), facecolor="#000000")
    ax.set_facecolor("#000000"); ax.set_aspect("equal"); ax.axis("off")
    t = np.linspace(-np.pi / 2, np.pi / 2, 181)
    ex, ey = mollweide(np.full_like(t, np.pi), t)
    ax.fill(np.r_[ex, -ex[::-1]], np.r_[ey, ey[::-1]], color="#05080c", lw=0)
    lon = np.linspace(-np.pi, np.pi, 361)
    bx1, by1 = mollweide(lon, np.full_like(lon, np.deg2rad(10)))
    bx2, by2 = mollweide(lon, np.full_like(lon, np.deg2rad(-10)))
    ax.fill(np.r_[bx1, bx2[::-1]], np.r_[by1, by2[::-1]], color=violet, alpha=0.22, lw=0)
    for lat in (-60, -30, 30, 60):
        gx, gy = mollweide(lon, np.full_like(lon, np.deg2rad(lat)))
        ax.plot(gx, gy, color=grid, lw=0.7)
        ax.text(gx[0] - 0.05, gy[0], f"{lat:+d}°".replace("-", "−"), ha="right", va="center",
                fontsize=14, color="#9aa7b4")
    for l in range(-150, 181, 30):
        gx, gy = mollweide(np.full_like(t, np.deg2rad(l)), t)
        ax.plot(gx, gy, color=grid, lw=0.7)
    zx, zy = mollweide(lon, np.zeros_like(lon))
    ax.plot(zx, zy, color=violet, lw=1.4, ls="--")
    ax.plot(np.r_[ex, -ex[::-1], ex[:1]], np.r_[ey, ey[::-1], ey[:1]], color="#5a6b7c", lw=1.0)
    for _, _, l0, b0, _, r90 in rows:
        cl, cb = circle(l0, b0, r90)
        px = to_plot_x(cl)
        breaks = np.where(np.abs(np.diff(px)) > np.pi)[0] + 1
        for sx, sy in zip(np.split(px, breaks), np.split(np.deg2rad(cb), breaks)):
            mx, my = mollweide(sx, sy)
            ax.fill(mx, my, color=orange, alpha=0.35, lw=0)
            ax.plot(mx, my, color=orange, lw=2)
        cx, cy = mollweide(to_plot_x(l0), np.deg2rad(b0))
        ax.plot(cx, cy, "o", ms=4, color=orange)
    tx, ty = mollweide(0.0, np.deg2rad(12))
    ax.text(tx, ty, r"$|b|<10^\circ$", ha="center", va="bottom", color=violet, fontsize=16)
    tx, ty = mollweide(0.0, np.deg2rad(-13))
    ax.text(tx, ty, "Galactic centre", ha="center", va="top", color="#cfd6dd", fontsize=15)
    ax.plot([], [], "o-", color=orange, lw=2, ms=4, label="Baikal-GVD cascade, 90% circle")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, -0.02), frameon=False, fontsize=15,
              labelcolor=orange)
    ax.set_xlim(-2 * np.sqrt(2) - 0.35, 2 * np.sqrt(2) + 0.05); ax.set_ylim(-np.sqrt(2) - 0.12, np.sqrt(2) + 0.05)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(OUT / "gvd-galactic-sky.svg")
    fig.savefig(OUT / "gvd-galactic-sky.png", dpi=150)
    plt.close(fig)


def test_plot(medians, observed):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    style(plt)
    blue, orange = "#73c7ff", "#ffbd70"
    fig, ax = plt.subplots(figsize=(7.6, 4.8), facecolor="#000000")
    ax.set_facecolor("#000000")
    w = np.full_like(medians, 1 / len(medians))
    ax.hist(medians, bins=np.arange(0, 91, 3), weights=w, color=blue, alpha=0.75, lw=0,
            label="random skies")
    ax.axvline(observed, color=orange, lw=3, label="Baikal-GVD data")
    ax.set_xlim(0, 90)
    ax.set_xlabel(r"Median $|b|$ of the 8 cascades [deg]")
    ax.set_ylabel("Fraction of skies")
    ax.grid(color="#344250", lw=0.7, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_color("#344250")
    ax.legend(frameon=False, fontsize=15, loc="upper right")
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.18)
    fig.savefig(OUT / "gvd-galactic-test.svg")
    fig.savefig(OUT / "gvd-galactic-test.png", dpi=150)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("tex", type=Path, help="GVD-Galactic.tex from the arXiv:2411.05608v2 source archive")
    rows = read_table(p.parse_args().tex)
    l = np.array([r[2] for r in rows]); b = np.array([r[3] for r in rows])
    observed = float(np.median(np.abs(b)))
    medians = scrambled_medians(l, b)
    pval = float(np.mean(medians <= observed))
    sky(rows)
    test_plot(medians, observed)
    print(f"observed median |b| = {observed:.1f} deg; random skies: mean {medians.mean():.1f} deg; "
          f"p = {pval:.4f} ({N_SKIES} skies)")


if __name__ == "__main__":
    main()
