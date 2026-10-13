"""Extract plotted values from the vector artwork of diffuse-flux figures.

Run once per figure with the path of the original file from the paper's arXiv
source archive (not stored here). Writes CSV tables to data/; build.py draws
the lecture-style versions from those tables only.

    python extract.py icecube2013 /path/to/1311.5238v2/energy_distribution.pdf

Axis calibration uses the drawn major tick marks (values read from the tick
labels). Histogram steps, lines and error bars are read from the path vertices,
so values are exact up to the drawing precision of the original PDF.
"""
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "evidence"))
import vector_paths as vp  # noqa: E402

DATA = HERE / "data"


def horizontal_segments(path):
    out = []
    for sp in path.subpaths:
        for a, b in zip(sp[:-1], sp[1:]):
            if abs(a[1] - b[1]) < 1e-3 and abs(a[0] - b[0]) > 1e-3:
                out.append((min(a[0], b[0]), max(a[0], b[0]), a[1]))
    return out


def step_top(path, x):
    """Page y of the highest horizontal segment covering x (smallest y)."""
    ys = [y for x0, x1, y in horizontal_segments(path) if x0 - 1e-3 <= x <= x1 + 1e-3]
    return min(ys) if ys else np.nan


def write(name, header, rows):
    DATA.mkdir(exist_ok=True)
    with (DATA / name).open("w", newline="") as stream:
        w = csv.writer(stream)
        w.writerow(header)
        for r in rows:
            w.writerow([f"{v:.5g}" if isinstance(v, float) else v for v in r])
    print(f"{len(rows)} rows -> data/{name}")


def icecube2013(pdf, which="energy"):
    """IceCube (2013) Science, arXiv:1311.5238v2, Fig. 4: energy_distribution.pdf (left, log axes)
    or zenith_distribution.pdf (right, linear axes)."""
    ps = vp.paths(pdf)
    if which == "energy":
        X = vp.LogAxis(253.39, 1e2, 487.12, 1e3)      # tick marks labelled 10^2, 10^3 TeV
        Y = vp.LogAxis(72.5, 1e2, 177.96, 1e1)        # tick marks labelled 10^2, 10^1 events
    else:
        X = vp.LinAxis(67.37, -1.0, 557.48, 1.0)      # sin(declination) ticks
        Y = vp.LinAxis(462.6, 0.0, 79.11, 10.0)       # event ticks 0 ... 10
    frame_x0, frame_x1 = 67.37, 557.48
    data_area = lambda p: p.bbox()[1] > 180 or p.bbox()[3] > 300      # legend sits above y = 180
    blue = max((p for p in ps if p.fill == (110, 143, 184) and data_area(p)), key=lambda p: len(p.points))
    red = max((p for p in ps if p.fill == (217, 102, 101) and data_area(p)), key=lambda p: len(p.points))
    lines = {name: next(p for p in ps if p.stroke == c and p.width > 1.5 and p.bbox()[2] > 400)
             for name, c in (("charm_benchmark", (0, 137, 0)), ("charm_90cl_limit", (186, 12, 191)),
                             ("signal_plus_background", (127, 127, 127)))}
    band = next(p for p in ps if isinstance(p.fill, str) and p.fill.startswith("url") and len(p.clip) > 5)
    xs = {round(x, 2) for x0, x1, _ in horizontal_segments(red) for x in (x0, x1)}
    if which == "zenith":                              # muons vanish in the north: add the line's steps
        xs |= {round(x, 2) for x0, x1, _ in horizontal_segments(lines["signal_plus_background"]) for x in (x0, x1)}
    xs = sorted(xs)
    floor = 462.6 if which == "zenith" else np.inf     # linear axis: frame bottom is zero
    edges = [x for x in xs if frame_x0 - 50 < x < frame_x1 + 50]
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        c = 0.5 * (lo + hi)
        if hi < frame_x0 + 0.5 or lo > frame_x1 - 0.5 or hi - lo < 5:
            continue
        nu = Y.value(min(step_top(blue, c), floor))
        total_bkg = Y.value(min(step_top(red, c), step_top(blue, c), floor))
        rects = [r for r in band.clip if r[:, 0].min() - 1e-3 <= c <= r[:, 0].max() + 1e-3]
        b_hi = Y.value(min(r[:, 1].min() for r in rects)) if rects else np.nan
        b_lo = Y.value(max(r[:, 1].max() for r in rects)) if rects else np.nan
        row = [float(X.value(lo)), float(X.value(hi)), float(nu), float(max(total_bkg - nu, 0.0)) if which == "zenith"
               else float(total_bkg - nu), float(b_lo), float(b_hi)]
        row += [float(Y.value(step_top(lines[k], c))) for k in lines]
        rows.append(row)
    lo_name = "e_lo_tev" if which == "energy" else "sindec_lo"
    hi_name = "e_hi_tev" if which == "energy" else "sindec_hi"
    write(f"icecube2013-{which}-histograms.csv",
          [lo_name, hi_name, "atm_nu", "atm_mu", "bkg_unc_lo", "bkg_unc_hi", *lines], rows)
    segs = [sp for p in ps if p.stroke == (0, 0, 0) and p.fill is None and p.dash is None and p.width > 1.5
            for sp in p.subpaths if len(sp) == 2]
    vert = [s for s in segs if abs(s[0, 0] - s[1, 0]) < 0.01 and abs(s[0, 1] - s[1, 1]) > 8
            and frame_x0 + 1 < s[0, 0] < frame_x1 - 1]
    horiz = [s for s in segs if abs(s[0, 1] - s[1, 1]) < 0.01 and 8 < abs(s[0, 0] - s[1, 0]) < 80]
    markers = [p.bbox() for p in ps if p.fill == (0, 0, 0) and p.bbox()[1] > 180 and p.bbox()[2] - p.bbox()[0] < 8]
    pts = []
    zero = Y.page(0.0) if which == "zenith" else 462.6
    for v in vert:
        x = v[0, 0]
        m = [bb for bb in markers if abs((bb[0] + bb[2]) / 2 - x) < 0.5]
        yc = (m[0][1] + m[0][3]) / 2 if m else None
        hs = [h for h in horiz if min(h[:, 0]) <= x <= max(h[:, 0]) and yc is not None and abs(h[0, 1] - yc) < 0.5]
        if hs:
            lo_e, hi_e = X.value(min(h[:, 0].min() for h in hs)), X.value(max(h[:, 0].max() for h in hs))
        else:
            lo_e, hi_e = next((X.value(a), X.value(b)) for a, b in zip(edges[:-1], edges[1:]) if a <= x <= b)
        top, bottom = v[:, 1].min(), v[:, 1].max()
        n = float(np.round(Y.value(yc))) if m else 0.0
        pts.append([float(X.value(x)), n, float(Y.value(bottom)) if (m and bottom < zero - 0.5) else 0.0,
                    float(Y.value(top)), float(lo_e), float(hi_e)])
    pts.sort()
    xname = "e_tev" if which == "energy" else "sindec"
    write(f"icecube2013-{which}-data.csv", [xname, "events", "err_lo", "err_hi", "x_bin_lo", "x_bin_hi"], pts)

