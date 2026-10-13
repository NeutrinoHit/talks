"""Digitize the two effective-area figures of the detector-response slide into data/*.csv.

1. IceCube HESE 2010-2012 effective areas (arXiv:1311.5238v2, Fig. 7 top panel), from the
   Poppler vector conversion media/response/icecube-hese-2013-effective-area.svg: exact
   step-histogram vertices. Calibration: dotted decade grid lines (x: 10..10^4 TeV;
   y: 10^-3..10^3 m^2, the bottom grid line coincides with the 10^-3 label).
2. Illustrative IceCube point-source effective areas (Spiering, arXiv:2609.26436v1, Fig. 6),
   only available as a raster (media/response/icecube-directional-area-2026.png): colour
   tracing column by column, calibrated piecewise-linearly on the drawn tick marks.
   Where two curves overlap (red under green below log E = 3.2, red under blue above 8.86),
   the visible upper curve supplies the hidden one.

Run: pyenv exec python digitize_effective_areas.py   (outputs are inputs of build_response_figures.py)
"""
from pathlib import Path
import csv
import re
import numpy as np

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parents[1] / "media/response"
DATA = HERE / "data"
HESE_SVG = MEDIA / "icecube-hese-2013-effective-area.svg"
SPIERING_PNG = MEDIA / "icecube-directional-area-2026.png"

HESE_COLOURS = {"nu_e": "rgb(100%, 0%, 0%)", "nu_mu": "rgb(0%, 50%, 0%)", "nu_tau": "rgb(0%, 0%, 100%)"}

# Spiering Fig. 6 raster: tick-mark centres in pixels (detected from the drawn tick marks).
SP_X_TICKS = {2: 104.0, 3: 204.0, 4: 304.0, 5: 402.5, 6: 497.0, 7: 597.0, 8: 697.0, 9: 797.0}
SP_Y_TICKS = {4: 48.5, 3: 120.0, 2: 191.0, 1: 262.5, 0: 334.0, -1: 405.5, -2: 477.0, -3: 548.0}
SP_COLOURS = {"90-120": (255, 0, 0), "150-180": (0, 176, 80), "0-30": (0, 112, 192)}
SP_SEED = {"90-120": (500, 146), "150-180": (420, 222), "0-30": (600, 130)}  # (column, row) on the visible curve


def _paths(svg):
    for m in re.finditer(r'<path ([^>]*?)d="([^"]*)"([^>]*)/>', svg):
        attrs = m.group(1) + m.group(3)
        n = np.array(list(map(float, re.findall(r"-?\d+\.?\d*", m.group(2)))))
        yield attrs, n[0::2], n[1::2]


def hese_calibration(svg):
    """Return (x_of_logE, y_of_logA) slopes/offsets from the dotted decade grid."""
    vertical, horizontal = [], []
    for attrs, x, y in _paths(svg):
        if 'stroke-dasharray="1 3"' not in attrs or len(x) != 2:
            continue
        (vertical if abs(x[0] - x[1]) < 1e-6 else horizontal).append(x[0] if abs(x[0] - x[1]) < 1e-6 else y[0])
    vertical, horizontal = sorted(vertical), sorted(horizontal)
    if len(vertical) != 4 or len(horizontal) != 7:
        raise ValueError(f"unexpected grid: {len(vertical)} vertical, {len(horizontal)} horizontal")
    kx = np.polyfit(np.arange(1, 5), vertical, 1)      # 10, 100, 1000, 10^4 TeV
    ky = np.polyfit(np.arange(-3, 4), horizontal, 1)   # 10^-3 ... 10^3 m^2
    return kx, ky, vertical, horizontal


