"""Editable schematic of one converter-acceleration cycle (Derishev et al., PRD 68, 043003, 2003).

A charged proton in a relativistic jet converts into a neutron, which leaves the jet
without feeling the magnetic field; outside it converts back into a proton, which the
ambient field returns into the jet. Each cycle multiplies the energy by roughly Gamma^2.
Geometry, trajectories and the number of neutrinos are illustrative; no rate is computed.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "media/theory/converter-cycle.svg"
COLORS = {"proton": "#ffb052", "neutron": "#f4f5ff", "nu": "#67ddf7", "muted": "#a0b5ca", "jet": "#73c7ff"}


def build():
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="600" viewBox="0 0 1600 600">
<title>One converter acceleration cycle</title>
<desc>Schematic: proton to neutron inside the jet, neutron escapes, converts back to a proton outside, the field returns it. No calculated trajectory or rate.</desc>
<rect width="1600" height="600" fill="#070d16"/>
<defs>''']
    for k, c in COLORS.items():
        parts.append(f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                     f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="{c}"/></marker>')
    parts.append('</defs>')

    def text(x, y, t, k="muted", size=30, anchor="middle", weight="normal"):
        parts.append(f'<text x="{x}" y="{y}" fill="{COLORS[k]}" font-family="Arial, sans-serif" font-size="{size}" '
                     f'font-weight="{weight}" text-anchor="{anchor}">{t}</text>')

    def path(d, k, width=4, dash=None, marker=True):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        end = f' marker-end="url(#{k})"' if marker else ""
        parts.append(f'<path d="{d}" fill="none" stroke="{COLORS[k]}" stroke-width="{width}"{extra}{end}/>')

    def nu_label(x, y):
        parts.append(f'<text x="{x}" y="{y}" fill="{COLORS["nu"]}" font-family="Times New Roman, serif" '
                     f'font-style="italic" font-size="38">ν</text>')

    def dot(x, y):
        parts.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#f4f5ff"/>')

    # Jet: a fast flow above the boundary, slow medium below.
    parts.append('<rect x="0" y="40" width="1600" height="210" fill="#0f2236"/>')
    for y, starts in ((105, (60, 520)), (205, (60, 520, 980))):
        for x0 in starts:
            path(f"M{x0} {y}H{x0 + 300}", "jet", width=3, dash="14 10")
    text(40, 74, "Relativistic jet · bulk Lorentz factor Γ", "jet", 26, "start")
    parts.append('<path d="M0 250H1600" stroke="#506a84" stroke-width="2" stroke-dasharray="10 10"/>')
    text(40, 292, "Slow surroundings with magnetic field", size=26, anchor="start")

    # 1. Proton in the jet converts into a neutron.
    path("M150 160H455", "proton")
    text(150, 145, "Proton", "proton", 30, "start")
    dot(480, 160)
    text(455, 240, "p + γ → n + π⁺", "neutron", 28, "end")
    path("M492 150L610 70", "nu", width=3)
    nu_label(622, 80)

    # 2. The neutron leaves the jet without feeling the field.
    path("M492 172L800 420", "neutron", width=4, dash="12 9")
    text(470, 375, "Neutron: no charge,", "neutron", 28, "end")
    text(470, 413, "crosses the field freely", "neutron", 28, "end")

    # 3. Outside it becomes a proton again; the field turns it back into the jet.
    dot(815, 432)
    text(790, 490, "n + γ → p + π⁻", "neutron", 28, "end")
    path("M828 448L960 545", "nu", width=3)
    nu_label(972, 555)
    path("M827 425C960 370 1150 440 1180 330C1200 250 1150 210 1120 175", "proton")
    text(1235, 430, "The field turns", "proton", 28, "start")
    text(1235, 468, "the proton back", "proton", 28, "start")

    # 4. Back in the jet: energy multiplied by ~Gamma^2.
    path("M1135 165H1450", "proton", width=6)
    text(1295, 125, "Energy × ~Γ² per cycle", "proton", 34, "middle", "bold")
    text(800, 585, "Illustrative cycle · Neutral particles cross the jet boundary unaffected by the field", size=23)
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build())