def icecube2026(pdf):
    """IceCube PRL 136 (2026), arXiv:2507.22233v3, Fig. 3 (figures/physics_context.pdf)."""
    ps = vp.paths(pdf)
    X = vp.LogAxis(106.34, 1e3, 473.46, 1e8)       # major ticks 10^3 ... 10^8 GeV
    Y = vp.LogAxis(371.78, 1e-10, 13.91, 1e-6)     # major ticks 10^-10 ... 10^-6
    legend_y = 135.0                               # legend box spans y < 131 at x > 256
    in_legend = lambda p: p.bbox()[1] < legend_y and p.bbox()[0] > 255 and p.bbox()[3] < legend_y
    rows = []
    for sample, colour, w_bar in (("CF", (255, 127, 14), 3.0), ("MESE", (31, 119, 180), 1.5)):
        bars = [p for p in ps if p.stroke == colour and abs(p.width - w_bar) < 0.05 and p.dash is None
                and len(p.subpaths) == 1 and len(p.subpaths[0]) == 2 and not in_legend(p)]
        horiz = [p.subpaths[0] for p in bars if abs(p.subpaths[0][0, 1] - p.subpaths[0][1, 1]) < 1e-3]
        vert = [p.subpaths[0] for p in bars if abs(p.subpaths[0][0, 0] - p.subpaths[0][1, 0]) < 1e-3]
        arrows = [p.bbox() for p in ps if p.fill == colour and len(p.subpaths) == 1 and len(p.subpaths[0]) <= 4
                  and not in_legend(p)]
        for h in sorted(horiz, key=lambda h: h[:, 0].min()):
            x0, x1, y = h[:, 0].min(), h[:, 0].max(), h[0, 1]
            v = next(v for v in vert if x0 < v[0, 0] < x1)
            limit = any(x0 < (a[0] + a[2]) / 2 < x1 for a in arrows)
            lo = v[:, 1].max()
            rows.append([sample, float(X.value(x0)), float(X.value(x1)), float(Y.value(y)),
                         0.0 if (limit or lo > 371.7) else float(Y.value(lo)),
                         float(Y.value(y)) if limit else float(Y.value(v[:, 1].min())), int(limit)])
    write("icecube2026-segments.csv",
          ["sample", "e_lo_gev", "e_hi_gev", "e2flux", "e2flux_lo", "e2flux_hi", "upper_limit"], rows)
    # Bands and lines (68% BPL bands; NGC 1068 and Galactic-plane reference bands).
    shapes = []
    for name, sel in (("CF_band", lambda p: p.fill == (255, 127, 14) and len(p.points) > 50),
                      ("MESE_band", lambda p: p.fill == (31, 119, 180) and len(p.points) > 50),
                      ("NGC1068_band", lambda p: p.fill == (128, 128, 128) and len(p.points) > 50),
                      ("Galactic_band", lambda p: p.fill == (0, 0, 0) and len(p.points) > 50),
                      ("CF_bpl", lambda p: p.stroke == (255, 127, 14) and abs(p.width - 1.5) < .05 and len(p.points) == 3),
                      ("MESE_bpl", lambda p: p.stroke == (31, 119, 180) and abs(p.width - 1.5) < .05 and len(p.points) == 3),
                      ("CF_extrapolation", lambda p: p.stroke == (255, 127, 14) and p.dash and len(p.points) == 2),
                      ("MESE_extrapolation", lambda p: p.stroke == (31, 119, 180) and p.dash and len(p.points) == 2),
                      ("NGC1068_line", lambda p: p.stroke == (128, 128, 128) and p.dash and len(p.points) > 5),
                      ("Galactic_line", lambda p: p.stroke == (0, 0, 0) and p.dash and len(p.points) > 5)):
        for k, p in enumerate(q for q in ps if sel(q) and not in_legend(q) and q.bbox()[0] >= 89):
            for sp in p.subpaths:
                if len(sp) < 2:
                    continue
                for x, y in sp:
                    shapes.append([f"{name}_{k}", float(X.value(x)), float(Y.value(y))])
    write("icecube2026-curves.csv", ["curve", "e_gev", "e2flux"], shapes)


