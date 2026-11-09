import os, sys, math, json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    
    month_set = set(months)
    visited = set()
    runs = []
    
    # Identify starts of contiguous cyclic runs
    starts = [m for m in months if (m - 1) % 12 not in month_set]
    if not starts:
        starts = [sorted(months)[0]]
    starts.sort()
    
    for start in starts:
        if start in visited:
            continue
        curr_run = []
        curr = start
        while curr in month_set and curr not in visited:
            curr_run.append(curr)
            visited.add(curr)
            curr = (curr + 1) % 12
        if curr_run:
            runs.append(curr_run)
            
    for m in sorted(months):
        if m not in visited:
            runs.append([m])
            visited.add(m)
            
    formatted_parts = []
    for run in runs:
        if len(run) == 1:
            formatted_parts.append(MONTH_FULL_NAMES[run[0]])
        else:
            formatted_parts.append(f"{MONTH_FULL_NAMES[run[0]]} - {MONTH_FULL_NAMES[run[-1]]}")
            
    return f"{' & '.join(formatted_parts)} ({len(months)} Months)"

def get_run_start_end(months: List[int]) -> Tuple[int, int]:
    if not months:
        return 0, 0
    if len(months) == 12:
        return 0, 11
    if len(months) == 1:
        return months[0], months[0]
    month_set = set(months)
    starts = [m for m in months if (m - 1) % 12 not in month_set]
    if starts:
        start = sorted(starts)[0]
        curr = start
        while (curr + 1) % 12 in month_set:
            curr = (curr + 1) % 12
        return start, curr
    return sorted(months)[0], sorted(months)[-1]

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hemisphere": self.hemisphere,
            "regime_classification": self.regime_classification,
            "annual_rainfall_mm": round(self.annual_rainfall_mm, 1),
            "annual_mean_temp_c": round(self.annual_mean_temp_c, 1),
            "cropping_intensity_k": self.cropping_intensity_k,
            "lgp_days": self.lgp_days,
            "seasons": {k: asdict(v) for k, v in self.seasons.items()}
        }

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
        min_monthly_tmean = min(monthly_tmean)
        temp_range = max_tmean - min_monthly_tmean

        monthly_pet = cls.calculate_monthly_pet(lat, monthly_tmean, monthly_tmin, monthly_tmax)
        annual_pet = sum(monthly_pet)
        aridity_index = annual_rain / max(1.0, annual_pet)

        # Freeze analysis
        is_freeze = [monthly_tmean[m] < 5.0 for m in range(12)]
        has_freeze_season = any(is_freeze)
        # High-elevation / radiation frost detection (e.g. South African Highveld, Altiplano)
        has_radiation_frost = any(monthly_tmin[m] < -3.0 and monthly_tmean[m] < 14.0 for m in range(12))

        summer_idx = [5, 6, 7] if hemisphere == "Northern" else [11, 0, 1]
        winter_idx = [11, 0, 1] if hemisphere == "Northern" else [5, 6, 7]
        summer_rain = sum(monthly_rain[i] for i in summer_idx)
        winter_rain = sum(monthly_rain[i] for i in winter_idx)
        summer_pet = sum(monthly_pet[i] for i in summer_idx)
        summer_aridity = summer_rain / max(1.0, summer_pet)

        is_mediterranean = (
            annual_rain >= 140.0 and
            (summer_rain < 100.0 or summer_aridity < 0.28) and
            winter_rain > 1.15 * summer_rain and
            min_monthly_tmean >= 1.0
        )

        is_tropical_highland = (
            abs(lat) < 23.5 and
            (annual_tmean < 14.0 or (annual_tmean < 16.0 and any(monthly_tmin[m] < 0.0 for m in range(12))))
        )
        freeze_month_count = sum(1 for m in range(12) if is_freeze[m])
        is_true_continental = (
            min_monthly_tmean <= 1.0 or
            (freeze_month_count >= 2 and annual_tmean < 13.0 and min_tmin < -4.0) or
            (min_tmin < -12.0 and min_monthly_tmean <= 2.5)
        )

        # -------------------------------------------------------------
        # 1. Regime Classification
        # -------------------------------------------------------------
        if is_tropical_highland:
            regime = "TROPICAL_HIGHLAND_VALLEY"
        elif annual_rain < 100.0 or (aridity_index < 0.11 and annual_rain < 150.0):
            regime = "HYPER_ARID_DESERT"
        elif is_mediterranean:
            if min_tmin < -4.0 or min_monthly_tmean < 4.0 or temp_range >= 18.0:
                regime = "MEDITERRANEAN_CONTINENTAL_STEPPE"
            else:
                regime = "MEDITERRANEAN_WINTER_RAIN"
        elif is_true_continental and abs(lat) >= 25.0:
            regime = "TEMPERATE_CONTINENTAL_FROST"
        elif abs(lat) >= 20.0 and annual_rain < 680.0 and aridity_index < 0.52:
            # Subtropical & mid-latitude drylands (Australia broadacre, Great Plains, Chaco, Zaragoza, Chihuahuan margin)
            regime = "SEMI_ARID_STEPPE"
        elif abs(lat) >= 28.0 and annual_tmean < 16.0 and annual_rain >= 500.0 and min_monthly_tmean >= 1.0:
            # Mild oceanic maritime (UK, Ireland, France, Belgium, Netherlands, Denmark, Germany, S. Chile, NZ)
            regime = "TEMPERATE_OCEANIC_MARITIME"
        elif has_freeze_season and abs(lat) >= 25.0 and min_monthly_tmean <= 2.0:
            # High-latitude / continental cold season safety net
            regime = "TEMPERATE_CONTINENTAL_FROST"
        elif abs(lat) >= 23.0 and annual_tmean < 24.0 and min_monthly_tmean >= 2.0 and annual_rain >= 680.0 and aridity_index >= 0.52:
            # Humid subtropical (US Mid-South, Pampas, S. Brazil/Paraguay, Yangtze, Po Valley)
            regime = "HUMID_SUBTROPICAL"
        elif abs(lat) < 23.0 and annual_rain >= 1400.0 and aridity_index >= 0.85 and sum(1 for m in range(12) if monthly_rain[m] >= 60.0) >= 9 and sum(1 for m in range(12) if monthly_rain[m] < 30.0) == 0:
            regime = "HUMID_TROPICAL_PERENNIAL"
        else:
            smoothed = [(monthly_rain[(i-1)%12] + monthly_rain[i] + monthly_rain[(i+1)%12]) / 3.0 for i in range(12)]
            peaks = [i for i in range(12) if smoothed[i] > smoothed[(i-1)%12] and smoothed[i] > smoothed[(i+1)%12] and smoothed[i] >= 75.0]
            if len(peaks) >= 2 and 3 <= abs(peaks[0] - peaks[1]) <= 9:
                regime = "TROPICAL_BIMODAL_RAIN"
            else:
                regime = "TROPICAL_MONOMODAL_RAIN"

        seasons: Dict[str, SeasonMetadata] = {}

        # -------------------------------------------------------------
        # 2. Season Segmentation by Regime
        # -------------------------------------------------------------
        if regime == "HYPER_ARID_DESERT":
            reason_str = (
                f"Hyper-arid pluvial desert ({annual_rain:.1f} mm < 120 mm). Rainfed crops cannot survive; requires irrigation."
                if annual_rain < 120.0
                else f"Hyper-arid moisture deficit (Aridity Index {aridity_index:.2f} < 0.20, Rain {annual_rain:.1f} mm). Rainfed crops cannot survive; requires irrigation."
            )
            seasons["season_1"] = SeasonMetadata(
                1, "Pluvial Hyper-Arid Fallow (Year-Round)", 0, 11, 12,
                "January - December (12 Months)", "DROUGHT_DORMANCY",
                annual_tmean, min_tmin, annual_rain, True,
                reason_str,
                "Drought Fallow (Irrigation Mandatory)"
            )
            seasons["season_2"] = SeasonMetadata(2, "None", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "Hyper-arid moisture deficit", "None")
            seasons["season_3"] = SeasonMetadata(3, "None", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "Hyper-arid moisture deficit", "None")

        elif regime == "TROPICAL_HIGHLAND_VALLEY":
            if hemisphere == "Southern":
                s1_months = [9, 10, 11, 0, 1, 2, 3] # October - April (7 mo)
                s2_months = [4, 5, 6, 7, 8]          # May - September (5 mo)
            else:
                s1_months = [3, 4, 5, 6, 7, 8, 9]   # April - October (7 mo)
                s2_months = [10, 11, 0, 1, 2]        # November - March (5 mo)
                
            s1_start, s1_end = get_run_start_end(s1_months)
            s2_start, s2_end = get_run_start_end(s2_months)
            
            seasons["season_1"] = SeasonMetadata(
                1, "Highland Rainy Growing Season", s1_start, s1_end, len(s1_months),
                format_cyclic_window(s1_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1),
                round(min(monthly_tmin[m] for m in s1_months), 1),
                round(sum(monthly_rain[m] for m in s1_months), 1), False, None,
                "Highland Staples (Native Potato, Andean Maize, Faba Bean, Quinoa, Barley)"
            )
            seasons["season_2"] = SeasonMetadata(
                2, "Winter Frost & Aridity Dormancy", s2_start, s2_end, len(s2_months),
                format_cyclic_window(s2_months), "FREEZE_DORMANCY",
                round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                round(min_tmin, 1), round(sum(monthly_rain[m] for m in s2_months), 1),
                True, f"Severe highland winter radiative frost down to {min_tmin:.1f}°C and aridity.",
                "Winter Frost Rest / Chuno Freeze-Drying"
            )
            seasons["season_3"] = SeasonMetadata(3, "None", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "None", "None")

        elif regime in ["MEDITERRANEAN_WINTER_RAIN", "MEDITERRANEAN_CONTINENTAL_STEPPE"]:
            def is_pluvial(m):
                return monthly_rain[m] >= 25.0 or (monthly_rain[m] / max(1.0, monthly_pet[m])) >= 0.35
            
            pref_start = 9 if hemisphere == "Northern" else 3
            wet_seq = []
            for i in range(12):
                m = (pref_start + i) % 12
                is_peak_summer = m in ([6, 7] if hemisphere == "Northern" else [0, 1])
                if not is_peak_summer and (is_pluvial(m) or len(wet_seq) < 6):
                    wet_seq.append(m)
                elif len(wet_seq) >= 6:
                    break
            
            s1_months = wet_seq
            s1_start, s1_end = get_run_start_end(s1_months)
            num_dry = 12 - len(s1_months)
            dry_months_cyclic = [(s1_end + 1 + i) % 12 for i in range(num_dry)]
            s2_dur = max(1, num_dry // 2)
            s2_months = dry_months_cyclic[:s2_dur]
            s3_months = dry_months_cyclic[s2_dur:]
            
            s2_start, s2_end = get_run_start_end(s2_months)
            s3_start, s3_end = get_run_start_end(s3_months)
            
            is_steppe = (regime == "MEDITERRANEAN_CONTINENTAL_STEPPE")
            seasons["season_1"] = SeasonMetadata(
                1, "Autumn-Sown Winter Cereal Season" if is_steppe else "Mild Pluvial Winter/Spring Season",
                s1_start, s1_end, len(s1_months), format_cyclic_window(s1_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1), round(min_tmin, 1),
                round(sum(monthly_rain[m] for m in s1_months), 1), False, None,
                "Primary Rainfed Winter Grain (Wheat, Barley, Chickpea)"
            )
            seasons["season_2"] = SeasonMetadata(
                2, "Early Summer Harvest / Stubble Rest", s2_start, s2_end, len(s2_months),
                format_cyclic_window(s2_months), "DROUGHT_DORMANCY",
                round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                round(min(monthly_tmin[m] for m in s2_months), 1),
                round(sum(monthly_rain[m] for m in s2_months), 1), True,
                "Rapid onset of Mediterranean summer drought.", "Post-Harvest Stubble Rest"
            )
            seasons["season_3"] = SeasonMetadata(
                3, "Summer Drought Fallow", s3_start, s3_end, len(s3_months),
                format_cyclic_window(s3_months), "DROUGHT_DORMANCY",
                round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1),
                round(min(monthly_tmin[m] for m in s3_months), 1),
                round(sum(monthly_rain[m] for m in s3_months), 1), True,
                "Severe summer moisture deficit (Rainfall < 25 mm, PET > 140 mm/month).", "Summer Drought Fallow"
            )

        elif regime == "SEMI_ARID_STEPPE":
            is_summer_dominant = (summer_rain >= winter_rain)
            if is_summer_dominant:
                if hemisphere == "Southern":
                    s1_months = [9, 10, 11, 0, 1, 2] # October - March (6 mo)
                    s2_months = [3, 4, 5, 6, 7, 8]    # April - September (6 mo)
                else:
                    s1_months = [4, 5, 6, 7, 8, 9]   # May - October (6 mo)
                    s2_months = [10, 11, 0, 1, 2, 3] # November - April (6 mo)
                s1_start, s1_end = get_run_start_end(s1_months)
                s2_start, s2_end = get_run_start_end(s2_months)
                frost_note = f" (Winter Tmin down to {min_tmin:.1f}°C)." if has_radiation_frost else "."
                seasons["season_1"] = SeasonMetadata(
                    1, "Summer Rainfed Grain & Oilseed Season", s1_start, s1_end, len(s1_months),
                    format_cyclic_window(s1_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1),
                    round(min(monthly_tmin[m] for m in s1_months), 1),
                    round(sum(monthly_rain[m] for m in s1_months), 1),
                    False, None, "Summer Cash & Staple Grains (Maize, Sunflower, Sorghum, Soybean, Cotton)"
                )
                seasons["season_2"] = SeasonMetadata(
                    2, "Winter Dryland Cold & Moisture Fallow", s2_start, s2_end, len(s2_months),
                    format_cyclic_window(s2_months), "DROUGHT_DORMANCY",
                    round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                    round(min(monthly_tmin[m] for m in s2_months), 1),
                    round(sum(monthly_rain[m] for m in s2_months), 1),
                    True, f"Winter dry season and cold thermal halt{frost_note}", "Winter Stubble Fallow / Frost Rest"
                )
                seasons["season_3"] = SeasonMetadata(3, "None", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "None", "None")
            else:
                # Winter-dominant steppe (Western Australia, Aragon)
                if hemisphere == "Southern":
                    s1_months = [4, 5, 6, 7, 8, 9, 10] # May - Nov (7 mo)
                else:
                    s1_months = [9, 10, 11, 0, 1, 2, 3, 4] # Oct - May (8 mo)
                dry_months = [m for m in range(12) if m not in s1_months]
                s2_dur = len(dry_months)
                s1_start, s1_end = get_run_start_end(s1_months)
                s2_start, s2_end = get_run_start_end(dry_months)
                seasons["season_1"] = SeasonMetadata(
                    1, "Cool-Season Rainfed Grain & Canola", s1_start, s1_end, len(s1_months),
                    format_cyclic_window(s1_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1),
                    round(min_tmin, 1), round(sum(monthly_rain[m] for m in s1_months), 1),
                    False, None, "Broadacre Winter Cereal & Oilseed (Wheat, Barley, Canola)"
                )
                seasons["season_2"] = SeasonMetadata(
                    2, "Summer Aridity & Extreme Heat Fallow", s2_start, s2_end, s2_dur,
                    format_cyclic_window(dry_months), "DROUGHT_DORMANCY",
                    round(sum(monthly_tmean[m] for m in dry_months)/s2_dur, 1),
                    round(min(monthly_tmin[m] for m in dry_months), 1),
                    round(sum(monthly_rain[m] for m in dry_months), 1), True,
                    "Summer heat and moisture deficit prevent rainfed summer crops.", "Summer Stubble Fallow"
                )
                seasons["season_3"] = SeasonMetadata(3, "None", 0, 0, 0, "None", "DROUGHT_DORMANCY", annual_tmean, min_tmin, 0.0, True, "None", "None")

        elif regime == "TEMPERATE_OCEANIC_MARITIME":
            if hemisphere == "Southern":
                growing_months = [9, 10, 11, 0, 1, 2, 3, 4] # October - May (8 mo)
            else:
                if monthly_tmean[2] >= 7.5:
                    growing_months = [2, 3, 4, 5, 6, 7, 8, 9, 10] # March - November (9 mo)
                else:
                    growing_months = [3, 4, 5, 6, 7, 8, 9, 10]    # April - November (8 mo)
                
            s1_start, s1_end = get_run_start_end(growing_months)
            num_off = 12 - len(growing_months)
            off_months_cyclic = [(s1_end + 1 + i) % 12 for i in range(num_off)]
            s2_dur = max(1, num_off // 2)
            s2_months = off_months_cyclic[:s2_dur]
            s3_months = off_months_cyclic[s2_dur:]
            
            s2_start, s2_end = get_run_start_end(s2_months)
            s3_start, s3_end = get_run_start_end(s3_months)
            
            seasons["season_1"] = SeasonMetadata(
                1, "Maritime Spring/Summer Growing Season", s1_start, s1_end, len(growing_months),
                format_cyclic_window(growing_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in growing_months)/len(growing_months), 1),
                round(min(monthly_tmin[m] for m in growing_months), 1),
                round(sum(monthly_rain[m] for m in growing_months), 1), False, None,
                "Cash Crops, Cereals & Forage (Wheat, Barley, Maize, Potato, Sugar Beet)"
            )
            seasons["season_2"] = SeasonMetadata(
                2, "Autumn/Early Winter Shoulder Rest", s2_start, s2_end, len(s2_months),
                format_cyclic_window(s2_months), "SHOULDER_SUCCESSION",
                round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                round(min(monthly_tmin[m] for m in s2_months), 1),
                round(sum(monthly_rain[m] for m in s2_months), 1), True,
                "Declining autumn photoperiod and temperatures.", "Post-Harvest Field Rest"
            )
            seasons["season_3"] = SeasonMetadata(
                3, "Cool Late Winter Rest", s3_start, s3_end, len(s3_months),
                format_cyclic_window(s3_months), "FREEZE_DORMANCY",
                round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1),
                round(min_tmin, 1), round(sum(monthly_rain[m] for m in s3_months), 1),
                True, "Low solar radiation and cool winter temperatures.", "Winter Rest"
            )

        elif regime == "TEMPERATE_CONTINENTAL_FROST":
            # Check for Huang-Huai-Hai / warm continental double-cropping (Winter Wheat + Summer Maize)
            can_temperate_double_crop = (
                annual_tmean >= 12.0 and lgp_days >= 170 and min_monthly_tmean >= -4.0
            )
            if can_temperate_double_crop:
                # Season 1: Summer grain anchor (June - September, 4 mo)
                s1_months = [5, 6, 7, 8]
                # Season 2: Overwintering cereal (October - May, 8 mo)
                s2_months = [9, 10, 11, 0, 1, 2, 3, 4]
                s1_start, s1_end = get_run_start_end(s1_months)
                s2_start, s2_end = get_run_start_end(s2_months)
                seasons["season_1"] = SeasonMetadata(
                    1, "Primary Summer Grain (Maize / Soybean / Peanut)", s1_start, s1_end, 4,
                    format_cyclic_window(s1_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s1_months)/4, 1),
                    round(min(monthly_tmin[m] for m in s1_months), 1),
                    round(sum(monthly_rain[m] for m in s1_months), 1), False, None,
                    "Intensive Summer Cash Crop (Corn, Soy, Peanut)"
                )
                seasons["season_2"] = SeasonMetadata(
                    2, "Overwintering Winter Grain (Wheat / Rapeseed)", s2_start, s2_end, 8,
                    format_cyclic_window(s2_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s2_months)/8, 1),
                    round(min_tmin, 1),
                    round(sum(monthly_rain[m] for m in s2_months), 1), False, None,
                    "Autumn-Sown Overwintering Grain with Winter Freeze Dormancy Pause"
                )
                seasons["season_3"] = SeasonMetadata(3, "None", 0, 0, 0, "None", "FREEZE_DORMANCY", annual_tmean, min_tmin, 0.0, True, "None", "None")
            else:
                freeze_months = [m for m in range(12) if is_freeze[m]]
                if not freeze_months: freeze_months = [11, 0, 1]
                non_freeze_months = [m for m in range(12) if m not in freeze_months]
                
                if len(non_freeze_months) <= 7:
                    s1_months = non_freeze_months
                    s2_months = []
                else:
                    s1_dur = min(7, len(non_freeze_months) - 1)
                    start_idx = 0
                    if hemisphere == "Northern":
                        while start_idx < len(non_freeze_months) - s1_dur and monthly_tmean[non_freeze_months[start_idx]] < 8.0:
                            start_idx += 1
                    s1_months = non_freeze_months[start_idx : start_idx + s1_dur]
                    s2_months = [m for m in non_freeze_months if m not in s1_months]
                    
                s1_start, s1_end = get_run_start_end(s1_months)
                s3_start, s3_end = get_run_start_end(freeze_months)
                
                seasons["season_1"] = SeasonMetadata(
                    1, "Primary Summer Growing Season", s1_start, s1_end, len(s1_months),
                    format_cyclic_window(s1_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1),
                    round(min(monthly_tmin[m] for m in s1_months), 1),
                    round(sum(monthly_rain[m] for m in s1_months), 1), False, None,
                    "Economic Anchor (Cash Crops & Staple Grains)"
                )
                if s2_months:
                    s2_start, s2_end = get_run_start_end(s2_months)
                    seasons["season_2"] = SeasonMetadata(
                        2, "Autumn Post-Harvest Shoulder Fallow", s2_start, s2_end, len(s2_months),
                        format_cyclic_window(s2_months), "SHOULDER_SUCCESSION",
                        round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                        round(min(monthly_tmin[m] for m in s2_months), 1),
                        round(sum(monthly_rain[m] for m in s2_months), 1), True,
                        "Late autumn temperature decline; field rest before ground freeze.", "Post-Harvest Stubble"
                    )
                else:
                    seasons["season_2"] = SeasonMetadata(2, "None", 0, 0, 0, "None", "SHOULDER_SUCCESSION", annual_tmean, min_tmin, 0.0, True, "None", "None")
                    
                seasons["season_3"] = SeasonMetadata(
                    3, "Winter Freeze Dormancy", s3_start, s3_end, len(freeze_months),
                    format_cyclic_window(freeze_months), "FREEZE_DORMANCY",
                    round(sum(monthly_tmean[m] for m in freeze_months)/len(freeze_months), 1),
                    round(min_tmin, 1), round(sum(monthly_rain[m] for m in freeze_months), 1),
                    True, f"Sub-zero ground frost and freezing air (Tmin down to {min_tmin:.1f}°C) halt plant cell division.", "Winter Biological Rest"
                )

        elif regime == "HUMID_SUBTROPICAL":
            if hemisphere == "Southern":
                summer_months = [9, 10, 11, 0, 1, 2] # October - March (6 mo)
                winter_months = [3, 4, 5, 6, 7, 8]   # April - September (6 mo)
            else:
                summer_months = [4, 5, 6, 7, 8, 9]   # May - October (6 mo)
                winter_months = [10, 11, 0, 1, 2, 3] # November - April (6 mo)
            
            s1_start, s1_end = get_run_start_end(summer_months)
            s2_start, s2_end = get_run_start_end(winter_months)
            
            is_k2 = (lgp_days >= 200 and sum(monthly_rain[m] for m in winter_months) >= 150.0)
            
            seasons["season_1"] = SeasonMetadata(
                1, "Subtropical Summer Growing Season", s1_start, s1_end, len(summer_months),
                format_cyclic_window(summer_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in summer_months)/len(summer_months), 1),
                round(min(monthly_tmin[m] for m in summer_months), 1),
                round(sum(monthly_rain[m] for m in summer_months), 1), False, None,
                "Economic Anchor (Soybean, Maize, Peanut, Cotton)"
            )
            seasons["season_2"] = SeasonMetadata(
                2, "Winter Small Grain / Cover Window" if is_k2 else "Winter Fallow",
                s2_start, s2_end, len(winter_months), format_cyclic_window(winter_months),
                "ACTIVE_GROWING" if is_k2 else "SHOULDER_SUCCESSION",
                round(sum(monthly_tmean[m] for m in winter_months)/len(winter_months), 1),
                round(min(monthly_tmin[m] for m in winter_months), 1),
                round(sum(monthly_rain[m] for m in winter_months), 1), (not is_k2),
                None if is_k2 else "Seasonal moisture deficit / GDD threshold.",
                "Winter Wheat / Cover Crop / Ryegrass" if is_k2 else "Winter Rest"
            )
            freeze_role = "Radiation Frost Pause" if has_radiation_frost else "None"
            seasons["season_3"] = SeasonMetadata(
                3, "Winter Radiation Frost Rest" if has_radiation_frost else "None",
                0, 0, 0, "None",
                "FREEZE_DORMANCY" if has_radiation_frost else "SHOULDER_SUCCESSION",
                annual_tmean, min_tmin, 0.0, True,
                f"Severe winter radiative frost down to {min_tmin:.1f}°C." if has_radiation_frost else "Subtropical 2-season rotation.",
                freeze_role
            )

        elif regime == "HUMID_TROPICAL_PERENNIAL":
            best_6 = []
            max_r6 = -1
            for start in range(12):
                block = [(start + i) % 12 for i in range(6)]
                r = sum(monthly_rain[m] for m in block)
                if r > max_r6:
                    max_r6 = r
                    best_6 = block
            s1_months = best_6
            s1_start, s1_end = get_run_start_end(s1_months)
            num_rem = 12 - len(s1_months)
            rem_cyclic = [(s1_end + 1 + i) % 12 for i in range(num_rem)]
            s2_months = rem_cyclic[:4]
            s3_months = rem_cyclic[4:]
            
            s2_start, s2_end = get_run_start_end(s2_months)
            s3_start, s3_end = get_run_start_end(s3_months)
            
            seasons["season_1"] = SeasonMetadata(
                1, "Primary Wet / Monsoon Season", s1_start, s1_end, 6,
                format_cyclic_window(s1_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in s1_months)/6, 1),
                round(min(monthly_tmin[m] for m in s1_months), 1),
                round(sum(monthly_rain[m] for m in s1_months), 1), False, None,
                "Primary Cash / Food Staple (Wet Rice, Soy, Sugarcane, Oil Palm)"
            )
            seasons["season_2"] = SeasonMetadata(
                2, "Secondary Succession Season", s2_start, s2_end, 4,
                format_cyclic_window(s2_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in s2_months)/4, 1),
                round(min(monthly_tmin[m] for m in s2_months), 1),
                round(sum(monthly_rain[m] for m in s2_months), 1), False, None,
                "Secondary Food / Palawija Rotation (Corn, Beans, Vegetables)"
            )
            seasons["season_3"] = SeasonMetadata(
                3, "Tertiary Inter-Monsoon Niche", s3_start, s3_end, 2,
                format_cyclic_window(s3_months), "SHOULDER_SUCCESSION",
                round(sum(monthly_tmean[m] for m in s3_months)/2, 1),
                round(min(monthly_tmin[m] for m in s3_months), 1),
                round(sum(monthly_rain[m] for m in s3_months), 1), True,
                "Brief soil aeration and aeration rest.", "Short Green Manure / Catch Rest"
            )

        elif regime == "TROPICAL_BIMODAL_RAIN":
            peak1 = max(range(12), key=lambda m: monthly_rain[m])
            candidates = [m for m in range(12) if min(abs(m - peak1), 12 - abs(m - peak1)) >= 3]
            peak2 = max(candidates, key=lambda m: monthly_rain[m]) if candidates else (peak1 + 6) % 12
            p1_months = [(peak1 - 1) % 12, peak1, (peak1 + 1) % 12]
            p2_months = [(peak2 - 1) % 12, peak2, (peak2 + 1) % 12]
            dry_months = [m for m in range(12) if m not in p1_months and m not in p2_months]
            
            p1_start, p1_end = get_run_start_end(p1_months)
            p2_start, p2_end = get_run_start_end(p2_months)
            dry_start, dry_end = get_run_start_end(dry_months)
            
            seasons["season_1"] = SeasonMetadata(
                1, "Primary Wet Season (Long Rains)", p1_start, p1_end, len(p1_months),
                format_cyclic_window(p1_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in p1_months)/len(p1_months), 1),
                round(min(monthly_tmin[m] for m in p1_months), 1),
                round(sum(monthly_rain[m] for m in p1_months), 1), False, None,
                "Primary Cash & Staple Grains (Long Rains Anchor)"
            )
            seasons["season_2"] = SeasonMetadata(
                2, "Secondary Wet Season (Short Rains)", p2_start, p2_end, len(p2_months),
                format_cyclic_window(p2_months), "ACTIVE_GROWING",
                round(sum(monthly_tmean[m] for m in p2_months)/len(p2_months), 1),
                round(min(monthly_tmin[m] for m in p2_months), 1),
                round(sum(monthly_rain[m] for m in p2_months), 1), False, None,
                "Secondary Food Security & Legumes (Short Rains)"
            )
            seasons["season_3"] = SeasonMetadata(
                3, "Dry Interval / Inter-Monsoon Niche", dry_start, dry_end, len(dry_months),
                format_cyclic_window(dry_months), "DROUGHT_DORMANCY",
                round(sum(monthly_tmean[m] for m in dry_months)/len(dry_months), 1),
                round(min(monthly_tmin[m] for m in dry_months), 1),
                round(sum(monthly_rain[m] for m in dry_months), 1), True,
                "Dry inter-season dry spell with low soil moisture storage.", "Dry Season Pasture / Field Rest"
            )

        else: # TROPICAL_MONOMODAL_RAIN
            best_wet = []
            for start in range(12):
                block = []
                for i in range(12):
                    m = (start + i) % 12
                    if monthly_rain[m] >= 50.0:
                        block.append(m)
                    else:
                        break
                if len(block) > len(best_wet):
                    best_wet = block
            if not best_wet:
                best_wet = sorted(range(12), key=lambda m: monthly_rain[m], reverse=True)[:4]
                
            wet_months = best_wet
            dry_months = [m for m in range(12) if m not in wet_months]
            
            # Cerrado / High-LGP Intra-Monsoon Splitting (e.g. Mato Grosso, Goias, Parakou, Sikasso)
            if len(wet_months) >= 6 and lgp_days >= 210:
                safra_dur = 4
                safrinha_dur = min(4, len(wet_months) - safra_dur + 1)
                s1_months = wet_months[:safra_dur]
                s2_months = [(wet_months[safra_dur - 1] + 1 + i) % 12 for i in range(safrinha_dur)]
                s2_months = [m for m in s2_months if m not in s1_months]
                fallow_months = [m for m in range(12) if m not in s1_months and m not in s2_months]
                
                s1_start, s1_end = get_run_start_end(s1_months)
                s2_start, s2_end = get_run_start_end(s2_months)
                s3_start, s3_end = get_run_start_end(fallow_months)
                
                is_south_asia = (0.0 <= lat <= 35.0 and 60.0 <= lon <= 95.0)
                is_brazil = (-35.0 <= lat <= 5.0 and -75.0 <= lon <= -34.0)
                
                if is_south_asia:
                    s1_name = "Primary Kharif / Monsoon Season"
                    s1_role = "Primary Monsoon Crop (Paddy Rice, Soybean, Maize, Cotton)"
                    s2_name = "Secondary Rabi / Post-Monsoon Season"
                    s2_role = "Rabi Succession on Residual Moisture (Chickpea, Mustard, Lentil, Wheat)"
                    s3_name = "Zaid / Hot Pre-Monsoon Fallow"
                    s3_role = "Hot Dry Season Field Rest / Land Prep"
                    s3_reason = "Extreme summer heat and moisture deficit before monsoon arrival."
                elif is_brazil:
                    s1_name = "Primary Wet Season (Safra / Summer Anchor)"
                    s1_role = "Primary Cash Crop (Soybean, Full-Season Maize, Cotton)"
                    s2_name = "Secondary Wet Season (Safrinha / Succession)"
                    s2_role = "Succession Grain / Pulse on Residual Moisture (Safrinha Corn, Sorghum, Cowpea)"
                    s3_name = "Dry Season Fallow / Vazio Sanitario"
                    s3_role = "Sanitary Fallow / Field Rest"
                    s3_reason = "Mandatory sanitary break / severe dry-season soil moisture deficit."
                else:
                    s1_name = "Primary Monsoonal Wet Season"
                    s1_role = "Primary Cash / Food Anchor (Maize, Yam, Groundnut, Cotton)"
                    s2_name = "Secondary Post-Monsoon Succession Season"
                    s2_role = "Residual Moisture / Short Pulses"
                    s3_name = "Dry Season Fallow / Field Rest"
                    s3_role = "Dry Season Pasture / Field Rest"
                    s3_reason = "Dry inter-season spell with low soil moisture storage."

                seasons["season_1"] = SeasonMetadata(
                    1, s1_name, s1_start, s1_end, len(s1_months),
                    format_cyclic_window(s1_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s1_months)/len(s1_months), 1),
                    round(min(monthly_tmin[m] for m in s1_months), 1),
                    round(sum(monthly_rain[m] for m in s1_months), 1), False, None,
                    s1_role
                )
                seasons["season_2"] = SeasonMetadata(
                    2, s2_name, s2_start, s2_end, len(s2_months),
                    format_cyclic_window(s2_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                    round(min(monthly_tmin[m] for m in s2_months), 1),
                    round(sum(monthly_rain[m] for m in s2_months), 1), False, None,
                    s2_role
                )
                seasons["season_3"] = SeasonMetadata(
                    3, s3_name, s3_start, s3_end, len(fallow_months),
                    format_cyclic_window(fallow_months), "DROUGHT_DORMANCY",
                    round(sum(monthly_tmean[m] for m in fallow_months)/len(fallow_months), 1),
                    round(min(monthly_tmin[m] for m in fallow_months), 1),
                    round(sum(monthly_rain[m] for m in fallow_months), 1), True,
                    s3_reason, s3_role
                )
            else:
                candidate_s2 = dry_months[:3] if len(dry_months) >= 3 else dry_months
                candidate_s2_rain = sum(monthly_rain[m] for m in candidate_s2)
                can_double_crop = (candidate_s2_rain >= 75.0 and lgp_days >= 200)
                
                s1_start, s1_end = get_run_start_end(wet_months)
                seasons["season_1"] = SeasonMetadata(
                    1, "Primary Monsoonal Wet Season", s1_start, s1_end, len(wet_months),
                    format_cyclic_window(wet_months), "ACTIVE_GROWING",
                    round(sum(monthly_tmean[m] for m in wet_months)/len(wet_months), 1),
                    round(min(monthly_tmin[m] for m in wet_months), 1),
                    round(sum(monthly_rain[m] for m in wet_months), 1), False, None,
                    "Primary Rainfed Anchor (Millets, Sorghum, Cowpea, Rice, Groundnut)"
                )
                if can_double_crop:
                    s2_months = candidate_s2
                    s3_months = [m for m in dry_months if m not in s2_months]
                    s2_start, s2_end = get_run_start_end(s2_months)
                    s3_start, s3_end = get_run_start_end(s3_months)
                    seasons["season_2"] = SeasonMetadata(
                        2, "Post-Monsoon Residual Moisture Season", s2_start, s2_end, len(s2_months),
                        format_cyclic_window(s2_months), "ACTIVE_GROWING",
                        round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                        round(min(monthly_tmin[m] for m in s2_months), 1),
                        round(sum(monthly_rain[m] for m in s2_months), 1), False, None,
                        "Residual Soil Moisture / Short Pulses"
                    )
                    seasons["season_3"] = SeasonMetadata(
                        3, "Late Dry Season Fallow", s3_start, s3_end, len(s3_months),
                        format_cyclic_window(s3_months), "DROUGHT_DORMANCY",
                        round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1),
                        round(min(monthly_tmin[m] for m in s3_months), 1),
                        round(sum(monthly_rain[m] for m in s3_months), 1), True,
                        "Peak dry season before monsoon arrival.", "Land Prep & Tillage"
                    )
                else:
                    num_dry = 12 - len(wet_months)
                    dry_months_cyclic = [(s1_end + 1 + i) % 12 for i in range(num_dry)]
                    s2_dur = max(1, num_dry // 2)
                    s2_months = dry_months_cyclic[:s2_dur]
                    s3_months = dry_months_cyclic[s2_dur:]
                    s2_start, s2_end = get_run_start_end(s2_months)
                    s3_start, s3_end = get_run_start_end(s3_months)
                    seasons["season_2"] = SeasonMetadata(
                        2, "Post-Harvest Dry Season Rest", s2_start, s2_end, len(s2_months),
                        format_cyclic_window(s2_months), "DROUGHT_DORMANCY",
                        round(sum(monthly_tmean[m] for m in s2_months)/len(s2_months), 1),
                        round(min(monthly_tmin[m] for m in s2_months), 1),
                        round(sum(monthly_rain[m] for m in s2_months), 1), True,
                        "Post-monsoon dryland moisture depletion.", "Field Rest / Stubble Grazing"
                    )
                    seasons["season_3"] = SeasonMetadata(
                        3, "Late Dry Season / Pre-Monsoon Fallow", s3_start, s3_end, len(s3_months),
                        format_cyclic_window(s3_months), "DROUGHT_DORMANCY",
                        round(sum(monthly_tmean[m] for m in s3_months)/len(s3_months), 1),
                        round(min(monthly_tmin[m] for m in s3_months), 1),
                        round(sum(monthly_rain[m] for m in s3_months), 1), True,
                        "Peak dry season before monsoon arrival.", "Land Prep & Tillage"
                    )

        # -------------------------------------------------------------
        # 3. Synchronize Intensity K and Guarantee 12-Month Conservation
        # -------------------------------------------------------------
        actual_k = sum(1 for s in seasons.values() if not s.is_fallow)
        cropping_intensity_k = actual_k
        
        total_months = sum(s.duration_months for s in seasons.values())
        assert total_months == 12, f"Month conservation violated: sum={total_months} for lat={lat}, lon={lon}"

        return AgroClimaticCalendar(
            lat, lon, hemisphere, regime,
            round(annual_rain, 1), round(annual_tmean, 1),
            cropping_intensity_k, lgp_days, seasons
        )
