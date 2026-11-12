"""
stage3_fao_selector.py - Stage 3 FAO EcoCrop & Ecological Candidate Pool Generator
Implements Trapezoidal Fuzzy Matching with epsilon guards, Sys et al. (1991) Square Root
Scoring, soil water buffer from FAO water balance, and 12-month cyclic modulo sliding window.
"""

import math
import os
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

# Ensure project root is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

try:
    from src.global_env_fetcher import EnvironmentalProfile
except ModuleNotFoundError:
    from global_env_fetcher import EnvironmentalProfile

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def trapezoidal_fuzzy(x: float, v_min: float, v_opmin: float, v_opmax: float, v_max: float) -> float:
    """
    Continuous trapezoidal fuzzy membership function with 1e-6 epsilon guards.
    Eliminates ZeroDivisionError when v_opmin == v_min or v_opmax == v_max.
    """
    if math.isnan(x) or x < v_min or x > v_max:
        return 0.0
    if v_opmin <= x <= v_opmax:
        return 1.0
    if x < v_opmin:
        denom = v_opmin - v_min
        return 1.0 if denom <= 1e-6 else max(0.0, min(1.0, (x - v_min) / denom))
    else:
        denom = v_max - v_opmax
        return 1.0 if denom <= 1e-6 else max(0.0, min(1.0, (v_max - x) / denom))


def sys_square_root_score(scores: List[float]) -> float:
    """
    Sys et al. (1991) Land Evaluation Square Root Method:
    S_total = S_min * sqrt( prod_{i != min} S_i )
    Strictly preserves Liebig's law of the minimum while avoiding Storie penalty collapse.
    """
    if not scores or any(s <= 0.0 for s in scores):
        return 0.0

    s_min = min(scores)
    
    # Calculate product of all other scores
    prod = 1.0
    min_found = False
    for s in scores:
        if s == s_min and not min_found:
            min_found = True
            continue
        prod *= s

    return round(s_min * math.sqrt(prod), 4)


@dataclass
class FAOCropRecord:
    crop_id: int
    name: str
    botanical_family: str
    root_type: str
    is_legume: bool
    duration_months: int
    duration_days: int
    t_min: float
    t_opmin: float
    t_opmax: float
    t_max: float
    r_min: float
    r_opmin: float
    r_opmax: float
    r_max: float
    ph_min: float
    ph_opmin: float
    ph_opmax: float
    ph_max: float
    allowable_textures: List[str]
    yield_ton_ha: float


