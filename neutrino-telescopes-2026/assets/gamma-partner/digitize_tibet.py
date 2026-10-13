"""Read Tibet ASgamma data points from the vector paths of Fig. 4, arXiv:2104.05181v2.

The source file f4.eps is not stored here. Pass its path from the arXiv source
archive. Ghostscript converts it to PDF and Poppler to SVG; the red circles
(centres) and red error bars are then read in plot coordinates. The axis
calibration uses the drawn tick marks: 10^-2 ... 10^4 TeV in x, and the
10^-5 / 10^-4 major ticks in y (E^2.7 dJ/dE, GeV^1.7 cm^-2 s^-1 sr^-1).
"""
import argparse
import csv
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "data/tibet-asgamma-fig4-2104.05181v2.csv"

# Internal (x10, y-up) coordinates of the frames, from the axis tick paths.
X_DECADE0, X_PER_DECADE = 890.35, 727.5          # x = 10^-2 TeV at the left frame
PANELS = {"a": 2973.32, "b": 375.0}              # y = 10^-5 at each lower frame
Y_PER_DECADE = 1412.5                            # 10^-5 -> 10^-4 tick distance
REGIONS = {"a": "25<l<100 deg, |b|<5 deg", "b": "50<l<200 deg, |b|<5 deg"}


def to_svg(eps):
    tmp = Path(tempfile.mkdtemp())
    pdf, svg = tmp / "f4.pdf", tmp / "f4.svg"
    subprocess.run(["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dEPSCrop",
                    "-sDEVICE=pdfwrite", f"-sOutputFile={pdf}", str(eps)], check=True)
    subprocess.run(["pdftocairo", "-svg", str(pdf), str(svg)], check=True)
    return svg.read_text()


def log_e(x):
    return -2 + (x - X_DECADE0) / X_PER_DECADE


def log_y(y, panel):
    return -5 + (y - PANELS[panel]) / Y_PER_DECADE


def panel_of(y):
    return "a" if y > 2900 else "b"


def points(svg):
    body = svg[svg.index("</defs>"):]
    centres, bars = [], []
    for m in re.finditer(r"<path ([^>]*)/>", body):
        attrs = m.group(1)
        d = re.search(r' d="([^"]*)"', attrs).group(1)
        if 'fill="rgb(100%, 0%, 0%)"' in attrs:
            nums = [float(v) for v in re.findall(r"[-\d.]+", d)]
            xs, ys = nums[0::2], nums[1::2]
            cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
            if cx > 200:                         # legend markers sit near x = 126 pt
                centres.append((cx * 10, (547 - cy) * 10))
        elif 'stroke="rgb(100%, 0%, 0%)"' in attrs:
            for seg in re.finditer(r"M ([\d.]+) ([\d.]+) L ([\d.]+) ([\d.]+)", d):
                bars.append(tuple(map(float, seg.groups())))
    rows = []
    for x, y in sorted(centres, key=lambda c: (panel_of(c[1]), c[0])):
        panel = panel_of(y)
        same = [b for b in bars if panel_of(b[1]) == panel]
        vertical = [b for b in same if abs(b[0] - x) < 1 and abs(b[2] - x) < 1 and b[1] != b[3]]
        ends = [v for b in vertical for v in (b[1], b[3])]
        horizontal = [b for b in same if b[1] == b[3] and abs(b[1] - y) < 1]
        edges = [v for b in horizontal for v in (b[0], b[2])]
        rows.append({
            "panel": panel, "region": REGIONS[panel],
            "e_tev": 10 ** log_e(x), "e_min_tev": 10 ** log_e(min(edges)), "e_max_tev": 10 ** log_e(max(edges)),
            "e27_flux": 10 ** log_y(y, panel),
            "e27_flux_low": 10 ** log_y(min(ends), panel), "e27_flux_high": 10 ** log_y(max(ends), panel),
        })
    if len(rows) != 6:
        raise ValueError(f"Expected 3 points in each panel, found {len(rows)}")
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("eps", type=Path, help="f4.eps from the arXiv:2104.05181v2 source archive")
    rows = points(to_svg(p.parse_args().eps))
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in row.items()})
    print(f"{len(rows)} points -> {OUT}")


if __name__ == "__main__":
    main()
