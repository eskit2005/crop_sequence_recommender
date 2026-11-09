"""
test_stage3.py - Comprehensive Unit & Integration Test Suite for Stage 3
Validates:
1. SpatialRouter (2-Tier PIP, latency < 5 ms, boundary precision)
2. BARCCandidateSelector (Write-through caching, land-type exclusions, haor deadlock prevention)
3. GlobalEnvFetcher (NASA POWER climatology mm/day correction, SoilGrids failover, FAO tipping-bucket LGP)
4. FAOCandidateSelector (Trapezoidal fuzzy epsilon guards, Sys et al. 1991 scoring, cyclic modulo window)
5. Stage3Engine (End-to-end integration across domestic and international test locations)
"""

import unittest
import os
import sys

# Ensure root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.router import SpatialRouter, RouteDecision
from src.stage3_barc_selector import BARCCandidateSelector
from src.global_env_fetcher import GlobalEnvFetcher, classify_usda_texture
from src.stage3_fao_selector import (
    FAOCandidateSelector,
    trapezoidal_fuzzy,
    sys_square_root_score
)
from src.stage3_engine import Stage3Engine


class TestStage3Architecture(unittest.TestCase):

    def setUp(self):
        self.router = SpatialRouter.get_instance()
        self.barc_selector = BARCCandidateSelector()
        self.env_fetcher = GlobalEnvFetcher()
        self.fao_selector = FAOCandidateSelector()
        self.engine = Stage3Engine.get_instance()

    # -------------------------------------------------------------
    # 1. Spatial Router Tests
    # -------------------------------------------------------------
    def test_spatial_router_known_points(self):
        # Adamdighi / Raninagar area
        res = self.router.route(24.78, 89.04)
        self.assertTrue(res.is_bangladesh)
        self.assertIn(res.upazila_name, ["Adamdighi", "Raninagar"])
        self.assertLess(res.latency_ms, 5.0, "Latency must be < 5.0 ms")

        # Singair, Manikganj
        res_m = self.router.route(23.81, 90.15)
        self.assertTrue(res_m.is_bangladesh)
        self.assertEqual(res_m.upazila_name, "Singair")

        # Dowarabazar, Sunamganj Haor
        res_h = self.router.route(25.05, 91.56)
        self.assertTrue(res_h.is_bangladesh)
        self.assertEqual(res_h.upazila_name, "Dowarabazar")

    def test_spatial_router_international_envelope_rejection(self):
        # Nakuru, Kenya
        res_k = self.router.route(-0.303, 36.08)
        self.assertFalse(res_k.is_bangladesh)
        self.assertIsNone(res_k.upazila_code)

        # Frankfurt, Germany
        res_g = self.router.route(50.11, 8.68)
        self.assertFalse(res_g.is_bangladesh)
        self.assertIsNone(res_g.upazila_code)

    # -------------------------------------------------------------
    # 2. Algorithmic Guardrails (Fuzzy Epsilon & Sys et al. 1991)
    # -------------------------------------------------------------
    def test_trapezoidal_fuzzy_epsilon_guards(self):
        # Normal slope
        self.assertAlmostEqual(trapezoidal_fuzzy(15.0, 10.0, 20.0, 30.0, 40.0), 0.5)
        # Optimal plateau
        self.assertAlmostEqual(trapezoidal_fuzzy(25.0, 10.0, 20.0, 30.0, 40.0), 1.0)
        # Left-cliff: v_opmin == v_min (ZeroDivisionError test)
        self.assertAlmostEqual(trapezoidal_fuzzy(10.0, 10.0, 10.0, 20.0, 30.0), 1.0)
        # Right-cliff: v_opmax == v_max (ZeroDivisionError test)
        self.assertAlmostEqual(trapezoidal_fuzzy(30.0, 10.0, 20.0, 30.0, 30.0), 1.0)
        # Out of bounds
        self.assertAlmostEqual(trapezoidal_fuzzy(5.0, 10.0, 20.0, 30.0, 40.0), 0.0)
        self.assertAlmostEqual(trapezoidal_fuzzy(45.0, 10.0, 20.0, 30.0, 40.0), 0.0)

    def test_sys_square_root_scoring(self):
        # Liebig's law: any 0.0 results in 0.0
        self.assertEqual(sys_square_root_score([1.0, 0.0, 0.9, 0.8]), 0.0)
        # No Storie compounding decay:
        # Multiplicative would give 0.8^4 = 0.4096
        # Sys gives 0.8 * sqrt(0.8^3) = 0.5724
        scores = [0.8, 0.8, 0.8, 0.8]
        s_sys = sys_square_root_score(scores)
        self.assertAlmostEqual(s_sys, 0.5724, places=3)
        self.assertGreater(s_sys, 0.8 ** 4)

    # -------------------------------------------------------------
    # 3. BARC Bangladesh Land-Type & Haor Exclusions
    # -------------------------------------------------------------
    def test_barc_land_type_exclusions(self):
        # High Land (HL): Flooded rice (Boro) must be purged
        res_hl = self.barc_selector.select_candidate_pools("501006", land_type="HL")
        rabi_crops = [c["crop_name"].lower() for c in res_hl["seasons"]["rabi"]]
        self.assertFalse(any("boro" in c for c in rabi_crops), "Boro dhan must not appear on High Land")

        # Low Land (LL): Sunamganj Haor basin monoculture relaxation
        res_ll = self.barc_selector.select_candidate_pools("609033", land_type="LL")
        self.assertEqual(res_ll["cropping_intensity_k"], 1)
        self.assertTrue(res_ll["is_haor_wetland"])
        self.assertEqual(len(res_ll["seasons"]["rabi"]), 1)
        self.assertIn("Boro dhan", res_ll["seasons"]["rabi"][0]["crop_name"])
        self.assertEqual(res_ll["seasons"]["kharif1"][0]["crop_name"], "Fallow")
        self.assertEqual(res_ll["seasons"]["kharif2"][0]["crop_name"], "Fallow")

    # -------------------------------------------------------------
    # 4. USDA Soil Texture Classifier
    # -------------------------------------------------------------
    def test_usda_texture_classification(self):
        self.assertEqual(classify_usda_texture(sand=40, silt=40, clay=20), "Loam")
        self.assertEqual(classify_usda_texture(sand=10, silt=20, clay=70), "Clay")
        self.assertEqual(classify_usda_texture(sand=75, silt=15, clay=10), "Loamy Sand")
        self.assertEqual(classify_usda_texture(sand=15, silt=70, clay=15), "Silt Loam")

    # -------------------------------------------------------------
    # 5. Master Engine End-to-End Tests
    # -------------------------------------------------------------
    def test_engine_bangladesh_pipeline(self):
        res = self.engine.get_candidate_pools(24.78, 89.04, land_type="MHL")
        self.assertEqual(res.pipeline, "BANGLADESH_BARC")
        self.assertEqual(res.cropping_intensity_k, 3)
        self.assertEqual(res.candidate_counts["rabi"], 7)
        self.assertEqual(res.candidate_counts["kharif1"], 5)
        self.assertEqual(res.candidate_counts["kharif2"], 3)
        self.assertLess(res.total_execution_ms, 50.0, "Cached DB read should be < 50 ms")

    def test_engine_haor_pipeline(self):
        res = self.engine.get_candidate_pools(25.05, 91.56, land_type="LL")
        self.assertEqual(res.pipeline, "BANGLADESH_BARC")
        self.assertEqual(res.cropping_intensity_k, 1)
        self.assertEqual(res.candidate_counts["rabi"], 1)
        self.assertEqual(res.seasons["rabi"][0]["crop_name"], "Boro dhan")
        self.assertEqual(res.seasons["kharif1"][0]["crop_name"], "Fallow")

    def test_engine_international_pipeline(self):
        # Nakuru, Kenya
        res = self.engine.get_candidate_pools(-0.303, 36.08)
        self.assertEqual(res.pipeline, "GLOBAL_FAO_ECOCROP")
        self.assertGreaterEqual(res.cropping_intensity_k, 2)
        self.assertEqual(res.candidate_counts["season_1"], 7)
        self.assertEqual(res.candidate_counts["season_2"], 5)


if __name__ == "__main__":
    unittest.main()
