"""Site map and geometrical below-horizon fraction; no detector response."""
from pathlib import Path
import json
import tomllib
import numpy as np

HERE = Path(__file__).resolve().parent
CFG = tomllib.loads((HERE / "config.toml").read_text())
OUT = HERE.parents[1] / "media/source-results"


def upgoing_fraction(latitude_deg, declination_deg):
    """Fraction of a sidereal day at cos(zenith)<0, surface horizon."""
    phi = np.deg2rad(latitude_deg)
    delta = np.deg2rad(np.asarray(declination_deg, dtype=float))
    a = np.sin(phi) * np.sin(delta)
    b = np.cos(phi) * np.cos(delta)
    # Covers both polar detector sites and celestial poles without tan poles.
    polar = np.abs(b) < 1e-12
    threshold = np.divide(-a, b, out=np.zeros_like(a), where=~polar)
    result = 1 - np.arccos(np.clip(threshold, -1, 1)) / np.pi
    return np.where(polar, np.where(a < 0, 1.0, np.where(a > 0, 0.0, 0.5)), result)


def setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    p = CFG["plot"]
    plt.rcParams.update({"font.size": p["font_size"], "text.color": p["foreground"],
                        "axes.labelcolor": p["foreground"], "xtick.color": p["foreground"],
                        "ytick.color": p["foreground"], "svg.fonttype": "path", "mathtext.fontset": "stix"})
    OUT.mkdir(parents=True, exist_ok=True)
    return plt


def save(fig, name, plt):
    fig.savefig(OUT / f"{name}.svg", facecolor=CFG["plot"]["background"])
    fig.savefig(OUT / f"{name}.png", facecolor=CFG["plot"]["background"], dpi=150)
    plt.close(fig)


def world_map(plt):
    from matplotlib.patches import Polygon
    from matplotlib.lines import Line2D
    p = CFG["plot"]
    fig = plt.figure(figsize=(p["width_in"], p["height_in"]), facecolor=p["background"])
    ax = fig.add_axes([0.015, 0.10, 0.97, 0.86], projection="mollweide")
    ax.set_facecolor(p["background"])
    data = json.loads((HERE / "data/ne_110m_land.geojson").read_text())
    for feature in data["features"]:
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            ring = np.deg2rad(np.array(polygon[0]))
            # Project the public 110m coastline vertices once. Do not densify
            # every already-short coast segment into hundreds of SVG points.
            projected = ax.transProjection.transform(ring)
            ax.add_patch(Polygon(projected, closed=True, facecolor=p["land"], edgecolor=p["coast"], lw=0.5,
                                 transform=ax.transAffine + ax.transAxes))
    ax.grid(color=p["grid"], alpha=0.7, lw=0.6)
    ax.set_xticklabels([]); ax.set_yticklabels([])
    ax.spines["geo"].set_edgecolor(p["grid"])
    for s in CFG["sites"]:
        xy = np.deg2rad([s["longitude_deg"], s["latitude_deg"]])
        ax.scatter(*xy, s=85, facecolor=s["colour"] if s["stage"] == "operating" else p["background"],
                   edgecolor=s["colour"], linewidth=2, zorder=4, clip_on=False)
        if "label_x" in s:
            ax.annotate(s["name"], xy, xytext=(s["label_x"], s["label_y"]), textcoords="axes fraction",
                        ha="center", va="center", color=s["colour"], fontsize=p["font_size"],
                        arrowprops={"arrowstyle": "-", "color": s["colour"], "lw": 1.0}, zorder=5,
                        bbox={"facecolor": p["background"], "edgecolor": "none", "pad": 2})
    handles = [Line2D([], [], marker="o", ls="", color=p["foreground"], label="Operating arrays", markersize=8),
               Line2D([], [], marker="o", ls="", markerfacecolor=p["background"], color="#ca9cff", label="Next-generation projects", markersize=8)]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=14)
    save(fig, "global-sites", plt)


def coverage(plt):
    p = CFG["plot"]
    fig, ax = plt.subplots(figsize=(p["width_in"], p["height_in"]), facecolor=p["background"])
    ax.set_facecolor(p["background"])
    delta = np.linspace(-90, 90, p["declination_samples"])
    gc = p["gc_declination_deg"]
    for s in CFG["sites"]:
        if not s["coverage"]:
            continue
        f = upgoing_fraction(s["latitude_deg"], delta)
        if abs(s["latitude_deg"]) == 90:
            for domain in [delta < 0, delta > 0]:
                ax.plot(delta[domain], 100 * f[domain], color=s["colour"], lw=3.5,
                        label=s["name"] if domain[0] else None)
        else:
            ax.plot(delta, 100 * f, color=s["colour"], lw=3.5, label=s.get("coverage_name", s["name"]))
        rate = float(upgoing_fraction(s["latitude_deg"], gc))
        ax.plot(gc, rate * 100, marker="o", color=s["colour"], markersize=7)
    ax.axvline(gc, color="#aaaaaa", lw=1, ls=":")
    ax.text(gc - 2, 92, "Galactic Centre", rotation=90, va="top", ha="right", color="#bbbbbb", fontsize=14)
    ax.set_xlabel(r"Source declination $\delta$")
    ax.set_ylabel("Time below horizon (%)")
    ax.set_xlim(-90, 90); ax.set_ylim(-3, 103)
    ax.set_xticks([-90, -60, -30, 0, 30, 60, 90], [r"$-90^\circ$", r"$-60^\circ$", r"$-30^\circ$", r"$0^\circ$", r"$30^\circ$", r"$60^\circ$", r"$90^\circ$"])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.grid(color=p["grid"], alpha=0.8, lw=0.8)
    for spine in ax.spines.values(): spine.set_color(p["grid"])
    ax.legend(loc="center right", frameon=False, labelcolor="linecolor", fontsize=p["font_size"])
    fig.subplots_adjust(left=0.10, right=0.96, top=0.96, bottom=0.18)
    save(fig, "sky-coverage", plt)
    for s in CFG["sites"]:
        if s["coverage"]:
            print(s["name"], "GC below horizon:", round(float(upgoing_fraction(s["latitude_deg"], gc)) * 100, 2), "%")


if __name__ == "__main__":
    plt = setup()
    world_map(plt)
    coverage(plt)