def hese_steps(svg_path=HESE_SVG):
    """Rows (flavour, log10 E_lo/TeV, log10 E_hi/TeV, A_eff m^2, below_plot_range)."""
    svg = Path(svg_path).read_text()
    kx, ky, _, _ = hese_calibration(svg)
    rows = []
    for flavour, colour in HESE_COLOURS.items():
        best = max(((x, y) for attrs, x, y in _paths(svg)
                    if f'stroke="{colour}"' in attrs and 'stroke-width="2"' in attrs), key=lambda p: len(p[0]))
        x, y = best
        for i in range(len(x) - 1):
            if abs(y[i] - y[i + 1]) < 1e-6 and x[i + 1] > x[i]:
                lo, hi = (x[i] - kx[1]) / kx[0], (x[i + 1] - kx[1]) / kx[0]
                log_a = (y[i] - ky[1]) / ky[0]
                rows.append((flavour, round(lo, 4), round(hi, 4), 10 ** log_a, bool(log_a < -3)))
    return rows


def _interp_ticks(ticks, pixels):
    keys = sorted(ticks, key=lambda k: ticks[k])
    return np.interp(pixels, [ticks[k] for k in keys], keys)


def spiering_curves(png_path=SPIERING_PNG, max_jump=25):
    """Dict label -> (log10 E/GeV, log10 A/m^2) arrays traced from the raster."""
    from PIL import Image
    rgb = np.array(Image.open(png_path).convert("RGB")).astype(int)
    out = {}
    masks = {k: (np.abs(rgb - np.array(c)).sum(-1) < 90) for k, c in SP_COLOURS.items()}
    for label in SP_COLOURS:
        mask = masks[label]
        col0, row0 = SP_SEED[label]
        points = {}
        for step, stop in ((1, 797), (-1, 103)):
            prev = row0
            for col in range(col0, stop, step):
                idx = np.flatnonzero(mask[20:552, col]) + 20
                runs = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1) if idx.size else []
                runs = [r for r in runs if r.size <= 14]
                if not runs:
                    continue
                centre = min((r.mean() for r in runs), key=lambda c: abs(c - prev))
                if abs(centre - prev) > max_jump:
                    continue
                points[col] = centre
                prev = centre
        xs = np.array(sorted(points), float)
        ys = np.array([points[c] for c in sorted(points)])
        # 5-column running median damps the +-1 pixel anti-aliasing jitter (about 0.01 dex).
        ys = np.array([np.median(ys[max(0, i - 2):i + 3]) for i in range(len(ys))])
        out[label] = (_interp_ticks(SP_X_TICKS, xs), _interp_ticks(SP_Y_TICKS, ys))
    # Below log E = 3.2 the red curve is hidden under the green one: use the green trace there.
    gx, gy = out["150-180"]
    rx, ry = out["90-120"]
    hidden = gx < rx.min()
    rx, ry = np.r_[gx[hidden], rx], np.r_[gy[hidden], ry]
    # Above log E = 8.86 the red curve runs under the blue one, which it joins at log E = 9.
    bx, by = out["0-30"]
    hidden = bx > rx.max()
    out["90-120"] = (np.r_[rx, bx[hidden]], np.r_[ry, by[hidden]])
    return out


def write():
    DATA.mkdir(exist_ok=True)
    with (DATA / "hese2013-effective-area-digitized.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["flavour", "log10_E_lo_TeV", "log10_E_hi_TeV", "A_eff_m2", "below_plotted_range_1e-3"])
        for r in hese_steps():
            w.writerow([r[0], r[1], r[2], f"{r[3]:.4g}", int(r[4])])
    with (DATA / "spiering2026-fig6-digitized.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["zenith_band_deg", "log10_E_GeV", "log10_A_eff_m2"])
        for label, (x, y) in spiering_curves().items():
            grid = np.arange(np.ceil(x.min() * 20) / 20, x.max() + 1e-9, 0.05)
            order = np.argsort(x)
            for gx, gy in zip(grid, np.interp(grid, x[order], y[order])):
                w.writerow([label, f"{gx:.2f}", f"{gy:.3f}"])


if __name__ == "__main__":
    write()
