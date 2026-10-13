"""Read drawn paths and text positions from vector publication figures.

Used by the lecture-style redraw generators. A PDF (or EPS, via Ghostscript)
is converted to SVG with Poppler; every <path> outside <defs> is returned with
its fill/stroke colours and its vertices in page coordinates (points, y down).
Cubic Bezier segments are sampled (BEZIER_STEPS points each); straight
segments are exact. Text positions come from
`pdftotext -bbox` when the figure carries real text.
"""
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np

SVG = "{http://www.w3.org/2000/svg}"
BEZIER_STEPS = 8          # samples per cubic Bezier segment


@dataclass
class Path_:
    fill: str | None
    stroke: str | None
    width: float
    subpaths: list = field(default_factory=list)   # list of (N, 2) arrays
    dash: str | None = None
    clip: list = field(default_factory=list)       # subpaths of the innermost clip path

    @property
    def points(self):
        return np.vstack(self.subpaths) if self.subpaths else np.zeros((0, 2))

    def bbox(self):
        p = self.points
        return p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()


def rgb(value):
    """'rgb(12.3%, 0%, 100%)' -> (r, g, b) in 0..255, or None."""
    if not value or value == "none" or value.startswith("url"):
        return value if value and value.startswith("url") else None
    m = re.match(r"rgb\(([\d.]+)%,\s*([\d.]+)%,\s*([\d.]+)%\)", value)
    if not m:
        return value
    return tuple(round(float(v) * 2.55) for v in m.groups())


def _matrix(transform):
    if not transform:
        return np.eye(3)
    m = re.match(r"matrix\(([^)]*)\)", transform)
    if m:
        a, b, c, d, e, f = (float(v) for v in re.split(r"[ ,]+", m.group(1).strip()))
        return np.array([[a, c, e], [b, d, f], [0, 0, 1]])
    m = re.match(r"translate\(([^)]*)\)", transform)
    if m:
        vals = [float(v) for v in re.split(r"[ ,]+", m.group(1).strip())]
        return np.array([[1, 0, vals[0]], [0, 1, vals[1] if len(vals) > 1 else 0], [0, 0, 1]])
    raise ValueError(f"Unsupported transform {transform}")


def _parse_d(d):
    tokens = re.findall(r"[MLCZHVmlczhv]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    subpaths, cur, i, cmd = [], [], 0, None
    pos = np.zeros(2)
    while i < len(tokens):
        t = tokens[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t; i += 1
            if cmd in "Zz":
                if cur:
                    cur.append(cur[0]); subpaths.append(np.array(cur)); cur = []
                continue
        nums = lambda k: [float(x) for x in tokens[i:i + k]]
        if cmd == "M":
            if cur:
                subpaths.append(np.array(cur))
            pos = np.array(nums(2)); cur = [pos]; i += 2; cmd = "L"
        elif cmd == "L":
            pos = np.array(nums(2)); cur.append(pos); i += 2
        elif cmd == "C":
            v = nums(6)
            p1, p2, p3 = np.array(v[0:2]), np.array(v[2:4]), np.array(v[4:6])
            t = np.linspace(0, 1, BEZIER_STEPS + 1)[1:, None]
            cur += list((1 - t) ** 3 * pos + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)
            pos = p3; i += 6
        elif cmd == "H":
            pos = np.array([float(tokens[i]), pos[1]]); cur.append(pos); i += 1
        elif cmd == "V":
            pos = np.array([pos[0], float(tokens[i])]); cur.append(pos); i += 1
        else:
            raise ValueError(f"Unsupported path command {cmd}")
    if cur:
        subpaths.append(np.array(cur))
    return subpaths


def to_svg(source):
    source = Path(source)
    tmp = Path(tempfile.mkdtemp())
    pdf = source
    if source.suffix.lower() in (".eps", ".ps"):
        pdf = tmp / "figure.pdf"
        subprocess.run(["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dEPSCrop",
                        "-sDEVICE=pdfwrite", f"-sOutputFile={pdf}", str(source)], check=True)
    svg = tmp / "figure.svg"
    subprocess.run(["pdftocairo", "-svg", str(pdf), str(svg)], check=True)
    return svg


def paths(source):
    """All drawn paths of a vector figure, in page coordinates (pt, y down)."""
    root = ET.parse(to_svg(source)).getroot()
    out = []
    clips = {}
    for cp in root.iter(SVG + "clipPath"):
        subs = []
        for el in cp:
            if el.tag == SVG + "path":
                m = _matrix(el.attrib.get("transform"))
                for sp in _parse_d(el.attrib.get("d", "")):
                    subs.append((np.c_[sp, np.ones(len(sp))] @ m.T)[:, :2])
        clips[cp.attrib["id"]] = subs

    def walk(node, mat, inherited):
        if node.tag == SVG + "defs":
            return
        style = dict(inherited)
        for key in ("fill", "stroke", "stroke-width", "stroke-dasharray"):
            if key in node.attrib:
                style[key] = node.attrib[key]
        if "clip-path" in node.attrib:
            style["clip"] = node.attrib["clip-path"][5:-1]
        m = mat @ _matrix(node.attrib.get("transform"))
        if node.tag == SVG + "path":
            subs = []
            for sp in _parse_d(node.attrib.get("d", "")):
                h = np.c_[sp, np.ones(len(sp))] @ m.T
                subs.append(h[:, :2])
            out.append(Path_(fill=rgb(style.get("fill", "rgb(0%,0%,0%)")) if "fill" in style else (0, 0, 0),
                             stroke=rgb(style.get("stroke")), width=float(style.get("stroke-width", 1)) * abs(m[0, 0]),
                             subpaths=subs, dash=style.get("stroke-dasharray"),
                             clip=clips.get(style.get("clip"), [])))
        for child in node:
            walk(child, m, style)

    walk(root, np.eye(3), {})
    return out


def words(pdf):
    """[(text, xMin, yMin, xMax, yMax)] from pdftotext -bbox (pt, y down)."""
    tmp = Path(tempfile.mkdtemp()) / "bbox.html"
    subprocess.run(["pdftotext", "-bbox", str(pdf), str(tmp)], check=True)
    rows = []
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',
                         tmp.read_text()):
        rows.append((m.group(5), *(float(m.group(i)) for i in range(1, 5))))
    return rows


class LogAxis:
    """Map page coordinate <-> value on a log10 axis from two reference ticks."""

    def __init__(self, p1, v1, p2, v2):
        self.p1, self.l1 = p1, np.log10(v1)
        self.scale = (np.log10(v2) - self.l1) / (p2 - p1)

    def value(self, p):
        return 10 ** (self.l1 + (np.asarray(p) - self.p1) * self.scale)

    def page(self, v):
        return self.p1 + (np.log10(v) - self.l1) / self.scale


class LinAxis:
    def __init__(self, p1, v1, p2, v2):
        self.p1, self.v1 = p1, v1
        self.scale = (v2 - v1) / (p2 - p1)

    def value(self, p):
        return self.v1 + (np.asarray(p) - self.p1) * self.scale

    def page(self, v):
        return self.p1 + (np.asarray(v) - self.v1) / self.scale


def colour_close(c, target, tol=6):
    return isinstance(c, tuple) and all(abs(a - b) <= tol for a, b in zip(c, target))
