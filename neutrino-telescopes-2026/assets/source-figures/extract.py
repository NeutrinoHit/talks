"""Extract plotted values from the vector artwork of point-source figures.

    python extract.py <figure> /path/to/original/file

The original file comes from the paper's arXiv source archive and is not
stored here. CSV tables are written to data/; build.py draws only from them.
Axis calibration uses drawn tick marks; values are exact up to the drawing
precision of the original, except where a docstring says otherwise.
"""
import base64
import csv
import io
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "evidence"))
import vector_paths as vp  # noqa: E402

DATA = HERE / "data"


def write(name, header, rows):
    DATA.mkdir(exist_ok=True)
    with (DATA / name).open("w", newline="") as stream:
        w = csv.writer(stream)
        w.writerow(header)
        for r in rows:
            w.writerow([f"{v:.6g}" if isinstance(v, float) else v for v in r])
    print(f"{len(rows)} rows -> data/{name}")


def embedded_image(pdf, index=0):
    """Decode the index-th embedded PNG of the Poppler SVG as an RGB array."""
    import matplotlib.image as mpimg
    svg = vp.to_svg(pdf).read_text()
    data = re.findall(r'xlink:href="data:image/png;base64,([^"]+)"', svg)[index]
    return mpimg.imread(io.BytesIO(base64.b64decode(data)), format="png")[..., :3] * 255


