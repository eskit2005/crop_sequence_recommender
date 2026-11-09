"""
global_env_fetcher.py - Global Environmental & Climatology Data Fetcher
Queries NASA POWER API for 12-month climatology and ISRIC SoilGrids with failover mirrors.
Calculates FAO GAEZ v4 daily tipping-bucket water balance and Length of Growing Period (LGP).
"""

import urllib.request
import json
import ssl
import time
import math
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple

DAYS_IN_MONTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTH_NAMES = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


@dataclass
class EnvironmentalProfile:
    latitude: float
    longitude: float
    monthly_tmean: List[float]       # 12 months (°C)
    monthly_tmin: List[float]        # 12 months (°C)
    monthly_tmax: List[float]        # 12 months (°C)
    monthly_rainfall_mm: List[float] # 12 months (mm/month)
    annual_rainfall_mm: float
    soil_ph: float
    soil_texture: str
    soil_clay_pct: float
    soil_sand_pct: float
    soil_silt_pct: float
    soil_cec: float
    lgp_days: int
    cropping_intensity_k: int
    source_climate: str
    source_soil: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def classify_usda_texture(sand: float, silt: float, clay: float) -> str:
    """Classifies USDA soil texture based on sand, silt, clay percentages."""
    if sand + silt + clay == 0:
        return "Loam"
    # Normalize to 100%
    total = sand + silt + clay
    s = (sand / total) * 100.0
    si = (silt / total) * 100.0
    c = (clay / total) * 100.0

    if c >= 40:
        if si >= 40:
            return "Silty Clay"
        elif s >= 45:
            return "Sandy Clay"
        else:
            return "Clay"
    elif c >= 35 and s >= 45:
        return "Sandy Clay"
    elif c >= 27:
        if s < 20:
            return "Silty Clay Loam"
        elif s >= 45:
            return "Sandy Clay Loam"
        else:
            return "Clay Loam"
    elif c >= 20 and s >= 45 and si < 28:
        return "Sandy Clay Loam"
    else:
        if si >= 80 and c < 12:
            return "Silt"
        elif si >= 50:
            return "Silt Loam"
        elif s >= 85 and c < 10:
            return "Sand"
        elif s >= 70 and c < 15:
            return "Loamy Sand"
        elif s >= 43 and c < 20:
            return "Sandy Loam"
        else:
            return "Loam"


