import os, sys, math, json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.planetary_benchmark_100 import BENCHMARK_100
from src.global_env_fetcher import GlobalEnvFetcher

MONTH_NAMES = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MONTH_FULL_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
DAYS_IN_MONTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MID_MONTH_DAY_OF_YEAR = [15, 45, 74, 105, 135, 165, 196, 227, 258, 288, 319, 349]

def format_cyclic_window(months: List[int]) -> str:
    if not months:
        return "None"
    if len(months) == 12:
        return "January - December (12 Months)"
    if len(months) == 1:
        return f"{MONTH_FULL_NAMES[months[0]]} (1 Month)"
    sorted_m = sorted(months)
    is_contiguous_straight = all(sorted_m[i+1] == sorted_m[i] + 1 for i in range(len(sorted_m) - 1))
    if is_contiguous_straight:
        return f"{MONTH_FULL_NAMES[sorted_m[0]]} - {MONTH_FULL_NAMES[sorted_m[-1]]} ({len(months)} Months)"
    if 0 in sorted_m and 11 in sorted_m:
        gaps = [i for i in range(len(sorted_m) - 1) if sorted_m[i + 1] > sorted_m[i] + 1]
        if len(gaps) == 1:
            gap_idx = gaps[0]
            start_m = sorted_m[gap_idx + 1]
            end_m = sorted_m[gap_idx]
            return f"{MONTH_FULL_NAMES[start_m]} - {MONTH_FULL_NAMES[end_m]} ({len(months)} Months)"
    if len(months) <= 3:
        return f"{' & '.join(MONTH_FULL_NAMES[m] for m in sorted_m)} ({len(months)} Months)"
    return f"{MONTH_FULL_NAMES[sorted_m[0]]} - {MONTH_FULL_NAMES[sorted_m[-1]]} ({len(months)} Months)"

@dataclass
class SeasonMetadata:
    season_id: int
    name: str
    start_month: int
    end_month: int
    duration_months: int
    calendar_window: str
    regime_type: str
    mean_temp_c: float
    min_temp_c: float
    total_rain_mm: float
    is_fallow: bool
    fallow_reason: Optional[str] = None
    role: str = ""

@dataclass
class AgroClimaticCalendar:
    latitude: float
    longitude: float
    hemisphere: str
    regime_classification: str
    annual_rainfall_mm: float
    annual_mean_temp_c: float
    cropping_intensity_k: int
    lgp_days: int
    seasons: Dict[str, SeasonMetadata]

