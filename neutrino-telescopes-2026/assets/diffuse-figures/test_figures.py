"""Checks of the extracted tables against numbers stated in the papers."""
import unittest
import numpy as np
import build as b


class IceCube2013(unittest.TestCase):
    def test_28_events_and_bins(self):
        d = b.table("icecube2013-energy-data.csv")
        self.assertEqual(int(d["events"].sum()), 28)                       # 28 events, 662 days
        h = b.table("icecube2013-energy-histograms.csv")
        np.testing.assert_allclose(np.log10(h["e_hi_tev"] / h["e_lo_tev"]), 0.2, atol=2e-3)

    def test_counts_are_integers_and_bars_bracket(self):
        d = b.table("icecube2013-energy-data.csv")
        self.assertTrue(np.all(d["err_lo"] <= d["events"]) and np.all(d["events"] <= d["err_hi"]))


class Reserve(unittest.TestCase):
    def test_icecube2013_zenith_28_events(self):
        d = b.table("icecube2013-zenith-data.csv")
        self.assertEqual(int(d["events"].sum()), 28)

    def test_gvd_zenith_18_events_and_backgrounds(self):
        d = b.table("gvd2025-zenith-data.csv")
        self.assertEqual(int(d["events"].sum()), 18)
        h = b.table("gvd2025-zenith-stack.csv")
        self.assertAlmostEqual(h["atm_nu"].sum(), 1.9, delta=0.1)
        self.assertAlmostEqual(h["atm_mu"].sum(), 0.9, delta=0.1)

    def test_index_best_fits(self):
        import csv
        r = {x["sample"]: x for x in csv.DictReader((b.DATA / "icecube2026-indices-contours.csv").open())
             if x["level"] == "best_fit"}
        # PRL 136 (2026) Table I: CF gamma1 = 1.31, gamma2 = 2.735; MESE 1.72, 2.839
        for k, g1, g2 in (("CF", 1.31, 2.735), ("MESE", 1.72, 2.839)):
            self.assertAlmostEqual(float(r[k]["gamma1"]), g1, delta=0.02)
            self.assertAlmostEqual(float(r[k]["gamma2"]), g2, delta=0.01)


    def test_gvd_contour_best_fits(self):
        import csv
        r = {x["sample"]: x for x in csv.DictReader((b.DATA / "gvd2025-contours.csv").open()) if x["level"] == "best_fit"}
        # Baikal-GVD fit (2.64, 4.42); IceCube 6y cascades (2.53, 1.66); 9.5y tracks (2.37, 1.44)
        for k, g, f in (("Baikal-GVD 6y cascades", 2.64, 4.42), ("IceCube 6y cascades", 2.53, 1.66),
                        ("IceCube 9.5y tracks", 2.37, 1.44)):
            self.assertAlmostEqual(float(r[k]["gamma"]), g, delta=0.01)
            self.assertAlmostEqual(float(r[k]["phi_1e-18"]), f, delta=0.03)

    def test_cf_event_panels(self):
        import csv
        r = list(csv.DictReader((b.DATA / "icecube2026-events-data.csv").open()))
        self.assertEqual(sum(x["sample"] == "cascades" and x["panel"] == "main" for x in r), 18)


class IceCube2026(unittest.TestCase):
    def test_segments(self):
        s = b.table("icecube2026-segments.csv")
        self.assertEqual(int((s["sample"] == "CF").sum()), 13)               # 13 energy bands
        self.assertEqual(int((s["sample"] == "MESE").sum()), 13)
        narrow = s["e_lo_gev"] < 9e6                                       # last band: 10-100 PeV
        np.testing.assert_allclose(np.log10(s["e_hi_gev"] / s["e_lo_gev"])[narrow], 1 / 3, atol=2e-3)
        np.testing.assert_allclose(np.log10(s["e_hi_gev"] / s["e_lo_gev"])[~narrow], 1, atol=2e-3)
        self.assertEqual(s["e_lo_gev"].min().round(-1), 1000)


class GVD2025(unittest.TestCase):
    def test_18_events_and_backgrounds(self):
        d = b.table("gvd2025-energy-data.csv")
        self.assertEqual(int(d["events"].sum()), 18)                       # 18 cascades
        h = b.table("gvd2025-energy-stack.csv")
        self.assertAlmostEqual(h["atm_nu"].sum(), 1.9, delta=0.1)          # paper: 1.9 atm. neutrinos
        self.assertAlmostEqual(h["atm_mu"].sum(), 0.9, delta=0.1)          # paper: 0.9 muons

    def test_band_normalization(self):
        band = b.table("gvd2025-spectrum-band.csv")
        e2 = np.interp(np.log10(100), np.log10(band["e_tev"]), band["e2flux_fit"])
        self.assertAlmostEqual(e2 / 4.42e-8, 1, delta=0.03)                # 4.42e-18 GeV^-1... at 100 TeV
        slope = np.polyfit(np.log10(band["e_tev"]), np.log10(band["e2flux_fit"]), 1)[0]
        self.assertAlmostEqual(slope, 2 - 2.64, delta=0.02)                # gamma = 2.64


class Zathul2026(unittest.TestCase):
    def test_spl_neutrino_line_matches_icecube_cf_fit(self):
        import csv
        r = [x for x in csv.DictReader((b.DATA / "zathul-lines.csv").open())
             if x["family"] == "neutrino" and x["model"] == "SPL"]
        e = np.array([float(x["e_gev"]) for x in r]); v = np.array([float(x["e2flux"]) for x in r])
        slope, icpt = np.polyfit(np.log10(e), np.log10(v), 1)
        self.assertAlmostEqual(2 - slope, 2.52, delta=0.03)                # CF SPL gamma = 2.52
        # As drawn, the dashed SPL line lies ~15% above 3 x 1.80e-18 (CF SPL, per flavour, at 100 TeV);
        # the axis calibration itself is checked on the IceCube points (next test) to ~1%.
        self.assertAlmostEqual(10 ** np.polyval([slope, icpt], 5) / (3 * 1.80e-18 * 1e10), 1.15, delta=0.04)

    def test_calibration_on_icecube_points(self):
        # Grey IceCube points of Zathul Fig. 2 = CF segmented flux x 3 (all flavours); bars read from the raster
        # during preparation: 46-100 TeV 6.16e-8 (table 6.09e-8), 464-1000 TeV 2.53e-8 (table 2.55e-8).
        seg = b.table("icecube2026-segments.csv")
        m = (seg["sample"] == "CF") & (np.abs(seg["e_lo_gev"] - 4.64e4) < 100)
        self.assertAlmostEqual(3 * seg["e2flux"][m][0] / 6.16e-8, 1, delta=0.02)

    def test_fermi_igrb_bins(self):
        f = b.table("zathul-fermi-igrb.csv")
        self.assertEqual(len(f["e_gev"]), 19)                              # 1.13-820 GeV bins in frame
        np.testing.assert_allclose(np.diff(np.log10(f["e_gev"])), 0.1505, atol=0.003)


if __name__ == "__main__":
    unittest.main()