def _frame(im):
    """Centres of the drawn frame lines (x0, x1, y0, y1) of a raster plot."""
    blk = im.max(axis=2) < 60
    def runs(m):
        i = np.where(m)[0]
        return [g for g in np.split(i, np.where(np.diff(i) > 1)[0] + 1) if len(g)]
    v = runs(blk.sum(axis=0) > 0.5 * blk.shape[0])
    h = runs(blk.sum(axis=1) > 0.5 * blk.shape[1])
    return v[0].mean(), v[-1].mean(), h[0].mean(), h[-1].mean()


def gvd2025_energy(png, which="energy"):
    """Baikal-GVD, arXiv:2507.01893v2, Fig. 2 top (Fig2_top.png, energy) or bottom (Fig2_bottom.png,
    zenith), digitized from the raster.

    Axis calibration on the centres of the drawn frame lines: energy log10(E_sh/TeV)
    1.2 -> 2.6 and 10^2 -> 10^-3 events per bin; zenith cos(theta) -1.0 -> -0.2 and
    10^2 -> 10^-2 events per bin (energy frame: x = 873 -> 5259 px, y = 179 -> 3713 px).
    Stack (bottom to top): atmospheric neutrinos, atmospheric muons, astrophysical
    neutrinos. Stack boundaries are read in one column per bin away from the
    error bars; precision about one pixel (0.0014 dex in counts).
    """
    import matplotlib.image as mpimg
    im = mpimg.imread(png)[..., :3] * 255
    fx0, fx1, fy0, fy1 = _frame(im)
    if which == "energy":
        x_lo, x_hi, nbins, y_bottom = 1.2, 2.6, 14, 1e-3
    else:
        x_lo, x_hi, nbins, y_bottom = -1.0, -0.2, 8, 1e-2
    X = vp.LinAxis(fx0, x_lo, fx1, x_hi)
    Y = vp.LogAxis(fy0, 1e2, fy1, y_bottom)
    width = (x_hi - x_lo) / nbins
    colours = {"astro": (239, 82, 0), "mu": (239, 181, 0), "nu": (148, 41, 0)}
    near = lambda px, c: np.abs(px - np.array(c)).max(axis=-1) < 25
    legend_bottom = int(Y.page(10 ** 1.1 if which == "energy" else 10 ** 1.1))
    rows = []
    for k in range(nbins):
        lo = x_lo + width * k
        col = int(round(X.page(lo + 0.3 * width)))
        y0 = legend_bottom                                         # below the legend
        line = im[y0:int(fy1) - 6, col]
        tops = {}
        for name, c in colours.items():
            hit = np.where(near(line, c))[0]
            tops[name] = float(Y.value(y0 + hit.min() - 0.5)) if len(hit) else np.nan
        total, nu = tops["astro"], tops["nu"]
        nu_mu = tops["mu"] if np.isfinite(tops["mu"]) else nu
        rows.append([round(lo, 2), round(lo + width, 2), nu, nu_mu - nu, total - nu_mu])
    xl = "log10e" if which == "energy" else "costheta"
    write(f"gvd2025-{which}-stack.csv", [f"{xl}_lo", f"{xl}_hi", "atm_nu", "atm_mu", "astro"], rows)
    blk = im.max(axis=2) < 60
    pts = []
    half = int(0.25 * width * (fx1 - fx0) / (x_hi - x_lo))
    for k in range(nbins):
        c = int(round(X.page(x_lo + width * (k + 0.5))))
        bar_rows = [y for y in range(legend_bottom, int(fy1) - 6) if blk[y, c - 2 * half:c - half].all()]
        if not bar_rows:
            continue                                               # no event in this bin
        yc = 0.5 * (min(bar_rows) + max(bar_rows))
        up = int(yc)
        while blk[up - 1, c]:
            up -= 1
        down = int(yc)
        while down + 1 < fy1 - 6 and blk[down + 1, c]:
            down += 1
        lo = 0.0 if down >= fy1 - 7 else float(Y.value(down))
        pts.append([round(x_lo + width * (k + 0.5), 3), float(np.round(Y.value(yc))), lo, float(Y.value(up))])
    write(f"gvd2025-{which}-data.csv", [f"{xl}_centre", "events", "err_lo", "err_hi"], pts)

