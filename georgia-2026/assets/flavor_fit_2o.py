"""Independent numerical implementation of the unified 2O benchmark.

Equations: Ding, Liu, Lu and Weng, JHEP 11 (2023) 083,
arXiv:2307.14926, Eqs. (2.16)-(2.18), (5.7)-(5.8), (5.53), (5.58)-(5.60).

The q series are truncated after q**6. Near the published modulus, |q| is
approximately 0.0012; the truncation must be checked against the printed
benchmark before any fit result is used in the talk.

The 2023 data set follows Table 3 of the paper. The optional JUNO update
replaces only the solar angle and the ratio of mass splittings; it is a local
refit with mixed-vintage inputs, not a new collaboration or global-fit result.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares


REFERENCE = {
    "tau_re": -0.19991,
    "tau_im": 1.07381,
    "e2": 0.69822,
    "e3": 86.19360,
    "u2": 122.34700,
    "u3": 0.49606,
    "d2": 45.08310,
    "d3": 1.15319,
    "d4": 0.01338,
    "d5": 0.00362,
}

REFERENCE_SCALES = {
    "e_gev": 0.07132,
    "nu_ev": 0.03027760,
    "u_gev": 0.58474,
    "d_gev": 0.29190,
}

# Paper Table 3, with lower and upper one-sigma errors in the final columns.
PAPER_DATA = {
    "sin2_theta12_pmns": (0.303, 0.012, 0.012),
    "sin2_theta13_pmns": (0.02225, 0.00059, 0.00056),
    "sin2_theta23_pmns": (0.451, 0.016, 0.019),
    "delta_cp_pmns_deg": (232.0, 26.0, 36.0),
    "me_over_mmu": (0.00474, 0.00004, 0.00004),
    "mmu_over_mtau": (0.0588, 0.0005, 0.0005),
    "dm21_over_dm31": (0.02956, 0.00084, 0.00084),
    "theta12_ckm": (0.2274, 0.0007, 0.0007),
    "theta13_ckm": (0.00349, 0.00013, 0.00013),
    "theta23_ckm": (0.0400, 0.0006, 0.0006),
    "delta_cp_ckm_deg": (69.21, 3.11, 3.11),
    "mu_over_mc": (0.00193, 0.00060, 0.00060),
    "mc_over_mt": (0.00280, 0.00012, 0.00012),
    "md_over_ms": (0.0505, 0.0062, 0.0062),
    "ms_over_mb": (0.0182, 0.0010, 0.0010),
}

JUNO_DRAFT = {
    "sin2_theta12_pmns": (0.3036, 0.0064, 0.0064),
    # Ratio and uncorrelated propagated error from the author's 31 Aug 2026
    # JUNO draft: dm21=(7.388±0.078)e-5 and dm31=(2.509±0.026)e-3 eV² (NO).
    "dm21_over_dm31": (7.388e-5 / 2.509e-3, 0.000436, 0.000436),
}


@dataclass(frozen=True)
class Series:
    power: float
    coefficients: tuple[float, ...]
    factor: float = 1.0

    def value(self, tau: complex) -> complex:
        q = np.exp(2j * np.pi * tau)
        return complex(self.factor * np.exp(2j * np.pi * tau * self.power)
                       * np.polynomial.polynomial.polyval(q, self.coefficients))


def divisor_sigma(n: int, power: int) -> int:
    return sum(d**power for d in range(1, n + 1) if n % d == 0)


E2 = tuple([1.0] + [-24.0 * divisor_sigma(n, 1) for n in range(1, 7)])
E4 = tuple([1.0] + [240.0 * divisor_sigma(n, 3) for n in range(1, 7)])
E6 = tuple([1.0] + [-504.0 * divisor_sigma(n, 5) for n in range(1, 7)])

Y2_WEIGHT2 = (
    Series(0, (1, 24, 24, 96, 24, 144, 96)),
    Series(1 / 2, (1, 4, 6, 8, 13, 12, 14), 8 * math.sqrt(3)),
)
YHAT2P_WEIGHT5 = (
    Series(1 / 8, (1, 123, 378, -191, -1428, -1134, -735)),
    Series(7 / 8, (7, 51, -27, -28, -459, 378, -357), 8),
)
Y3P_WEIGHT4 = (
    Series(1 / 2, (1, -4, -2, 24, -11, -44, 22), 2 * math.sqrt(2)),
    Series(3 / 4, (1, -6, 11, -2, -11, 14, -38), 4),
    Series(1 / 4, (-1, 2, 11, -22, -50, 96, 121)),
)
YHAT4_WEIGHT3 = (
    Series(5 / 8, (1, -1, -4, 3, 1, 3, 13), 4 * math.sqrt(3)),
    Series(3 / 8, (1, 1, -7, -6, 16, 9, -6), 2 * math.sqrt(3)),
    Series(7 / 8, (1, -3, 3, -4, 3, 6, -3), -8),
    Series(1 / 8, (1, 3, -6, -23, 12, 66, -15)),
)
Y1P_WEIGHT6 = Series(1 / 2, (1, -12, 54, -88, -99, 540, -418))


def serre_derivative(series: Series, weight: int) -> Series:
    """Compute D_k=q*d/dq-k*E2/12 for a fractional-power q series."""
    coefficients = np.asarray(series.coefficients, dtype=float)
    e2_product = np.convolve(E2, coefficients)[: len(coefficients)]
    derivative = (series.power + np.arange(len(coefficients))) * coefficients
    return Series(series.power,
                  tuple(float(x) for x in derivative - weight * e2_product / 12),
                  series.factor)


YHAT4_WEIGHT5 = tuple(
    Series(s.power, s.coefficients, -8 * s.factor)
    for s in (serre_derivative(component, 3) for component in YHAT4_WEIGHT3)
)


def modular_forms(tau: complex) -> dict[str, object]:
    y2 = np.array([s.value(tau) for s in Y2_WEIGHT2], dtype=complex)
    e4 = Series(0, E4).value(tau)
    return {
        "y2": y2,
        "y2w6": e4 * y2,
        "yh2p": np.array([s.value(tau) for s in YHAT2P_WEIGHT5], dtype=complex),
        "y3p": np.array([s.value(tau) for s in Y3P_WEIGHT4], dtype=complex),
        "yh4w3": np.array([s.value(tau) for s in YHAT4_WEIGHT3], dtype=complex),
        "yh4w5": np.array([s.value(tau) for s in YHAT4_WEIGHT5], dtype=complex),
        "y1w6": Series(0, E6).value(tau),
        "y1pw6": Y1P_WEIGHT6.value(tau),
    }


def mass_matrices(params: dict[str, float], scales: dict[str, float] | None = None):
    if scales is None:
        scales = REFERENCE_SCALES
    tau = complex(params["tau_re"], params["tau_im"])
    f = modular_forms(tau)
    y2, a, b, c, d = f["y2"], f["yh2p"], f["y3p"], f["yh4w3"], f["yh4w5"]
    w6, s6, sp6 = f["y2w6"], f["y1w6"], f["y1pw6"]
    e2, e3 = params["e2"], params["e3"]
    u2, u3 = params["u2"], params["u3"]
    d2, d3, d4, d5 = (params[key] for key in ("d2", "d3", "d4", "d5"))
    root2, root3 = math.sqrt(2), math.sqrt(3)

    charged_lepton = np.array([
        [-a[1] - root2 * e2 * d[2], root3 * e2 * d[0], root2 * a[0] + e2 * d[3]],
        [-a[0] + root2 * e2 * d[3], -root2 * a[1] + e2 * d[2], -root3 * e2 * d[1]],
        [e3 * b[0], e3 * b[2], e3 * b[1]],
    ], dtype=complex) * scales["e_gev"]

    denominator = y2[0] ** 2 - 3 * y2[1] ** 2
    neutrino = np.array([
        [1 / (2 * y2[0]), 0, 0],
        [0, root3 * y2[1] / denominator, -y2[0] / denominator],
        [0, -y2[0] / denominator, root3 * y2[1] / denominator],
    ], dtype=complex) * scales["nu_ev"]

    up_quark = np.array([
        [c[2], -c[1], 0],
        [c[3], c[0], 0],
        [-u2 * w6[1], u2 * w6[0], u3 * s6],
    ], dtype=complex) * scales["u_gev"]
    down_quark = np.array([
        [s6 - d3 * w6[0], d2 * sp6 + d3 * w6[1], -d4 * w6[1]],
        [d3 * w6[1] - d2 * sp6, d3 * w6[0] + s6, d4 * w6[0]],
        [0, 0, d5],
    ], dtype=complex) * scales["d_gev"]
    return charged_lepton, neutrino, up_quark, down_quark


def dirac_masses_and_left_rotation(matrix: np.ndarray):
    # The paper's mass matrices use right-handed rows and left-handed columns.
    # Hence the physical left rotation is the right singular-vector matrix.
    _right_rotation, singular_values, left_h = np.linalg.svd(matrix)
    order = np.argsort(singular_values)
    return singular_values[order], left_h.conj().T[:, order]


def neutrino_masses_and_rotation(matrix: np.ndarray):
    eigenvalues, vectors = np.linalg.eigh(matrix.conj().T @ matrix)
    return np.sqrt(np.maximum(eigenvalues, 0)), vectors


def angles_and_delta(matrix: np.ndarray):
    s13 = min(1.0, abs(matrix[0, 2]))
    c13 = math.sqrt(max(0.0, 1 - s13 * s13))
    s12 = min(1.0, abs(matrix[0, 1]) / c13)
    s23 = min(1.0, abs(matrix[1, 2]) / c13)
    c12 = math.sqrt(max(0.0, 1 - s12 * s12))
    c23 = math.sqrt(max(0.0, 1 - s23 * s23))
    jarlskog = float(np.imag(matrix[0, 0] * matrix[1, 1]
                              * np.conj(matrix[0, 1] * matrix[1, 0])))
    denominator = s12 * c12 * s23 * c23 * s13 * c13 * c13
    sin_delta = np.clip(jarlskog / denominator, -1, 1)
    cos_delta = (abs(matrix[1, 0]) ** 2 - s12 * s12 * c23 * c23
                 - c12 * c12 * s23 * s23 * s13 * s13)
    cos_delta /= 2 * s12 * c12 * c23 * s23 * s13
    delta = math.degrees(math.atan2(float(sin_delta), float(np.clip(cos_delta, -1, 1)))) % 360
    return s12 * s12, s13 * s13, s23 * s23, delta, (math.asin(s12), math.asin(s13), math.asin(s23))


def observables(params: dict[str, float], scales: dict[str, float] | None = None):
    me, mnu, mu, md = mass_matrices(params, scales)
    charged, ue = dirac_masses_and_left_rotation(me)
    neutrinos, unu = neutrino_masses_and_rotation(mnu)
    up, uu = dirac_masses_and_left_rotation(mu)
    down, ud = dirac_masses_and_left_rotation(md)
    pmns = ue.conj().T @ unu
    ckm = uu.conj().T @ ud
    l12, l13, l23, ldelta, _ = angles_and_delta(pmns)
    _, _, _, qdelta, qangles = angles_and_delta(ckm)
    return {
        "sin2_theta12_pmns": l12,
        "sin2_theta13_pmns": l13,
        "sin2_theta23_pmns": l23,
        "delta_cp_pmns_deg": ldelta,
        "me_over_mmu": charged[0] / charged[1],
        "mmu_over_mtau": charged[1] / charged[2],
        "dm21_over_dm31": ((neutrinos[1] ** 2 - neutrinos[0] ** 2)
                               / (neutrinos[2] ** 2 - neutrinos[0] ** 2)),
        "theta12_ckm": qangles[0],
        "theta13_ckm": qangles[1],
        "theta23_ckm": qangles[2],
        "delta_cp_ckm_deg": qdelta,
        "mu_over_mc": up[0] / up[1],
        "mc_over_mt": up[1] / up[2],
        "md_over_ms": down[0] / down[1],
        "ms_over_mb": down[1] / down[2],
        "m1_mev": neutrinos[0] * 1000,
        "m2_mev": neutrinos[1] * 1000,
        "m3_mev": neutrinos[2] * 1000,
        "mt_gev": up[2],
        "mb_gev": down[2],
        "mtau_gev": charged[2],
    }


def dataset(version: str):
    values = dict(PAPER_DATA)
    if version == "juno-aug-2026":
        values.update(JUNO_DRAFT)
    return values


def profiled_scales(params: dict[str, float], version: str):
    """Set the four overall scales using the paper's measured anchor values."""
    unit_scales = {name: 1.0 for name in REFERENCE_SCALES}
    me, mnu, mu, md = mass_matrices(params, unit_scales)
    charged, _ = dirac_masses_and_left_rotation(me)
    neutrinos, _ = neutrino_masses_and_rotation(mnu)
    up, _ = dirac_masses_and_left_rotation(mu)
    down, _ = dirac_masses_and_left_rotation(md)
    solar_splitting = 7.388e-5 if version == "juno-aug-2026" else 7.41e-5
    return {
        "e_gev": 1.293 / charged[2],
        "nu_ev": math.sqrt(solar_splitting /
                           (neutrinos[1] ** 2 - neutrinos[0] ** 2)),
        "u_gev": 89.213 / up[2],
        "d_gev": 0.965 / down[2],
    }


