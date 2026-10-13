import unittest
import numpy as np
import build_energy_budget as eb
import converter_cycle


class IgrbTests(unittest.TestCase):
    def test_table_rows(self):
        rows = eb.igrb_bins()
        self.assertEqual(len(rows), 26)
        self.assertEqual(rows[0][:5], (0.1, 0.14, 2.8e-6, 0.6e-6, 0.6e-6))
        self.assertAlmostEqual(rows[0][5] / 0.9e-6, 1)   # FG model: +0.1/-0.9 x 1e-6
        self.assertAlmostEqual(rows[0][6] / 0.1e-6, 1)
        self.assertEqual(rows[-1][0:3], (580.0, 820.0, 2.3e-12))
        self.assertTrue(rows[-1][-1] and not any(r[-1] for r in rows[:-1]))

    def test_bins_sum_to_published_integral(self):
        total = sum(r[2] for r in eb.igrb_bins() if not r[-1])
        self.assertLess(abs(total / eb.IGRB_FIT["i_above_100mev"] - 1), 0.1)

    def test_converted_points_follow_published_fit(self):
        f = eb.IGRB_FIT
        for row in eb.igrb_bins()[:-1]:
            ec, k = eb.igrb_e2flux(row)
            fit = ec**2 * f["i100_per_mev"] * 1e3 * (ec / 0.1) ** (-f["gamma"]) * np.exp(-ec / f["ecut_gev"])
            sigma = k * max(row[3], row[4])
            with self.subTest(e=ec):
                self.assertLess(abs(k * row[2] - fit), 3.5 * sigma)


class AugerTests(unittest.TestCase):
    def test_table_rows(self):
        rows = eb.auger_points()
        self.assertEqual(len(rows), 20)
        self.assertEqual(sum(r[-1] for r in rows), 2)
        self.assertEqual(rows[10][0], 19.45)
        self.assertAlmostEqual(rows[10][1] / 2.492e-21, 1)

    def test_table_matches_fitted_normalization(self):
        # Table III: J0 = 1.315e-18 at 10^18.5 eV; interpolate the two neighbouring data bins.
        rows = {r[0]: r[1] for r in eb.auger_points()}
        self.assertLess(abs(np.sqrt(rows[18.45] * rows[18.55]) / 1.315e-18 - 1), 0.02)

    def test_unit_conversion(self):
        value = eb.auger_e2flux(19.45, 2.492e-21)
        hand = 10**38.9 * 2.492e-21 / 1e10 / 3.15576e7 / 1e9
        self.assertAlmostEqual(value / hand, 1, places=6)
        self.assertTrue(5e-9 < value < 8e-9)


class NeutrinoTests(unittest.TestCase):
    def test_bpl_normalization(self):
        self.assertAlmostEqual(eb.bpl_e2flux(1e5, **eb.CF_BPL) / 1.77e-8, 1, places=6)

    def test_best_fit_inside_digitized_band(self):
        e, f = eb.icecube_band()
        self.assertAlmostEqual(np.log10(e.min()), 4.143, places=2)
        self.assertAlmostEqual(np.log10(e.max()), 6.668, places=2)
        for log_e in (4.3, 4.6, 5.0, 5.5, 6.0, 6.5):
            near = np.abs(np.log10(e) - log_e) < 0.03
            with self.subTest(log_e=log_e):
                self.assertTrue(f[near].min() < eb.bpl_e2flux(10**log_e, **eb.CF_BPL) < f[near].max())


class WaxmanBahcallTests(unittest.TestCase):
    def test_per_flavour_band(self):
        lo, hi = eb.wb_per_flavour()
        self.assertAlmostEqual(lo / 0.45e-8, 1)
        self.assertAlmostEqual(hi / 2.25e-8, 1)

    def test_flavour_bookkeeping(self):
        # At the source: nu_mu+anti-nu_mu = I_max, nu_e = I_max/2; oscillations share 1.5 I_max over 3 flavours.
        self.assertAlmostEqual((1 + 0.5) / 3, eb.WB_PER_FLAVOUR)


class ConverterTests(unittest.TestCase):
    def test_svg_has_no_flux_numbers(self):
        svg = converter_cycle.build()
        self.assertIn("Γ²", svg)
        self.assertNotIn("cm", svg)


if __name__ == "__main__":
    unittest.main()
