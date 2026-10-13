import unittest
import numpy as np
import build_gamma as g


class GammaTests(unittest.TestCase):
    def test_lhaaso_rows(self):
        rows = g.lhaaso_points()
        self.assertEqual(sum(r["region"] == "inner" for r in rows), 10)
        self.assertEqual(sum(r["region"] == "outer" for r in rows), 5)

    def test_lhaaso_matches_published_e25_axis(self):
        # Fig. 2(a) of arXiv:2305.05372v2 plots E^2.5 Flux in TeV^1.5 units;
        # first inner point is about 3.7e-10 there.
        e, phi = 12.6, 6.61e-13
        self.assertAlmostEqual(e ** 2.5 * phi / 3.725e-10, 1, places=2)
        # E^2.7 dN/dE in GeV units equals 10^5.1 times the TeV-unit product.
        self.assertAlmostEqual(g.e27_gev(e, phi) / (e ** 2.7 * phi * 10 ** 5.1), 1)

    def test_tibet_bins_recover_published_edges(self):
        # Paper bins: 100-158, 158-398, 398-1000 TeV. Agreement checks the axis calibration.
        edges = {(round(r["e_min_tev"], -0), round(r["e_max_tev"], -0)) for r in g.tibet_points()}
        for lo, hi in [(100, 158), (158, 398), (398, 1000)]:
            self.assertTrue(any(abs(a / lo - 1) < 0.01 and abs(b / hi - 1) < 0.01 for a, b in edges))

    def test_errors_bracket_points(self):
        for r in g.tibet_points():
            self.assertLess(r["e27_flux_low"], r["e27_flux"])
            self.assertLess(r["e27_flux"], r["e27_flux_high"])
        for r in g.lhaaso_points():
            self.assertTrue(r["total"][0] <= r["stat"][0] < r["y"] < r["stat"][1] <= r["total"][1])

    def test_values_in_plot_range(self):
        ys = [r["y"] for r in g.lhaaso_points()] + [r["e27_flux"] for r in g.tibet_points()]
        self.assertTrue(6e-6 < min(ys) and max(ys) < 5e-4)


if __name__ == "__main__":
    unittest.main()