def raster_points(im, colour, X, Y, region, erode=15, tol=40):
    """Markers, error bars and arrow upper limits of one colour in a raster figure.

    Thin bars vanish under binary erosion, markers and arrowheads remain.
    Arrowheads (triangles) are told from markers by their fill fraction.
    """
    import scipy.ndimage as nd
    y0, y1, x0, x1 = region
    mask = np.zeros(im.shape[:2], bool)
    mask[y0:y1, x0:x1] = np.abs(im[y0:y1, x0:x1] - np.array(colour)).max(axis=2) < tol
    core = nd.binary_erosion(mask, np.ones((erode, erode)))
    lab, n = nd.label(core)
    blobs = []
    for sl, k in zip(nd.find_objects(lab), range(1, n + 1)):
        area = (lab[sl] == k).sum()
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        cy, cx = nd.center_of_mass(lab == k)
        blobs.append((cx, cy, area / (h * w), sl))
    markers = [b for b in blobs if b[2] > 0.68]
    arrows = [b for b in blobs if b[2] <= 0.68]
    rows = []
    for cx, cy, _, sl in markers:
        c, r = int(round(cx)), int(round(cy))
        up = r
        while mask[up - 1, c - 1:c + 2].any():
            up -= 1
        down = r
        while down + 1 < y1 and mask[down + 1, c - 1:c + 2].any():
            down += 1
        left = c
        while mask[r - 1:r + 2, left - 1].any():
            left -= 1
        right = c
        while right + 1 < x1 and mask[r - 1:r + 2, right + 1].any():
            right += 1
        ul = any(abs(a[0] - cx) < 15 and a[1] > cy for a in arrows)
        rows.append(["upper_limit" if ul else "point", float(X.value(cx)), float(Y.value(cy)),
                     np.nan if ul else (0.0 if down >= y1 - 3 else float(Y.value(down))),
                     np.nan if ul else float(Y.value(up)), float(X.value(left)), float(X.value(right))])
    return rows


def gvd2025_spectrum(png):
    """Baikal-GVD, arXiv:2507.01893v2, Fig. 4 (Fig4_col5_600.png), digitized from the raster.

    Frame lines: E 10^0 -> 10^5 TeV at x = 959 -> 5344 px; E^2 Phi 10^-6 -> 10^-11
    GeV cm^-2 s^-1 sr^-1 at y = 179 -> 3712 px. Per flavour, nu + antinu.
    """
    import matplotlib.image as mpimg
    im = mpimg.imread(png)[..., :3] * 255
    X = vp.LogAxis(959, 1.0, 5344, 1e5)
    Y = vp.LogAxis(179, 1e-6, 3712, 1e-11)
    legend = (2800, 3500, 1100, 1700)                  # rows/cols of the legend (excluded)
    plot = (190, 3700, 970, 5335)
    rows = []
    for name, colour in (("IceCube starting tracks", (255, 0, 0)), ("IceCube combined (preliminary)", (0, 0, 255))):
        for r in raster_points(im, colour, X, Y, plot):
            px, py = X.page(r[1]), Y.page(r[2])
            if not (legend[2] < px < legend[3] and legend[0] < py < legend[1]):
                rows.append([name] + r)
    write("gvd2025-spectrum-points.csv", ["sample", "kind", "e_tev", "e2flux", "e2flux_lo", "e2flux_hi",
                                          "e_lo_tev", "e_hi_tev"], rows)
    band = np.abs(im - np.array([132, 198, 132])).max(axis=2) < 50
    line = np.abs(im - np.array([0, 132, 0])).max(axis=2) < 50
    band[2800:, :] = False; line[2800:, :] = False
    cols = np.where(band.any(axis=0))[0]
    curve = []
    for c in cols[2:-2]:
        b = np.where(band[:, c] | line[:, c])[0]
        l = np.where(line[:, c])[0]
        if len(b) and len(l):
            curve.append([float(X.value(c)), float(Y.value(l.mean())), float(Y.value(b.max())), float(Y.value(b.min()))])
    write("gvd2025-spectrum-band.csv", ["e_tev", "e2flux_fit", "e2flux_lo", "e2flux_hi"], curve[::8])


