"""Digitize the IceCube Combined-Fit BPL 68% band from the vector Fig. 3 of arXiv:2507.22233v3.

Input: the Poppler (pdftocairo -svg) conversion of figures/physics_context.pdf,
byte-identical to media/diffuse/icecube-spectrum-2026.svg on 13 October 2026
(output SHA-256 07b055b2... in assets/evidence/figures.json).
Output: data/icecube2026-cf-bpl-band-digitized.txt, the input of build_energy_budget.py.

x calibration: centres of the 10^3 and 10^8 tick labels (pdftotext -bbox of the PDF).
y calibration: the published best-fit CF BPL line (Table III parameters) drawn in the
same figure, so the band inherits the table normalization; residuals are printed.
"""
from pathlib import Path
import re
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT = HERE.parents[1] / "media/diffuse/icecube-spectrum-2026.svg"
OUT = HERE / "data/icecube2026-cf-bpl-band-digitized.txt"
ORANGE = "49.803162"  # matplotlib C1 in the Poppler conversion
X1E3 = (91.021372 + 120.827074) / 2
X1E8 = (458.870458 + 488.676161) / 2
CF_BPL = dict(phi0=1.77, gamma1=1.31, gamma2=2.74, log_ebreak=4.39)  # Table III, CF column


def bpl_log_e2flux(log_e, phi0, gamma1, gamma2, log_ebreak):
    """log10 E^2 Phi per flavour [GeV cm^-2 s^-1 sr^-1]; Table III definition (E_break < 100 TeV)."""
    e, eb = 10.0 ** np.asarray(log_e), 10.0 ** log_ebreak
    norm = phi0 * (eb / 1e5) ** (-(gamma1 if eb > 1e5 else gamma2))
    gamma = np.where(e < eb, gamma1, gamma2)
    return np.log10(1e-18 * norm * (e / eb) ** (-gamma) * e**2)


def paths(svg):
    for m in re.finditer(r'<path ([^>]*?)d="([^"]*)"([^>]*)/>', svg):
        attrs = m.group(1) + m.group(3)
        tr = re.search(r'transform="matrix\(([^)]*)\)"', attrs)
        if not tr:
            continue
        a, b, c, d, e, f = map(float, tr.group(1).split(","))
        n = np.array(list(map(float, re.findall(r"-?\d+\.?\d*", m.group(2)))))
        x, y = n[0::2], n[1::2]
        yield attrs, a * x + c * y + e, b * x + d * y + f


def digitize(svg_path=DEFAULT):
    svg = Path(svg_path).read_text()
    band = line = None
    for attrs, x, y in paths(svg):
        if ORANGE in attrs and 'fill-opacity="0.4"' in attrs and band is None:
            band = (x, y)
        elif ORANGE in attrs and 'stroke-width="1.5"' in attrs and "square" in attrs and line is None:
            line = (x, y)
    log_x = lambda X: 3 + 5 * (X - X1E3) / (X1E8 - X1E3)
    lx = log_x(line[0])
    slope, offset = np.polyfit(bpl_log_e2flux(lx, **CF_BPL), line[1], 1)
    residual = line[1] - (slope * bpl_log_e2flux(lx, **CF_BPL) + offset)
    return log_x(band[0]), (band[1] - offset) / slope, lx, residual


if __name__ == "__main__":
    bx, by, lx, residual = digitize(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
    print("BPL line vertices log10(E/GeV):", np.round(lx, 3), "y residuals [pt]:", np.round(residual, 2))
    print(f"band range log10(E/GeV) {bx.min():.3f}-{bx.max():.3f}")
    np.savetxt(OUT, np.c_[bx, by], fmt="%.4f",
               header="log10(E/GeV) log10(E2Phi per flavour nu+nubar [GeV cm-2 s-1 sr-1]); "
                      "IceCube CF BPL 68% band, digitized from Fig. 3 of arXiv:2507.22233v3 (vector source)")
