"""Side view of the Baikal NT-36 array (April 1993 - March 1995) for the history slide.

Numbers from the Baikal Collaboration, astro-ph/9601161 (Rome, 1995), section 2 and Fig. 1:
3 strings with 6 pairs of optical modules each (36 modules); pairs alternate up/down from top to bottom
(1994 configuration: up, down, up, down, up, down); pairs facing each other are 7.5 m apart, back to back 5 m;
the strings hang from the umbrella frame of the future NT-200, whose arms are 21.5 m long;
depth 1.1 km, 3.6 km from shore. In a side view the outer strings are drawn at +-21.5 m from the central one.
Distances along and across the strings are drawn to the same scale; the depth is not to scale (a break in the cable).
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "figures" / "nt36-side.svg"

ARM_M = 21.5                                    # arm of the umbrella frame
FACE_M, BACK_M = 7.5, 5.0                       # spacing of pairs facing each other / back to back
ORIENT = ["up", "down", "up", "down", "up", "down"]   # top to bottom, 1994 configuration
TOP_GAP_M = 6.0                                 # frame to the first pair: schematic, not given in the source

C = {"bg": "#070d16", "fg": "#eeeeee", "muted": "#a0b5ca", "frame": "#506a84", "om": "#73c7ff",
     "pair": "#ffd477", "ice": "#cfe6ff", "water": "#0b1a2c"}
FONT = "Arial, sans-serif"
TEXT = {
    "ice": "лёд",
    "depth": "1,1 км",
    "shore": "к берегу, 3,6 км",
    "arm": "21,5 м",
    "face": "7,5 м",
    "back": "5 м",
    "up": "пара смотрит вверх",
    "down": "пара смотрит вниз",
    "sum": "3 гирлянды × 6 пар = 36 модулей",
    "scale": "Расстояния у гирлянд в масштабе, глубина — нет",
}


def pair_depths():
    """Depths of the pairs below the first one, m."""
    z = [0.0]
    for a, b in zip(ORIENT[:-1], ORIENT[1:]):
        facing = a == "down" and b == "up"      # the upper pair looks down, the lower looks up
        z.append(z[-1] + (FACE_M if facing else BACK_M))
    return z


def text(x, y, s, color, size=26, anchor="middle", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="{FONT}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>')


def om(x, y, up, r=10):
    """An optical module: a glass sphere with the photocathode hemisphere facing up or down."""
    sweep = "0 0 1" if up else "0 0 0"
    cath = f'<path d="M{x - r} {y}A{r} {r} {sweep} {x + r} {y}Z" fill="{C["om"]}"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{C["om"]}" stroke-width="2"/>' + cath


def build() -> str:
    W, H, s = 1000, 960, 11.0                    # canvas and pixels per metre
    cx, y_frame = 560, 300
    zs = pair_depths()
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             "<title>NT-36: три гирлянды на раме NT-200</title>",
             f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>',
             f'<rect x="0" y="70" width="{W}" height="{H - 70}" fill="{C["water"]}"/>',
             f'<rect x="0" y="58" width="{W}" height="14" fill="{C["ice"]}" opacity="0.85"/>',
             text(30, 50, TEXT["ice"], C["ice"], 30, "start")]
    # cable from the frame up to the ice, with a break: the depth is not to scale
    y_break = 170
    parts.append(f'<path d="M{cx} {y_frame - 40}V{y_break + 14}M{cx} {y_break - 14}V72" stroke="{C["frame"]}" stroke-width="3" fill="none"/>')
    for dy in (-14, 14):
        parts.append(f'<path d="M{cx - 16} {y_break + dy + 6}L{cx + 16} {y_break + dy - 6}" stroke="{C["muted"]}" stroke-width="3"/>')
    parts.append(text(cx + 30, y_break + 9, TEXT["depth"], C["fg"], 38, "start", "bold"))
    parts.append(f'<path d="M{cx} {y_frame - 40}C{cx - 160} {y_frame - 70} {cx - 300} {y_frame - 60} {cx - 470} {y_frame - 90}" '
                 f'stroke="{C["frame"]}" stroke-width="3" fill="none" stroke-dasharray="8 6"/>')
    parts.append(text(cx - 470, y_frame - 105, TEXT["shore"], C["muted"], 30, "start"))
    # the umbrella frame
    xs = [cx - ARM_M * s, cx, cx + ARM_M * s]
    parts.append(f'<path d="M{xs[0]} {y_frame}L{cx} {y_frame - 40}L{xs[2]} {y_frame}" stroke="{C["frame"]}" stroke-width="4" fill="none"/>')
    parts.append(f'<path d="M{cx} {y_frame + 22}H{xs[2]}" stroke="{C["muted"]}" stroke-width="1.5"/>')
    parts.append(text((cx + xs[2]) / 2, y_frame + 46, TEXT["arm"], C["muted"], 30))
    # strings and pairs
    y0 = y_frame + TOP_GAP_M * s
    bottom = y0 + zs[-1] * s + 40
    for x in xs:
        parts.append(f'<path d="M{x} {y_frame}V{bottom}" stroke="{C["frame"]}" stroke-width="2.5"/>')
        for z, o in zip(zs, ORIENT):
            y = y0 + z * s
            parts.append(f'<rect x="{x - 34}" y="{y - 16}" width="68" height="32" rx="10" fill="none" stroke="{C["pair"]}" stroke-width="1.5" opacity="0.6"/>')
            parts.append(om(x - 16, y, o == "up"))
            parts.append(om(x + 16, y, o == "up"))
    # spacings along the left string
    xl = xs[0] - 70
    for i in range(2):
        ya, yb = y0 + zs[i] * s, y0 + zs[i + 1] * s
        label = TEXT["face"] if ORIENT[i] == "down" else TEXT["back"]
        parts.append(f'<path d="M{xl} {ya}V{yb}M{xl - 8} {ya}H{xl + 8}M{xl - 8} {yb}H{xl + 8}" stroke="{C["muted"]}" stroke-width="1.5"/>')
        parts.append(text(xl - 14, (ya + yb) / 2 + 8, label, C["muted"], 30, "end"))
    # legend
    ly = bottom + 70
    parts.append(om(60, ly, True))
    parts.append(text(85, ly + 8, TEXT["up"], C["fg"], 30, "start"))
    parts.append(om(520, ly, False))
    parts.append(text(545, ly + 8, TEXT["down"], C["fg"], 30, "start"))
    parts.append(text(W / 2, ly + 62, TEXT["sum"], C["pair"], 38, "middle", "bold"))
    parts.append(text(W / 2, ly + 100, TEXT["scale"], C["muted"], 27))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build())
    print(OUT, "pair depths below the first pair:", pair_depths())