ZATHUL_COLOURS = {"SPL": (0, 0, 0), "BPL": (239, 116, 92), "LogP": (33, 102, 172)}   # line colours


def _composite(states, alpha):
    """Colour of every overlap state; layers drawn SPL, BPL, LogP with one alpha over white."""
    out = {}
    for mask in range(1, 8):
        c = np.array([255.0, 255.0, 255.0])
        for k, name in enumerate(states):
            if mask >> k & 1:
                c = c * (1 - alpha) + np.array(ZATHUL_COLOURS[name]) * alpha
        out[mask] = c
    return out


def zathul(png):
    """Zathul, Fang, Halzen, Hooper, arXiv:2606.00249v2, Fig. 2 (exsitu_CFBPLLogPSPL.png; CC BY 4.0).

    Digitized from the raster. Frame: E 10^0 -> 10^8 GeV at x = 877 -> 8472 px;
    E^2 dN/dE 10^-6 -> 10^-10 GeV cm^-2 s^-1 sr^-1 at y = 143 -> 5533 px.
    Bands are matplotlib fills drawn in the order SPL, BPL, LogP with alpha 0.3
    (gamma-ray cascades) and 0.4 (neutrino fits) in the line colours; each pixel
    is assigned to the overlap state with the nearest predicted composite colour
    (all observed overlap colours agree with the model within 2 units).
    The legend box hides the bands below ~7e-10 GeV cm^-2 s^-1 sr^-1 for
    E < 1.5e7 GeV; band edges there are not recovered (the redraw keeps a legend
    in the same place).
    """
    import matplotlib.image as mpimg
    import scipy.ndimage as nd
    im = mpimg.imread(png)[..., :3] * 255
    X = vp.LogAxis(877, 1.0, 8472, 1e8)
    Y = vp.LogAxis(143, 1e-6, 5533, 1e-10)
    names = ("SPL", "BPL", "LogP")
    y_top, y_bot = 150, 5526
    legend_y = int(Y.page(7.2e-10))
    sub = im[y_top:y_bot]
    member = {}
    for family, alpha in (("gamma", 0.3), ("neutrino", 0.4)):
        states = _composite(names, alpha)
        cols = np.array(list(states.values()))
        d = ((sub[:, :, None, :] - cols[None, None, :, :]) ** 2).sum(-1)
        best = np.argmin(d, axis=2); ok = d.min(axis=2) < 3 ** 2 * 3
        keys = np.array(list(states.keys()))
        for k, name in enumerate(names):
            m = ok & ((keys[best] >> k) & 1).astype(bool)
            m = nd.binary_closing(m, np.ones((90, 1)))        # bridge lines drawn over the band
            member[(family, name)] = m
    band_rows, line_rows = [], []
    step = 12
    y_lim_gamma_hi = Y.page(1.2e-8) - y_top            # above this, at E > 600 GeV, only neutrino bands
    y_lim_nu_lo = Y.page(2.5e-9) - y_top
    edges = {}
    for c in range(890, 8440, step):
        e = float(X.value(c))
        for (family, name), m in member.items():
            if (family == "gamma" and e > 6e4) or (family == "neutrino" and e < 2e3):
                continue
            col = m[:, c].copy()
            if family == "gamma" and e > 600:
                col[:int(y_lim_gamma_hi)] = False
            if family == "neutrino":
                col[int(y_lim_nu_lo):] = False
            if not col.any():
                continue
            idx = np.where(col)[0]
            runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
            run = max(runs, key=len)
            if len(run) < 25:
                continue
            hi_px, lo_px = y_top + run.min(), y_top + run.max()
            hidden = lo_px >= legend_y - 6 and c < X.page(1.5e7)
            edges.setdefault((family, name), []).append((c, lo_px, hi_px, hidden))
    for (family, name), rows_ in edges.items():
        arr = np.array([(c, lo, hi) for c, lo, hi, _ in rows_], float)
        hid = np.array([h for *_, h in rows_])
        k = 7                                             # rolling median: removes columns crossed by error bars
        lo_s = np.array([np.median(arr[max(0, i - k // 2):i + k // 2 + 1, 1]) for i in range(len(arr))])
        hi_s = np.array([np.median(arr[max(0, i - k // 2):i + k // 2 + 1, 2]) for i in range(len(arr))])
        for (c, _, _), lo, hi, h in zip(arr, lo_s, hi_s, hid):
            band_rows.append([family, name, float(X.value(c)), np.nan if h else float(Y.value(lo)), float(Y.value(hi))])
    for c in range(890, 8440, step):
        e = float(X.value(c))
        for name, colour in ZATHUL_COLOURS.items():
            colm = np.abs(im[y_top:y_bot, c] - np.array(colour)).max(axis=1) < 30
            colm[:130] = False; colm[-130:] = False             # frame tick marks
            if c < X.page(1.5e7):
                colm[legend_y - y_top - 5:] = False
            idx = np.where(colm)[0]
            if not len(idx):
                continue
            for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
                if len(run) < 15 or len(run) > 120:            # line width ~40 px; skip bars/text
                    continue
                v = float(Y.value(y_top + run.mean()))
                family = "neutrino" if (e >= 900 and (v > 1e-8 or e > 6e4)) else "gamma"
                line_rows.append([family, name, e, v])
    write("zathul-bands.csv", ["family", "model", "e_gev", "e2flux_lo", "e2flux_hi"], band_rows)
    write("zathul-lines.csv", ["family", "model", "e_gev", "e2flux"], line_rows)
    purple = np.abs(im - np.array([133, 36, 130])).max(axis=2) < 45
    purple[legend_y - 5:] = False
    # one vertical error bar per point: columns whose longest purple run is long
    def longest(col):
        idx = np.where(col)[0]
        if not len(idx):
            return 0, 0, 0
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        r = max(runs, key=len)
        return len(r), r.min(), r.max()
    info = [longest(purple[:, c]) for c in range(purple.shape[1])]
    barcols = np.array([c for c, (n, _, _) in enumerate(info) if n > 90])
    groups = np.split(barcols, np.where(np.diff(barcols) > 3)[0] + 1) if len(barcols) else []
    pts = []
    for g in groups:
        c = int(round(g.mean()))
        _, top, bottom = info[c]
        widths = [purple[y, c - 60:c + 61].sum() for y in range(top, bottom + 1)]
        cy = top + int(np.argmax(widths))
        row = np.where(purple[cy])[0]
        near = row[np.abs(row - c) < 200]
        runs = np.split(near, np.where(np.diff(near) > 2)[0] + 1)
        hr = next(r for r in runs if r.min() <= c <= r.max())
        lo_e, hi_e, e_c = X.value(hr.min()), X.value(hr.max()), X.value(c)
        if abs(np.log10(e_c) - 0.5 * np.log10(lo_e * hi_e)) > 0.02 or hr.min() <= 880:
            continue                                   # marker edges / point cut by the frame
        pts.append([float(e_c), float(Y.value(cy)), float(Y.value(bottom)), float(Y.value(top)),
                    float(lo_e), float(hi_e)])
    pts.sort()
    write("zathul-fermi-igrb.csv", ["e_gev", "e2flux", "e2flux_lo", "e2flux_hi", "e_lo_gev", "e_hi_gev"], pts)


def icecube2026_indices(pdf):
    """IceCube PRL 136 (2026), arXiv:2507.22233v3, Fig. 2 (figures/BPL_2D_gamma_1_gamma_2.pdf)."""
    ps = vp.paths(pdf)
    G1 = vp.LinAxis(62.04, 0.0, 439.24, 3.0)
    G2 = vp.LinAxis(316.33, 2.6, 13.65, 3.4)
    rows = []
    for sample, colour in (("CF", (255, 127, 14)), ("MESE", (31, 119, 180))):
        for p in ps:
            if p.stroke == colour and p.fill is None and len(p.points) > 10:
                level = "68%" if p.dash else "95%"
                for x, y in np.vstack([sp for sp in p.subpaths if len(sp) > 1]):
                    rows.append([sample, level, float(G1.value(x)), float(G2.value(y))])
        star = next(p for p in ps if p.fill == colour).bbox()
        rows.append([sample, "best_fit", float(G1.value((star[0] + star[2]) / 2)), float(G2.value((star[1] + star[3]) / 2))])
    write("icecube2026-indices-contours.csv", ["sample", "level", "gamma1", "gamma2"], rows)


def gvd2025_contours(png):
    """Baikal-GVD, arXiv:2507.01893v2, Fig. 3 (Fig3_col9_precise.png): single-power-law fit contours,
    digitized. Frame lines: gamma 2.0 -> 3.4, phi 9 -> 0 (1e-18 GeV^-1 cm^-2 s^-1 sr^-1 per flavour).

    Each contour is traced along 360 rays from the sample's best-fit marker: the
    first crossing of the sample colour is the inner (68%) contour, the last one
    the outer (GVD 90%, IceCube 95%) contour; a running median over 9 rays removes
    the in-line percentage labels; rays through gaps of the dashed outer contour
    are interpolated.
    """
    import matplotlib.image as mpimg
    import scipy.ndimage as nd
    im = mpimg.imread(png)[..., :3] * 255
    fx0, fx1, fy0, fy1 = _frame(im)
    G = vp.LinAxis(fx0, 2.0, fx1, 3.4)
    P = vp.LinAxis(fy1, 0.0, fy0, 9.0)
    samples = {"Baikal-GVD 6y cascades": ((255, 0, 0), "90%"), "IceCube 7.5y HESE": ((0, 0, 255), "95%"),
               "IceCube 6y cascades": ((255, 128, 0), "95%"), "IceCube 9.5y tracks": ((0, 128, 0), "95%")}
    legend = (int(fy0), int(P.page(6.6)), int(G.page(2.68)), int(fx1))   # rows, cols of the legend
    rows = []
    for name, (colour, outer) in samples.items():
        mask = np.abs(im - np.array(colour)).max(axis=2) < 70
        mask[:int(fy0) + 8] = False; mask[int(fy1) - 8:] = False
        mask[:, :int(fx0) + 8] = False; mask[:, int(fx1) - 8:] = False
        lm = mask.copy(); lm[legend[0]:legend[1], legend[2]:legend[3]] = False
        core = nd.binary_erosion(lm, np.ones((9, 9)))
        lab, n = nd.label(core)
        best, k = 0, None
        for j, sl in enumerate(nd.find_objects(lab), 1):          # compact blob = marker, not a line
            h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            area = (lab[sl] == j).sum()
            if max(h, w) < 1.8 * min(h, w) and area / (h * w) > 0.35 and area > best:
                best, k = area, j
        cy, cx = nd.center_of_mass(lab == k)
        rows.append([name, "best_fit", float(G.value(cx)), float(P.value(cy))])
        mask[legend[0]:legend[1], legend[2]:legend[3]] = False
        mask &= ~nd.binary_dilation(lab == k, np.ones((25, 25)))     # drop the marker itself
        inner, outer_r = [], []
        th = np.deg2rad(np.arange(360))
        for t in th:
            r = np.arange(30, 3000, 2.0)
            xs = np.round(cx + r * np.cos(t)).astype(int); ys = np.round(cy - r * np.sin(t)).astype(int)
            ok = (xs > 0) & (xs < im.shape[1]) & (ys > 0) & (ys < im.shape[0])
            hit = r[ok][mask[ys[ok], xs[ok]]]
            inner.append(hit.min() if len(hit) else np.nan)
            outer_r.append(hit.max() if len(hit) else np.nan)
        inner, outer_r = np.array(inner), np.array(outer_r)
        outer_r[outer_r - inner < 25] = np.nan               # ray went through a gap of the dashed contour
        for level, rad in (("68%", inner), (outer, outer_r)):
            good = np.isfinite(rad)
            rad = np.interp(np.arange(360), np.arange(360)[good], rad[good], period=360)
            wide = np.array([np.median(np.take(rad, range(i - 10, i + 11), mode="wrap")) for i in range(360)])
            bad = np.abs(rad - wide) > 0.12 * wide              # labels / other contours crossing the ray
            rad[bad] = np.nan
            good = np.isfinite(rad)
            rad = np.interp(np.arange(360), np.arange(360)[good], rad[good], period=360)
            rad = np.array([np.median(np.take(rad, range(i - 4, i + 5), mode="wrap")) for i in range(360)])
            rad = np.array([np.mean(np.take(rad, range(i - 2, i + 3), mode="wrap")) for i in range(360)])
            for t, rr in zip(th, rad):
                rows.append([name, level, float(G.value(cx + rr * np.cos(t))), float(P.value(cy - rr * np.sin(t)))])
    write("gvd2025-contours.csv", ["sample", "level", "gamma", "phi_1e-18"], rows)


def icecube2026_events(pdf):
    """IceCube PRL 136 (2026), arXiv:2507.22233v3, Fig. 1 CF panel (figures/data_mc_globalfit_2panel_2yaxes.pdf).

    Ticks: energy proxy 10^3 -> 10^7 GeV at x = 98.7 -> 379.6; tracks (left axis)
    10^-3 -> 10^6 and cascades (right axis) 10^-1 -> 10^8 at y = 302.3 -> 24.2;
    ratio panel 0.5 -> 1.5 at y = 392.8 -> 323.2.
    """
    ps = vp.paths(pdf)
    X = vp.LogAxis(98.7, 1e3, 379.6, 1e7)
    YT = vp.LogAxis(302.3, 1e-3, 24.2, 1e6)
    YC = vp.LogAxis(302.3, 1e-1, 24.2, 1e8)
    R = vp.LinAxis(392.8, 0.5, 323.2, 1.5)
    legend = lambda b: b[0] > 255 and b[3] < 166
    rows = []
    def poly(name, sel, Y):
        p = next(q for q in ps if sel(q) and not legend(q.bbox()))
        for x, y in p.points:
            rows.append([name, float(X.value(min(max(x, 63.6), 379.6))), float(Y.value(min(y, 302.3)))])
    poly("tracks_total_mc", lambda q: q.fill == (214, 39, 40) and len(q.points) > 50, YT)
    poly("tracks_bkg", lambda q: q.stroke == (128, 128, 128) and q.dash and len(q.points) > 50, YT)
    poly("tracks_astro", lambda q: q.stroke == (214, 39, 40) and q.dash and len(q.points) > 50, YT)
    poly("cascades_total_mc", lambda q: q.fill == (31, 119, 180) and len(q.points) > 30, YC)
    poly("cascades_bkg", lambda q: q.stroke == (0, 0, 0) and q.dash and len(q.points) > 30, YC)
    poly("cascades_astro", lambda q: q.stroke == (176, 224, 230) and len(q.points) > 30, YC)
    write("icecube2026-events-curves.csv", ["curve", "e_proxy_gev", "events"], rows)
    segs = [sp for p in ps if p.stroke == (0, 0, 0) and p.dash is None for sp in p.subpaths
            if len(sp) == 2 and abs(sp[0, 0] - sp[1, 0]) < 1e-3 and abs(sp[0, 1] - sp[1, 1]) > 1
            and not legend((sp[0, 0], sp[:, 1].min(), sp[0, 0], sp[:, 1].min())) and sp[:, 1].min() > 24.0]
    pts = []
    for p in ps:
        b = p.bbox()
        if legend(b) or not (63 < b[0] < 380):
            continue
        square = len(p.subpaths[0]) == 5 and (p.stroke == (0, 0, 0) or p.fill == (255, 255, 255)) and b[2] - b[0] < 7
        circle = p.fill == (0, 0, 0) and len(p.subpaths[0]) > 20 and b[2] - b[0] < 7
        if not (square or circle):
            continue
        x, y = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        panel = "ratio" if y > 315 else "main"
        kind = "tracks" if square else "cascades"
        Y = R if panel == "ratio" else (YT if square else YC)
        bars = [v for sp in segs if abs(sp[0, 0] - x) < 0.3 and (sp[:, 1].min() - 4 <= y <= sp[:, 1].max() + 4)
                for v in sp[:, 1]]
        lo = float(Y.value(max(bars))) if bars else np.nan
        hi = float(Y.value(min(bars))) if bars else np.nan
        key = (kind, panel, round(x, 1), round(y, 1))
        if any((r[0], r[1], round(X.page(r[2]), 1), round(Y.page(r[3]) if not np.isnan(r[3]) else 0, 1)) == key for r in pts):
            continue
        pts.append([kind, panel, float(X.value(x)), float(Y.value(y)), lo, hi])
    # de-duplicate fill+stroke pairs of the same marker
    uniq = {}
    for r in pts:
        uniq[(r[0], r[1], round(r[2], 3), round(r[3], 4))] = r
    write("icecube2026-events-data.csv", ["sample", "panel", "e_proxy_gev", "value", "lo", "hi"], list(uniq.values()))


if __name__ == "__main__":
    {"icecube2013": icecube2013, "icecube2013_zenith": lambda f: icecube2013(f, "zenith"), "icecube2026": icecube2026, "gvd2025_energy": gvd2025_energy, "gvd2025_zenith": lambda f: gvd2025_energy(f, "zenith"), "gvd2025_spectrum": gvd2025_spectrum, "zathul": zathul, "icecube2026_events": icecube2026_events, "gvd2025_contours": gvd2025_contours, "icecube2026_indices": icecube2026_indices}[sys.argv[1]](sys.argv[2])
