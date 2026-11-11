"""English figures of this lecture that differ from the figures of ../neutrino-telescopes-2026.

people-chain.svg     the chain of ../neutrino-telescopes-2026/assets/prospects/build_prospects.py, with the
                     programme box naming the subject only ("neutrino physics and particle astrophysics")
nt36-side.svg        ../neutrino-telescopes-ru-2026/assets/build_nt36.py with English labels
solar-neutrinos.png  ../neutrino-telescopes-ru-2026/assets/build_intro.py with English labels

The generators stay the single source of numbers, geometry and drawing: this script loads them, replaces
only the visible labels and writes the figures into media/figures of this lecture. A label that is not found
where it is expected is an error, so a changed generator cannot silently produce a figure in another language.
"""
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent
TALKS = HERE.parents[1]
EN = TALKS / "neutrino-telescopes-2026" / "assets"
RU = TALKS / "neutrino-telescopes-ru-2026" / "assets"
OUT = HERE.parent / "media" / "figures"
CYRILLIC = re.compile(r"[\u0400-\u04ff]")

# programme box of the people chain: the course label before ": neutrino physics" is dropped
PROGRAMME_LINE = "neutrino physics"

NT36_TEXT = {
    "ice": "ice",
    "depth": "1.1 km",
    "shore": "to shore, 3.6 km",
    "arm": "21.5 m",
    "face": "7.5 m",
    "back": "5 m",
    "up": "pair looks up",
    "down": "pair looks down",
    "sum": "3 strings × 6 pairs = 36 modules",
    "scale": "Distances on the strings to scale, depth not",
}
NT36_TITLE = "NT-36: three strings on the NT-200 frame"

# labels of build_intro.py, identified by their colour and font size
SOLAR_TEXT = {
    ((255, 212, 119), 34): "Sun",
    ((238, 238, 238), 34): "Earth",
    ((255, 176, 82), 30): "1 cm²",
    ((238, 238, 238), 38): "≈ 60 billion",
    ((238, 238, 238), 30): "every second",
    ((160, 181, 202), 26): "Almost all pass straight through the Earth · sizes and distances not to scale",
}


def load(path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)                      # data and imports resolve next to the original generator
    sys.modules[name] = mod
    exec(compile(path.read_text(), str(path), "exec"), mod.__dict__)
    return mod


def no_cyrillic(text: str, what: str) -> str:
    if CYRILLIC.search(text):
        raise SystemExit(f"{what}: Cyrillic text left in the figure")
    return text


def people_chain() -> None:
    pr = load(EN / "prospects" / "build_prospects.py", "cn_prospects")
    title, key, lines = pr.PEOPLE[0]
    hits = [i for i, line in enumerate(lines) if line.endswith(": " + PROGRAMME_LINE)]
    if title != "Programme" or len(hits) != 1:
        raise SystemExit(f"build_prospects.py: programme label '...: {PROGRAMME_LINE}' not found in PEOPLE[0]")
    lines = list(lines)
    lines[hits[0]] = PROGRAMME_LINE
    pr.PEOPLE[0] = (title, key, lines)
    svg = no_cyrillic(pr.people_chain(), "people-chain.svg")
    (OUT / "people-chain.svg").write_text(svg)


def nt36() -> None:
    nt = load(RU / "build_nt36.py", "cn_nt36")
    if set(nt.TEXT) != set(NT36_TEXT):
        raise SystemExit(f"build_nt36.py: labels changed: {sorted(set(nt.TEXT) ^ set(NT36_TEXT))}")
    nt.TEXT.update(NT36_TEXT)
    svg, n = re.subn(r"<title>[^<]*</title>", f"<title>{NT36_TITLE}</title>", nt.build(), count=1)
    if n != 1:
        raise SystemExit("build_nt36.py: <title> not found")
    (OUT / "nt36-side.svg").write_text(no_cyrillic(svg, "nt36-side.svg"))


def solar() -> None:
    intro = load(RU / "build_intro.py", "cn_intro")
    draw_cls = intro.ImageDraw.ImageDraw
    original = draw_cls.text
    seen = []

    def text(self, xy, label, fill=None, font=None, *args, **kwargs):
        key = (tuple(fill) if fill is not None else None, getattr(font, "size", None))
        if key not in SOLAR_TEXT:
            raise SystemExit(f"build_intro.py: unexpected label style {key}")
        seen.append(key)
        return original(self, xy, SOLAR_TEXT[key], fill, font, *args, **kwargs)

    draw_cls.text = text
    try:
        img = intro.build()
    finally:
        draw_cls.text = original
    if sorted(seen) != sorted(SOLAR_TEXT):
        raise SystemExit(f"build_intro.py: labels changed: {seen}")
    img.save(OUT / "solar-neutrinos.png", optimize=True)


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    people_chain()
    nt36()
    solar()
    print("\n".join(str(p.relative_to(HERE.parent)) for p in sorted(OUT.iterdir())))


if __name__ == "__main__":
    build()