# Curated FAO EcoCrop parameters for representative global crops
FAO_ECOCROP_DB: List[FAOCropRecord] = [
    # Cereals
    FAOCropRecord(1, "Bread Wheat", "Poaceae", "shallow_fibrous", False, 4, 120, 5, 15, 23, 32, 250, 400, 750, 1200, 5.5, 6.0, 7.5, 8.5, ["Loam", "Clay Loam", "Silt Loam", "Silty Clay Loam"], 4.2),
    FAOCropRecord(2, "Maize (Corn)", "Poaceae", "deep_fibrous", False, 4, 125, 10, 18, 30, 40, 350, 550, 1000, 1600, 5.2, 5.8, 7.2, 8.2, ["Loam", "Sandy Loam", "Clay Loam", "Silty Clay Loam"], 7.5),
    FAOCropRecord(3, "Barley", "Poaceae", "shallow_fibrous", False, 3, 100, 3, 12, 20, 30, 200, 300, 650, 1000, 5.8, 6.5, 8.0, 9.0, ["Loam", "Sandy Loam", "Clay Loam", "Silty Clay Loam"], 3.8),
    FAOCropRecord(4, "Grain Sorghum", "Poaceae", "deep_fibrous", False, 4, 115, 12, 24, 32, 42, 200, 350, 750, 1300, 5.0, 5.5, 7.5, 8.5, ["Loam", "Clay Loam", "Sandy Clay Loam", "Clay", "Silty Clay Loam"], 4.5),
    FAOCropRecord(5, "Pearl Millet", "Poaceae", "deep_fibrous", False, 3, 95, 15, 25, 35, 45, 150, 250, 600, 1100, 4.5, 5.5, 7.5, 8.5, ["Sandy Loam", "Loam", "Sand", "Silty Clay Loam"], 2.2),
    FAOCropRecord(6, "Lowland Paddy Rice", "Poaceae", "shallow_fibrous", False, 4, 130, 17, 24, 32, 38, 700, 1100, 2000, 3000, 5.0, 5.5, 6.8, 7.8, ["Clay", "Silty Clay", "Clay Loam", "Silty Clay Loam"], 5.5),
    FAOCropRecord(7, "Rye", "Poaceae", "shallow_fibrous", False, 4, 120, 2, 10, 18, 28, 200, 350, 700, 1200, 4.8, 5.5, 7.0, 8.0, ["Sandy Loam", "Loam", "Sand", "Silty Clay Loam"], 3.2),
    FAOCropRecord(8, "Oat", "Poaceae", "shallow_fibrous", False, 4, 110, 4, 12, 20, 29, 250, 400, 800, 1200, 5.0, 5.8, 7.0, 8.0, ["Loam", "Clay Loam", "Silt Loam", "Silty Clay Loam"], 3.5),
    FAOCropRecord(9, "Quinoa", "Amaranthaceae", "deep_tap", False, 4, 120, 3, 10, 20, 30, 150, 300, 600, 1000, 4.5, 6.0, 8.0, 9.0, ["Sandy Loam", "Loam", "Silty Clay Loam"], 2.0),
    FAOCropRecord(10, "Teff", "Poaceae", "shallow_fibrous", False, 3, 90, 10, 18, 27, 35, 250, 400, 700, 1200, 5.0, 6.0, 7.5, 8.2, ["Loam", "Clay Loam", "Silt Loam", "Silty Clay Loam"], 1.8),

    # Legumes & Pulses
    FAOCropRecord(11, "Soybean", "Fabaceae", "nodulated", True, 4, 115, 12, 20, 30, 38, 300, 500, 900, 1400, 5.5, 6.0, 7.0, 7.8, ["Loam", "Sandy Loam", "Clay Loam", "Silty Clay Loam"], 2.8),
    FAOCropRecord(12, "Chickpea (Garbanzo)", "Fabaceae", "nodulated", True, 4, 110, 8, 18, 26, 34, 200, 300, 600, 900, 5.5, 6.2, 7.8, 8.8, ["Sandy Loam", "Loam", "Clay Loam", "Silty Clay Loam"], 1.8),
    FAOCropRecord(13, "Lentil", "Fabaceae", "nodulated", True, 3, 100, 6, 15, 24, 32, 200, 300, 550, 850, 5.5, 6.0, 7.5, 8.2, ["Loam", "Sandy Loam", "Silt Loam", "Silty Clay Loam"], 1.5),
    FAOCropRecord(14, "Common Bean", "Fabaceae", "nodulated", True, 3, 90, 10, 17, 25, 32, 250, 350, 700, 1100, 5.5, 6.0, 7.2, 8.0, ["Loam", "Sandy Loam", "Silt Loam", "Silty Clay Loam"], 2.2),
    FAOCropRecord(15, "Cowpea", "Fabaceae", "nodulated", True, 3, 85, 15, 24, 32, 38, 200, 350, 750, 1200, 5.0, 5.8, 7.5, 8.5, ["Sandy Loam", "Loam", "Sand", "Silty Clay Loam"], 1.7),
    FAOCropRecord(16, "Groundnut (Peanut)", "Fabaceae", "nodulated", True, 4, 125, 15, 22, 30, 38, 300, 450, 800, 1300, 5.2, 5.8, 6.8, 7.5, ["Sandy Loam", "Sand", "Loamy Sand", "Silty Clay Loam"], 2.5),
    FAOCropRecord(17, "Field Pea", "Fabaceae", "nodulated", True, 3, 95, 5, 13, 22, 29, 200, 300, 650, 1000, 5.8, 6.2, 7.5, 8.5, ["Loam", "Clay Loam", "Silt Loam", "Silty Clay Loam"], 2.4),
    FAOCropRecord(18, "Faba Bean", "Fabaceae", "nodulated", True, 4, 120, 5, 14, 22, 30, 250, 400, 750, 1100, 5.8, 6.5, 7.8, 8.6, ["Clay Loam", "Loam", "Clay", "Silty Clay Loam"], 3.0),
    FAOCropRecord(19, "Pigeon Pea", "Fabaceae", "nodulated", True, 5, 150, 15, 22, 32, 38, 350, 550, 1000, 1500, 5.0, 5.5, 7.5, 8.5, ["Loam", "Clay Loam", "Sandy Loam", "Silty Clay Loam"], 1.6),
    FAOCropRecord(20, "Mungbean", "Fabaceae", "nodulated", True, 2, 70, 16, 25, 34, 40, 150, 300, 650, 1000, 5.5, 6.2, 7.5, 8.2, ["Sandy Loam", "Loam", "Silty Clay Loam"], 1.4),

    # Oilseeds
    FAOCropRecord(21, "Rapeseed / Canola", "Brassicaceae", "medium_tap", False, 4, 110, 5, 14, 22, 30, 250, 400, 750, 1100, 5.5, 6.0, 7.5, 8.2, ["Loam", "Clay Loam", "Silt Loam", "Silty Clay Loam"], 2.6),
    FAOCropRecord(22, "Sunflower", "Asteraceae", "deep_tap", False, 4, 105, 10, 18, 28, 36, 250, 400, 750, 1200, 5.5, 6.0, 7.5, 8.3, ["Loam", "Sandy Loam", "Clay Loam", "Silty Clay Loam"], 2.3),
    FAOCropRecord(23, "Sesame", "Pedaliaceae", "medium_tap", False, 3, 90, 16, 24, 33, 40, 200, 350, 700, 1100, 5.5, 6.0, 7.5, 8.2, ["Sandy Loam", "Loam", "Silty Clay Loam"], 1.2),
    FAOCropRecord(24, "Flax / Linseed", "Linaceae", "medium_tap", False, 3, 95, 6, 14, 22, 30, 200, 350, 650, 1000, 5.5, 6.0, 7.2, 8.0, ["Loam", "Clay Loam", "Silt Loam", "Silty Clay Loam"], 1.5),
    FAOCropRecord(25, "Safflower", "Asteraceae", "deep_tap", False, 4, 120, 8, 18, 28, 38, 150, 300, 600, 900, 5.5, 6.2, 7.8, 8.6, ["Loam", "Clay Loam", "Clay", "Silty Clay Loam"], 1.8),

    # Roots & Tubers
    FAOCropRecord(26, "Potato", "Solanaceae", "shallow", False, 3, 100, 8, 15, 22, 28, 250, 400, 700, 1000, 5.0, 5.5, 6.8, 7.5, ["Sandy Loam", "Loam", "Silt Loam", "Silty Clay Loam"], 28.0),
    FAOCropRecord(27, "Sweet Potato", "Convolvulaceae", "shallow", False, 4, 120, 14, 20, 29, 36, 300, 450, 900, 1400, 5.0, 5.8, 6.8, 7.8, ["Sandy Loam", "Loam", "Silty Clay Loam"], 20.0),
    FAOCropRecord(28, "Cassava", "Euphorbiaceae", "deep_fibrous", False, 9, 270, 16, 24, 32, 38, 450, 800, 1500, 2400, 4.5, 5.5, 7.0, 8.0, ["Sandy Loam", "Loam", "Silty Clay Loam"], 25.0),
    FAOCropRecord(29, "Sugar Beet", "Amaranthaceae", "deep_tap", False, 6, 180, 5, 15, 24, 30, 300, 500, 850, 1200, 6.0, 6.8, 7.8, 8.5, ["Loam", "Silt Loam", "Clay Loam", "Silty Clay Loam"], 55.0),

    # Vegetables
    FAOCropRecord(30, "Tomato", "Solanaceae", "shallow", False, 3, 105, 10, 18, 27, 35, 250, 400, 750, 1100, 5.5, 6.0, 7.0, 7.8, ["Sandy Loam", "Loam", "Silty Clay Loam"], 35.0),
    FAOCropRecord(31, "Dry Bulb Onion", "Amaryllidaceae", "shallow", False, 4, 120, 8, 16, 25, 32, 200, 350, 650, 950, 5.8, 6.2, 7.2, 8.0, ["Sandy Loam", "Loam", "Silt Loam", "Silty Clay Loam"], 25.0),
    FAOCropRecord(32, "Cabbage", "Brassicaceae", "shallow", False, 3, 90, 5, 14, 22, 28, 200, 350, 650, 950, 5.8, 6.2, 7.5, 8.2, ["Loam", "Clay Loam", "Sandy Loam", "Silty Clay Loam"], 30.0),
    FAOCropRecord(33, "Carrot", "Apiaceae", "deep_tap", False, 3, 95, 6, 14, 21, 28, 200, 350, 600, 900, 5.5, 6.0, 7.0, 7.8, ["Sandy Loam", "Loam", "Silty Clay Loam"], 28.0),
    FAOCropRecord(34, "Brinjal (Eggplant)", "Solanaceae", "shallow", False, 4, 120, 13, 21, 30, 36, 250, 400, 750, 1100, 5.5, 6.0, 7.0, 7.8, ["Sandy Loam", "Loam", "Silty Clay Loam"], 22.0),
    FAOCropRecord(35, "Spinach", "Amaranthaceae", "shallow", False, 2, 50, 3, 12, 20, 27, 120, 200, 450, 700, 6.0, 6.5, 7.5, 8.2, ["Loam", "Sandy Loam", "Silty Clay Loam"], 15.0),

    # Fiber & Industrial
    FAOCropRecord(36, "Upland Cotton", "Malvaceae", "deep_tap", False, 5, 150, 15, 24, 33, 40, 350, 550, 1000, 1500, 5.5, 6.2, 7.8, 8.5, ["Loam", "Clay Loam", "Sandy Loam", "Silty Clay Loam"], 2.5),
    FAOCropRecord(37, "Sugarcane", "Poaceae", "deep_fibrous", False, 11, 330, 16, 24, 32, 38, 900, 1400, 2500, 3500, 5.0, 6.0, 7.5, 8.2, ["Loam", "Clay Loam", "Clay", "Silty Clay Loam"], 75.0),
]


