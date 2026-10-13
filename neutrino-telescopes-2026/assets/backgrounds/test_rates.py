"""Regression data from nuflux 2.0.7 tests/test_data.json; physics checks."""
import unittest
from unittest.mock import patch
import numpy as np
import build_rates as r


class RatesTests(unittest.TestCase):
    def test_upstream_spline_reference(self):
        e = np.logspace(3, 7, 5)
        references = {
            "H3a_SIBYLL23C_conv_numu.fits": [4.798311601687468e-11, 3.310667616402243e-14, 7.871596989407697e-18, 5.942323605794342e-22, 2.892727509066889e-26],
            "H3a_SIBYLL23C_conv_nue.fits": [4.350807132758245e-12, 1.413597521850716e-15, 2.766743624412999e-19, 3.080483243122591e-23, 7.387700702936858e-27],
            "BERSS_H3p_central.fits": [1.5600759862696282e-14, 4.94780108444536e-17, 9.296651876102378e-20, 7.020820395051275e-23, 6.744784031618625e-26],
        }
        for name, expected in references.items():
            with self.subTest(name=name):
                # Photospline's float32 basis evaluation differs at ~1e-6.
                np.testing.assert_allclose(r.load_flux(name)(e, 0), expected, rtol=1e-5, atol=0)

    def test_quadrature_convergence(self):
        e = np.geomspace(1e3, 1e7, 31)
        np.testing.assert_allclose(r.conventional_rate(e, 96), r.conventional_rate(e, 192), rtol=2e-5)

    def test_hemisphere_solid_angle(self):
        actual = r.angular_integral(lambda e, z: np.ones(np.broadcast_shapes(e.shape, z.shape)), np.array([1e3]))
        np.testing.assert_allclose(actual, [2 * np.pi], rtol=1e-12)

    def test_csms_signs_and_units(self):
        nu, bar = r.cross_sections(np.array([1e3, 1e6]))
        np.testing.assert_allclose(nu, [8.2e-36, 9.5e-34], rtol=1e-12)
        np.testing.assert_allclose(bar, [4.8e-36, 9.0e-34], rtol=1e-12)

    def test_cross_section_domain(self):
        with self.assertRaises(ValueError):
            r.cross_sections(np.array([100]))

    def test_astro_normalization_and_break(self):
        c = r.CFG["astrophysical"]
        self.assertAlmostEqual(r.astro_flux(np.array([1e5]))[0] / c["per_flavour_nu_plus_antinu"], 1.0)
        eb = 10 ** c["log10_break_gev"]
        values = r.astro_flux(np.array([eb * (1 - 1e-8), eb * (1 + 1e-8)]))
        np.testing.assert_allclose(values[0], values[1], rtol=1e-6)
        with patch.dict(c, {"log10_break_gev": 6.0}):
            self.assertAlmostEqual(r.astro_flux(np.array([1e5]))[0] / c["per_flavour_nu_plus_antinu"], 1.0)

    def test_prompt_band_and_positive_rates(self):
        e = np.geomspace(1e3, 1e7, 100)
        lower, central, upper = (r.prompt_rate(e, v) for v in ("lower", "central", "upper"))
        self.assertTrue(np.all(lower <= central))
        self.assertTrue(np.all(central <= upper))
        self.assertTrue(np.all(r.conventional_rate(e) > 0))
        self.assertTrue(np.all(r.astro_rate(e) > 0))

    def test_all_flavour_and_year_normalization(self):
        e = np.array([1e5])
        nu, bar = r.cross_sections(e)
        t, a = r.CFG["target"], r.CFG["astrophysical"]
        expected = np.log(10) * e * t["exposure_s"] * t["volume_cm3"] * t["density_g_cm3"] * t["avogadro"] * 2 * np.pi * 3 * r.astro_flux(e) * (nu + bar) / 2
        np.testing.assert_allclose(r.astro_rate(e), expected, rtol=1e-12)


if __name__ == "__main__":
    unittest.main()
