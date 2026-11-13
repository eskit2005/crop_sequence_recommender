"""
test_evaluator_stages.py - Unit Tests for Crop Sequence Evaluator DSS
Tests Stages 1-5 deterministically: NASA Hargreaves ET0, tipping-bucket water balance,
duration-weighted SOC, legume BNF, Maas-Hoffman salinity, turnaround buffers, and disease rules.
"""

import unittest
import math

from src.evaluator.models import (
    FarmerProfile,
    LocationInput,
    FieldConditions,
    FarmerPriorities,
    CropInput,
    CropEpisode,
)
from src.evaluator.nasa_climate_enricher import NASAClimateEnricher
from src.evaluator.soil_biogeochem_auditor import SoilBiogeochemAuditor
from src.evaluator.temporal_turnaround_auditor import TemporalTurnaroundAuditor
from src.evaluator.biological_disease_auditor import BiologicalDiseaseAuditor
from src.evaluator.sequence_scorer_remediator import SequenceScorerRemediator
from src.evaluator.evaluator_engine import CropSequenceEvaluatorEngine


class TestCropSequenceEvaluatorStages(unittest.TestCase):

    def setUp(self):
        self.engine = CropSequenceEvaluatorEngine()

    def test_nasa_hargreaves_et0_calculation(self):
        """Verifies FAO-56 Hargreaves-Samani formulation against audited benchmark."""
        # Bogura Day 105: Tmax=35.8, Tmin=21.4, Tmean=28.6, Ra=15.14 mm/day
        ra_mm = 15.14
        tmean = 28.6
        tmax = 35.8
        tmin = 21.4
        et0 = NASAClimateEnricher.calculate_et0(tmean, tmax, tmin, ra_mm)
        # 0.0023 * (28.6 + 17.8) * sqrt(14.4) * 15.14 = 6.1317 mm/day
        self.assertAlmostEqual(et0, 6.13, places=1)

    def test_tipping_bucket_sequential_water_balance(self):
        """Verifies sequential two-step tipping bucket water storage and drainage."""
        enricher = NASAClimateEnricher()
        res = enricher.run_water_balance(
            lat=24.785, lon=89.042, start_doy=319, duration_days=90, kc=1.0, s_max=120.0, initial_w=60.0
        )
        self.assertIn("total_precip_mm", res)
        self.assertIn("total_etc_mm", res)
        self.assertIn("final_storage_mm", res)
        self.assertGreater(res["net_water_deficit_mm"], 0.0)

    def test_soc_duration_weighted_trajectory(self):
        """Verifies duration-weighted SOC balance between exhaustive and regenerative sequences."""
        fc = FieldConditions(soil_organic_carbon_pct=1.1, bulk_density=1.5)
        # Exhaustive: Potato (90d) -> Tomato (100d) -> T. Aman (115d)
        episodes_exhaustive = [
            CropEpisode(1, "Rabi", "Potato", 90, 319, "Solanaceae", "shallow", False, 300, 1.7, 12, 10, "removed"),
            CropEpisode(1, "Kharif-1", "Tomato", 100, 435, "Solanaceae", "shallow", False, 350, 2.5, 10, 10, "incorporated"),
            CropEpisode(1, "Kharif-2", "T. Aman Rice", 115, 566, "Poaceae", "shallow_fibrous", False, 600, 3.0, 12, 90, "incorporated"),
        ]
        res_ex, issues_ex = SoilBiogeochemAuditor.audit_soc_trajectory(episodes_exhaustive, fc, horizon_years=1)
        # Should yield negative carbon flux
        self.assertLess(res_ex["delta_soc_annual_t_c_ha"], -0.30)
        self.assertTrue(any(iss.code == "SEVERE_SOC_DEPLETION" for iss in issues_ex))

        # Regenerative: Potato -> Mungbean (incorporated) -> T. Aman
        episodes_regen = [
            CropEpisode(1, "Rabi", "Potato", 90, 319, "Solanaceae", "shallow", False, 300, 1.7, 12, 10, "removed"),
            CropEpisode(1, "Kharif-1", "Mungbean", 65, 435, "Fabaceae", "nodulated", True, 200, 1.6, 18, 10, "incorporated"),
            CropEpisode(1, "Kharif-2", "T. Aman Rice", 115, 566, "Poaceae", "shallow_fibrous", False, 600, 3.0, 12, 90, "incorporated"),
        ]
        res_reg, _ = SoilBiogeochemAuditor.audit_soc_trajectory(episodes_regen, fc, horizon_years=1)
        # Carbon loss in regenerative should be significantly less negative than exhaustive
        self.assertGreater(res_reg["delta_soc_annual_t_c_ha"], res_ex["delta_soc_annual_t_c_ha"])

    def test_maas_hoffman_salinity_thresholds(self):
        """Verifies Maas-Hoffman salinity response for Lentil vs BRRI dhan67."""
        fc_saline = FieldConditions(soil_salinity_ec_e=7.5)
        episodes = [
            CropEpisode(1, "Rabi", "Lentil", 105, 319, "Fabaceae", "nodulated", True, 250, 1.5, 20.0, 10),
            CropEpisode(1, "Rabi", "BRRI dhan67", 145, 319, "Poaceae", "shallow_fibrous", False, 1200, 4.2, 9.0, 30, cultivar="BRRI dhan67"),
        ]
        res, issues = SoilBiogeochemAuditor.audit_salinity(episodes, fc_saline)
        responses = res["crop_responses"]

        # Lentil at 7.5 dS/m should have 0% yield
        self.assertEqual(responses["Lentil"]["relative_yield_pct"], 0.0)
        # BRRI dhan67 at 7.5 dS/m: 100 - 9.0 * (7.5 - 4.2) = 70.3%
        self.assertAlmostEqual(responses["BRRI dhan67"]["relative_yield_pct"], 70.3, places=1)
        # Should detect critical blocker for Lentil
        self.assertTrue(any(iss.code == "CRITICAL_SALINITY_TOXICITY" for iss in issues))

    def test_biological_solanaceae_bridge_and_maize_host(self):
        """Verifies Solanaceae disease bridge and Maize nematode multiplier host."""
        fc = FieldConditions()
        # Potato -> Tomato consecutive
        episodes_sol = [
            CropEpisode(1, "Rabi", "Potato", 90, 319, "Solanaceae", "shallow", False, 300, 1.7, 12, 10),
            CropEpisode(1, "Kharif-1", "Tomato", 100, 435, "Solanaceae", "shallow", False, 350, 2.5, 10, 10),
        ]
        subscore, issues = BiologicalDiseaseAuditor.audit_biology(episodes_sol, fc, 1)
        self.assertTrue(any(iss.code == "SOLANACEAE_DISEASE_BRIDGE" for iss in issues))
        self.assertLess(subscore, 70.0)

        # Potato -> Maize -> Potato (Maize nematode bridge)
        episodes_maize = [
            CropEpisode(1, "Rabi", "Potato", 90, 319, "Solanaceae", "shallow", False, 300, 1.7, 12, 10),
            CropEpisode(1, "Kharif-1", "Maize", 120, 435, "Poaceae", "deep_fibrous", False, 500, 1.7, 12, 10),
            CropEpisode(2, "Rabi", "Potato", 90, 684, "Solanaceae", "shallow", False, 300, 1.7, 12, 10),
        ]
        _, issues_m = BiologicalDiseaseAuditor.audit_biology(episodes_maize, fc, 2)
        self.assertTrue(any(iss.code == "MAIZE_NEMATODE_REPRODUCTIVE_HOST" for iss in issues_m))

    def test_haor_flash_flood_hazard_collision(self):
        """Verifies that late harvesting of Rabi crop in Haor triggers critical flash flood risk."""
        loc_haor = LocationInput(lat=25.07, lon=91.18, upazila="Tahirpur", district="Sunamganj")
        # Late Boro harvesting May 10 (DOY 130 > DOY 105 April 15)
        episodes = [
            CropEpisode(1, "Rabi", "Boro Rice", 160, 335, "Poaceae", "shallow_fibrous", False, 1200, 3.0, 12, 30)
        ]
        _, _, issues = TemporalTurnaroundAuditor.audit_turnaround(episodes, loc_haor, 1)
        self.assertTrue(any(iss.code == "CRITICAL_HAOR_FLASH_FLOOD_RISK" for iss in issues))

    def test_evaluator_directory_structure_integrity(self):
        """Guarantees that the Evaluator DSS directory tree and all its components exist in exact paths."""
        import os
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        expected_paths = [
            os.path.join(repo_root, "src", "evaluator", "__init__.py"),
            os.path.join(repo_root, "src", "evaluator", "evaluator_engine.py"),
            os.path.join(repo_root, "src", "evaluator", "models.py"),
            os.path.join(repo_root, "src", "evaluator", "nasa_climate_enricher.py"),
            os.path.join(repo_root, "src", "evaluator", "soil_biogeochem_auditor.py"),
            os.path.join(repo_root, "src", "evaluator", "temporal_turnaround_auditor.py"),
            os.path.join(repo_root, "src", "evaluator", "biological_disease_auditor.py"),
            os.path.join(repo_root, "src", "evaluator", "sequence_scorer_remediator.py"),
            os.path.join(repo_root, "src", "evaluator", "ai_agronomic_advisor.py"),
            os.path.join(repo_root, "src", "evaluate_sequence_cli.py"),
            os.path.join(repo_root, "docs", "crop_sequence_evaluator_architecture.md"),
        ]
        for path in expected_paths:
            self.assertTrue(os.path.exists(path), f"CRITICAL STRUCTURAL FAILURE: Missing expected file at {path}")


if __name__ == "__main__":
    unittest.main()
