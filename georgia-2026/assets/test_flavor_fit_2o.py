"""Independent checks against the printed unified 2O benchmark."""

import unittest

from flavor_fit_2o import REFERENCE, observables, profiled_scales


class PublishedBenchmarkTests(unittest.TestCase):
    def test_eq_5_60_values(self):
        values = observables(REFERENCE)
        # Ding et al., JHEP 11 (2023) 083, Eq. (5.60). Tolerances reflect
        # the number of digits printed in the paper, not a fitted objective.
        expected = {
            "sin2_theta12_pmns": (0.3409, 0.00005),
            "sin2_theta13_pmns": (0.02271, 0.00001),
            "sin2_theta23_pmns": (0.5079, 0.00005),
            "delta_cp_pmns_deg": (244.3, 0.1),
            "dm21_over_dm31": (0.02909, 0.00001),
            "theta12_ckm": (0.227, 0.0005),
            "theta13_ckm": (0.00350, 0.00001),
            "theta23_ckm": (0.0389, 0.00005),
            "delta_cp_ckm_deg": (71.08, 0.1),
            "md_over_ms": (0.0503, 0.00005),
            "m1_mev": (15.00, 0.02),
            "m2_mev": (17.30, 0.02),
            "m3_mev": (52.69, 0.02),
        }
        for name, (published, tolerance) in expected.items():
            with self.subTest(name=name):
                self.assertLessEqual(abs(values[name] - published), tolerance)

    def test_four_overall_scales_match_their_anchor_data(self):
        scales = profiled_scales(REFERENCE, "paper-2023")
        values = observables(REFERENCE, scales)
        self.assertAlmostEqual(values["mt_gev"], 89.213, places=9)
        self.assertAlmostEqual(values["mb_gev"], 0.965, places=9)
        self.assertAlmostEqual(values["mtau_gev"], 1.293, places=9)


class ScorecardBookkeepingTests(unittest.TestCase):
    def test_reference_pulls_and_counts(self):
        from flavor_fit_2o import COUNTS, PAPER_DATA, reference_block
        block = reference_block()
        self.assertEqual(len(block["paper-2023"]["residuals"]), COUNTS["pulls"])
        self.assertEqual(COUNTS["pulls"], len(PAPER_DATA))
        self.assertEqual(COUNTS["measured"] - COUNTS["anchored_by_scales"], COUNTS["pulls"])
        self.assertEqual(COUNTS["measured"] - COUNTS["real_parameters"], COUNTS["degrees_of_freedom"])
        # Printed benchmark: the article quotes chi2 = 32.6; the printed inputs give 33.0.
        self.assertAlmostEqual(block["paper-2023"]["chi2"], 32.98, delta=0.05)


if __name__ == "__main__":
    unittest.main()
