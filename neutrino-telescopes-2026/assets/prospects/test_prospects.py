import unittest
import numpy as np
import build_prospects as bp


class GeometryTests(unittest.TestCase):
    def test_galactic_centre_and_pole(self):
        ra, dec = bp.galactic_to_equatorial(0.0, 0.0)
        self.assertAlmostEqual(float(ra), 266.40, delta=0.02)
        self.assertAlmostEqual(float(dec), -28.94, delta=0.02)
        ra, dec = bp.galactic_to_equatorial(0.0, 90.0)
        self.assertAlmostEqual(float(dec), bp.NGP_DEC, places=6)

    def test_plane_maximum_declination(self):
        ra, dec = bp.galactic_to_equatorial(np.linspace(0, 360, 36001), np.zeros(36001))
        self.assertAlmostEqual(dec.max(), 90 - bp.NGP_DEC, places=3)

    def test_sky_positions_match_published_table(self):
        self.assertEqual(bp.SKY["NGC 1068"], (40.67, -0.01))
        self.assertEqual(bp.SKY["TXS 0506+056"], (77.36, 5.69))
        self.assertEqual(bp.SKY["KM3-230213A"], (94.30, -7.80))

    def test_cubes_encode_volume_ratio(self):
        self.assertAlmostEqual(bp.cube_side_ratio() ** 3, 30.0)


class ContentTests(unittest.TestCase):
    def test_milestones_have_sources_and_order(self):
        years = [int(m[0].lstrip("≈")) for m in bp.MILESTONES]
        self.assertEqual(years, sorted(years))
        self.assertTrue(all(m[3] for m in bp.MILESTONES))

    def test_break_matches_theory_fit(self):
        import build_energy_budget as eb
        self.assertAlmostEqual(np.log10(bp.QUESTIONS["break"]["at"]), eb.CF_BPL["log_ebreak"])

    def test_questions_have_sources(self):
        self.assertTrue(all(v["source"] for v in bp.QUESTIONS.values()))

    def test_people_chain_has_no_names(self):
        svg = bp.people_chain()
        for name in ("Allakhverdyan", "Sheshukov", "Naumov", "Аллахвердян", "Шешуков"):
            self.assertNotIn(name, svg)


if __name__ == "__main__":
    unittest.main()
