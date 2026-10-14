"""Picture for the slide "Что такое нейтрино?": solar neutrinos stream through the Earth.

Rendered (numpy + Pillow): a limb-darkened Sun with granulation, a few spots and a corona; the Earth in orthographic
projection with the Natural Earth 1:110m coastlines (the file used by ../neutrino-telescopes-2026/assets/global-sky),
lit from the Sun's side, with procedural clouds and an atmospheric rim. The clouds, colours and spots are illustrative.
Flux of solar neutrinos at the Earth: about 6.5e10 per cm^2 per second, dominated by the pp chain
(standard solar model; Bahcall, Serenelli & Basu, ApJ 621 (2005) L85). The slide rounds it to "about 60 billion".
Sizes and distances are not to scale.
"""
import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "figures" / "solar-neutrinos.png"
LAND = HERE.parents[1] / "neutrino-telescopes-2026" / "assets" / "global-sky" / "data" / "ne_110m_land.geojson"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

SS = 2                                   # supersampling
W, H = 1600, 700
SUN = (250, 360, 120)                    # centre x, y and radius (px)
EARTH = (960, 360, 150)
LON0, LAT0 = 25.0, 18.0                  # centre of the Earth's visible face (deg)
NU = (103, 221, 247)


def noise(shape, scales, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros(shape)
    for s, a in scales:
        out += a * gaussian_filter(rng.normal(size=shape), s)
    return (out - out.mean()) / out.std()


def sun_layer(size):
    cx, cy, r = (v * SS for v in SUN)
    y, x = np.mgrid[0:size[1], 0:size[0]]
    d = np.hypot(x - cx, y - cy) / r
    rgba = np.zeros((size[1], size[0], 4))
    out = np.clip(d - 1, 0, None)
    glow = (np.exp(-out ** 2 / 0.02) + 0.35 * np.exp(-out / 0.35)) * (d >= 1)
    rgba[..., :3] = glow[..., None] * np.array([1.0, 0.72, 0.35])
    rgba[..., 3] = np.clip(glow, 0, 1)
    inside = d < 1
    mu = np.sqrt(np.clip(1 - d ** 2, 0, 1))
    inten = 1 - 0.6 * (1 - mu)                                     # limb darkening
    inten = inten * (1 + 0.045 * noise(d.shape, [(1.2 * SS, 1.0), (3 * SS, 0.6)], 7))   # granulation
    for sx, sy, sr in ((0.25, -0.2, 0.07), (0.32, -0.12, 0.04), (-0.35, 0.3, 0.05)):   # spots
        ds = np.hypot((x - cx) / r - sx, (y - cy) / r - sy) / sr
        inten *= 1 - 0.75 * np.exp(-ds ** 2) - 0.25 * np.exp(-(ds / 1.8) ** 2)
    col = np.stack([np.ones_like(inten), 0.55 + 0.42 * inten, 0.15 + 0.6 * inten ** 2], -1)
    disc = np.clip(col * (0.55 + 0.6 * inten)[..., None], 0, 1)
    rgba[inside, :3] = disc[inside]
    rgba[inside, 3] = 1
    rgba[..., :3] = np.clip(rgba[..., :3], 0, 1)
    return rgba


def ortho(lon, lat):
    """Orthographic projection about (LON0, LAT0): x, y on the unit disc and the visibility cos(c)."""
    l, p = np.radians(lon - LON0), np.radians(lat)
    p0 = math.radians(LAT0)
    x = np.cos(p) * np.sin(l)
    y = math.cos(p0) * np.sin(p) - math.sin(p0) * np.cos(p) * np.cos(l)
    c = math.sin(p0) * np.sin(p) + math.cos(p0) * np.cos(p) * np.cos(l)
    return x, y, c


def earth_layer(size):
    cx, cy, r = (v * SS for v in EARTH)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for f in json.loads(LAND.read_text())["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = np.array(poly[0])
            t = np.linspace(0, len(ring) - 1, len(ring) * 4)
            lon = np.interp(t, np.arange(len(ring)), ring[:, 0])
            lat = np.interp(t, np.arange(len(ring)), ring[:, 1])
            x, y, c = ortho(lon, lat)
            if (c > 0).sum() < 3:
                continue
            k = np.hypot(x, y)
            far = c <= 0                         # points behind the limb are pushed onto it
            x = np.where(far, x / np.maximum(k, 1e-9), x)
            y = np.where(far, y / np.maximum(k, 1e-9), y)
            draw.polygon(list(zip(cx + r * x, cy - r * y)), fill=255)
    land = np.asarray(mask, float) / 255
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    u, v = (xx - cx) / r, -(yy - cy) / r
    rho = np.hypot(u, v)
    inside = rho < 1
    z = np.sqrt(np.clip(1 - rho ** 2, 0, 1))
    p0 = math.radians(LAT0)
    lat = np.degrees(np.arcsin(np.clip(z * math.sin(p0) + v * math.cos(p0), -1, 1)))
    ocean = np.array([0.05, 0.22, 0.48]) * (0.75 + 0.25 * z[..., None])
    a = np.abs(lat)[..., None]
    green, desert, tundra = np.array([0.20, 0.42, 0.18]), np.array([0.66, 0.55, 0.36]), np.array([0.35, 0.38, 0.30])
    w_des = np.exp(-((a - 23) / 9) ** 2)
    w_tun = np.clip((a - 50) / 15, 0, 1)
    landc = green * np.clip(1 - w_des - w_tun, 0, 1) + desert * w_des + tundra * w_tun
    landc = landc * (1 + 0.12 * noise(lat.shape, [(4 * SS, 1.0)], 3)[..., None])
    ice = np.clip((a - 66) / 6, 0, 1)
    landc = landc * (1 - ice) + 0.92 * ice
    col = ocean * (1 - land[..., None]) + landc * land[..., None]
    cl = noise(lat.shape, [(2 * SS, 0.25), (8 * SS, 1.0), (22 * SS, 0.9)], 11)     # clouds
    cl = gaussian_filter(np.clip((cl - 0.55) / 1.6, 0, 1), 1.5 * SS) * 0.55
    col = col * (1 - cl[..., None]) + 0.97 * cl[..., None]
    L = np.array([-0.85, 0.15, 0.5]); L /= np.linalg.norm(L)                       # light from the Sun's side
    lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
    col = col * (0.12 + 0.88 * lam ** 0.8)[..., None]
    rgba = np.zeros((size[1], size[0], 4))
    rgba[inside, :3] = np.clip(col[inside], 0, 1)
    rgba[inside, 3] = 1
    rim = np.exp(-((rho - 1.0) / 0.035) ** 2) * (0.35 + 0.65 * np.clip(lam + 0.3, 0, 1))   # atmosphere
    a_rim = np.clip(rim * 0.9, 0, 1)
    rgba[..., :3] = rgba[..., :3] * (1 - a_rim[..., None]) + np.array([0.45, 0.70, 1.0]) * a_rim[..., None]
    rgba[..., 3] = np.maximum(rgba[..., 3], a_rim)
    return rgba


def over(base, layer):
    a = layer[..., 3:4]
    base[..., :3] = base[..., :3] * (1 - a) + layer[..., :3] * a
    return base


def build():
    size = (W * SS, H * SS)
    rng = np.random.default_rng(5)
    img = np.zeros((size[1], size[0], 4))
    img[..., :3] = np.array([0.02, 0.03, 0.055])
    img[..., 3] = 1
    sx, sy = rng.uniform(0, size[0], 260).astype(int), rng.uniform(0, size[1], 260).astype(int)
    img[sy, sx, :3] = rng.uniform(0.3, 0.9, (260, 1))
    beams = Image.new("RGBA", size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    rnd = random.Random(3)
    for _ in range(70):
        y0 = (SUN[1] + rnd.uniform(-0.8, 0.8) * SUN[2]) * SS
        slope = rnd.uniform(-0.06, 0.06)
        x0, x1 = (SUN[0] + 40) * SS, (W - 20) * SS
        bd.line([(x0, y0), (x1, y0 + slope * (x1 - x0))], fill=NU + (int(255 * rnd.uniform(0.25, 0.7)),), width=2 * SS)
    b = np.asarray(beams, float) / 255
    img = over(img, b)
    img = over(img, sun_layer(size))
    img = over(img, earth_layer(size))
    b2 = b.copy()                                           # neutrinos keep going through the Earth
    ex, ey, er = (v * SS for v in EARTH)
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    b2[..., 3] *= 0.55 * (np.hypot(xx - ex, yy - ey) < er)
    img = over(img, b2)
    out = Image.fromarray((np.clip(img[..., :3], 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(out)
    fb = lambda s: ImageFont.truetype(FONT_B, s)
    fr = lambda s: ImageFont.truetype(FONT, s)
    d.text((SUN[0], SUN[1] + SUN[2] + 95), "Солнце", fill=(255, 212, 119), font=fb(34), anchor="mm")
    d.text((EARTH[0], EARTH[1] + EARTH[2] + 45), "Земля", fill=(238, 238, 238), font=fb(34), anchor="mm")
    bx, by, bs = 1400, 50, 120
    for k in range(9):
        yk = by + 15 + k * (bs - 30) / 8
        d.line([(bx - 30, yk), (bx + bs + 30, yk)], fill=NU, width=2)
    d.rounded_rectangle([bx, by, bx + bs, by + bs], radius=8, outline=(255, 176, 82), width=4)
    d.text((bx + bs / 2, by + bs + 32), "1 см²", fill=(255, 176, 82), font=fb(30), anchor="mm")
    d.text((bx - 55, by + 45), "≈ 60 миллиардов", fill=(238, 238, 238), font=fb(38), anchor="rm")
    d.text((bx - 55, by + 90), "каждую секунду", fill=(238, 238, 238), font=fr(30), anchor="rm")
    d.text((W / 2, H - 28), "Почти все пролетают Землю насквозь · размеры и расстояния не в масштабе",
           fill=(160, 181, 202), font=fr(26), anchor="mm")
    return out


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build().save(OUT, optimize=True)
    old = OUT.with_suffix(".svg")
    if old.exists():
        old.unlink()
    print(OUT)
