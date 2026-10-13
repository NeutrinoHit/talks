"""Geometry tests run always; data tests need NT_GVD_GALACTIC_TEX=<path to GVD-Galactic.tex>."""
import os
import unittest
import numpy as np
import build_gvd_galactic as g

TEX = os.environ.get("NT_GVD_GALACTIC_TEX")


class GeometryTests(unittest.TestCase):
    def test_galactic_centre_and_pole(self):
        ra, dec = g.gal_to_eq(0.0, 0.0)
        self.assertAlmostEqual(float(ra), 266.405, places=2)
        self.assertAlmostEqual(float(dec), -28.936, places=2)
        ra, dec = g.gal_to_eq(0.0, 90.0)
        self.assertAlmostEqual(float(ra), 192.859, places=2)
        self.assertAlmostEqual(float(dec), 27.128, places=2)

    def test_round_trip(self):
        l, b = np.array([10.0, 200.0, 300.0]), np.array([-40.0, 5.0, 70.0])
        l2, b2 = g.eq_to_gal(*g.gal_to_eq(l, b))
        np.testing.assert_allclose(l2, l, atol=1e-9)
        np.testing.assert_allclose(b2, b, atol=1e-9)

    def test_circle_radius(self):
        cl, cb = g.circle(75.0, -6.0, 5.0)
        sep = np.rad2deg(np.arccos(np.clip(g.unit(cl, cb) @ g.unit(75.0, -6.0), -1, 1)))
        np.testing.assert_allclose(sep, 5.0, atol=1e-9)


@unittest.skipUnless(TEX, "set NT_GVD_GALACTIC_TEX to the arXiv:2411.05608v2 source file")
class PaperTests(unittest.TestCase):
    def test_reproduces_published_test(self):
        rows = g.read_table(TEX)
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(r[1] >= 200 for r in rows))
        b = np.array([r[3] for r in rows]); l = np.array([r[2] for r in rows])
        self.assertAlmostEqual(float(np.median(np.abs(b))), 10.4, delta=0.1)   # paper: 10.4 deg
        med = g.scrambled_medians(l, b, n=50_000)
        self.assertAlmostEqual(float(med.mean()), 31.4, delta=0.5)             # paper: 31.4 deg
        self.assertAlmostEqual(float(np.mean(med <= np.median(np.abs(b)))), 0.014, delta=0.003)  # paper: 1.4e-2


if __name__ == "__main__":
    unittest.main()
