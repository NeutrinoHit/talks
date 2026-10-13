"""Contained nu-N interactions, not selected telescope events.

Independent FITS-image reader and tensor B-spline evaluation using SciPy.
Input splines: unmodified IceCube nuflux 2.0.7 data (LGPL-3.0).
No nuflux C++ implementation is copied. See README for provenance/checks.
"""
from pathlib import Path
import csv
import tomllib
import numpy as np
from scipy.interpolate import NdBSpline

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CFG = tomllib.loads((HERE / "rates.toml").read_text())


def fits_images(path):
    """Read only the simple uncompressed FITS image HDUs in these tables."""
    raw = path.read_bytes()
    pos, result = 0, []
    while pos < len(raw):
        header = {}
        while True:
            block = raw[pos:pos + 2880].decode("ascii")
            pos += 2880
            ended = False
            for start in range(0, 2880, 80):
                card = block[start:start + 80]
                key = card[:8].strip()
                if key == "END":
                    ended = True
                    break
                if card[8:10] == "= ":
                    value = card[10:].split("/")[0].strip()
                    if value.startswith("'"):
                        value = value.strip("'").strip()
                    elif value not in ("T", "F"):
                        value = float(value) if any(c in value for c in ".Ee") else int(value)
                    header[key] = value
            if ended:
                break
        axes = [header[f"NAXIS{i}"] for i in range(1, header["NAXIS"] + 1)]
        count = int(np.prod(axes)) if axes else 0
        dtype = {-32: ">f4", -64: ">f8", 32: ">i4", 64: ">i8", 8: "u1"}[header["BITPIX"]]
        nbytes = count * abs(header["BITPIX"]) // 8
        array = np.frombuffer(raw, dtype=dtype, count=count, offset=pos).astype(float)
        if axes:
            array = array.reshape(tuple(reversed(axes)))
        result.append((header, array))
        pos += ((nbytes + 2879) // 2880) * 2880
    return result


def load_flux(filename):
    images = fits_images(DATA / filename)
    header, coeff = images[0]
    extensions = {h.get("EXTNAME"): a for h, a in images[1:]}
    knots = tuple(extensions[f"KNOTS{i}"] for i in range(coeff.ndim))
    degrees = tuple(header[f"ORDER{i}"] for i in range(coeff.ndim))
    # Photospline evaluates the compact-support basis at the horizon even
    # below the usual SciPy base interval (cos zenith = 0.01745 for MCEq).
    # Zero-padding retains exactly those basis functions, without polynomial
    # extrapolation or discarding near-horizontal neutrinos.
    coeff = np.pad(coeff, [(k, k) for k in degrees])
    knots = tuple(np.r_[t[0] - (t[1] - t[0]) * np.arange(k, 0, -1),
                          t, t[-1] + (t[-1] - t[-2]) * np.arange(1, k + 1)]
                  for t, k in zip(knots, degrees))
    spline = NdBSpline(knots, coeff, degrees, extrapolate=False)
    def flux(energy, coszen):
        energy, coszen = np.broadcast_arrays(energy, coszen)
        coords = np.stack((np.log10(energy), np.abs(coszen)), axis=-1)
        values = 10.0 ** spline(coords)
        if not np.isfinite(values).all():
            raise ValueError(f"Coordinates outside spline domain: {filename}")
        return values
    return flux


def cross_sections(energy):
    s = CFG["cross_sections"]
    result = []
    for sign in ("nu", "antinu"):
        total = np.array(s[f"{sign}_cc_pb"]) + np.array(s[f"{sign}_nc_pb"])
        if np.any(energy < s["energy_gev"][0]) or np.any(energy > s["energy_gev"][-1]):
            raise ValueError("Cross-section extrapolation forbidden")
        result.append(np.exp(np.interp(np.log(energy), np.log(s["energy_gev"]), np.log(total))) * s["cm2_per_pb"])
    return result


def angular_integral(flux, energy, order=None):
    c = CFG["target"]
    x, w = np.polynomial.legendre.leggauss(order or c["quadrature_order"])
    width = c["coszen_max"] - c["coszen_min"]
    cz = c["coszen_min"] + width * (x + 1) / 2
    return 2 * np.pi * width / 2 * np.sum(flux(energy[:, None], cz[None, :]) * w, axis=1)


def interaction_rate(energy, nu_integral, antinu_integral):
    c = CFG["target"]
    nu_sigma, bar_sigma = cross_sections(energy)
    targets = c["volume_cm3"] * c["density_g_cm3"] * c["avogadro"]
    return np.log(10) * energy * c["exposure_s"] * targets * (nu_integral * nu_sigma + antinu_integral * bar_sigma)


def conventional_rate(energy, order=None):
    nu = sum(angular_integral(load_flux(f"H3a_SIBYLL23C_conv_{f}.fits"), energy, order) for f in ("nue", "numu"))
    bar = sum(angular_integral(load_flux(f"H3a_SIBYLL23C_conv_{f}bar.fits"), energy, order) for f in ("nue", "numu"))
    # No conventional atmospheric tau component in this input model.
    return interaction_rate(energy, nu, bar)


def prompt_rate(energy, variant="central", order=None):
    integral = angular_integral(load_flux(f"BERSS_H3p_{variant}.fits"), energy, order)
    # BERSS tables give equal fluxes for nue, numu and each antiparticle;
    # atmospheric nutau is zero in this benchmark.
    return interaction_rate(energy, 2 * integral, 2 * integral)


def astro_flux(energy):
    c = CFG["astrophysical"]
    eb = 10 ** c["log10_break_gev"]
    reference_index = c["gamma_low"] if eb > c["reference_energy_gev"] else c["gamma_high"]
    norm_break = c["per_flavour_nu_plus_antinu"] * (eb / c["reference_energy_gev"]) ** (-reference_index)
    return norm_break * (energy / eb) ** (-np.where(energy < eb, c["gamma_low"], c["gamma_high"]))


def astro_rate(energy):
    c, t = CFG["astrophysical"], CFG["target"]
    integral = 2 * np.pi * (t["coszen_max"] - t["coszen_min"]) * c["flavours"] * astro_flux(energy)
    return interaction_rate(energy, c["nu_fraction"] * integral, (1 - c["nu_fraction"]) * integral)


def build():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import LogLocator, LogFormatterMathtext
    c, p = CFG["target"], CFG["plot"]
    energy = np.geomspace(c["energy_min_gev"], c["energy_max_gev"], c["energy_samples"])
    conv, prompt, lower, upper, astro = conventional_rate(energy), prompt_rate(energy), prompt_rate(energy, "lower"), prompt_rate(energy, "upper"), astro_rate(energy)
    out = HERE.parents[1] / "media/backgrounds"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "neutrino_interaction_rates.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["energy_gev", "conventional_per_year_per_decade", "prompt_central", "prompt_lower", "prompt_upper", "astro_per_year_per_decade"])
        writer.writerows(zip(energy, conv, prompt, lower, upper, astro))
    plt.rcParams.update({"font.size": p["font_size"], "text.color": p["foreground"], "axes.labelcolor": p["foreground"], "xtick.color": p["foreground"], "ytick.color": p["foreground"], "svg.fonttype": "path", "mathtext.fontset": "stix"})
    fig, ax = plt.subplots(figsize=(p["width_in"], p["height_in"]), facecolor=p["background"])
    ax.set_facecolor(p["background"])
    ax.fill_between(energy, lower, upper, color=p["prompt"], alpha=0.18, linewidth=0)
    ax.loglog(energy, conv, color=p["conventional"], lw=3, label=r"Atmospheric — $\pi/K$")
    ax.loglog(energy, prompt, color=p["prompt"], lw=2.5, ls="--", label="Prompt — charm (model)")
    a = CFG["astrophysical"]
    valid = (energy >= a["sensitive_min_gev"]) & (energy <= a["sensitive_max_gev"])
    ax.loglog(energy, astro, color=p["astrophysical"], lw=2, ls=":")
    ax.loglog(energy[valid], astro[valid], color=p["astrophysical"], lw=3.5, label="Astrophysical — IceCube fit")
    ax.set_xlim(energy[0], energy[-1]); ax.set_ylim(p["y_min"], p["y_max"])
    ax.set_xticks([1e3, 1e4, 1e5, 1e6, 1e7], [r"$1\,\mathrm{TeV}$", r"$10\,\mathrm{TeV}$", r"$100\,\mathrm{TeV}$", r"$1\,\mathrm{PeV}$", r"$10\,\mathrm{PeV}$"])
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=8))
    ax.yaxis.set_major_formatter(LogFormatterMathtext())
    ax.set_xlabel(r"Neutrino energy $E_\nu$")
    ax.set_ylabel(r"$\nu N$ interactions / year / decade")
    ax.grid(which="major", color=p["grid"], alpha=0.65, lw=0.7)
    ax.tick_params(which="minor", length=0)
    for spine in ax.spines.values():
        spine.set_color(p["grid"])
    ax.legend(loc="upper right", frameon=False, labelcolor="linecolor", fontsize=p["font_size"])
    fig.subplots_adjust(left=0.11, bottom=0.16, right=0.94, top=0.95)
    fig.savefig(out / "neutrino_interaction_rates.svg")
    fig.savefig(out / "neutrino_interaction_rates.png", dpi=150)
    plt.close(fig)
    for e in [1e3, 1e4, 1e5, 1e6]:
        ee = np.array([e])
        print(f"{e:g} GeV: conventional={conventional_rate(ee)[0]:.3g}, prompt={prompt_rate(ee)[0]:.3g}, astro={astro_rate(ee)[0]:.3g} / year / decade")


if __name__ == "__main__":
    build()
