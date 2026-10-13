import build_km3_energy as b


def test_published_numbers():
    mu, nu = b.ROWS
    assert mu[2] == 120.0 and mu[3] == (60.0, 230.0) and mu[4] == (35.0, 380.0)     # 120 +110 -60 PeV; 90 %: 35-380
    assert nu[2] == 220.0 and nu[3] == (110.0, 790.0) and nu[4] == (72.0, 2600.0)   # median; 68 %; 90 %: 72 PeV-2.6 EeV
    for r in b.ROWS:
        assert r[4][0] < r[3][0] < r[2] < r[3][1] < r[4][1]
