import unittest
from pathlib import Path
import numpy as np
import digitize_effective_areas as d
import build_response_figures as b


class HeseTests(unittest.TestCase):
    def test_grid_calibration_is_linear(self):
        kx, ky, vertical, horizontal = d.hese_calibration(Path(d.HESE_SVG).read_text())
        self.assertLess(np.abs(np.polyval(kx, np.arange(1, 5)) - vertical).max(), 0.01)
        self.assertLess(np.abs(np.polyval(ky, np.arange(-3, 4)) - horizontal).max(), 0.01)

    def test_bins_are_common_and_008_dex_wide(self):
        steps = b.hese_steps()
        self.assertEqual(set(steps), {"nu_e", "nu_mu", "nu_tau"})
        for rows in steps.values():
            widths = np.array([r[1] - r[0] for r in rows])
            self.assertLess(np.abs(widths - 0.08).max(), 0.002)

    def test_glashow_bin(self):
        rows = b.hese_steps()["nu_e"]
        peak = max(rows, key=lambda r: r[2])
        self.assertTrue(peak[0] < np.log10(6300) < peak[1])
        self.assertTrue(400 < peak[2] < 800)

    def test_flavour_order_at_low_energy(self):
        s = b.hese_steps()
        at = lambda f: next(r[2] for r in s[f] if r[0] <= 1.7 < r[1])
        self.assertTrue(at("nu_e") > at("nu_tau") > at("nu_mu"))


class SpieringTests(unittest.TestCase):
    def test_trace_lies_on_original_pixels(self):
        from PIL import Image
        rgb = np.array(Image.open(d.SPIERING_PNG).convert("RGB")).astype(int)
        inv = lambda t, v: np.interp(v, sorted(t), [t[k] for k in sorted(t)])
        for label, (x, y) in d.spiering_curves().items():
            mask = np.abs(rgb - np.array(d.SP_COLOURS[label])).sum(-1) < 90
            if label == "90-120":   # hidden segments are filled from the curves drawn on top
                mask |= np.abs(rgb - np.array(d.SP_COLOURS["150-180"])).sum(-1) < 90
                mask |= np.abs(rgb - np.array(d.SP_COLOURS["0-30"])).sum(-1) < 90
            px, py = np.rint(inv(d.SP_X_TICKS, x)).astype(int), np.rint(inv(d.SP_Y_TICKS, y)).astype(int)
            hits = [mask[max(0, j - 3):j + 4, i].any() for i, j in zip(px, py)]
            with self.subTest(label=label):
                self.assertGreater(np.mean(hits), 0.97)

    def test_curve_ranges(self):
        c = b.spiering_curves()
        self.assertAlmostEqual(c["150-180"][1].max(), 1.58, delta=0.05)   # upward maximum near log E = 5.2
        self.assertAlmostEqual(c["0-30"][1][-1], c["90-120"][1][-1], delta=0.05)  # curves meet at log E = 9


if __name__ == "__main__":
    unittest.main()
