import numpy as np

import build_tomography as tg
import build_transmission as bt


def test_homogeneous_earth_has_the_prem_mass():
    rho = tg.mean_density()
    assert abs(rho - 5.514) < 0.01                       # Earth's mean density, g/cm^3


def test_columns_agree_with_the_transmission_module():
    for t in (95.0, 130.0, 170.0):
        assert np.isclose(tg.column_with(bt.density, t), bt.column(t), rtol=1e-12)


def test_core_paths_are_darker_in_prem_and_mantle_paths_lighter():
    rho, e, z, xp, xh, tp, th = tg.grids()
    i = np.argmin(abs(e - 3e4))
    assert tp[i, -1] < th[i, -1]                         # through the centre PREM has more matter
    j = np.argmin(abs(z - 125.0))
    assert tp[i, j] > th[i, j]                           # mantle-only paths cross lighter rock than the mean
    low = e <= 1e4
    assert np.allclose(tp[low, 0], th[low, 0], atol=0.02)   # at the horizon both are nearly transparent below 10 TeV
