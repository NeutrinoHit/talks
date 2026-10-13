import unittest
import numpy as np
from build_figures import upgoing_fraction


class GeometryTests(unittest.TestCase):
    def test_pole(self):
        np.testing.assert_allclose(upgoing_fraction(-90, [-30, 0, 30]), [0, 0.5, 1])
        np.testing.assert_allclose(upgoing_fraction(90, [-30, 0, 30]), [1, 0.5, 0])

    def test_equator(self):
        np.testing.assert_allclose(upgoing_fraction(0, [-60, -30, 0, 30, 60]), 0.5)

    def test_complementarity(self):
        delta = np.linspace(-89, 89, 151)
        np.testing.assert_allclose(upgoing_fraction(36.27, delta) + upgoing_fraction(36.27, -delta), 1)

    def test_against_sampled_rotation(self):
        h = np.linspace(0, 2 * np.pi, 100001, endpoint=False)
        for phi in [-90, 0, 36.27, 51.7666667]:
            for delta in [-70, -28.94, 5.69, 50]:
                p, d = np.deg2rad([phi, delta])
                cosz = np.sin(p) * np.sin(d) + np.cos(p) * np.cos(d) * np.cos(h)
                self.assertAlmostEqual(float(upgoing_fraction(phi, delta)), np.mean(cosz < 0), delta=3e-5)

    def test_gc(self):
        self.assertAlmostEqual(float(upgoing_fraction(36.27, -28.94)), 0.63254, delta=0.001)
        self.assertAlmostEqual(float(upgoing_fraction(51.7666667, -28.94)), 0.74757, delta=0.001)


if __name__ == "__main__":
    unittest.main()