def txs_flare(pdf):
    """IceCube, Science 361, 147 (2018), arXiv:1807.08794v1, Fig. 2 (fig2_Tdep_IC86b_lightcurve.pdf).

    Event weights are read from the bar heights. The muon-energy proxy is
    colour-coded in the original; it is decoded by matching each bar colour to
    the embedded colour-bar image (log scale, 0.1-20 TeV ticks), so it is
    approximate (one colour-bar pixel is about 0.4% of a decade x 85 = ~6%).
    """
    ps = vp.paths(pdf)
    T = vp.LinAxis(71.93, 56200, 272.09, 57000)            # MJD tick marks
    W = vp.LinAxis(108.31, 1.0, 35.38, 4.0)                # log10 weight tick marks
    C = vp.LogAxis(108.31, 0.1, 34.39, 10.0)               # colour-bar ticks, TeV
    bar = embedded_image(pdf)                              # 357 x 18 px, top = high energy
    y_top, y_bot = 23.137, 23.137 + 0.238528 * bar.shape[0]
    ramp = bar[:, bar.shape[1] // 2, :]
    rows = []
    for p in ps:
        if isinstance(p.fill, tuple) and p.fill not in ((0, 0, 0), (255, 255, 255)) and p.bbox()[0] < 313:
            x0, y0, x1, y1 = p.bbox()
            k = int(np.argmin(((ramp - np.array(p.fill)) ** 2).sum(axis=1)))
            y_c = y_top + (k + 0.5) * (y_bot - y_top) / bar.shape[0]
            rows.append([float(T.value(0.5 * (x0 + x1))), float(W.value(y0)), float(C.value(y_c))])
    rows.sort()
    write("txs-flare-events.csv", ["mjd", "log10_weight", "muon_energy_proxy_tev_approx"], rows)
    box = next(p for p in ps if p.stroke == (0, 0, 0) and len(p.points) == 4).points
    gauss = next(p for p in ps if p.stroke == (0, 0, 0) and p.dash and len(p.points) > 20).points
    curves = [["box", float(T.value(x)), float(W.value(y))] for x, y in box]
    curves += [["gaussian", float(T.value(x)), float(W.value(y))] for x, y in gauss if x <= 312.12]
    write("txs-flare-fits.csv", ["curve", "mjd", "log10_weight_axis"], curves)


def ngc_scan(pdf):
    """IceCube, arXiv:2510.13403v2, Fig. 2 right (finescan_ngc1068_fixed.pdf).

    The local-significance map is an embedded raster; each pixel colour is
    matched to the embedded colour bar to recover -log10(p_local). Values are
    therefore quantized to the colour-bar resolution (about 0.005). The 68% and
    95% contours and the markers are vector paths.
    """
    ps = vp.paths(pdf)
    RA = vp.LinAxis(83.1, 41.0, 179.35, 40.4)              # tick marks
    DEC = vp.LinAxis(206.57, -0.4, 78.24, 0.4)
    V = vp.LinAxis(68.59, 1.0, 188.96, 6.0)                # colour-bar ticks
    scale, x0, y_map, y_bar = 0.119574, 50.967231, 54.04621, 34.074854
    img, bar = embedded_image(pdf, 1), embedded_image(pdf, 3)
    ramp = bar[bar.shape[0] // 2]
    ramp_v = V.value(x0 + (np.arange(ramp.shape[0]) + 0.5) * scale)
    step = 5                                               # 1275 px -> 255 samples
    sub = img[step // 2::step, step // 2::step]
    d = ((sub[:, :, None, :] - ramp[None, None, ::3, :]) ** 2).sum(-1)
    value = ramp_v[::3][np.argmin(d, axis=2)]
    centres = x0 + (np.arange(step // 2, img.shape[1], step) + 0.5) * scale
    ra = RA.value(centres)
    dec = DEC.value(y_map + (np.arange(step // 2, img.shape[0], step) + 0.5) * scale)
    DATA.mkdir(exist_ok=True)
    np.savez_compressed(DATA / "ngc1068-scan-grid.npz", ra_deg=ra, dec_deg=dec, neg_log10_p_local=value)
    print(f"{value.shape} grid -> data/ngc1068-scan-grid.npz; range {value.min():.2f}-{value.max():.2f}")
    rows = []
    for name, sel in (("68%", lambda p: p.stroke == (255, 255, 255) and p.dash is None),
                      ("95%", lambda p: p.stroke == (255, 255, 255) and p.dash)):
        p = next(q for q in ps if sel(q) and len(q.points) > 20)
        rows += [[name, float(RA.value(x)), float(DEC.value(y))] for x, y in p.points]
    ngc = next(p for p in ps if p.stroke == (255, 165, 0) and p.bbox()[1] > 100).bbox()
    best = next(p for p in ps if p.fill == (255, 255, 255) and p.stroke == (0, 0, 0) and p.bbox()[1] > 100).bbox()
    for name, b in (("NGC 1068", ngc), ("best fit", best)):
        rows.append([name, float(RA.value((b[0] + b[2]) / 2)), float(DEC.value((b[1] + b[3]) / 2))])
    write("ngc1068-scan-contours.csv", ["item", "ra_deg", "dec_deg"], rows)


def _segments(ps, colour):
    out = []
    for p in ps:
        if p.stroke == colour:
            for sp in p.subpaths:
                if len(sp) == 2:
                    out.append(sp)
    return out


def points_and_limits(ps, colour, X, Y, keep):
    """Markers with error bars, and arrow upper limits, of one colour.

    Markers are filled closed curves (>10 vertices); arrows are filled
    triangles. `keep(bbox)` excludes the legend.
    """
    segs = [s for s in _segments(ps, colour) if keep((s[:, 0].min(), s[:, 1].min(), s[:, 0].max(), s[:, 1].max()))]
    vert = [s for s in segs if abs(s[0, 0] - s[1, 0]) < 1e-3]
    horiz = [s for s in segs if abs(s[0, 1] - s[1, 1]) < 1e-3 and abs(s[0, 0] - s[1, 0]) > 1e-3]
    markers, arrows = [], []
    for p in ps:
        if p.fill == colour and keep(p.bbox()):
            n = len(p.subpaths[0])
            b = p.bbox()
            (markers if n > 10 else arrows if n == 3 else []).append(b)
    markers = list({(round(b[0], 2), round(b[1], 2)): b for b in markers}.values())
    arrows = list({(round(b[0], 2), round(b[1], 2)): b for b in arrows}.values())
    rows = []
    for b in markers:
        x, y = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        hx = [v for s in horiz if abs(s[0, 1] - y) < 0.3 and s[:, 0].min() - 0.3 <= x <= s[:, 0].max() + 0.3
              for v in s[:, 0]] or [x]
        arrow = any(abs((a[0] + a[2]) / 2 - x) < 0.3 for a in arrows)
        r = 0.5 * (b[3] - b[1]) + 0.3                     # bar must pass through or start at this marker
        vy = [v for s in vert if abs(s[0, 0] - x) < 0.3 and
              (s[:, 1].min() - r <= y <= s[:, 1].max() + r) for v in s[:, 1]] or [y]
        if arrow:                                          # marker drawn on an upper limit
            rows.append(["upper_limit", float(X.value(x)), float(Y.value(y)), np.nan, np.nan,
                         float(X.value(min(hx + [x]))), float(X.value(max(hx + [x])))])
            continue
        rows.append(["point", float(X.value(x)), float(Y.value(y)), float(Y.value(max(vy + [y]))),
                     float(Y.value(min(vy + [y]))), float(X.value(min(hx + [x]))), float(X.value(max(hx + [x])))])
    for b in arrows:
        x = (b[0] + b[2]) / 2
        stem = [s for s in vert if abs(s[0, 0] - x) < 0.3 and abs(s[:, 1].max() - b[1]) < 0.5]
        if not stem:
            continue
        top = stem[0][:, 1].min()
        hx = [v for s in horiz if abs(s[0, 1] - top) < 0.3 for v in s[:, 0]] or [x]
        if any(abs((m[0] + m[2]) / 2 - x) < 0.3 for m in markers):
            continue
        rows.append(["upper_limit", float(X.value(x)), float(Y.value(top)), np.nan, np.nan,
                     float(X.value(min(hx))), float(X.value(max(hx)))])
    return rows


def ngc_sed(pdf):
    """IceCube, Science 378, 538 (2022), arXiv:2211.09972v1, Fig. 4 (fig4.pdf)."""
    ps = vp.paths(pdf)
    X = vp.LogAxis(91.61, 1e-15, 372.56, 1e6)             # GeV, tick marks
    Y = vp.LogAxis(207.9, 1e-14, 50.23, 1e-9)             # TeV cm^-2 s^-1
    keep = lambda b: b[1] > 40                              # legend is above the frame
    rows = []
    for name, colour in (("archival", (104, 104, 104)), ("4FGL-DR2", (51, 160, 44)), ("MAGIC", (178, 223, 138))):
        rows += [[name] + r for r in points_and_limits(ps, colour, X, Y, keep)]
    write("ngc1068-sed-points.csv", ["dataset", "kind", "e_gev", "e2flux", "e2flux_lo", "e2flux_hi",
                                     "e_lo_gev", "e_hi_gev"], rows)
    curves = []
    for name, sel in (("icecube_band", lambda p: p.fill == (52, 62, 120)),
                      ("icecube_best", lambda p: p.stroke == (52, 62, 120) and p.dash is None and p.fill is None),
                      ("icecube_edge_lo", lambda p: p.stroke == (52, 62, 120) and p.dash and p.bbox()[1] > 100),
                      ("icecube_edge_hi", lambda p: p.stroke == (52, 62, 120) and p.dash and p.bbox()[1] < 100),
                      ("inoue_band", lambda p: p.fill == (152, 198, 234)),
                      ("murase", lambda p: p.stroke == (204, 204, 198))):
        p = next(q for q in ps if sel(q) and keep(q.bbox()))
        pts = np.vstack([sp for sp in p.subpaths if len(sp) > 1])
        pts[:, 1] = np.minimum(pts[:, 1], 1e4)             # clipped band edges far below the frame
        curves += [[name, float(X.value(x)), float(Y.value(y))] for x, y in pts]
    write("ngc1068-sed-curves.csv", ["curve", "e_gev", "e2flux"], curves)


def radio_sky(pdf):
    """Plavin, Kovalev, Kovalev, Troitsky, ApJ 894, 101 (2020), arXiv:2001.00930v3, Fig. 1 (figures/skymap.pdf).

    The original is a composite: four binary raster layers (enlarged and
    original IceCube error ellipses, the Galactic plane, the complete VLBI
    sample as dots), vector graticule and vector stars coloured by 8 GHz VLBI
    flux density. The layers are stored unchanged as masks with their page
    placement; star colours are converted to flux density with the embedded
    colour bar (log scale, ticks 0.15-15 Jy). Everything stays in the page
    coordinates of the original, so the projection is unchanged.
    """
    import matplotlib.pyplot as plt
    ps = vp.paths(pdf)
    scale = 0.239422
    layers = {"ellipses_enlarged": (1, 36.635748, 55.067027), "ellipses_original": (3, 38.072279, 56.024714),
              "galactic_plane": (5, 131.925646, 33.040216), "vlbi_sample": (7, 25.861764, 4.549015)}
    meta = []
    for name, (k, x0, y0) in layers.items():
        img = embedded_image(pdf, k)
        mask = img.mean(axis=2) < 250
        plt.imsave(DATA / f"radio-sky-{name}.png", mask, cmap="gray_r", vmin=0, vmax=1)
        meta.append([name, x0, y0, x0 + scale * mask.shape[1], y0 + scale * mask.shape[0]])
    write("radio-sky-layers.csv", ["layer", "x0_pt", "y0_pt", "x1_pt", "y1_pt"], meta)
    bar = embedded_image(pdf, 8)
    ramp = bar[bar.shape[0] // 2]
    F = vp.LogAxis(262.2, 1.0, 515.9, 10.0)                # colour-bar tick marks (Jy)
    ramp_f = F.value(53.155856 + (np.arange(ramp.shape[0]) + 0.5) * scale)
    stars = []
    for i, p in enumerate(q for q in ps if isinstance(q.fill, tuple)
                          and q.fill not in ((0, 0, 0), (38, 38, 38), (255, 255, 255)) and q.bbox()[3] < 300):
        k = int(np.argmin(((ramp - np.array(p.fill)) ** 2).sum(axis=1)))
        for x, y in p.subpaths[0]:
            stars.append([i, float(ramp_f[k]), float(x), float(y)])
    write("radio-sky-stars.csv", ["star", "vlbi_flux_jy", "x_pt", "y_pt"], stars)
    grid = []
    for i, p in enumerate(q for q in ps if q.stroke == (204, 204, 204) and q.bbox()[3] < 300):
        for j, sp in enumerate(p.subpaths):
            grid += [[f"{i}.{j}", float(x), float(y)] for x, y in sp]
    write("radio-sky-graticule.csv", ["line", "x_pt", "y_pt"], grid)
    names = {"0506": "TXS 0506+056", "2145": "PKS 2145+067", "1741": "PKS 1741−038",
             "1730": "NRAO 530", "1253": "3C 279"}
    labels = [[names[w[0]], w[1], w[4]] for w in vp.words(pdf) if w[0] in names]
    visible = ("60°", "45°", "30°", "15°", "0°", "-15°", "-30°", "-45°", "-60°", "-75°",
               "12h", "10h", "8h", "6h", "4h", "2h", "0h", "22h", "20h", "18h", "16h", "14h")
    labels += [[w[0].replace("-", "−"), w[1], w[4]] for w in vp.words(pdf)
               if w[0] in visible and not (w[2] > 120 and w[2] < 130 and w[0].endswith("°"))]
    write("radio-sky-labels.csv", ["text", "x_pt", "y_baseline_pt"], labels)


def radio_flux(pdf):
    """Plavin et al., ApJ 894, 101 (2020), arXiv:2001.00930v3, Fig. 3 (figures/avg_flux.pdf)."""
    ps = vp.paths(pdf)
    F = vp.LogAxis(107.86, 1.0, 238.76, 10.0)            # tick marks (Jy)
    rows = []
    for p in ps:
        if p.stroke == (25, 25, 25) and abs(p.width - 0.5) < 0.05 and p.bbox()[1] > 50:
            rows.append(["individual_neutrino_agn", float(F.value(p.bbox()[0])), np.nan, np.nan])
    tri = next(p for p in ps if p.fill == (25, 25, 25) and p.bbox()[1] > 50).bbox()
    rows.append(["neutrino_agn_average", float(F.value((tri[0] + tri[2]) / 2)), np.nan, np.nan])
    bar = next(p for p in ps if p.stroke == (31, 119, 180) and abs(p.width - 1.5) < 0.05 and p.bbox()[1] > 50).bbox()
    tick = next(p for p in ps if p.stroke == (31, 119, 180) and abs(p.width - 1.0) < 0.05 and p.bbox()[1] > 50).bbox()
    rows.append(["random_average_68pct", float(F.value(tick[0])), float(F.value(bar[0])), float(F.value(bar[2]))])
    write("radio-flux-average.csv", ["item", "flux_jy", "interval_lo_jy", "interval_hi_jy"], rows)


def txs_radio(png):
    """Baikal-GVD, ICRC 2023, arXiv:2308.13686v1, Fig. 4 (lc_Fermi_RATAN_11GHz.png), digitized.

    Tick marks: epoch 2010 -> 2022 at x = 147.5 -> 1479.5 px; Fermi-LAT flux
    0 -> 8e-7 ph cm^-2 s^-1 at y = 654 -> 51.5 px (left axis); RATAN-600 11 GHz
    0 -> 2 Jy at y = 656 -> 177.5 px (right axis).
    Fermi points: filled black markers with vertical bars. RATAN: open red
    diamonds located as connected components (merged clusters split by k-means
    with the single-diamond area); their small error bars are not digitized.
    Flare model: thick dark-red sum and thin dashed components, separated by
    stroke thickness.
    """
    import matplotlib.image as mpimg
    import scipy.ndimage as nd
    im = (mpimg.imread(png)[..., :3] * 255).round()
    T = vp.LinAxis(147.5, 2010.0, 1479.5, 2022.0)
    F = vp.LinAxis(654.0, 0.0, 51.5, 8.0)            # 1e-7 ph cm^-2 s^-1
    R = vp.LinAxis(656.0, 0.0, 177.5, 2.0)           # Jy
    frame = (4, 667, 150, 1566)
    legend = (0, 190, 120, 640)                      # rows, cols of the legend box
    inside = np.zeros(im.shape[:2], bool)
    inside[frame[0]:frame[1], frame[2]:frame[3]] = True
    inside[legend[0]:legend[1], legend[2]:legend[3]] = False
    # Fermi-LAT
    blk = (im.max(axis=2) < 70) & inside
    core = nd.binary_erosion(blk, np.ones((5, 5)))
    lab, n = nd.label(core)
    fermi = []
    for k, sl in enumerate(nd.find_objects(lab), 1):
        cy, cx = nd.center_of_mass(lab == k)
        c, r = int(round(cx)), int(round(cy))
        up = r
        while blk[up - 1, c - 1:c + 2].any() and up > frame[0] + 1:
            up -= 1
        down = r
        while blk[down + 1, c - 1:c + 2].any() and down < frame[1] - 1:
            down += 1
        fermi.append([float(T.value(cx)), float(F.value(cy)), float(F.value(down)), float(F.value(up))])
    fermi.sort()
    write("txs-lightcurve-fermi.csv", ["epoch_yr", "flux_1e-7_ph_cm2_s", "lo", "hi"], fermi)
    # RATAN-600 diamonds
    red = (im[..., 0] > 200) & (im[..., 1] < 80) & (im[..., 2] < 80) & inside
    red[:, 1560:] = False
    lab, n = nd.label(nd.binary_closing(red, np.ones((3, 3))))
    sizes = nd.sum(red, lab, range(1, n + 1))
    single = np.median([sz for sz in sizes if sz > 15])
    ratan = []
    for k in range(1, n + 1):
        if sizes[k - 1] < 0.4 * single:
            continue
        ys, xs = np.where(lab == k)
        m = max(1, int(round(sizes[k - 1] / single)))
        pts = np.c_[xs, ys].astype(float)
        cent = pts[np.linspace(0, len(pts) - 1, m).astype(int)]
        for _ in range(30):                                # k-means on pixel coordinates
            d = ((pts[:, None, :] - cent[None]) ** 2).sum(-1)
            lbl = d.argmin(1)
            cent = np.array([pts[lbl == j].mean(0) if (lbl == j).any() else cent[j] for j in range(m)])
        # an open diamond's centroid is its centre
        ratan += [(x, y) for x, y in cent]
    dark0 = (np.abs(im - np.array([176, 44, 44])).max(axis=2) < 40) & inside
    bars = np.zeros_like(dark0)
    ratan_rows = []
    for x, y in sorted(ratan):
        c, r = int(round(x)), int(round(y))
        up, down = r - 7, r + 7                          # diamond half-height ~7 px
        while up > frame[0] + 1 and dark0[up - 1, c - 1:c + 2].any() and not dark0[up - 1, c - 4:c + 5].all():
            up -= 1
        while down < frame[1] - 1 and dark0[down + 1, c - 1:c + 2].any() and not dark0[down + 1, c - 4:c + 5].all():
            down += 1
        bars[up:down + 1, c - 2:c + 3] = True
        ratan_rows.append([float(T.value(x)), float(R.value(y)),
                           float(R.value(down)) if down > r + 7 else float(R.value(y)),
                           float(R.value(up)) if up < r - 7 else float(R.value(y))])
    write("txs-lightcurve-ratan.csv", ["epoch_yr", "flux_jy", "lo", "hi"], ratan_rows)
    # flare model curves (dark red); thick = sum, thin dashed = components
    dark = (np.abs(im - np.array([176, 44, 44])).max(axis=2) < 40) & inside
    dark[:, 1548:] = False                                 # right-axis tick marks
    dt = nd.distance_transform_edt(dark)
    core = nd.binary_dilation(dt >= 2.0, np.ones((3, 3))) & dark     # thick stroke (sum)
    thin = dark & ~nd.binary_dilation(core, np.ones((7, 7))) & ~bars   # thin dashed strokes, minus RATAN bars
    model = []
    for c in range(frame[2] + 2, 1546, 3):
        for kind, mask in (("sum", core), ("component", thin)):
            idx = np.where(mask[:, c])[0]
            if not len(idx):
                continue
            for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
                model.append([kind, float(T.value(c)), float(R.value(run.mean()))])
    s_pts = sorted((r for r in model if r[0] == "sum"), key=lambda r: r[1])
    ys = np.array([r[2] for r in s_pts])
    keep = [abs(y - np.median(ys[max(0, i - 6):i + 7])) < 0.08 for i, y in enumerate(ys)]
    model = [r for r in model if r[0] != "sum"] + [r for r, k in zip(s_pts, keep) if k]
    write("txs-lightcurve-flares.csv", ["curve", "epoch_yr", "flux_jy"], model)
    grey = (np.abs(im - np.array([168, 168, 168])).max(axis=2) < 12) & inside
    rows = np.where(grey.sum(axis=1) > 400)[0]
    median = float(F.value(rows.mean()))
    blue = (np.abs(im - np.array([0, 120, 248])).max(axis=2) < 40) & inside
    vcols = np.where(blue.sum(axis=0) > 200)[0]
    groups = np.split(vcols, np.where(np.diff(vcols) > 3)[0] + 1)
    band = (np.abs(im - np.array([168, 168, 240])).max(axis=2) < 20) & inside
    bcols = np.where(band.sum(axis=0) > 300)[0]
    marks = [["fermi_median", median, np.nan]] + [["neutrino_line", float(T.value(g.mean())), np.nan] for g in groups]
    marks.append(["icecube_2014_band", float(T.value(bcols.min())), float(T.value(bcols.max()))])
    write("txs-lightcurve-marks.csv", ["item", "value", "value2"], marks)


def _baikal_table(tex):
    """Table 1 of arXiv:2603.21261v2: name, dec, and the three 90% limits as printed."""
    rows = []
    for line in Path(tex).read_text().splitlines():
        f = [x.strip() for x in line.split("&")]
        if len(f) != 8 or f[0].startswith("Name"):
            continue
        num = lambda x: float(re.search(r"[-+]?\d+(?:\.\d+)?", x).group(0))
        rows.append((re.sub(r"\\bf |[{}]", "", f[0]).strip(), num(f[1]), num(f[5]), num(f[6]), num(f[7])))
    return rows


def baikal_limits(pdf, table_tex):
    """Baikal-GVD, arXiv:2603.21261v2, Fig. 2: limits from Table 1 (scaled), sensitivities from the vector curves.

    The power of ten of each Table 1 column is fixed by matching the table to the
    plotted markers at the same declinations (the figure confirms the table).
    """
    ps = vp.paths(pdf)
    S = vp.LinAxis(101.21, -1.0, 837.21, 0.6)
    Y = vp.LogAxis(577.59, 1e-9, 20.34, 1.0)
    table = _baikal_table(table_tex)
    colours = {"2.0": (0, 0, 0), "2.5": (65, 105, 225), "3.2": (0, 139, 139)}
    out, scales = [], {}
    for k, (gamma, colour) in enumerate(colours.items()):
        marks = [p.bbox() for p in ps if p.fill in (colour, (255, 0, 0)) and len(p.subpaths) == 2
                 and p.bbox()[2] - p.bbox()[0] < 12 and 20.5 < p.bbox()[1] < 577]
        ratios = []
        for name, dec, *lims in table:
            x = S.page(np.sin(np.deg2rad(dec)))
            near = [m for m in marks if abs((m[0] + m[2]) / 2 - x) < 0.6]
            if near:
                vals = [Y.value((m[1] + m[3]) / 2) / lims[k] for m in near]
                ratios.append(min(vals, key=lambda v: abs(np.log10(v) - np.median(np.log10(vals)))))
        scale = 10 ** np.round(np.median(np.log10(ratios)))
        scales[gamma] = (scale, float(np.median(ratios) / scale))
        for name, dec, *lims in table:
            out.append([gamma, name, dec, float(lims[k] * scale)])
    write("baikal-limits-table1.csv", ["gamma", "source", "dec_deg", "limit_gev_gamma_minus_1_cm2_s"], out)
    curves = []
    for gamma, colour in colours.items():
        p = next(q for q in ps if q.stroke == colour and abs(q.width - 2.0) < 0.1 and len(q.points) > 50)
        curves += [[gamma, float(S.value(x)), float(Y.value(y))] for x, y in p.points if x <= 837.3]
    write("baikal-limits-sensitivity.csv", ["gamma", "sin_dec", "sensitivity"], curves)
    print("column scales and marker/table agreement:", scales)


def baikal_antares(pdf):
    """Baikal-GVD, arXiv:2603.21261v2, Fig. 3: ANTARES 15-yr limits (open markers) from the vector artwork.

    Baikal-GVD points are those of Table 1 (baikal-limits-table1.csv); the GVD
    sensitivity curves are read again from this figure.
    """
    ps = vp.paths(pdf)
    S = vp.LinAxis(104.87, -1.0, 889.38, 0.6)
    Y = vp.LogAxis(577.59, 1e-9, 42.98, 1e-4)
    rows = []
    for gamma, colour in (("2.5", (255, 165, 0)), ("2.0", (50, 205, 50))):
        for p in ps:
            if p.stroke == colour and p.fill is None:
                b = p.bbox()
                if b[1] < 85 and b[0] > 450:                      # legend (top right)
                    continue
                rows.append([gamma, float(S.value((b[0] + b[2]) / 2)), float(Y.value((b[1] + b[3]) / 2))])
    write("antares-limits-fig3.csv", ["gamma", "sin_dec", "limit_gev_gamma_minus_1_cm2_s"], rows)
    curves = []
    for gamma, colour in (("2.0", (0, 0, 0)), ("2.5", (65, 105, 225))):
        p = next(q for q in ps if q.stroke == colour and abs(q.width - 2.0) < 0.1 and len(q.points) > 50)
        curves += [[gamma, float(S.value(x)), float(Y.value(y))] for x, y in p.points if x <= 925]
    write("baikal-antares-sensitivity.csv", ["gamma", "sin_dec", "sensitivity"], curves)


def xray_spectra(pdf):
    """IceCube, arXiv:2510.13403v2, Fig. 5 (some_seyfert_spectra_broken_PL.pdf): fitted spectral bands."""
    ps = vp.paths(pdf)
    E = vp.LogAxis(57.13, 1e2, 237.6, 1e7)
    Y = vp.LogAxis(151.7, 1e-15, 9.96, 1e-7)
    names = {(218, 162, 28): "Diffuse astrophysical", (70, 130, 180): "NGC 1068", (0, 51, 102): "NGC 7469",
             (192, 27, 60): "CGCG 420-015", (240, 128, 128): "NGC 4151"}
    rows = []
    for colour, name in names.items():
        band = max((p for p in ps if p.fill == colour and p.bbox()[2] < 240), key=lambda p: len(p.points))
        rows += [[name, "band", float(E.value(x)), float(Y.value(y))] for x, y in band.subpaths[0]]
    write("xray-agn-spectra-bands.csv", ["source", "kind", "e_gev", "e2flux_tev_cm2_s"], rows)


def txs_dirs(pdf, out_name):
    """IceCube, ICRC 2023, arXiv:2307.14559v1, Fig. 3 panels (figures/PSTracksv2evtplot.pdf,
    figures/ntv5evts.pdf): event directions, 1-sigma circles and energy proxy.

    Axes are calibrated on the tick marks and their numeric labels; the colour
    of each event is decoded with the embedded colour bar (log10 energy proxy,
    ticks 1.0-5.0), so the proxy is approximate (~0.02).
    """
    ps = vp.paths(pdf)
    words = vp.words(pdf)
    ticks_x = sorted({round(sp[0, 0], 2) for p in ps if p.stroke == (0, 0, 0) and abs(p.width - 0.8) < 0.05
                      for sp in p.subpaths if len(sp) == 2 and abs(sp[0, 0] - sp[1, 0]) < 1e-3
                      and abs(sp[0, 1] - sp[1, 1]) < 5 and sp[:, 1].min() > 230})
    ticks_y = sorted({round(sp[0, 1], 2) for p in ps if p.stroke == (0, 0, 0) and abs(p.width - 0.8) < 0.05
                      for sp in p.subpaths if len(sp) == 2 and abs(sp[0, 1] - sp[1, 1]) < 1e-3
                      and abs(sp[0, 0] - sp[1, 0]) < 5 and sp[:, 0].max() < 60})
    num = lambda w: re.fullmatch(r"\d+(\.\d+)?", w[0]) is not None
    xl = sorted((w for w in words if num(w) and w[2] > 230 and w[1] < 290), key=lambda w: w[1])
    yl = sorted((w for w in words if num(w) and w[1] < 52 and w[2] < 230), key=lambda w: -w[2])
    RA = vp.LinAxis(ticks_x[0], float(xl[0][0]), ticks_x[-1], float(xl[len(ticks_x) - 1][0]))
    DEC = vp.LinAxis(ticks_y[-1], float(yl[0][0]), ticks_y[0], float(yl[len(ticks_y) - 1][0]))
    bar = embedded_image(pdf, 0)
    ramp = bar[:, bar.shape[1] // 2, :]
    cb_ticks = sorted({round(sp[0, 1], 2) for p in ps if p.stroke == (0, 0, 0)
                       for sp in p.subpaths if len(sp) == 2 and sp[:, 0].min() > 300 and abs(sp[0, 1] - sp[1, 1]) < 1e-3})
    E = vp.LinAxis(cb_ticks[-1], 1.0, cb_ticks[0], 5.0)
    y_bar0 = 15.0
    energy = lambda c: float(E.value(y_bar0 + int(np.argmin(((ramp - np.array(c)) ** 2).sum(axis=1))) + 0.5))
    rows = []
    for p in ps:
        if isinstance(p.stroke, tuple) and p.fill is None and abs(p.width - 2.0) < 0.05 and len(p.points) > 30:
            b = p.bbox()
            rows.append(["circle", float(RA.value((b[0] + b[2]) / 2)), float(DEC.value((b[1] + b[3]) / 2)),
                         float((b[2] - b[0]) / 2 * abs(RA.scale)), energy(p.stroke), int(p.dash is not None)])
        elif isinstance(p.stroke, tuple) and p.fill is None and abs(p.width - 3.0) < 0.05 and np.ptp(p.points[:, 0]) < 1e-3:
            x, y = p.points[0]
            rows.append(["event", float(RA.value(x)), float(DEC.value(y)), np.nan, energy(p.stroke), 0])
    txs = [p.bbox() for p in ps if p.fill == (0, 0, 0) and abs(p.width - 4.0) < 0.05]
    txs = min(txs, key=lambda b: abs(b[1] - 150))
    rows.append(["TXS 0506+056", float(RA.value((txs[0] + txs[2]) / 2)), float(DEC.value((txs[1] + txs[3]) / 2)), np.nan, np.nan, 0])
    for w in words:
        if w[0].startswith("MJD:"):
            rows.append(["label " + w[0], float(RA.value(w[1])), float(DEC.value(w[4])), np.nan, np.nan, 0])
    write(out_name, ["kind", "ra_deg", "dec_deg", "sigma_deg", "log10_energy_proxy_approx", "dashed"], rows)


def xray_population(pdf):
    """IceCube, arXiv:2510.13403v2, X-ray population test without NGC 1068
    (population_excess_seyfert_floating_gamma_without_NGC1068.pdf).

    Ticks: N sources 0 -> 33 at x = 52.0 -> 203.6 (the broken-axis segment holds
    N = 47 at x = 244.5); p_local 1e-6 -> 1 at y = 31.5 -> 120.5; p_binom
    1e-1 -> 1e-5 at y = 138.2 -> 176.9.
    """
    ps = vp.paths(pdf)
    N = vp.LinAxis(52.0, 0.0, 203.6, 33.0)
    N_right = lambda x: 47.0 + (x - 244.5) / (N.scale ** -1)
    PL = vp.LogAxis(120.5, 1.0, 31.5, 1e-6)
    PB = vp.LogAxis(138.2, 1e-1, 176.9, 1e-5)
    nval = lambda x: float(N.value(x)) if x < 220 else float(N_right(x))
    rows = []
    for shade, colour in (("3sigma", (183, 216, 242)), ("2sigma", (122, 186, 229)), ("1sigma", (31, 119, 180))):
        band = [p for p in ps if p.fill == colour]
        for part, b in zip(("main", "right"), sorted(band, key=lambda p: p.bbox()[0], reverse=True)):
            rows += [[f"band_{shade}_{part}", nval(x) if part == "main" else float(N_right(x)), float(PL.value(y))]
                     for x, y in b.subpaths[0]]
    for p in ps:
        if p.stroke == (0, 0, 0) and p.dash and p.bbox()[1] > 12 and p.bbox()[3] < 125 and len(p.points) > 2:
            rows += [["bkg_expectation", nval(x), float(PL.value(y))] for x, y in p.points]
        if p.fill == (0, 0, 0) and p.stroke == (255, 255, 255) and p.bbox()[1] > 40 and not (
                110 < p.bbox()[0] < 150 and p.bbox()[1] < 50):           # legend marker
            b = p.bbox()
            rows.append(["observed", nval((b[0] + b[2]) / 2), float(PL.value((b[1] + b[3]) / 2))])
        if p.stroke == (0, 0, 0) and abs(p.width - 2.0) < 0.05 and p.bbox()[1] > 123:
            rows += [["p_binom", nval(x), float(PB.value(y))] for x, y in p.points]
    star = next(p for p in ps if p.fill == (218, 162, 28)).bbox()
    rows.append(["ngc1068_excluded", nval((star[0] + star[2]) / 2), float(PL.value((star[1] + star[3]) / 2))])
    thr = next(p for p in ps if p.stroke == (255, 0, 0) and abs(p.points[0, 1] - p.points[1, 1]) < 1e-3 and p.bbox()[1] > 90)
    rows.append(["max_deviation", float(N.value(thr.points[:, 0].max())), float(PL.value(thr.points[0, 1]))])
    write("xray-agn-population.csv", ["item", "n_sources", "p"], rows)


FIGURES = {"xray_population": xray_population, "txs_original": lambda f: txs_dirs(f, "txs-original-directions.csv"), "txs_updated": lambda f: txs_dirs(f, "txs-updated-directions.csv"), "xray_spectra": xray_spectra, "baikal_antares": baikal_antares, "baikal_limits": lambda pdf: baikal_limits(pdf, sys.argv[3]), "txs_radio": txs_radio, "radio_flux": radio_flux, "txs_flare": txs_flare, "ngc_scan": ngc_scan, "ngc_sed": ngc_sed, "radio_sky": radio_sky}

if __name__ == "__main__":
    FIGURES[sys.argv[1]](sys.argv[2])
