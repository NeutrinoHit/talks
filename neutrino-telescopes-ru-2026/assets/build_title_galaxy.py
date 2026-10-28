"""Background of the title slide: the Milky Way band with a blue model "neutrino glow" laid over it.

Photo: ESO/S. Brunier, "The Milky Way panorama" (eso0932a), CC BY 4.0, https://www.eso.org/public/images/eso0932a/
(equirectangular, Galactic coordinates, l = 0 in the centre and growing to the left, b = 0 on the middle row).
The file is kept unchanged in assets/title-galaxy/eso0932a.jpg.

Glow: the illustrative model sky I(l, b) = integral of n_gas * n_CR ds of the film "The Milky Way in neutrinos"
(../../dvnanima/milky_way_neutrinos/galaxy_model.py with its config.toml; profiles chosen to look like the Milky Way,
not fitted to surveys), computed on the same (l, b) grid as the crop, asinh-stretched and screen-blended in blue.
It is a picture of where the emission is expected, not a measured neutrino map.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom

HERE = Path(__file__).resolve().parent
FILM = HERE.parents[2] / "dvnanima" / "milky_way_neutrinos"
sys.path.insert(0, str(FILM.parent))
sys.path.insert(0, str(FILM))
from dvconfig import load_config  # noqa: E402
import galaxy_model as gm  # noqa: E402

PHOTO = HERE / "title-galaxy" / "eso0932a.jpg"
# lecture language -> (output file, credit line burned into the frame)
OUTPUTS = {
    "ru": (HERE.parent / "media" / "figures" / "title-galaxy.jpg",
           "Млечный Путь: ESO/S. Brunier, CC BY 4.0  ·  голубое свечение — модель нейтринного излучения Галактики"),
    "en": (HERE.parents[1] / "neutrino-telescopes-2026" / "media" / "galactic" / "title-galaxy.jpg",
           "Milky Way: ESO/S. Brunier, CC BY 4.0  ·  blue glow: model of the Galaxy's neutrino emission"),
}
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"

W, H = 1920, 1080
L_HALF = 66.0                  # crop: l from +66 deg (left edge) to -66 deg (right edge)
BAND_Y = 0.76                  # the Galactic plane b = 0 at this fraction of the height
DEG_PX = W / (2 * L_HALF)      # output pixels per degree
MODEL_STEP = 4                 # model grid: one value per MODEL_STEP output pixels
STRETCH = 0.15                 # asinh(I / (STRETCH * I_max)); softer than the film's 0.02, so the centre stays brightest
NU = np.array([103, 221, 247]) / 255.0
GLOW = 0.8
BLACK = 0.05                   # photo black level removed (sky background of the panorama)


def lb_grid(w, h):
    x = (np.arange(w) + 0.5) / w * W
    y = (np.arange(h) + 0.5) / h * H
    l = L_HALF - x / DEG_PX
    b = (BAND_Y * H - y) / DEG_PX
    return np.meshgrid(l, b)


def photo_crop():
    im = Image.open(PHOTO).convert("RGB")
    pw, ph = im.size
    ppd = pw / 360.0
    b_top = BAND_Y * H / DEG_PX
    b_bot = b_top - H / DEG_PX
    box = (pw / 2 - L_HALF * ppd, ph / 2 - b_top * ppd, pw / 2 + L_HALF * ppd, ph / 2 - b_bot * ppd)
    return np.asarray(im.resize((W, H), Image.LANCZOS, box=box), dtype=float) / 255.0


def model_sky():
    cfg = load_config(FILM)
    gal, s = gm.Galaxy(cfg.galaxy), cfg.sky
    l, b = lb_grid(W // MODEL_STEP, H // MODEL_STEP)
    I = np.zeros(l.shape)
    for r in range(0, l.shape[0], 16):
        I[r:r + 16] = gal.line_of_sight(l[r:r + 16], b[r:r + 16], s.s_min_kpc, s.s_max_kpc, s.near_steps, s.far_step_kpc)
    v = np.arcsinh(I / (STRETCH * I.max()))
    v /= v.max()
    return np.clip(zoom(v, MODEL_STEP, order=3), 0.0, 1.0)


def main(lang="ru"):
    out, credit = OUTPUTS[lang]
    rgb = np.clip((photo_crop() - BLACK) / (1.0 - BLACK), 0.0, 1.0) ** 1.15
    _, b = lb_grid(W, H)
    # darker sky away from the band: above it the title, below it the credit line
    rgb *= (0.5 + 0.5 * np.exp(-np.abs(b) / np.where(b > 0, 16.0, 7.0)))[..., None]
    rgb[H - 60:] *= np.linspace(1.0, 0.35, 60)[:, None, None]

    v = model_sky()
    # a sharp core and wider halos (each normalised to its own peak), so the band glows rather than reads as a line
    layers = [(0.2, 0), (0.4, 6), (0.45, 20), (0.35, 60)]
    glow = sum(w * (gaussian_filter(v, r) if r else v) / (gaussian_filter(v, r) if r else v).max() for w, r in layers)
    glow = GLOW * np.clip(glow, 0.0, 1.0)[..., None] * NU
    rgb = 1.0 - (1.0 - rgb) * (1.0 - np.clip(glow, 0.0, 1.0))      # screen blend

    img = Image.fromarray((np.clip(rgb, 0, 1) ** 0.95 * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 17)
    tw = d.textlength(credit, font=f)
    d.text(((W - tw) / 2, H - 34), credit, font=f, fill=(150, 160, 175))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=90)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ru")