class FAOCandidateSelector:
    """
    Selects candidate crops for international locations using FAO EcoCrop parameters,
    NASA POWER climate profile, and ISRIC SoilGrids.
    """

    def __init__(self, crops_db: Optional[List[FAOCropRecord]] = None):
        self.crops_db = crops_db or FAO_ECOCROP_DB

    def score_crop_in_window(
        self,
        crop: FAOCropRecord,
        start_month: int,
        profile: EnvironmentalProfile
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculates suitability score for a crop planted in `start_month` (0 = Jan, 11 = Dec).
        Uses cyclic modulo indexing `(start_month + i) % 12` over `crop.duration_months`.
        Incorporates available soil moisture buffer (~75 mm) from preceding water balance.
        """
        d_months = max(1, min(12, crop.duration_months))
        window_indices = [(start_month + i) % 12 for i in range(d_months)]

        # Window Temperature and Rainfall
        t_mean_win = sum(profile.monthly_tmean[idx] for idx in window_indices) / float(d_months)
        raw_rain_win = sum(profile.monthly_rainfall_mm[idx] for idx in window_indices)

        # Available water = Precipitation in window + Soil water storage buffer (up to 75 mm)
        soil_water_buffer = min(75.0, profile.annual_rainfall_mm * 0.10)
        water_avail_win = raw_rain_win + soil_water_buffer

        # 1. Temperature Suitability
        s_temp = trapezoidal_fuzzy(t_mean_win, crop.t_min, crop.t_opmin, crop.t_opmax, crop.t_max)
        
        # 2. Water Availability Suitability
        s_rain = trapezoidal_fuzzy(water_avail_win, crop.r_min, crop.r_opmin, crop.r_opmax, crop.r_max)

        # 3. Soil pH Suitability
        s_ph = trapezoidal_fuzzy(profile.soil_ph, crop.ph_min, crop.ph_opmin, crop.ph_opmax, crop.ph_max)

        # 4. Soil Texture Suitability
        prof_tex = profile.soil_texture
        if prof_tex in crop.allowable_textures:
            s_tex = 1.0
        elif any(sub in prof_tex for sub in ["Loam", "Silt", "Clay"]):
            s_tex = 0.8
        else:
            s_tex = 0.5

        # Combine via Sys et al. (1991) Square Root Method
        scores_list = [s_temp, s_rain, s_ph, s_tex]
        s_total = sys_square_root_score(scores_list)

        detail = {
            "s_temp": round(s_temp, 3),
            "s_rain": round(s_rain, 3),
            "s_ph": round(s_ph, 3),
            "s_tex": round(s_tex, 3),
            "t_mean_win": round(t_mean_win, 1),
            "water_avail_mm": round(water_avail_win, 1)
        }
        return s_total, detail

    def evaluate_crop(
        self,
        crop: FAOCropRecord,
        profile: EnvironmentalProfile
    ) -> Dict[str, Any]:
        """Evaluates crop across all 12 potential planting months and finds optimal window."""
        best_month = 0
        best_score = -1.0
        best_detail: Dict[str, float] = {}

        for m in range(12):
            score, detail = self.score_crop_in_window(crop, m, profile)
            if score > best_score:
                best_score = score
                best_month = m
                best_detail = detail

        tier = "Ideal" if best_score >= 0.70 else ("Suitable" if best_score >= 0.40 else ("Marginal" if best_score >= 0.20 else "Unsuitable"))

        return {
            "crop_id": crop.crop_id,
            "crop_name": crop.name,
            "botanical_family": crop.botanical_family,
            "root_type": crop.root_type,
            "is_legume": crop.is_legume,
            "duration_days": crop.duration_days,
            "duration_months": crop.duration_months,
            "yield_ton_ha": crop.yield_ton_ha,
            "optimal_start_month": best_month,
            "optimal_start_name": MONTH_NAMES[best_month],
            "suitability_score": round(best_score, 3),
            "suitability_tier": tier,
            "scores_detail": best_detail
        }

    def select_candidate_pools(
        self,
        profile: EnvironmentalProfile
    ) -> Dict[str, Any]:
        """
        Generates 3 seasonal candidate pools based on dynamic cropping intensity K.
        Target counts:
        - Season 1: Target 7 crops
        - Season 2: Target 5 crops
        - Season 3: Target 3 crops
        """
        evaluated = [self.evaluate_crop(c, profile) for c in self.crops_db]
        # Viable crops with score >= 0.20
        viable = [e for e in evaluated if e["suitability_score"] >= 0.20]

        k = profile.cropping_intensity_k

        # Fallow placeholder
        fallow_crop = {
            "crop_id": 999,
            "crop_name": "Fallow",
            "botanical_family": "None",
            "root_type": "none",
            "is_legume": False,
            "duration_days": 0,
            "duration_months": 0,
            "yield_ton_ha": 0.0,
            "optimal_start_month": 0,
            "optimal_start_name": "Any",
            "suitability_score": 1.0,
            "suitability_tier": "Ideal",
            "scores_detail": {}
        }

        def bucket_crops(
            crops_subset: List[Dict[str, Any]],
            target_count: int
        ) -> List[Dict[str, Any]]:
            # Sort by suitability score descending, then duration
            sorted_c = sorted(crops_subset, key=lambda x: (x["suitability_score"], x["yield_ton_ha"]), reverse=True)
            if len(sorted_c) >= target_count:
                return sorted_c[:target_count]
            res = list(sorted_c)
            if not res:
                res.append(fallow_crop)
            return res

        # Check if winter thermal freeze exists (e.g. Frankfurt or North America)
        min_winter_temp = min(profile.monthly_tmean)
        is_temperate_winter = min_winter_temp < 5.0

        if k == 3 and not is_temperate_winter:
            # Humid / Tropical perennial climate (e.g. Nakuru, Kenya)
            p1 = [c for c in viable if c["optimal_start_month"] in [2, 3, 4, 5]]
            p2 = [c for c in viable if c["optimal_start_month"] in [6, 7, 8, 9]]
            p3 = [c for c in viable if c["optimal_start_month"] in [10, 11, 0, 1]]

            if len(p1) < 4: p1 = viable
            if len(p2) < 4: p2 = viable
            if len(p3) < 2: p3 = viable

            final_s1 = bucket_crops(p1, 7)
            final_s2 = bucket_crops(p2, 5)
            final_s3 = bucket_crops(p3, 3)
            effective_k = 3

        elif is_temperate_winter or k == 2:
            # Temperate Europe/North America (Summer growing season + Spring/Autumn + Winter freeze/fallow)
            # or sub-humid tropical double cropping
            # Season 1: Warm Summer (May - Aug)
            # Season 2: Spring / Autumn (Mar - May or Sep - Nov)
            # Season 3: Winter Cold Fallow
            p1 = [c for c in viable if c["optimal_start_month"] in [3, 4, 5, 6]]
            p2 = [c for c in viable if c["optimal_start_month"] in [1, 2, 7, 8]]
            if len(p1) < 4: p1 = viable
            if len(p2) < 3: p2 = viable

            final_s1 = bucket_crops(p1, 7)
            final_s2 = bucket_crops(p2, 5)
            final_s3 = [fallow_crop]
            effective_k = 2

        elif k == 1:
            # Arid / Single Season
            final_s1 = bucket_crops(viable, 7)
            final_s2 = [fallow_crop]
            final_s3 = [fallow_crop]
            effective_k = 1

        else:  # k == 0 (hyper-arid / extreme permafrost LGP < 60 days)
            final_s1 = [fallow_crop]
            final_s2 = [fallow_crop]
            final_s3 = [fallow_crop]
            effective_k = 0

        return {
            "region_type": "GLOBAL_FAO_ECOCROP",
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "annual_rainfall_mm": profile.annual_rainfall_mm,
            "soil_ph": profile.soil_ph,
            "soil_texture": profile.soil_texture,
            "lgp_days": profile.lgp_days,
            "cropping_intensity_k": effective_k,
            "seasons": {
                "season_1": final_s1,
                "season_2": final_s2,
                "season_3": final_s3
            },
            "candidate_counts": {
                "season_1": len(final_s1),
                "season_2": len(final_s2),
                "season_3": len(final_s3)
            }
        }