class UniversalSeasonalSegmenter:
    @staticmethod
    def calculate_ra_fao56(lat_deg: float, day_of_year: int) -> float:
        phi = math.radians(lat_deg)
        delta = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)
        dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
        x = -math.tan(phi) * math.tan(delta)
        if x < -1.0: ws = math.pi
        elif x > 1.0: ws = 0.0
        else: ws = math.acos(x)
        ra_mj = (24 * 60 / math.pi) * 0.0820 * dr * (
            ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws)
        )
        return max(0.5, ra_mj * 0.408)

    @classmethod
    def calculate_monthly_pet(cls, lat: float, monthly_tmean: List[float], monthly_tmin: List[float], monthly_tmax: List[float]) -> List[float]:
        monthly_pet = []
        for m in range(12):
            days = DAYS_IN_MONTHS[m]
            t_m = monthly_tmean[m]
            raw_diff = max(5.0, monthly_tmax[m] - monthly_tmin[m])
            dtr = min(16.0, max(7.0, raw_diff * 0.35))
            ra = cls.calculate_ra_fao56(lat, MID_MONTH_DAY_OF_YEAR[m])
            pet_day = max(0.5, 0.0023 * (t_m + 17.8) * math.sqrt(dtr) * ra)
            monthly_pet.append(pet_day * days)
        return monthly_pet

    @classmethod
    def segment_calendar(cls, lat: float, lon: float, monthly_tmean: List[float], monthly_tmin: List[float], monthly_tmax: List[float], monthly_rain: List[float], lgp_days: int = 120) -> AgroClimaticCalendar:
        hemisphere = "Northern" if lat >= 0 else "Southern"
        annual_rain = sum(monthly_rain)
        annual_tmean = sum(monthly_tmean) / 12.0
        min_tmin = min(monthly_tmin)
        max_tmean = max(monthly_tmean)

        monthly_pet = cls.calculate_monthly_pet(lat, monthly_tmean, monthly_tmin, monthly_tmax)
        annual_pet = sum(monthly_pet)
        aridity_index = annual_rain / max(1.0, annual_pet)

        is_freeze = [monthly_tmean[m] < 5.0 for m in range(12)]
        has_freeze_season = any(is_freeze)
        if min_tmin < -2.0 and annual_tmean < 10.0:
            has_freeze_season = True

        frost_free = [not is_freeze[m] for m in range(12)]
        extended = frost_free + frost_free
        max_streak = 0
        curr = 0
        for v in extended:
            if v:
                curr += 1
                if curr > max_streak: max_streak = curr
            else: curr = 0
        max_frost_free_months = min(12, max_streak)

        summer_idx = [5, 6, 7] if hemisphere == "Northern" else [11, 0, 1]
        winter_idx = [11, 0, 1] if hemisphere == "Northern" else [5, 6, 7]
        summer_rain = sum(monthly_rain[i] for i in summer_idx)
        winter_rain = sum(monthly_rain[i] for i in winter_idx)
        summer_pet = sum(monthly_pet[i] for i in summer_idx)
        summer_aridity = summer_rain / max(1.0, summer_pet)
        min_monthly_tmean = min(monthly_tmean)

        is_mediterranean = (
            annual_rain >= 200 and
            (summer_rain < 75 or summer_aridity < 0.25) and
            winter_rain > 1.2 * summer_rain and
            min_monthly_tmean >= 2.0
        )

        if annual_rain < 120 or (aridity_index < 0.20 and annual_tmean >= 15.0):
            regime = "HYPER_ARID_DESERT"
        elif has_freeze_season:
            if summer_aridity < 0.25 and summer_rain < 100:
                regime = "MEDITERRANEAN_CONTINENTAL_STEPPE"
            else:
                regime = "TEMPERATE_CONTINENTAL_FROST"
        elif is_mediterranean:
            regime = "MEDITERRANEAN_WINTER_RAIN"
        elif annual_tmean < 15.0 and abs(lat) >= 28.0:
            regime = "TEMPERATE_OCEANIC_MARITIME"
        elif annual_tmean < 22.0 and min_monthly_tmean >= 4.0 and abs(lat) >= 23.0:
            regime = "HUMID_SUBTROPICAL"
        elif sum(1 for m in range(12) if monthly_rain[m] >= 60.0) >= 10 and annual_rain >= 1400:
            regime = "HUMID_TROPICAL_PERENNIAL"
        else:
            smoothed = [(monthly_rain[(i-1)%12] + monthly_rain[i] + monthly_rain[(i+1)%12]) / 3.0 for i in range(12)]
            peaks = [i for i in range(12) if smoothed[i] > smoothed[(i-1)%12] and smoothed[i] > smoothed[(i+1)%12] and smoothed[i] >= 75.0]
            if len(peaks) >= 2 and 3 <= abs(peaks[0] - peaks[1]) <= 9:
                regime = "TROPICAL_BIMODAL_RAIN"
            else:
                regime = "TROPICAL_MONOMODAL_RAIN"

        if regime in ["HYPER_ARID_DESERT", "MEDITERRANEAN_WINTER_RAIN", "MEDITERRANEAN_CONTINENTAL_STEPPE"]:
            cropping_intensity_k = 1
        elif regime == "TEMPERATE_CONTINENTAL_FROST":
            mean_summer_t = max(monthly_tmean)
            if max_frost_free_months >= 8 and lgp_days >= 210 and mean_summer_t >= 22.0:
                cropping_intensity_k = 2
            else:
                cropping_intensity_k = 1
        elif regime == "TEMPERATE_OCEANIC_MARITIME":
            cropping_intensity_k = 1
        elif regime == "HUMID_SUBTROPICAL":
            cropping_intensity_k = 2 if lgp_days >= 200 else 1
        elif regime == "TROPICAL_BIMODAL_RAIN":
            if lgp_days >= 330: cropping_intensity_k = 3
            elif lgp_days >= 150: cropping_intensity_k = 2
            else: cropping_intensity_k = 1
        elif regime == "HUMID_TROPICAL_PERENNIAL":
            if lgp_days >= 290 and annual_rain >= 1800: cropping_intensity_k = 3
            else: cropping_intensity_k = 2
        else:
            dry_season_rain = sum(monthly_rain[m] for m in range(12) if monthly_rain[m] < 0.5 * monthly_pet[m])
            if dry_season_rain < 60.0 or lgp_days < 140:
                cropping_intensity_k = 1
            elif lgp_days >= 260 and annual_tmean >= 22.0:
                cropping_intensity_k = 3
            else:
                cropping_intensity_k = 2

        seasons: Dict[str, SeasonMetadata] = {}

        if regime == "HYPER_ARID_DESERT":
            seasons["season_1"] = SeasonMetadata(1, "Pluvial Hyper-Arid Fallow (Year-Round)", 0, 11, 12, "January - December (12 Months)", "DROUGHT_DORMANCY", annual_tmean, min_tmin, annual_rain, True, f"Hyper-arid pluvial desert ({annual_rain:.1f} mm < 120 mm). Rainfed crops cannot survive; requires irrigation.", "Drought Fallow (Irrigation Mandatory)")
            seasons["season_2"] = SeasonMetadata(2, "Dormancy Window", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "Hyper-arid moisture deficit", "None")
            seasons["season_3"] = SeasonMetadata(3, "Dormancy Window", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "Hyper-arid moisture deficit", "None")

        elif regime == "MEDITERRANEAN_CONTINENTAL_STEPPE":
            s1_start = 9 if hemisphere == "Northern" else 3
            s1_end = 5 if hemisphere == "Northern" else 11
            s1_months = [(s1_start + i) % 12 for i in range(9)]
            seasons["season_1"] = SeasonMetadata(1, "Autumn-Sown Winter Cereal Season", s1_start, s1_end, 9, format_cyclic_window(s1_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in s1_months)/9, 1), round(min_tmin, 1), round(sum(monthly_rain[m] for m in s1_months), 1), False, None, "Primary Rainfed Winter Grain (Wheat, Barley, Chickpea)")
            seasons["season_2"] = SeasonMetadata(2, "Mid-Summer Desiccation Window", (s1_end + 1) % 12, (s1_end + 1) % 12, 1, f"{MONTH_FULL_NAMES[(s1_end + 1) % 12]} (1 Month)", "DROUGHT_DORMANCY", round(monthly_tmean[(s1_end + 1) % 12], 1), round(monthly_tmin[(s1_end + 1) % 12], 1), round(monthly_rain[(s1_end + 1) % 12], 1), True, "Intense summer heat and drought onset.", "Post-Harvest Stubble Rest")
            s3_months = [(s1_end + 2 + i) % 12 for i in range(2)]
            seasons["season_3"] = SeasonMetadata(3, "Late Summer Drought Fallow", s3_months[0], s3_months[-1], len(s3_months), format_cyclic_window(s3_months), "DROUGHT_DORMANCY", round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1), round(min(monthly_tmin[m] for m in s3_months), 1), round(sum(monthly_rain[m] for m in s3_months), 1), True, "Severe dryland moisture deficit in high plateau summer.", "Summer Drought Fallow")

        elif regime == "TEMPERATE_CONTINENTAL_FROST":
            growing_months = [m for m in range(12) if monthly_tmean[m] >= 10.0]
            if not growing_months: growing_months = [m for m in range(12) if monthly_tmean[m] >= 5.0]
            s1_start = growing_months[0]
            s1_end = growing_months[-1]
            s1_dur = (s1_end - s1_start + 1) if s1_end >= s1_start else (12 - s1_start + s1_end + 1)
            seasons["season_1"] = SeasonMetadata(1, "Primary Summer Growing Season", s1_start, s1_end, s1_dur, format_cyclic_window(growing_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in growing_months)/len(growing_months), 1), round(min(monthly_tmin[m] for m in growing_months), 1), round(sum(monthly_rain[m] for m in growing_months), 1), False, None, "Economic Anchor (Cash Crops & Staple Grains)")
            freeze_months = [m for m in range(12) if is_freeze[m]]
            s3_start = freeze_months[0] if freeze_months else 11
            s3_end = freeze_months[-1] if freeze_months else 1
            s3_dur = max(1, len(freeze_months))
            shoulder_months = [m for m in range(12) if 5.0 <= monthly_tmean[m] < 10.0]
            if shoulder_months and cropping_intensity_k >= 2:
                seasons["season_2"] = SeasonMetadata(2, "Spring/Autumn Shoulder Window", shoulder_months[0], shoulder_months[-1], len(shoulder_months), format_cyclic_window(shoulder_months), "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in shoulder_months)/len(shoulder_months), 1), round(min(monthly_tmin[m] for m in shoulder_months), 1), round(sum(monthly_rain[m] for m in shoulder_months), 1), False, None, "Succession / Short Cover Crop / Pulse")
            else:
                seasons["season_2"] = SeasonMetadata(2, "Pre-Winter Shoulder Fallow", (s1_end + 1) % 12, (s1_end + 1) % 12, 1, f"{MONTH_FULL_NAMES[(s1_end + 1) % 12]} (1 Month)", "SHOULDER_SUCCESSION", round(monthly_tmean[(s1_end + 1) % 12], 1), round(monthly_tmin[(s1_end + 1) % 12], 1), round(monthly_rain[(s1_end + 1) % 12], 1), True, "Insufficient thermal units to mature a second crop before frost onset.", "Field Rest / Stubble Cover")
            seasons["season_3"] = SeasonMetadata(3, "Winter Freeze Dormancy", s3_start, s3_end, s3_dur, format_cyclic_window(freeze_months), "FREEZE_DORMANCY", round(sum(monthly_tmean[m] for m in freeze_months)/s3_dur, 1), round(min_tmin, 1), round(sum(monthly_rain[m] for m in freeze_months), 1), True, f"Sub-zero ground frost and freezing air (Tmin down to {min_tmin:.1f}°C) halt plant cell division.", "Winter Biological Rest")

        elif regime == "MEDITERRANEAN_WINTER_RAIN":
            wet_months = [m for m in range(12) if monthly_rain[m] >= 30.0]
            if not wet_months: wet_months = sorted(range(12), key=lambda m: monthly_rain[m], reverse=True)[:5]
            dry_months = [m for m in range(12) if m not in wet_months]
            if not dry_months: dry_months = [0]
            sorted_wet = sorted(wet_months)
            if 0 in sorted_wet and 11 in sorted_wet and len(sorted_wet) < 12:
                s1_start = sorted_wet[0]; s1_end = sorted_wet[-1]
                for i in range(len(sorted_wet) - 1):
                    if sorted_wet[i + 1] > sorted_wet[i] + 1:
                        s1_start = sorted_wet[i + 1]; s1_end = sorted_wet[i]; break
            else: s1_start = sorted_wet[0]; s1_end = sorted_wet[-1]
            s1_dur = len(wet_months)
            seasons["season_1"] = SeasonMetadata(1, "Mild Pluvial Winter/Spring Season", s1_start, s1_end, s1_dur, format_cyclic_window(wet_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in wet_months)/s1_dur, 1), round(min_tmin, 1), round(sum(monthly_rain[m] for m in wet_months), 1), False, None, "Primary Rainfed Cropping (Wheat, Barley, Chickpea, Olive)")
            seasons["season_2"] = SeasonMetadata(2, "Early Summer Harvest Window", dry_months[0], dry_months[0], 1, f"{MONTH_FULL_NAMES[dry_months[0]]} (1 Month)", "SHOULDER_SUCCESSION", round(monthly_tmean[dry_months[0]], 1), round(monthly_tmin[dry_months[0]], 1), round(monthly_rain[dry_months[0]], 1), True, "Rapid onset of Mediterranean summer drought.", "Crop Desiccation & Harvest")
            seasons["season_3"] = SeasonMetadata(3, "Dry Summer Dormancy Window", dry_months[1] if len(dry_months) > 1 else dry_months[0], dry_months[-1], max(1, len(dry_months) - 1), f"{MONTH_FULL_NAMES[dry_months[1] if len(dry_months) > 1 else dry_months[0]]} - {MONTH_FULL_NAMES[dry_months[-1]]} ({max(1, len(dry_months)-1)} Months)", "DROUGHT_DORMANCY", round(sum(monthly_tmean[m] for m in dry_months[1:]) / max(1, len(dry_months) - 1), 1), round(min(monthly_tmin[m] for m in dry_months[1:]), 1), round(sum(monthly_rain[m] for m in dry_months[1:]), 1), True, "Severe summer moisture deficit (Rainfall < 20 mm, PET > 150 mm/month).", "Summer Drought Fallow")

        elif regime == "TEMPERATE_OCEANIC_MARITIME":
            growing_months = [m for m in range(12) if monthly_tmean[m] >= 10.0]
            if not growing_months: growing_months = [m for m in range(12) if monthly_tmean[m] >= 7.0]
            s1_start = growing_months[0]; s1_end = growing_months[-1]
            s1_dur = len(growing_months)
            seasons["season_1"] = SeasonMetadata(1, "Maritime Spring/Summer Growing Season", s1_start, s1_end, s1_dur, format_cyclic_window(growing_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in growing_months)/s1_dur, 1), round(min(monthly_tmin[m] for m in growing_months), 1), round(sum(monthly_rain[m] for m in growing_months), 1), False, None, "Cash Crops, Cereals & Forage (Wheat, Barley, Maize, Potato)")
            off_months = [m for m in range(12) if m not in growing_months]
            if not off_months: off_months = [(s1_end + 1) % 12]
            half = max(1, len(off_months) // 2)
            s2_months = off_months[:half]
            s3_months = off_months[half:] if len(off_months) > half else s2_months
            seasons["season_2"] = SeasonMetadata(2, "Autumn Shoulder / Post-Harvest", s2_months[0], s2_months[-1], len(s2_months), format_cyclic_window(s2_months), "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1), round(min(monthly_tmin[m] for m in s2_months), 1), round(sum(monthly_rain[m] for m in s2_months), 1), True, "Declining autumn photoperiod and temperatures.", "Post-Harvest Field Rest")
            seasons["season_3"] = SeasonMetadata(3, "Cool Winter Rest", s3_months[0], s3_months[-1], len(s3_months), format_cyclic_window(s3_months), "FREEZE_DORMANCY", round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1), round(min_tmin, 1), round(sum(monthly_rain[m] for m in s3_months), 1), True, "Low solar radiation and cool winter temperatures.", "Winter Rest")

        elif regime == "HUMID_SUBTROPICAL":
            summer_months = [m for m in range(12) if monthly_tmean[m] >= 18.0]
            if not summer_months: summer_months = [m for m in range(12) if monthly_tmean[m] >= 14.0]
            s1_start = summer_months[0]; s1_end = summer_months[-1]
            s1_dur = len(summer_months)
            seasons["season_1"] = SeasonMetadata(1, "Subtropical Summer Growing Season", s1_start, s1_end, s1_dur, format_cyclic_window(summer_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in summer_months)/s1_dur, 1), round(min(monthly_tmin[m] for m in summer_months), 1), round(sum(monthly_rain[m] for m in summer_months), 1), False, None, "Economic Anchor (Soybean, Maize, Peanut, Cotton)")
            winter_months = [m for m in range(12) if m not in summer_months]
            if cropping_intensity_k >= 2 and len(winter_months) >= 3:
                seasons["season_2"] = SeasonMetadata(2, "Winter Small Grain / Cover Window", winter_months[0], winter_months[-1], len(winter_months), format_cyclic_window(winter_months), "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in winter_months)/len(winter_months), 1), round(min(monthly_tmin[m] for m in winter_months), 1), round(sum(monthly_rain[m] for m in winter_months), 1), False, None, "Winter Wheat / Cover Crop / Ryegrass")
            else:
                seasons["season_2"] = SeasonMetadata(2, "Winter Fallow", winter_months[0], winter_months[-1], len(winter_months), format_cyclic_window(winter_months), "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in winter_months)/len(winter_months), 1), round(min(monthly_tmin[m] for m in winter_months), 1), round(sum(monthly_rain[m] for m in winter_months), 1), True, "Seasonal moisture deficit / GDD threshold.", "Winter Fallow")
            seasons["season_3"] = SeasonMetadata(3, "Transitional Niche", 0, 0, 0, "None", "SHOULDER_SUCCESSION", annual_tmean, min_tmin, 0.0, True, "Subtropical 2-season rotation.", "None")

        elif regime == "HUMID_TROPICAL_PERENNIAL":
            s1_months = [i for i in range(12) if monthly_rain[i] >= 100.0][:6]
            if not s1_months: s1_months = list(range(6))
            seasons["season_1"] = SeasonMetadata(1, "Primary Monsoon / Wet Season", s1_months[0], s1_months[-1], len(s1_months), format_cyclic_window(s1_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1), round(min(monthly_tmin[m] for m in s1_months), 1), round(sum(monthly_rain[m] for m in s1_months), 1), False, None, "Primary Cash / Food Staple (Wet Rice, Soy, Sugarcane)")
            s2_months = [i for i in range(12) if i not in s1_months][:4]
            if not s2_months: s2_months = [6, 7, 8, 9]
            seasons["season_2"] = SeasonMetadata(2, "Secondary Succession Season", s2_months[0], s2_months[-1], len(s2_months), format_cyclic_window(s2_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1), round(min(monthly_tmin[m] for m in s2_months), 1), round(sum(monthly_rain[m] for m in s2_months), 1), False, None, "Secondary Food / Palawija Rotation (Corn, Beans, Vegetables)")
            s3_months = [i for i in range(12) if i not in s1_months and i not in s2_months]
            if not s3_months: s3_months = [10, 11]
            seasons["season_3"] = SeasonMetadata(3, "Tertiary Dry-Season / Cover Niche", s3_months[0], s3_months[-1], len(s3_months), format_cyclic_window(s3_months), "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1), round(min(monthly_tmin[m] for m in s3_months), 1), round(sum(monthly_rain[m] for m in s3_months), 1), cropping_intensity_k < 3, "Dry season soil moisture rest." if cropping_intensity_k < 3 else None, "Short Grain / Legume Cover Catch" if cropping_intensity_k >= 3 else "Field Rest")

        elif regime == "TROPICAL_BIMODAL_RAIN":
            peak1 = max(range(0, 6), key=lambda m: monthly_rain[m])
            peak2 = max(range(6, 12), key=lambda m: monthly_rain[m])
            p1_months = [(peak1 - 1) % 12, peak1, (peak1 + 1) % 12]
            p2_months = [(peak2 - 1) % 12, peak2, (peak2 + 1) % 12]
            seasons["season_1"] = SeasonMetadata(1, "Primary Wet Season (Long Rains)", p1_months[0], p1_months[-1], 3, format_cyclic_window(p1_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in p1_months)/3, 1), round(min(monthly_tmin[m] for m in p1_months), 1), round(sum(monthly_rain[m] for m in p1_months), 1), False, None, "Primary Cash & Staple Grains (Long Rains Anchor)")
            seasons["season_2"] = SeasonMetadata(2, "Secondary Wet Season (Short Rains)", p2_months[0], p2_months[-1], 3, format_cyclic_window(p2_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in p2_months)/3, 1), round(min(monthly_tmin[m] for m in p2_months), 1), round(sum(monthly_rain[m] for m in p2_months), 1), False, None, "Secondary Food Security & Legumes (Short Rains)")
            dry_months = [m for m in range(12) if m not in p1_months and m not in p2_months]
            seasons["season_3"] = SeasonMetadata(3, "Dry Interval / Inter-Monsoon Niche", dry_months[0], dry_months[-1], len(dry_months), format_cyclic_window(dry_months), "DROUGHT_DORMANCY" if cropping_intensity_k < 3 else "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in dry_months)/len(dry_months), 1), round(min(monthly_tmin[m] for m in dry_months), 1), round(sum(monthly_rain[m] for m in dry_months), 1), (cropping_intensity_k < 3), "Dry inter-season dry spell with low soil moisture storage." if cropping_intensity_k < 3 else None, "Dry Season Pasture / Fast Short Legume Catch")

        else:
            wet_months = [m for m in range(12) if monthly_rain[m] >= 50.0]
            if not wet_months: wet_months = sorted(range(12), key=lambda m: monthly_rain[m], reverse=True)[:4]
            sorted_wet = sorted(wet_months)
            if 0 in sorted_wet and 11 in sorted_wet and len(sorted_wet) < 12:
                s1_start = sorted_wet[0]; s1_end = sorted_wet[-1]
                for i in range(len(sorted_wet) - 1):
                    if sorted_wet[i + 1] > sorted_wet[i] + 1:
                        s1_start = sorted_wet[i + 1]; s1_end = sorted_wet[i]; break
            else: s1_start = sorted_wet[0]; s1_end = sorted_wet[-1]
            s1_dur = len(wet_months)
            seasons["season_1"] = SeasonMetadata(1, "Primary Monsoonal Wet Season", s1_start, s1_end, s1_dur, format_cyclic_window(wet_months), "ACTIVE_GROWING", round(sum(monthly_tmean[m] for m in wet_months)/s1_dur, 1), round(min(monthly_tmin[m] for m in wet_months), 1), round(sum(monthly_rain[m] for m in wet_months), 1), False, None, "Primary Rainfed Anchor (Millets, Sorghum, Cowpea, Rice)")

            dry_months = [m for m in range(12) if m not in wet_months]
            dry_months_cyclic = sorted(dry_months, key=lambda m: (m - s1_end) % 12)
            dry_season_rain = sum(monthly_rain[m] for m in dry_months)
            if cropping_intensity_k >= 2 and len(dry_months_cyclic) >= 3 and dry_season_rain >= 60.0:
                s2_months = dry_months_cyclic[:3]
                seasons["season_2"] = SeasonMetadata(2, "Post-Monsoon Residual Moisture Season", s2_months[0], s2_months[-1], 3, format_cyclic_window(s2_months), "SHOULDER_SUCCESSION", round(sum(monthly_tmean[m] for m in s2_months)/3, 1), round(min(monthly_tmin[m] for m in s2_months), 1), round(sum(monthly_rain[m] for m in s2_months), 1), False, None, "Residual Soil Moisture / Short Pulses")
            else:
                s2_months = dry_months_cyclic[:len(dry_months_cyclic)//2] if dry_months_cyclic else [0]
                seasons["season_2"] = SeasonMetadata(2, "Dry Season Dormancy", s2_months[0], s2_months[-1], len(s2_months), format_cyclic_window(s2_months), "DROUGHT_DORMANCY", round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1), round(min(monthly_tmin[m] for m in s2_months), 1), round(sum(monthly_rain[m] for m in s2_months), 1), True, "Severe dryland moisture deficit.", "Field Rest / Stubble Grazing")

            rem_months = dry_months_cyclic[len(s2_months):] if len(dry_months_cyclic) > len(s2_months) else [0]
            seasons["season_3"] = SeasonMetadata(3, "Late Dry Season / Pre-Monsoon Fallow", rem_months[0], rem_months[-1], len(rem_months), format_cyclic_window(rem_months), "DROUGHT_DORMANCY", round(sum(monthly_tmean[m] for m in rem_months)/len(rem_months), 1), round(min(monthly_tmin[m] for m in rem_months), 1), round(sum(monthly_rain[m] for m in rem_months), 1), True, "Peak dry season before monsoon arrival.", "Land Prep & Tillage")

        return AgroClimaticCalendar(lat, lon, hemisphere, regime, round(annual_rain, 1), round(annual_tmean, 1), cropping_intensity_k, lgp_days, seasons)

with open('data/planetary_100_cache.json') as f:
    cache = json.load(f)

fetcher = GlobalEnvFetcher()
k_matches = 0
regime_matches = 0

for loc in BENCHMARK_100:
    clim = cache[f"{loc.lat:.4f}_{loc.lon:.4f}"]
    calc_lgp, _ = fetcher.compute_daily_lgp_and_k(clim["monthly_tmean"], clim["monthly_tmin"], clim["monthly_tmax"], clim["monthly_rain"], lat=loc.lat)
    cal = UniversalSeasonalSegmenter.segment_calendar(loc.lat, loc.lon, clim["monthly_tmean"], clim["monthly_tmin"], clim["monthly_tmax"], clim["monthly_rain"], lgp_days=calc_lgp)
    if cal.cropping_intensity_k == loc.ground_truth_rainfed_k:
        k_matches += 1

print(f"Evaluated 100 locations. Dynamic K matches: {k_matches}/100 ({k_matches}%)")
