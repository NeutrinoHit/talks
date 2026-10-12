"""Reproduce the 1 PeV slide's estimates; no transport simulation or plotting.

CSMS: arXiv:1106.3723, Table I, E=10^6 GeV (neutrino, isoscalar target).
PDG astrophysical constants: n_b,0=2.515e-7 cm^-3 (Planck 2018).
Observable diameter today: approximately 93 Gly, not c times cosmic age.
PREM diameter column: approximately 1.1e10 g/cm^2, Gandhi et al.,
Fermilab-Pub-95/221-T (Astropart. Phys. 5 (1996) 81).

Only neutrino-nucleon DIS is counted. The cosmic mean free path is evaluated
at today's homogeneous baryon density. It is not a statement about the early
Universe, dense source interiors, or a full sum over cosmic backgrounds.
P0 below is the probability of zero CC/NC interactions, not a regenerated
differential flux ratio. Surface-to-surface diameter; no detector efficiency.
"""

import json
import math


def estimate():
    sigma_cc = 690.0e-36  # cm^2; 1 pb = 10^-36 cm^2
    sigma_nc = 260.0e-36
    sigma = sigma_cc + sigma_nc
    n_b = 2.515e-7  # nucleons / cm^3
    ly_cm = 9.4607304725808e17
    mpc_cm = 3.0856775814913673e24
    diameter_ly = 93.0e9
    nucleons_per_g = 6.02214076e23  # approx. N_A nucleons per gram
    column = 1.1e10  # g/cm^2, PREM diameter, rounded
    mean_free_path_cm = 1.0 / (n_b * sigma)
    mass_interaction_length = 1.0 / (nucleons_per_g * sigma)
    tau = column / mass_interaction_length
    result = {
        "energy_GeV": 1e6,
        "sigma_cc_cm2": sigma_cc,
        "sigma_nc_cm2": sigma_nc,
        "sigma_total_cm2": sigma,
        "cosmic_nucleon_density_cm3": n_b,
        "cosmic_nucleon_density_m3": n_b * 1e6,
        "cosmic_mean_free_path_cm": mean_free_path_cm,
        "cosmic_mean_free_path_Mpc": mean_free_path_cm / mpc_cm,
        "cosmic_mean_free_path_ly": mean_free_path_cm / ly_cm,
        "observable_diameter_ly": diameter_ly,
        "mean_free_path_over_observable_diameter": mean_free_path_cm / ly_cm / diameter_ly,
        "mass_interaction_length_g_cm2": mass_interaction_length,
        "mean_free_path_water_km": mass_interaction_length / 1e5,
        "mean_free_path_at_5_5_g_cm3_km": mass_interaction_length / 5.5 / 1e5,
        "earth_diameter_column_g_cm2": column,
        "earth_diameter_optical_depth": tau,
        "earth_diameter_zero_interaction_probability": math.exp(-tau),
    }
    # Independent unit and scale checks.
    assert math.isclose(n_b * sigma * mean_free_path_cm, 1.0)
    assert 4.7e10 < result["mean_free_path_over_observable_diameter"] < 4.9e10
    assert 3000 < result["mean_free_path_at_5_5_g_cm3_km"] < 3300
    assert 0.001 < result["earth_diameter_zero_interaction_probability"] < 0.003
    return result


if __name__ == "__main__":
    print(json.dumps(estimate(), indent=2))