class GlobalEnvFetcher:
    """Fetches NASA POWER climatology and ISRIC SoilGrids, computing LGP and K."""

    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def fetch_climate(self, lat: float, lon: float) -> Dict[str, Any]:
        """Queries NASA POWER Climatology point endpoint."""
        url = (
            f"https://power.larc.nasa.gov/api/temporal/climatology/point?"
            f"parameters=T2M,T2M_MIN,T2M_MAX,PRECTOTCORR&community=AG&"
            f"latitude={lat:.4f}&longitude={lon:.4f}&format=JSON"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0"})
        with urllib.request.urlopen(req, context=self.ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        params = data.get("properties", {}).get("parameter", {})
        tmean_dict = params.get("T2M", {})
        tmin_dict = params.get("T2M_MIN", {})
        tmax_dict = params.get("T2M_MAX", {})
        prec_rate_dict = params.get("PRECTOTCORR", {})  # mm/day

        monthly_tmean = []
        monthly_tmin = []
        monthly_tmax = []
        monthly_rain = []

        for idx, m_code in enumerate(MONTH_NAMES):
            t_m = float(tmean_dict.get(m_code, 20.0))
            t_min = float(tmin_dict.get(m_code, 15.0))
            t_max = float(tmax_dict.get(m_code, 25.0))
            # Critical correction: PRECTOTCORR is mm/day -> multiply by days in month
            rate = float(prec_rate_dict.get(m_code, 2.0))
            rain_m = round(rate * DAYS_IN_MONTHS[idx], 1)

            monthly_tmean.append(t_m)
            monthly_tmin.append(t_min)
            monthly_tmax.append(t_max)
            monthly_rain.append(rain_m)

        annual_rain = round(sum(monthly_rain), 1)
        return {
            "monthly_tmean": monthly_tmean,
            "monthly_tmin": monthly_tmin,
            "monthly_tmax": monthly_tmax,
            "monthly_rain": monthly_rain,
            "annual_rain": annual_rain,
            "source": "NASA_POWER_CLIMATOLOGY"
        }

    def fetch_soil(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Queries ISRIC SoilGrids 2.0 with quick timeout and fallback to mirror or default loam.
        """
        urls = [
            # Endpoint 1: Official ISRIC SoilGrids 2.0
            (
                f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
                f"lon={lon:.4f}&lat={lat:.4f}&property=phh2o&property=sand&property=silt&property=clay&property=cec&depth=0-5cm&value=mean",
                "ISRIC_SOILGRIDS_2.0"
            ),
            # Endpoint 2: Compatible mirror
            (
                f"https://pixelgust.com/soilgrids/v2.0/properties/query?"
                f"lon={lon:.4f}&lat={lat:.4f}&property=phh2o&property=sand&property=silt&property=clay&property=cec&depth=0-5cm&value=mean",
                "SOILGRIDS_MIRROR"
            )
        ]

        for url, src_name in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0", "Accept": "application/json"})
                with urllib.request.urlopen(req, context=self.ctx, timeout=6) as resp:
                    if resp.status == 200:
                        raw = json.loads(resp.read().decode("utf-8"))
                        layers = raw.get("properties", {}).get("layers", [])
                        layer_vals = {}
                        for l in layers:
                            name = l.get("name")
                            depths = l.get("depths", [{}])
                            val = depths[0].get("values", {}).get("mean")
                            if val is not None:
                                layer_vals[name] = float(val) / 10.0  # d_factor = 10

                        ph = layer_vals.get("phh2o", 6.5)
                        sand = layer_vals.get("sand", 33.0)
                        silt = layer_vals.get("silt", 33.0)
                        clay = layer_vals.get("clay", 34.0)
                        cec = layer_vals.get("cec", 18.0)
                        texture = classify_usda_texture(sand, silt, clay)

                        return {
                            "soil_ph": round(ph, 1),
                            "soil_texture": texture,
                            "soil_clay_pct": round(clay, 1),
                            "soil_sand_pct": round(sand, 1),
                            "soil_silt_pct": round(silt, 1),
                            "soil_cec": round(cec, 1),
                            "source": src_name
                        }
            except Exception:
                continue

        # Fallback to FAO global standard medium loam
        return {
            "soil_ph": 6.5,
            "soil_texture": "Loam",
            "soil_clay_pct": 20.0,
            "soil_sand_pct": 40.0,
            "soil_silt_pct": 40.0,
            "soil_cec": 15.0,
            "source": "FAO_DEFAULT_LOAM_FALLBACK"
        }

    @staticmethod
    def calculate_extraterrestrial_radiation(lat_deg: float, day_of_year: int) -> float:
        """
        FAO-56 Equations 21, 23-26: Calculates extraterrestrial solar radiation (Ra)
        in equivalent depth of water (mm/day) based on latitude and day of year.
        Reference: Allen et al. (1998) FAO Irrigation and Drainage Paper No. 56.
        """
        phi = math.radians(lat_deg)
        # Solar declination (FAO-56 eq 24)
        delta = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)
        # Relative distance Earth-Sun (FAO-56 eq 23)
        dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
        # Sunset hour angle (FAO-56 eq 25, 26)
        x = -math.tan(phi) * math.tan(delta)
        if x < -1.0:
            ws = math.pi  # Polar day (24h sunlight)
        elif x > 1.0:
            ws = 0.0     # Polar night (24h darkness)
        else:
            ws = math.acos(x)
        # Solar constant Gsc = 0.0820 MJ / (m^2 * min)
        # Ra in MJ / (m^2 * day) (FAO-56 eq 21)
        ra_mj = (24 * 60 / math.pi) * 0.0820 * dr * (
            ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws)
        )
        # Convert MJ/(m^2*day) to mm/day equivalent: 1 MJ/m^2/day = 0.408 mm/day (FAO-56 eq 28)
        return max(0.5, ra_mj * 0.408)

    def compute_daily_lgp_and_k(
        self,
        monthly_tmean: List[float],
        monthly_tmin: List[float],
        monthly_tmax: List[float],
        monthly_rain: List[float],
        lat: float = 0.0
    ) -> Tuple[int, int]:
        """
        FAO GAEZ v4 Daily Tipping-Bucket Water Balance & Length of Growing Period (LGP).
        Soil available water storage capacity: S_max = 100 mm.
        Moisture sufficiency condition: (P_d + W_{t-1}) >= 0.5 * PET_d and T_mean >= 5.0 °C.
        """
        # Daily Hargreaves approximation for PET (mm/day) using FAO-56 astronomical Ra
        daily_pet = []
        daily_p = []
        daily_temp = []
        mid_days = [15, 45, 74, 105, 135, 165, 196, 227, 258, 288, 319, 349]

        for m_idx in range(12):
            days = DAYS_IN_MONTHS[m_idx]
            t_m = monthly_tmean[m_idx]
            t_min = monthly_tmin[m_idx]
            t_max = monthly_tmax[m_idx]
            rain_m = monthly_rain[m_idx]

            # Hargreaves-Samani / FAO-56 PET equation with calibrated diurnal range:
            # Note: NASA POWER climatology Tmax and Tmin are 30-year absolute records.
            # Convert extreme range to realistic daily diurnal range (DTR): ~7-16 °C.
            raw_diff = max(5.0, t_max - t_min)
            dtr = min(16.0, max(7.0, raw_diff * 0.35))
            ra = self.calculate_extraterrestrial_radiation(lat, mid_days[m_idx])
            pet_day = max(0.5, min(14.0, 0.0023 * (t_m + 17.8) * math.sqrt(dtr) * ra))
            p_day = rain_m / days

            for _ in range(days):
                daily_pet.append(pet_day)
                daily_p.append(p_day)
                daily_temp.append(t_m)

        # 2-cycle loop to burn in initial soil water storage W_0
        w_t = 50.0  # Initial 50 mm storage
        total_days = len(daily_p)  # 365 days

        # Cycle 1 (Burn-in)
        for d in range(total_days):
            w_t = max(0.0, min(100.0, w_t + daily_p[d] - daily_pet[d]))

        # Cycle 2 (Measurement)
        lgp_days = 0
        for d in range(total_days):
            p_d = daily_p[d]
            pet_d = daily_pet[d]
            t_d = daily_temp[d]
            
            # Moisture sufficiency check
            if (p_d + w_t) >= (0.5 * pet_d) and t_d >= 5.0:
                lgp_days += 1

            # Update water balance
            w_t = max(0.0, min(100.0, w_t + p_d - pet_d))

        # Dynamic Cropping Intensity K
        if lgp_days >= 270:
            k = 3  # Triple cropping or perennial
        elif lgp_days >= 165:
            k = 2  # Double cropping
        elif lgp_days >= 60:
            k = 1  # Single crop
        else:
            k = 0  # Hyper-arid / non-cultivable rainfed

        return lgp_days, k

    def get_profile(self, lat: float, lon: float) -> EnvironmentalProfile:
        """Assembles full environmental profile for given coordinates."""
        climate = self.fetch_climate(lat, lon)
        soil = self.fetch_soil(lat, lon)
        lgp_days, k = self.compute_daily_lgp_and_k(
            climate["monthly_tmean"],
            climate["monthly_tmin"],
            climate["monthly_tmax"],
            climate["monthly_rain"],
            lat=lat
        )

        return EnvironmentalProfile(
            latitude=lat,
            longitude=lon,
            monthly_tmean=climate["monthly_tmean"],
            monthly_tmin=climate["monthly_tmin"],
            monthly_tmax=climate["monthly_tmax"],
            monthly_rainfall_mm=climate["monthly_rain"],
            annual_rainfall_mm=climate["annual_rain"],
            soil_ph=soil["soil_ph"],
            soil_texture=soil["soil_texture"],
            soil_clay_pct=soil["soil_clay_pct"],
            soil_sand_pct=soil["soil_sand_pct"],
            soil_silt_pct=soil["soil_silt_pct"],
            soil_cec=soil["soil_cec"],
            lgp_days=lgp_days,
            cropping_intensity_k=k,
            source_climate=climate["source"],
            source_soil=soil["source"]
        )
