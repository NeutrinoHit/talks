import numpy as np
import pytest
import build_transport as bt

pytestmark = pytest.mark.skipif(not bt.DATA.exists(), reason="transport table not in data/")


def test_horizon_open_and_ratio_bounded():
    e, z, full, bare = bt.load()
    assert abs(z[0] - 90.0) < 1e-9 and abs(z[-1] - 180.0) < 1e-9
    assert full[:, 0].min() > 0.95                               # horizon: transparent at all energies
    assert full.max() <= 1.0 + 1e-9                              # transport never adds flux


def test_regeneration_only_adds():
    e, z, full, bare = bt.load()
    assert (full >= bare * (1 - 1e-9)).all()
    i = int(np.argmin(abs(np.log10(e) - 6.0)))
    assert full[i, -1] > 2 * bare[i, -1]                         # 1 PeV through the centre: regeneration matters


def test_no_regeneration_matches_cc_plus_nc_attenuation():
    # bare = exp(-N_A sigma_tot X): its optical depth exceeds the lecture CC-only one by sigma_tot / sigma_CC
    import build_transmission as tr
    e, z, full, bare = bt.load()
    i = int(np.argmin(abs(np.log10(e) - 5.0)))
    tau_bare = -np.log(bare[i, -1])
    tau_cc = 6.02214076e23 * tr.sigma_cc(e[i]) * tr.column(180.0)
    assert 1.2 < tau_bare / tau_cc < 1.6
