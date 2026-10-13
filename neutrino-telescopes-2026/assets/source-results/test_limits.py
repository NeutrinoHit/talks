import unittest
import build_limits as limits


class LimitsTests(unittest.TestCase):
    def test_source_count(self):
        self.assertEqual(len(limits.source_limits()), 92)

    def test_no_duplicate_sources(self):
        self.assertEqual(len({r[0] for r in limits.source_limits()}), 92)

    def test_source_values_and_units(self):
        rows = {r[0]: r[1:] for r in limits.source_limits()}
        for name, dec, flux in [("NGC 1068", -.01, 1.5e-8), ("TXS 0506+056", 5.69, .93e-8), ("KM3-230213A", -7.8, .71e-8)]:
            with self.subTest(name=name):
                self.assertAlmostEqual(rows[name][0], dec)
                self.assertAlmostEqual(rows[name][1] / flux, 1)

    def test_all_values_in_plot_range(self):
        for name, dec, flux in limits.source_limits():
            self.assertTrue(-90 <= dec <= 90, name)
            self.assertTrue(1.5e-9 < flux < 1e-7, name)


if __name__ == "__main__":
    unittest.main()
