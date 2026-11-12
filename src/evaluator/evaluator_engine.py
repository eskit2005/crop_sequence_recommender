"""
evaluator_engine.py - Master Engine Orchestrator for Crop Sequence Evaluator DSS
Executes Stages 1 through 6 deterministically, bridging spatial routing, NASA Earth observations,
biogeochemistry, epidemiology, and explainable bilingual AI advisory generation.
"""

import os
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

from ..router import SpatialRouter
from .models import (
    FarmerProfile,
    CropEpisode,
    DetectedIssue,
    SequenceAuditResult,
    SmartSwapRecommendation,
)
from .nasa_climate_enricher import NASAClimateEnricher
from .soil_biogeochem_auditor import SoilBiogeochemAuditor
from .temporal_turnaround_auditor import TemporalTurnaroundAuditor
from .biological_disease_auditor import BiologicalDiseaseAuditor
from .sequence_scorer_remediator import SequenceScorerRemediator
from .ai_agronomic_advisor import AIAgronomicAdvisor


class CropSequenceEvaluatorEngine:
    """
    Unified end-to-end evaluator coordinating Stages 1 to 6.
    """

    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "crop_recommender.db"
    )

    # Standard vernacular mapping for Bengali and colloquial crop names
    CROP_NAME_CANONICAL_MAP = {
        "alu": "Potato",
        "gol alu": "Potato",
        "গোল আলু": "Potato",
        "potato": "Potato",
        "tometo": "Tomato",
        "tomato": "Tomato",
        "টমেটো": "Tomato",
        "begun": "Brinjal",
        "brinjal": "Brinjal",
        "বেগুন": "Brinjal",
        "chilli": "Chilli",
        "morich": "Chilli",
        "মরিচ": "Chilli",
        "boro": "Boro Rice",
        "boro dhan": "Boro Rice",
        "বোরো": "Boro Rice",
        "বোরো ধান": "Boro Rice",
        "boro rice": "Boro Rice",
        "t. aman": "T. Aman Rice",
        "aman": "T. Aman Rice",
        "t. aman rice": "T. Aman Rice",
        "রোপা আমন": "T. Aman Rice",
        "আমন ধান": "T. Aman Rice",
        "aus": "Aus Rice",
        "aus rice": "Aus Rice",
        "আউশ": "Aus Rice",
        "mug": "Mungbean",
        "mung": "Mungbean",
        "mungbean": "Mungbean",
        "মুগডাল": "Mungbean",
        "shorisha": "Mustard",
        "mustard": "Mustard",
        "সরিষা": "Mustard",
        "mosur": "Lentil",
        "lentil": "Lentil",
        "মসুর": "Lentil",
        "chola": "Gram / Chickpea",
        "chickpea": "Gram / Chickpea",
        "ছোলা": "Gram / Chickpea",
        "khesari": "Grass pea",
        "grass pea": "Grass pea",
        "খেসারি": "Grass pea",
        "vutta": "Maize",
        "maize": "Maize",
        "ভুট্টা": "Maize",
        "gom": "Wheat",
        "wheat": "Wheat",
        "গম": "Wheat",
        "pat": "Jute",
        "jute": "Jute",
        "পাট": "Jute",
        "surjamukhi": "Sunflower",
        "sunflower": "Sunflower",
        "সূর্যমুখী": "Sunflower",
        "dhaincha": "Sesbania",
        "sesbania": "Sesbania",
        "ধৈঞ্চা": "Sesbania",
    }

    # Seasonal standard starting calendar day of year (approximate DOY)
    SEASON_START_DOY = {
        "Rabi": 319,     # Nov 15
        "Kharif-1": 70,  # Mar 10
        "Kharif-2": 201, # Jul 20
        "Fallow": 100
    }

    def __init__(self):
        self.router = SpatialRouter()
        self.climate_enricher = NASAClimateEnricher()

    def canonicalize_crop_name(self, raw_name: str) -> str:
        """Resolves vernacular or informal crop strings to canonical names."""
        clean = raw_name.lower().strip()
        return self.CROP_NAME_CANONICAL_MAP.get(clean, raw_name.strip().title())

    def _query_crop_attributes(self, crop_name: str, cultivar: Optional[str] = None, upazila_code: Optional[str] = None) -> Dict[str, Any]:
        """Queries local database for crop botanical and agronomic attributes."""
        default_attrs = {
            "botanical_family": "Other",
            "root_type": "medium",
            "is_legume": False,
            "duration_days": 90,
            "salinity_threshold_a": 3.0,
            "salinity_slope_b": 10.0,
            "water_need_mm": 350.0,
            "flood_depth_tolerance_cm": 15.0
        }

        # Botanical rules fallback
        clean = crop_name.lower()
        if "potato" in clean:
            default_attrs.update({"botanical_family": "Solanaceae", "root_type": "shallow", "duration_days": 90, "salinity_threshold_a": 1.7, "salinity_slope_b": 12.0})
        elif "tomato" in clean:
            default_attrs.update({"botanical_family": "Solanaceae", "root_type": "medium", "duration_days": 100, "salinity_threshold_a": 2.5, "salinity_slope_b": 9.9})
        elif "brinjal" in clean:
            default_attrs.update({"botanical_family": "Solanaceae", "root_type": "shallow", "duration_days": 120})
        elif "chilli" in clean:
            default_attrs.update({"botanical_family": "Solanaceae", "root_type": "shallow", "duration_days": 110})
        elif "boro" in clean:
            default_attrs.update({"botanical_family": "Poaceae", "root_type": "shallow_fibrous", "duration_days": 145, "water_need_mm": 1200.0, "salinity_threshold_a": 3.0, "salinity_slope_b": 12.0})
        elif "aman" in clean:
            default_attrs.update({"botanical_family": "Poaceae", "root_type": "shallow_fibrous", "duration_days": 115, "water_need_mm": 600.0, "flood_depth_tolerance_cm": 90.0, "salinity_threshold_a": 3.0, "salinity_slope_b": 12.0})
        elif "aus" in clean:
            default_attrs.update({"botanical_family": "Poaceae", "root_type": "shallow_fibrous", "duration_days": 105, "water_need_mm": 450.0})
        elif "maize" in clean:
            default_attrs.update({"botanical_family": "Poaceae", "root_type": "deep_fibrous", "duration_days": 130, "water_need_mm": 550.0, "salinity_threshold_a": 1.7, "salinity_slope_b": 12.0})
        elif "wheat" in clean:
            default_attrs.update({"botanical_family": "Poaceae", "root_type": "shallow_fibrous", "duration_days": 110, "salinity_threshold_a": 6.0, "salinity_slope_b": 7.1})
        elif "mungbean" in clean:
            default_attrs.update({"botanical_family": "Fabaceae", "root_type": "nodulated", "is_legume": True, "duration_days": 65, "salinity_threshold_a": 1.6, "salinity_slope_b": 18.0})
        elif "lentil" in clean:
            default_attrs.update({"botanical_family": "Fabaceae", "root_type": "nodulated", "is_legume": True, "duration_days": 105, "salinity_threshold_a": 1.5, "salinity_slope_b": 20.0})
        elif "chickpea" in clean or "gram" in clean:
            default_attrs.update({"botanical_family": "Fabaceae", "root_type": "nodulated", "is_legume": True, "duration_days": 115, "salinity_threshold_a": 1.5, "salinity_slope_b": 17.0})
        elif "grass pea" in clean or "khesari" in clean:
            default_attrs.update({"botanical_family": "Fabaceae", "root_type": "nodulated", "is_legume": True, "duration_days": 110})
        elif "sesbania" in clean or "dhaincha" in clean:
            default_attrs.update({"botanical_family": "Fabaceae", "root_type": "nodulated", "is_legume": True, "duration_days": 55})
        elif "mustard" in clean:
            default_attrs.update({"botanical_family": "Brassicaceae", "root_type": "medium_tap", "duration_days": 80, "salinity_threshold_a": 5.0, "salinity_slope_b": 7.0})
        elif "sunflower" in clean:
            default_attrs.update({"botanical_family": "Asteraceae", "root_type": "deep_tap", "duration_days": 105, "salinity_threshold_a": 5.5, "salinity_slope_b": 5.0})
        elif "jute" in clean:
            default_attrs.update({"botanical_family": "Malvaceae", "root_type": "deep_tap", "duration_days": 120, "flood_depth_tolerance_cm": 60.0})

        # Cultivar duration fine-tuning
        if cultivar:
            cult_lower = cultivar.lower()
            if "late" in cult_lower or "dhan29" in cult_lower:
                default_attrs["duration_days"] = 160
            elif "early" in cult_lower or "dhan88" in cult_lower or "dhan96" in cult_lower:
                default_attrs["duration_days"] = 140
            elif "dhan75" in cult_lower or "dhan71" in cult_lower:
                default_attrs["duration_days"] = 110

        if os.path.exists(self.DB_PATH):
            try:
                conn = sqlite3.connect(self.DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT botanical_family, root_type, is_legume, duration_days
                    FROM upazila_suitable_crops
                    WHERE crop_name LIKE ?
                    LIMIT 1
                    """,
                    (f"%{crop_name}%",)
                )
                row = cursor.fetchone()
                if row:
                    default_attrs["botanical_family"] = row[0] or default_attrs["botanical_family"]
                    default_attrs["root_type"] = row[1] or default_attrs["root_type"]
                    default_attrs["is_legume"] = bool(row[2])
                    default_attrs["duration_days"] = int(row[3]) if row[3] else default_attrs["duration_days"]
                conn.close()
            except Exception:
                pass

        return default_attrs

    def evaluate(self, profile: FarmerProfile) -> SequenceAuditResult:
        """
        Runs the full 6-stage scientific evaluation on a farmer's proposed sequence.
        """
        # --- STAGE 1: Input Ingestion & Agro-Ecological Context Enrichment ---
        loc = profile.location
        if not loc.upazila or not loc.district:
            route_res = self.router.route(loc.lat, loc.lon)
            if route_res.is_bangladesh:
                loc.upazila = loc.upazila or route_res.upazila_name
                loc.district = loc.district or route_res.district_name
                loc.division = loc.division or route_res.division_name

        clima = self.climate_enricher.get_climatology(loc.lat, loc.lon)

        # Build chronological event stream episodes with monotonic cumulative day offsets
        episodes: List[CropEpisode] = []
        accum_year = 0

        for idx, raw_crop in enumerate(profile.farmer_evaluated_sequence):
            c_name = self.canonicalize_crop_name(raw_crop.crop_name)
            attrs = self._query_crop_attributes(c_name, raw_crop.cultivar)
            is_fallow = "fallow" in c_name.lower() or raw_crop.season == "Fallow"

            season_doy = self.SEASON_START_DOY.get(raw_crop.season, 100)

            if idx == 0:
                accum_year = raw_crop.year - 1
                start_day = accum_year * 365 + season_doy
            else:
                prev_raw = profile.farmer_evaluated_sequence[idx - 1]
                prev_season_doy = self.SEASON_START_DOY.get(prev_raw.season, 100)

                if season_doy < prev_season_doy:
                    accum_year += 1
                elif raw_crop.year > prev_raw.year:
                    accum_year = raw_crop.year - 1

                start_day = accum_year * 365 + season_doy

            episodes.append(CropEpisode(
                year=raw_crop.year,
                season=raw_crop.season,
                crop_name=c_name,
                duration_days=attrs["duration_days"] if not is_fallow else 90,
                start_day_offset=start_day,
                botanical_family=attrs["botanical_family"] if not is_fallow else "Fallow",
                root_type=attrs["root_type"] if not is_fallow else "none",
                is_legume=attrs["is_legume"] if not is_fallow else False,
                water_need_mm=attrs["water_need_mm"] if not is_fallow else 0.0,
                salinity_threshold_a=attrs["salinity_threshold_a"],
                salinity_slope_b=attrs["salinity_slope_b"],
                flood_depth_tolerance_cm=attrs["flood_depth_tolerance_cm"],
                stover_management=raw_crop.stover_management,
                cultivar=raw_crop.cultivar,
                is_fallow=is_fallow
            ))

        all_detected_issues: List[DetectedIssue] = []

        # --- STAGE 2: Temporal & Turnaround Feasibility Engine ---
        gaps_record, turnaround_subscore, s2_issues = TemporalTurnaroundAuditor.audit_turnaround(
            episodes=episodes,
            location=loc,
            horizon_years=profile.target_horizon_years
        )
        all_detected_issues.extend(s2_issues)

        # Calculate climate & water balance
        water_bal = self.climate_enricher.run_water_balance(
            lat=loc.lat,
            lon=loc.lon,
            start_doy=319,
            duration_days=min(365, sum(ep.duration_days for ep in episodes)),
            kc=1.0,
            s_max=120.0,
            initial_w=70.0,
            irrigation_daily=1.5 if profile.farmer_priorities.irrigation_source not in ["rainfed", "rainfed_only", "none"] else 0.0
        )
        climate_subscore = max(0.0, 100.0 - (water_bal["deficit_days"] * 1.5))
        climate_score_combined = 0.5 * turnaround_subscore + 0.5 * climate_subscore

        # --- STAGE 3: Agro-Hydrological & Land Compatibility Validator ---
        hydro_subscore, s3_issues = SequenceScorerRemediator.evaluate_hydrology_and_land(episodes, profile)
        all_detected_issues.extend(s3_issues)

        salinity_data, sal_issues = SoilBiogeochemAuditor.audit_salinity(episodes, profile.field_conditions)
        all_detected_issues.extend(sal_issues)
        if sal_issues:
            sal_deduction = sum(iss.penalty_points for iss in sal_issues)
            hydro_subscore = max(0.0, hydro_subscore - sal_deduction)

        # --- STAGE 4: Biological & Soil Health Audit Engine ---
        bio_subscore, s4_issues = BiologicalDiseaseAuditor.audit_biology(
            episodes, profile.field_conditions, profile.target_horizon_years
        )
        all_detected_issues.extend(s4_issues)

        soc_res, soc_issues = SoilBiogeochemAuditor.audit_soc_trajectory(
            episodes, profile.field_conditions, profile.target_horizon_years
        )
        all_detected_issues.extend(soc_issues)

        n_res, n_issues = SoilBiogeochemAuditor.audit_nutrient_balance(
            episodes, profile.target_horizon_years
        )
        all_detected_issues.extend(n_issues)

        ph_subscore, ph_issues = SoilBiogeochemAuditor.audit_soil_ph(episodes, profile.field_conditions)
        all_detected_issues.extend(ph_issues)

        # Composite soil sub-score
        soil_penalty = sum(iss.penalty_points for iss in soc_issues + n_issues + ph_issues)
        soil_subscore = max(0.0, 100.0 - soil_penalty)

        # --- STAGE 5: Multi-Factor Scoring & Targeted Remediation Engine ---
        econ_subscore, s5_econ_issues = SequenceScorerRemediator.evaluate_economics_and_staples(episodes, profile)
        all_detected_issues.extend(s5_econ_issues)

        sub_scores = {
            "climate": climate_score_combined,
            "hydrology": hydro_subscore,
            "biology": bio_subscore,
            "soil": soil_subscore,
            "economics": econ_subscore
        }

        overall_score, grade, risk_category = SequenceScorerRemediator.calculate_overall_score(
            sub_scores, all_detected_issues
        )

        smart_swaps = SequenceScorerRemediator.generate_smart_swap(
            episodes, all_detected_issues, profile, overall_score
        )

        cultural_mitigations = SequenceScorerRemediator.generate_cultural_mitigations(
            episodes, all_detected_issues
        )

        result = SequenceAuditResult(
            farmer_profile=profile,
            overall_health_score=overall_score,
            grade=grade,
            risk_category=risk_category,
            sub_scores=sub_scores,
            detected_issues=all_detected_issues,
            soc_trajectory=soc_res,
            nitrogen_balance=n_res,
            water_balance=water_bal,
            turnaround_gaps=gaps_record,
            episodes=episodes,
            smart_swaps=smart_swaps,
            cultural_mitigations=cultural_mitigations
        )

        # --- STAGE 6: The AI Agronomic Advisory Agent ---
        advisory_report = AIAgronomicAdvisor.generate_advisory(result)
        result.advisory_report = advisory_report.to_dict()

        return result
