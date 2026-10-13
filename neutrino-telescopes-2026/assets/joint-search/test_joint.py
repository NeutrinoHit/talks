import unittest
from pathlib import Path
import numpy as np
import joint_discovery as j


class JointTests(unittest.TestCase):
    def test_decades_and_frame(self):
        (x0, x1), k, decades = j.calibration(Path(j.SOURCE_SVG).read_text())
        self.assertEqual(len(decades), 3)
        self.assertGreater(x1, x0)

    def test_samples_at_integer_declinations(self):
        for name, (s, v) in j.digitize().items():
            dec = np.degrees(np.arcsin(s))
            with self.subTest(name=name):
                self.assertLess(np.abs(dec - np.arange(-85, 0, 10)).max(), 0.05)

    def test_joint_not_worse_than_individual(self):
        data = j.read_data()
        best = np.minimum(data["IceCube 7 years"][1], data["ANTARES 9 years"][1])
        self.assertTrue(np.all(data["IceCube+ANTARES"][1] <= 1.03 * best))

    def test_csv_matches_source(self):
        data, live = j.read_data(), j.digitize()
        for name in live:
            self.assertLess(np.abs(np.log10(data[name][1] / live[name][1])).max(), 1e-3)


if __name__ == "__main__":
    unittest.main()