def residuals(params: dict[str, float], version: str):
    return pulls_from_predictions(observables(params), version)


def pulls_from_predictions(predicted: dict[str, float], version: str):
    terms = []
    for name, (central, lower, upper) in dataset(version).items():
        delta = predicted[name] - central
        if name.endswith("_deg"):
            delta = (delta + 180) % 360 - 180
        terms.append(delta / (upper if delta >= 0 else lower))
    return np.asarray(terms, dtype=float)


FIT_NAMES = ("tau_re", "tau_im", "e2", "e3", "u2", "u3", "d2", "d3", "d4", "d5")


def encode(params: dict[str, float]):
    return np.array([params["tau_re"], params["tau_im"]]
                    + [math.log(params[name]) for name in FIT_NAMES[2:]], dtype=float)


def decode(vector: np.ndarray):
    return {name: (float(vector[i]) if i < 2 else float(math.exp(vector[i])))
            for i, name in enumerate(FIT_NAMES)}


def fit(version: str, starts: int = 4, seed: int = 20260929):
    initial = encode(REFERENCE)
    lower = np.array([-0.5, 0.87] + [math.log(REFERENCE[name]) - 3.0 for name in FIT_NAMES[2:]])
    upper = np.array([0.5, 1.6] + [math.log(REFERENCE[name]) + 3.0 for name in FIT_NAMES[2:]])
    generator = np.random.default_rng(seed)
    best = None
    for run in range(starts):
        start = initial.copy()
        if run:
            if run < max(2, starts // 2):
                start[:2] += generator.normal(0, [0.008, 0.008])
                start[2:] += generator.normal(0, 0.08, size=len(start) - 2)
            else:
                start[0] = generator.uniform(-0.43, 0.43)
                start[1] = generator.uniform(
                    math.sqrt(1 - start[0] ** 2) + 0.01, 1.55)
                start[2:] += generator.normal(0, 0.6, size=len(start) - 2)
            start = np.clip(start, lower + 1e-7, upper - 1e-7)
        try:
            solution = least_squares(lambda x: residuals(decode(x), version), start,
                                     bounds=(lower, upper), max_nfev=2500,
                                     xtol=1e-11, ftol=1e-11, gtol=1e-11)
        except (FloatingPointError, ValueError, ZeroDivisionError):
            continue
        if best is None or np.sum(solution.fun**2) < np.sum(best.fun**2):
            best = solution
    assert best is not None
    fitted = decode(best.x)
    scales = profiled_scales(fitted, version)
    predictions = observables(fitted, scales)
    return {
        "dataset": version,
        "fit_scope": "local multi-start search on the positive-coupling branch of the published model",
        "starts": starts,
        "params": fitted,
        "profiled_scales": scales,
        "chi2": float(np.sum(best.fun**2)),
        "success": bool(best.success),
        "message": best.message,
        "predictions": {key: float(value) for key, value in predictions.items()},
        "residuals": {name: float(value) for name, value in zip(dataset(version), best.fun)},
    }


def reference_block():
    """Published benchmark scored against both data vintages, for the talk's scorecard."""
    predicted = observables(REFERENCE)
    block = {
        "params": REFERENCE,
        "scales": REFERENCE_SCALES,
        "predictions": {key: float(value) for key, value in predicted.items()},
    }
    for version in ("paper-2023", "juno-aug-2026"):
        pulls = pulls_from_predictions(predicted, version)
        block[version] = {
            "residuals": {name: float(p) for name, p in zip(dataset(version), pulls)},
            "chi2": float(np.sum(pulls**2)),
        }
    return block


# Counting used on the slides. The paper's 22 masses and mixing parameters are 12 masses
# (6 quark, 3 charged lepton, 3 neutrino), 4 + 4 mixing parameters, and 2 Majorana phases.
# The measured ones are 9 lepton and 10 quark quantities, 19 in all. Four of these
# (m_tau, m_t, m_b and the solar splitting) fix the four overall scales, which leaves
# the 15 pulls in PAPER_DATA. With 14 real parameters this gives 19 - 14 = 5 degrees of freedom.
COUNTS = {"paper_parameters": 22, "measured": 19, "pulls": len(PAPER_DATA),
          "anchored_by_scales": 4, "real_parameters": 14, "shape_parameters": 10,
          "degrees_of_freedom": 19 - 14}


def export_browser_grid(result: dict, path: Path, size: int = 51,
                        half_width: float = 0.025):
    """Precompute exact model outputs for the static RevealJS interaction."""
    names = list(PAPER_DATA) + ["m3_mev"]
    center_re = result["params"]["tau_re"]
    center_im = result["params"]["tau_im"]
    re_axis = np.linspace(center_re - half_width, center_re + half_width, size)
    im_axis = np.linspace(center_im - half_width, center_im + half_width, size)
    rows = []
    for im in im_axis:
        row = []
        for re in re_axis:
            params = dict(result["params"])
            params["tau_re"] = float(re)
            params["tau_im"] = float(im)
            predicted = observables(params, result["profiled_scales"])
            chi2 = float(np.sum(pulls_from_predictions(predicted, result["dataset"]) ** 2))
            row.append([float(predicted[name]) for name in names] + [chi2])
        rows.append(row)
    exported = {
        "source": "Ding et al., JHEP 11 (2023) 083, arXiv:2307.14926",
        "generator": "georgia-2026/assets/flavor_fit_2o.py",
        "fit_scope": result["fit_scope"],
        "dataset": result["dataset"],
        "names": names + ["chi2"],
        "center": [center_re, center_im],
        "re_axis": [float(x) for x in re_axis],
        "im_axis": [float(x) for x in im_axis],
        "grid": rows,
        "fit": result,
        "reference": reference_block(),
        "inputs": {version: {name: list(values) for name, values in dataset(version).items()}
                   for version in ("paper-2023", "juno-aug-2026")},
        "counts": COUNTS,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("window.NH_FLAVOR_MODEL_DATA = "
                    + json.dumps(exported, separators=(",", ":"), ensure_ascii=False)
                    + ";\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("paper-2023", "juno-aug-2026"),
                        default="paper-2023")
    parser.add_argument("--starts", type=int, default=4)
    parser.add_argument("--fit", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--export-browser", type=Path,
                        help="write a compact exact-model grid as a static JavaScript asset")
    arguments = parser.parse_args()
    if arguments.fit:
        result = fit(arguments.dataset, starts=arguments.starts)
    else:
        values = observables(REFERENCE)
        result = {
            "dataset": "published-point",
            "params": REFERENCE,
            "chi2_paper_inputs": float(np.sum(residuals(REFERENCE, "paper-2023") ** 2)),
            "predictions": {key: float(value) for key, value in values.items()},
        }
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if arguments.out:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(payload, encoding="utf-8")
    else:
        print(payload)
    if arguments.export_browser:
        if not arguments.fit:
            parser.error("--export-browser requires --fit")
        export_browser_grid(result, arguments.export_browser)


if __name__ == "__main__":
    main()
