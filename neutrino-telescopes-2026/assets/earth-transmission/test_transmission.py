import math
import numpy as np
import build_transmission as bt


def test_prem_mass_and_diameter_column():
    r = np.linspace(0, 6371, 200001)
    mass = np.trapezoid(4 * np.pi * (r * 1e5) ** 2 * bt.density(r), r * 1e5)
    assert abs(mass / 5.972e27 - 1) < 0.01                       # Earth mass, g
    x = bt.column(180.0, depth_km=0.0, steps=20000)
    assert 1.05e10 < x < 1.12e10                                  # Gandhi et al.: about 1.1e10 g/cm^2


def test_horizon_and_monotonic():
    # horizontal from 1 km depth: a chord of about sqrt(2 R d) = 113 km through water and crust
    xs = [bt.column(z) for z in (90.0, 120.0, 150.0, 180.0)]
    assert xs[0] < 3e7 and all(a < b for a, b in zip(xs, xs[1:]))


def test_cross_sections_and_pev_diameter():
    assert math.isclose(bt.sigma_cc(1e6), 690e-36, rel_tol=1e-9)
    assert math.isclose(bt.sigma_cc(1e6, anti=True), 660e-36, rel_tol=1e-9)
    x = bt.column(180.0, depth_km=0.0, steps=20000)
    t = bt.transmission([1e6], [x])[0, 0]
    tau = 6.02214076e23 * 690e-36 * x
    assert 0.5 * math.exp(-tau) < t < 2 * math.exp(-tau) and t < 0.03


def test_low_energy_transparent():
    e, z, x, T = bt.grid()
    assert T[0].min() > 0.99                                     # 10 GeV: essentially transparent
    assert T[-1, -1] < 1e-10 and T[-1, 0] > 0.5                  # 100 PeV: opaque through the centre, open at the horizon
