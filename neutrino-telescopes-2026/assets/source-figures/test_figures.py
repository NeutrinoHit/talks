"""Checks of the extracted tables against numbers stated in the papers."""
import csv
import unittest
import numpy as np
import build as b

HERE = b.HERE


class Figures(unittest.TestCase):
    def test_txs_box_is_158_days(self):
        box = [float(r["mjd"]) for r in b.rows("txs-flare-fits.csv") if r["curve"] == "box"]
        self.assertAlmostEqual(max(box) - min(box), 158.4, delta=1.0)     # paper: 158 days

    def test_ngc_scan(self):
        g = np.load(b.DATA / "ngc1068-scan-grid.npz")
        self.assertAlmostEqual(g["neg_log10_p_local"].max(), 6.54, delta=0.1)  # local 5.0 sigma
        pos = {r["item"]: r for r in b.rows("ngc1068-scan-contours.csv")}
        self.assertAlmostEqual(float(pos["NGC 1068"]["ra_deg"]), 40.670, delta=0.01)
        self.assertAlmostEqual(float(pos["NGC 1068"]["dec_deg"]), -0.013, delta=0.01)

    def test_fermi_bands(self):
        f = [r for r in b.rows("ngc1068-sed-points.csv") if r["dataset"] == "4FGL-DR2"]
        edges = sorted({round(float(r[k]), 2) for r in f for k in ("e_lo_gev", "e_hi_gev")})
        np.testing.assert_allclose(edges, [0.05, 0.1, 0.3, 1, 3, 10, 30, 300], rtol=0.01)

    def test_radio_samples(self):
        r = b.rows("radio-flux-average.csv")
        self.assertEqual(sum(x["item"] == "individual_neutrino_agn" for x in r), 36)   # Fig. 2: 36 AGN
        stars = {x["star"] for x in b.rows("radio-sky-stars.csv")}
        self.assertEqual(len(stars), 36)

    def test_ic170922a_contour(self):
        c = np.array([(float(r["ra_deg"]), float(r["dec_deg"])) for r in b.rows("ic170922a-contour-digitized.csv")])
        # Science 361 (2018): RA 77.43 +0.95/-0.65, Dec 5.72 +0.50/-0.30 (90%)
        for got, ref in ((c[:, 0].min(), 76.78), (c[:, 0].max(), 78.38), (c[:, 1].min(), 5.42), (c[:, 1].max(), 6.22)):
            self.assertAlmostEqual(got, ref, delta=0.06)


    def test_txs_lightcurve(self):
        marks = b.rows("txs-lightcurve-marks.csv")
        lines = sorted(float(r["value"]) for r in marks if r["item"] == "neutrino_line")
        self.assertAlmostEqual(lines[0], 2017.724, delta=0.02)               # IC-170922A, 22 Sep 2017
        self.assertAlmostEqual(lines[1], 2021.293, delta=0.02)               # GVD210418CA, 18 Apr 2021
        flares = [r for r in b.rows("txs-lightcurve-flares.csv") if r["curve"] == "sum"]
        peak = max(flares, key=lambda r: float(r["flux_jy"]))
        self.assertAlmostEqual(float(peak["epoch_yr"]), 2020.15, delta=0.15)  # main radio flare
        self.assertTrue(len(b.rows("txs-lightcurve-fermi.csv")) > 100)


    def test_baikal_tables(self):
        t = b.rows("baikal-limits-table1.csv")
        self.assertEqual(len(t), 3 * 92)
        ngc = {r["gamma"]: float(r["limit_gev_gamma_minus_1_cm2_s"]) for r in t if r["source"] == "NGC 1068"}
        self.assertAlmostEqual(ngc["2.0"] / 1.5e-8, 1)                     # Table 1 x 1e-8 (as before)
        self.assertAlmostEqual(ngc["2.5"] / 5.12e-6, 1)
        self.assertAlmostEqual(ngc["3.2"] / 17.06e-3, 1)
        a = b.rows("antares-limits-fig3.csv")
        self.assertEqual(sum(r["gamma"] == "2.0" for r in a), 167)
        self.assertEqual(sum(r["gamma"] == "2.5" for r in a), 167)

    def test_xray_bands(self):
        self.assertEqual(len({r["source"] for r in b.rows("xray-agn-spectra-bands.csv")}), 5)


    def test_txs_reprocessing(self):
        o = b.rows("txs-original-directions.csv"); u = b.rows("txs-updated-directions.csv")
        circ = lambda r: [x for x in r if x["kind"] == "circle"]
        self.assertEqual(sum(x["dashed"] == "1" for x in circ(o)), 2)       # two cascade-like events removed
        self.assertEqual(len(circ(o)), 14); self.assertEqual(len(circ(u)), 13)

    def test_xray_population_minimum_at_11(self):
        r = [x for x in b.rows("xray-agn-population.csv") if x["item"] == "p_binom"]
        best = min(r, key=lambda x: float(x["p"]))
        self.assertAlmostEqual(float(best["n_sources"]), 11, delta=0.1)       # 11-source ensemble


if __name__ == "__main__":
    unittest.main()
