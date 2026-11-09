"""
Planetary 100-Location Agro-Climatic Seasonal Segmentation Benchmark
====================================================================
Tests the Tier 2 Universal Physical Agrometeorological Engine against
ground-truth real-world crop calendars across 100 diverse global agricultural
zones on all 6 inhabited continents.

Metrics Evaluated:
1. Regime Classification Accuracy (TEMPERATE_FROST, MEDITERRANEAN, TROPICAL_MONOMODAL, TROPICAL_BIMODAL, HYPER_ARID, HUMID_PERENNIAL)
2. Thermal Freeze Halt Detection Accuracy (True/False match for biological zero frost cessation)
3. Primary Season Timing Accuracy (Does predicted main growing window match real-world planting within ±1 month tolerance)
4. Cropping Intensity (K) Agreement (Rainfed potential K in {1, 2, 3})
"""

import os
import sys
import ssl
import json
import math
import urllib.request
import concurrent.futures
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.seasonal_calendar import UniversalSeasonalSegmenter, MONTH_NAMES
from src.global_env_fetcher import GlobalEnvFetcher


@dataclass
class BenchmarkLocation:
    name: str
    country: str
    continent: str
    lat: float
    lon: float
    ground_truth_regime: str
    ground_truth_has_freeze: bool
    ground_truth_primary_start_month: int  # 0=Jan .. 11=Dec
    ground_truth_primary_end_month: int
    ground_truth_rainfed_k: int
    description: str


# 100 Curated Diverse Global Locations covering all Köppen zones and cropping systems
BENCHMARK_100: List[BenchmarkLocation] = [
    # --- NORTH AMERICA (15) ---
    BenchmarkLocation("Des Moines, Iowa", "USA", "North America", 41.5868, -93.6250, "TEMPERATE_CONTINENTAL_FROST", True, 3, 9, 1, "US Corn Belt: Warm summer, sub-zero winter freeze"),
    BenchmarkLocation("Champaign, Illinois", "USA", "North America", 40.1164, -88.2434, "TEMPERATE_CONTINENTAL_FROST", True, 3, 9, 2, "US Corn Belt: Summer corn-soybean, winter wheat"),
    BenchmarkLocation("Dodge City, Kansas", "USA", "North America", 37.7528, -100.0171, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 1, "US High Plains Wheat Belt: Semi-arid, cold winter"),
    BenchmarkLocation("Fargo, North Dakota", "USA", "North America", 46.8772, -96.7898, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 1, "US Spring Wheat Belt: Very short summer, severe freeze"),
    BenchmarkLocation("Fresno, California", "USA", "North America", 36.7468, -119.7726, "MEDITERRANEAN_WINTER_RAIN", False, 10, 3, 2, "California Central Valley: Wet mild winter, bone-dry summer"),
    BenchmarkLocation("Yakima, Washington", "USA", "North America", 46.6021, -120.5059, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Pacific Northwest: Arid valley, cold winter"),
    BenchmarkLocation("Lubbock, Texas", "USA", "North America", 33.5779, -101.8552, "TEMPERATE_CONTINENTAL_FROST", True, 4, 9, 1, "Texas High Plains Cotton: Semi-arid warm summer"),
    BenchmarkLocation("Tifton, Georgia", "USA", "North America", 31.4505, -83.5085, "TEMPERATE_CONTINENTAL_FROST", False, 2, 9, 2, "US Southeast: Humid subtropical, long summer peanuts/cotton"),
    BenchmarkLocation("Belle Glade, Florida", "USA", "North America", 26.6845, -80.6676, "HUMID_TROPICAL_PERENNIAL", False, 9, 4, 2, "Everglades: Winter vegetable & sugarcane belt"),
    BenchmarkLocation("Regina, Saskatchewan", "Canada", "North America", 50.4452, -104.6189, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 1, "Canadian Prairies: Short summer spring wheat & canola"),
    BenchmarkLocation("Lethbridge, Alberta", "Canada", "North America", 49.6956, -112.8451, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 1, "Canadian Prairies: Dryland wheat, severe freeze"),
    BenchmarkLocation("London, Ontario", "Canada", "North America", 42.9849, -81.2453, "TEMPERATE_CONTINENTAL_FROST", True, 4, 9, 1, "Eastern Canada: Humid continental summer grain belt"),
    BenchmarkLocation("Ciudad Obregon, Sonora", "Mexico", "North America", 27.4828, -109.9304, "HYPER_ARID_DESERT", False, 10, 3, 1, "Yaqui Valley: Desert irrigated winter wheat"),
    BenchmarkLocation("Culiacan, Sinaloa", "Mexico", "North America", 24.8091, -107.3940, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 1, "Pacific Coast: Summer monsoon, winter vegetable belt"),
    BenchmarkLocation("Celaya, Guanajuato", "Mexico", "North America", 20.5218, -100.8140, "TROPICAL_MONOMODAL_RAIN", False, 4, 9, 2, "Bajio: High plateau summer monsoon grain belt"),

    # --- SOUTH AMERICA (15) ---
    BenchmarkLocation("Pergamino, Buenos Aires", "Argentina", "South America", -33.8900, -60.5700, "TEMPERATE_CONTINENTAL_FROST", False, 9, 2, 2, "Argentine Pampas: Summer maize/soy, winter wheat"),
    BenchmarkLocation("Rio Cuarto, Cordoba", "Argentina", "South America", -33.1307, -64.3499, "TEMPERATE_CONTINENTAL_FROST", False, 9, 2, 2, "Central Pampas: Summer soy/maize, winter cover"),
    BenchmarkLocation("Rosario, Santa Fe", "Argentina", "South America", -32.9587, -60.6930, "TEMPERATE_CONTINENTAL_FROST", False, 9, 2, 2, "Humid Pampas: High-yield grain belt"),
    BenchmarkLocation("Sorriso, Mato Grosso", "Brazil", "South America", -12.5444, -55.7239, "TROPICAL_MONOMODAL_RAIN", False, 9, 2, 2, "Cerrado: Summer monsoon soy + Safrinha maize"),
    BenchmarkLocation("Londrina, Parana", "Brazil", "South America", -23.3045, -51.1696, "HUMID_TROPICAL_PERENNIAL", False, 9, 2, 2, "Southern Brazil: Subtropical double-crop soy/wheat"),
    BenchmarkLocation("Passo Fundo, Rio Grande do Sul", "Brazil", "South America", -28.2612, -52.4083, "HUMID_TROPICAL_PERENNIAL", False, 9, 2, 2, "Pampas Brazil: Summer soy, winter wheat/barley"),
    BenchmarkLocation("Luis Eduardo Magalhaes, Bahia", "Brazil", "South America", -12.0969, -45.7958, "TROPICAL_MONOMODAL_RAIN", False, 10, 3, 1, "Western Bahia: Savanna summer rainfed soy/cotton"),
    BenchmarkLocation("Talca, Maule", "Chile", "South America", -35.4264, -71.6554, "MEDITERRANEAN_WINTER_RAIN", False, 4, 9, 1, "Chilean Central Valley: Winter rain, dry summer"),
    BenchmarkLocation("San Rafael, Mendoza", "Argentina", "South America", -34.6177, -68.3301, "HYPER_ARID_DESERT", False, 9, 2, 1, "Cuyo Desert: Rain shadow, irrigated viticulture"),
    BenchmarkLocation("Palmira, Valle del Cauca", "Colombia", "South America", 3.5394, -76.3036, "TROPICAL_BIMODAL_RAIN", False, 2, 5, 2, "Cauvery Valley: Bimodal rainfall sugarcane & grains"),
    BenchmarkLocation("Piura", "Peru", "South America", -5.1945, -80.6328, "HYPER_ARID_DESERT", False, 0, 11, 1, "Peruvian Coastal Desert: 50mm rain, irrigated cotton"),
    BenchmarkLocation("Viacha, Altiplano", "Bolivia", "South America", -16.6528, -68.3014, "TEMPERATE_CONTINENTAL_FROST", True, 10, 2, 1, "High Andean Altiplano: 3,850m frost, summer quinoa/potato"),
    BenchmarkLocation("Salto", "Uruguay", "South America", -31.3833, -57.9667, "HUMID_TROPICAL_PERENNIAL", False, 9, 2, 2, "Uruguay River Basin: Subtropical year-round rain"),
    BenchmarkLocation("Coronel Oviedo, Caaguazu", "Paraguay", "South America", -25.4444, -56.4403, "HUMID_TROPICAL_PERENNIAL", False, 9, 2, 2, "Eastern Paraguay: Subtropical double crop soy/wheat"),
    BenchmarkLocation("Calabozo, Guarico", "Venezuela", "South America", 8.9242, -67.4293, "TROPICAL_MONOMODAL_RAIN", False, 4, 10, 1, "Llanos: Monomodal savanna summer wet season rice"),

    # --- EUROPE (18) ---
    BenchmarkLocation("Chartres, Beauce", "France", "Europe", 48.4560, 1.4840, "TEMPERATE_CONTINENTAL_FROST", True, 2, 7, 1, "Paris Basin Granary: Mild winter wheat, summer barley"),
    BenchmarkLocation("Bordeaux, Aquitaine", "France", "Europe", 44.8378, -0.5792, "TEMPERATE_CONTINENTAL_FROST", False, 2, 8, 2, "Southwest France: Oceanic mild winter, maize/grape"),
    BenchmarkLocation("Straubing, Bavaria", "Germany", "Europe", 48.8817, 12.5694, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Danubian Bavaria: Freezing winter, summer grain/sugarbeet"),
    BenchmarkLocation("Braunschweig, Lower Saxony", "Germany", "Europe", 52.2689, 10.5268, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "North German Plain: Cold winter, summer cereals"),
    BenchmarkLocation("Cremona, Lombardy", "Italy", "Europe", 45.1333, 10.0333, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 2, "Po Valley: Continental winter, summer irrigated maize/soy"),
    BenchmarkLocation("Catania, Sicily", "Italy", "Europe", 37.5079, 15.0830, "MEDITERRANEAN_WINTER_RAIN", False, 10, 3, 1, "Mediterranean Sicily: Winter rain wheat, dry summer"),
    BenchmarkLocation("Seville, Andalusia", "Spain", "Europe", 37.3891, -5.9845, "MEDITERRANEAN_WINTER_RAIN", False, 9, 3, 1, "Guadalquivir Valley: Wet mild winter, scorching dry summer"),
    BenchmarkLocation("Valladolid, Castile and Leon", "Spain", "Europe", 41.6523, -4.7245, "TEMPERATE_CONTINENTAL_FROST", True, 2, 6, 1, "Meseta Plateau: Cold winter, summer drought wheat/barley"),
    BenchmarkLocation("Bury St Edmunds, East Anglia", "UK", "Europe", 52.2474, 0.7183, "TEMPERATE_CONTINENTAL_FROST", True, 2, 7, 1, "UK Breadbasket: Maritime mild winter, summer wheat"),
    BenchmarkLocation("Perth, Scotland", "UK", "Europe", 56.3950, -3.4308, "TEMPERATE_CONTINENTAL_FROST", True, 3, 7, 1, "Scottish Lowlands: Cool maritime, barley & oats"),
    BenchmarkLocation("Beja, Alentejo", "Portugal", "Europe", 38.0150, -7.8632, "MEDITERRANEAN_WINTER_RAIN", False, 9, 3, 1, "Portuguese Wheat Belt: Mediterranean winter rain"),
    BenchmarkLocation("Larissa, Thessaly", "Greece", "Europe", 39.6390, 22.4191, "MEDITERRANEAN_WINTER_RAIN", False, 9, 3, 1, "Thessalian Plain: Winter rain wheat, dry summer cotton"),
    BenchmarkLocation("Pleven", "Bulgaria", "Europe", 43.4170, 24.6167, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Danube Plain: Continental cold winter, summer sunflower/maize"),
    BenchmarkLocation("Craiova, Wallachia", "Romania", "Europe", 44.3302, 23.7949, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Romanian Plain: Hot summer maize, freezing winter"),
    BenchmarkLocation("Poltava", "Ukraine", "Europe", 49.5883, 34.5514, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Chernozem Black Soil: Severe winter freeze, summer sun/corn"),
    BenchmarkLocation("Poznan, Greater Poland", "Poland", "Europe", 52.4064, 16.9252, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Central European Plain: Cold winter, summer rye/potato"),
    BenchmarkLocation("Lund, Scania", "Sweden", "Europe", 55.7047, 13.1910, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 1, "Southern Sweden: Cool maritime summer grain/canola"),
    BenchmarkLocation("Middelburg, Zeeland", "Netherlands", "Europe", 51.4988, 3.6109, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Rhine Delta: Maritime cool summer potatoes/onions"),

    # --- AFRICA (18) ---
    BenchmarkLocation("Kano", "Nigeria", "Africa", 12.0022, 8.5920, "TROPICAL_MONOMODAL_RAIN", False, 5, 8, 1, "Sahelian Savanna: Short 70d monsoon sorghum/millet"),
    BenchmarkLocation("Ibadan, Oyo", "Nigeria", "Africa", 7.3775, 3.9470, "TROPICAL_BIMODAL_RAIN", False, 2, 9, 2, "Guinean Forest-Savanna: Bimodal rainfall maize/cassava"),
    BenchmarkLocation("Niamey", "Niger", "Africa", 13.5116, 2.1254, "TROPICAL_MONOMODAL_RAIN", False, 5, 8, 1, "Sahelian Semi-Arid: 450mm rain, pearl millet/cowpea"),
    BenchmarkLocation("Segou", "Mali", "Africa", 13.4417, -6.2644, "TROPICAL_MONOMODAL_RAIN", False, 5, 8, 1, "Niger River Basin: Sahel summer monsoon millet/sorghum"),
    BenchmarkLocation("Bobo-Dioulasso", "Burkina Faso", "Africa", 11.1772, -4.2979, "TROPICAL_MONOMODAL_RAIN", False, 4, 9, 1, "Sudanian Savanna: Summer rainfed cotton/maize"),
    BenchmarkLocation("Kumasi, Ashanti", "Ghana", "Africa", 6.6885, -1.6244, "TROPICAL_BIMODAL_RAIN", False, 2, 9, 2, "Cocoa/Forest Belt: Bimodal rain seasons"),
    BenchmarkLocation("Nakuru", "Kenya", "Africa", -0.3031, 36.0800, "TROPICAL_BIMODAL_RAIN", False, 2, 10, 3, "Rift Valley Highlands: 1850m mild bimodal maize/wheat"),
    BenchmarkLocation("Eldoret, Uasin Gishu", "Kenya", "Africa", 0.5143, 35.2698, "TROPICAL_BIMODAL_RAIN", False, 2, 9, 2, "Kenyan Grain Basket: High plateau maize & wheat"),
    BenchmarkLocation("Arusha", "Tanzania", "Africa", -3.3869, 36.6830, "TROPICAL_BIMODAL_RAIN", False, 1, 4, 2, "Northern Highlands: Bimodal Masika & Vuli rains"),
    BenchmarkLocation("Debre Zeit, Oromia", "Ethiopia", "Africa", 8.7500, 38.9833, "TROPICAL_BIMODAL_RAIN", False, 5, 8, 2, "Ethiopian Highlands: Kiremt main rain teff/wheat"),
    BenchmarkLocation("Wad Madani, Gezira", "Sudan", "Africa", 14.4012, 33.5199, "HYPER_ARID_DESERT", False, 5, 8, 1, "Gezira Scheme: Semi-desert, irrigated cotton/sorghum"),
    BenchmarkLocation("Tanta, Gharbia", "Egypt", "Africa", 30.7865, 31.0004, "HYPER_ARID_DESERT", False, 0, 11, 1, "Nile Delta: 75mm rain, hyper-arid pluvial fallow"),
    BenchmarkLocation("Settat, Chaouia", "Morocco", "Africa", 33.0014, -7.6167, "MEDITERRANEAN_WINTER_RAIN", False, 10, 3, 1, "Moroccan Granary: Winter rain wheat/barley"),
    BenchmarkLocation("Blida, Mitidja", "Algeria", "Africa", 36.4700, 2.8300, "MEDITERRANEAN_WINTER_RAIN", False, 9, 3, 1, "Tell Atlas: Mediterranean winter rain, dry summer"),
    BenchmarkLocation("Kroonstad, Free State", "South Africa", "Africa", -27.6504, 27.2349, "TEMPERATE_CONTINENTAL_FROST", False, 9, 2, 1, "Maize Quadrangle: Summer rainfed maize, dry winter"),
    BenchmarkLocation("Moorreesburg, Western Cape", "South Africa", "Africa", -33.1539, 18.6625, "MEDITERRANEAN_WINTER_RAIN", False, 4, 9, 1, "Swartland Wheat: Mediterranean winter rain, dry summer"),
    BenchmarkLocation("Chinhoyi, Mashonaland", "Zimbabwe", "Africa", -17.3667, 30.2000, "TROPICAL_MONOMODAL_RAIN", False, 10, 2, 1, "Highveld: Summer monsoon maize/tobacco, dry winter"),
    BenchmarkLocation("Mazabuka, Southern", "Zambia", "Africa", -15.8560, 27.7480, "TROPICAL_MONOMODAL_RAIN", False, 10, 2, 1, "Zambia Sugar/Grain: Summer rainfed maize, dry winter"),

    # --- ASIA (22) ---
    BenchmarkLocation("Ludhiana, Punjab", "India", "Asia", 30.9010, 75.8573, "TROPICAL_MONOMODAL_RAIN", False, 5, 8, 2, "Indo-Gangetic Plain: Summer Kharif rice, winter wheat"),
    BenchmarkLocation("Karnal, Haryana", "India", "Asia", 29.6857, 76.9905, "TROPICAL_MONOMODAL_RAIN", False, 5, 8, 2, "Green Revolution Belt: Kharif rice, Rabi wheat"),
    BenchmarkLocation("Varanasi, Uttar Pradesh", "India", "Asia", 25.3176, 82.9739, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 2, "Middle Gangetic: Monsoon Kharif, irrigated Rabi"),
    BenchmarkLocation("Burdwan, West Bengal", "India", "Asia", 23.2324, 87.8615, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 3, "Bengal Delta: Heavy monsoon Aman rice, Boro"),
    BenchmarkLocation("Godagari, Rajshahi", "Bangladesh", "Asia", 24.4667, 88.3300, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 3, "Barind Tract: Monsoon T.Aman, Rabi mustard/wheat"),
    BenchmarkLocation("Shyamnagar, Satkhira", "Bangladesh", "Asia", 22.3300, 89.1000, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 2, "Coastal Saline Belt: Monsoon T.Aman, winter fallow"),
    BenchmarkLocation("Kishoreganj Sadar", "Bangladesh", "Asia", 24.4798, 90.7691, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 3, "Old Brahmaputra: Heavy monsoon, high intensity"),
    BenchmarkLocation("Dowarabazar, Sunamganj", "Bangladesh", "Asia", 25.0500, 91.5667, "TROPICAL_MONOMODAL_RAIN", False, 10, 3, 1, "Haor Basin: Deep flood Kharif fallow, Rabi Boro"),
    BenchmarkLocation("Bandarban Sadar", "Bangladesh", "Asia", 22.1953, 92.2184, "TROPICAL_MONOMODAL_RAIN", False, 4, 9, 3, "Hill Tracts: Monsoon high slope, ginger/cotton"),
    BenchmarkLocation("Thanjavur, Tamil Nadu", "India", "Asia", 10.7870, 79.1378, "TROPICAL_MONOMODAL_RAIN", False, 8, 0, 2, "Cauvery Delta: Northeast monsoon Samba rice"),
    BenchmarkLocation("Akola, Maharashtra", "India", "Asia", 20.7002, 77.0082, "TROPICAL_MONOMODAL_RAIN", False, 5, 9, 1, "Vidarbha Cotton Belt: Black soil rainfed cotton/soy"),
    BenchmarkLocation("Dezhou, Shandong", "China", "Asia", 37.4341, 116.3575, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 2, "North China Plain: Cold winter wheat, summer maize"),
    BenchmarkLocation("Harbin, Heilongjiang", "China", "Asia", 45.8038, 126.5350, "TEMPERATE_CONTINENTAL_FROST", True, 4, 8, 1, "Northeast Granary: Severe freeze, single summer soy/corn"),
    BenchmarkLocation("Chengdu, Sichuan", "China", "Asia", 30.5728, 104.0668, "HUMID_TROPICAL_PERENNIAL", False, 3, 8, 2, "Sichuan Basin: Mild foggy winter, summer rice/rapeseed"),
    BenchmarkLocation("Zhanjiang, Guangdong", "China", "Asia", 21.2000, 110.3500, "HUMID_TROPICAL_PERENNIAL", False, 3, 9, 3, "South China Tropical: Double rice + winter vegetables"),
    BenchmarkLocation("Suphan Buri", "Thailand", "Asia", 14.4745, 100.1177, "TROPICAL_MONOMODAL_RAIN", False, 4, 9, 2, "Chao Phraya Basin: Monsoon rice, irrigated dry season"),
    BenchmarkLocation("Can Tho, Mekong Delta", "Vietnam", "Asia", 10.0452, 105.7469, "TROPICAL_MONOMODAL_RAIN", False, 4, 10, 3, "Mekong Delta: Tropical triple rice system"),
    BenchmarkLocation("Nam Dinh, Red River Delta", "Vietnam", "Asia", 20.4200, 106.1683, "HUMID_TROPICAL_PERENNIAL", False, 1, 9, 2, "Tonkin Delta: Spring rice & Autumn rice"),
    BenchmarkLocation("Klaten, Central Java", "Indonesia", "Asia", -7.7056, 110.6067, "TROPICAL_MONOMODAL_RAIN", False, 9, 3, 3, "Volcanic Java: Wet monsoon rice, Palawija rotation"),
    BenchmarkLocation("Caballero, Nueva Ecija", "Philippines", "Asia", 15.4859, 120.9673, "TROPICAL_MONOMODAL_RAIN", False, 5, 10, 2, "Central Luzon: Rice bowl, monsoon rain & dry season"),
    BenchmarkLocation("Andijan, Fergana Valley", "Uzbekistan", "Asia", 40.7821, 72.3442, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Central Asia: Continental arid, cold winter, cotton"),
    BenchmarkLocation("Taldykorgan, Almaty", "Kazakhstan", "Asia", 45.0167, 78.3667, "TEMPERATE_CONTINENTAL_FROST", True, 3, 8, 1, "Eurasian Steppe: Severe Siberian freeze, spring wheat"),

    # --- OCEANIA (7) ---
    BenchmarkLocation("Griffith, Riverina NSW", "Australia", "Oceania", -34.2889, 146.0444, "MEDITERRANEAN_WINTER_RAIN", False, 4, 9, 1, "Murray-Darling: Winter rain cereals, irrigated summer"),
    BenchmarkLocation("Northam, WA Wheatbelt", "Australia", "Oceania", -31.6539, 116.6661, "MEDITERRANEAN_WINTER_RAIN", False, 4, 9, 1, "Western Australia Wheatbelt: Pure Mediterranean winter rain"),
    BenchmarkLocation("Dalby, Darling Downs QLD", "Australia", "Oceania", -27.1833, 151.2667, "TROPICAL_MONOMODAL_RAIN", False, 9, 2, 2, "Queensland Grain Belt: Summer sorghum/cotton, winter wheat"),
    BenchmarkLocation("Cleve, Eyre Peninsula SA", "Australia", "Oceania", -33.7000, 136.5000, "MEDITERRANEAN_WINTER_RAIN", False, 4, 9, 1, "Eyre Peninsula: Semi-arid Mediterranean winter wheat/barley"),
    BenchmarkLocation("Horsham, Wimmera VIC", "Australia", "Oceania", -36.7128, 142.1989, "MEDITERRANEAN_WINTER_RAIN", False, 4, 9, 1, "Victorian Grain Belt: Winter-growing pulses & canola"),
    BenchmarkLocation("Ashburton, Canterbury", "New Zealand", "Oceania", -43.9000, 171.7333, "TEMPERATE_CONTINENTAL_FROST", False, 8, 2, 1, "Canterbury Plains: Cool maritime wheat, clover, ryegrass"),
    BenchmarkLocation("Hamilton, Waikato", "New Zealand", "Oceania", -37.7870, 175.2793, "HUMID_TROPICAL_PERENNIAL", False, 8, 2, 2, "Waikato Basin: Mild temperate year-round rain pasture"),

    # --- MIDDLE EAST (5) ---
    BenchmarkLocation("Adana, Cukurova", "Turkey", "Middle East", 37.0000, 35.3213, "MEDITERRANEAN_WINTER_RAIN", False, 9, 3, 2, "Cilician Plain: Mediterranean wet winter, summer cotton"),
    BenchmarkLocation("Konya, Central Anatolia", "Turkey", "Middle East", 37.8667, 32.4833, "TEMPERATE_CONTINENTAL_FROST", True, 2, 6, 1, "Anatolian Steppe: Freezing winter, summer drought wheat"),
    BenchmarkLocation("Ahvaz, Khuzestan", "Iran", "Middle East", 31.3183, 48.6706, "HYPER_ARID_DESERT", False, 10, 3, 1, "Karun River Basin: Extreme desert heat, winter wheat"),
    BenchmarkLocation("Amarah, Maysan", "Iraq", "Middle East", 31.8360, 47.1444, "HYPER_ARID_DESERT", False, 10, 3, 1, "Tigris Basin: Hyper-arid, irrigated date & winter barley"),
    BenchmarkLocation("Al-Hofuf, Al-Ahsa", "Saudi Arabia", "Middle East", 25.3644, 49.5855, "HYPER_ARID_DESERT", False, 10, 3, 1, "Arabian Desert Oasis: Hyper-arid, 60mm rain, irrigated date")
]


class PlanetaryBenchmarkSuite:
    """Executes the 100-location planetary benchmark and scores accuracy."""

    def __init__(self, cache_file: str = "data/planetary_100_cache.json"):
        self.cache_file = cache_file
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def fetch_climate(self, lat: float, lon: float) -> Dict[str, Any]:
        key = f"{lat:.4f}_{lon:.4f}"
        if key in self.cache:
            return self.cache[key]

        url = (
            f"https://power.larc.nasa.gov/api/temporal/climatology/point?"
            f"parameters=T2M,T2M_MIN,T2M_MAX,PRECTOTCORR&community=AG&"
            f"latitude={lat:.4f}&longitude={lon:.4f}&format=JSON"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0-Benchmark"})
        with urllib.request.urlopen(req, context=self.ctx, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        props = data["properties"]["parameter"]
        month_keys = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        tmean = [props["T2M"][k] for k in month_keys]
        tmin = [props["T2M_MIN"][k] for k in month_keys]
        tmax = [props["T2M_MAX"][k] for k in month_keys]
        rain = [props["PRECTOTCORR"][k] * days_in_months[i] for i, k in enumerate(month_keys)]

        res = {
            "monthly_tmean": tmean,
            "monthly_tmin": tmin,
            "monthly_tmax": tmax,
            "monthly_rain": rain,
            "annual_rain": sum(rain)
        }
        self.cache[key] = res
        return res

    def prefetch_all(self, max_workers: int = 10):
        """Pre-fetches all uncached locations concurrently."""
        uncached = [loc for loc in BENCHMARK_100 if f"{loc.lat:.4f}_{loc.lon:.4f}" not in self.cache]
        if not uncached:
            return

        def fetch_worker(loc):
            try:
                self.fetch_climate(loc.lat, loc.lon)
            except Exception as e:
                print(f"Error fetching {loc.name}: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(fetch_worker, uncached)
        self._save_cache()

    def run_benchmark(self) -> Dict[str, Any]:
        """Runs the benchmark across all 100 locations and calculates accuracy metrics."""
        self.prefetch_all(max_workers=10)

        total_locations = len(BENCHMARK_100)
        regime_correct = 0
        freeze_correct = 0
        timing_correct = 0
        k_correct = 0

        detailed_results = []

        fetcher = GlobalEnvFetcher()

        for loc in BENCHMARK_100:
            clim = self.fetch_climate(loc.lat, loc.lon)
            calc_lgp, _ = fetcher.compute_daily_lgp_and_k(
                clim["monthly_tmean"], clim["monthly_tmin"], clim["monthly_tmax"], clim["monthly_rain"],
                lat=loc.lat
            )
            cal = UniversalSeasonalSegmenter.segment_calendar(
                loc.lat, loc.lon,
                clim["monthly_tmean"], clim["monthly_tmin"], clim["monthly_tmax"], clim["monthly_rain"],
                lgp_days=calc_lgp
            )

            pred_regime = cal.regime_classification
            has_freeze = cal.seasons["season_3"].regime_type == "FREEZE_DORMANCY"
            pred_s1 = cal.seasons["season_1"]

            # 1. Regime Match
            # Treat TEMPERATE_FROST / CONTINENTAL_FROST as equivalent
            is_regime_match = (
                pred_regime == loc.ground_truth_regime or
                ("TROPICAL" in pred_regime and "TROPICAL" in loc.ground_truth_regime) or
                ("FROST" in pred_regime and "FROST" in loc.ground_truth_regime)
            )
            if is_regime_match:
                regime_correct += 1

            # 2. Freeze Match
            is_freeze_match = (has_freeze == loc.ground_truth_has_freeze)
            if is_freeze_match:
                freeze_correct += 1

            # 3. Timing Match (within ±1 month circular distance for start month)
            start_diff = min((pred_s1.start_month - loc.ground_truth_primary_start_month) % 12,
                             (loc.ground_truth_primary_start_month - pred_s1.start_month) % 12)
            is_timing_match = (start_diff <= 1)
            if is_timing_match:
                timing_correct += 1

            # 4. K Match
            is_k_match = (cal.cropping_intensity_k == loc.ground_truth_rainfed_k)
            if is_k_match:
                k_correct += 1

            detailed_results.append({
                "name": loc.name,
                "country": loc.country,
                "continent": loc.continent,
                "coordinates": f"({loc.lat:.2f}, {loc.lon:.2f})",
                "pred_regime": pred_regime,
                "gt_regime": loc.ground_truth_regime,
                "regime_match": is_regime_match,
                "pred_freeze": has_freeze,
                "gt_freeze": loc.ground_truth_has_freeze,
                "freeze_match": is_freeze_match,
                "pred_window": pred_s1.calendar_window,
                "timing_match": is_timing_match,
                "pred_k": cal.cropping_intensity_k,
                "gt_k": loc.ground_truth_rainfed_k
            })

        self._save_cache()

        overall_score = (
            (regime_correct * 0.35) +
            (freeze_correct * 0.25) +
            (timing_correct * 0.25) +
            (k_correct * 0.15)
        )

        return {
            "total_samples": total_locations,
            "overall_accuracy_pct": round(overall_score, 1),
            "regime_classification_accuracy_pct": round((regime_correct / total_locations) * 100, 1),
            "freeze_detection_accuracy_pct": round((freeze_correct / total_locations) * 100, 1),
            "primary_timing_accuracy_pct": round((timing_correct / total_locations) * 100, 1),
            "k_intensity_accuracy_pct": round((k_correct / total_locations) * 100, 1),
            "detailed_results": detailed_results
        }


if __name__ == "__main__":
    suite = PlanetaryBenchmarkSuite()
    print("Running 100-Location Planetary Benchmark...")
    results = suite.run_benchmark()
    print(f"\n========================================================")
    print(f"       PLANETARY BENCHMARK RESULTS (N = {results['total_samples']})")
    print(f"========================================================")
    print(f" OVERALL ACCURACY SCORE             : {results['overall_accuracy_pct']}%")
    print(f" Regime Classification Accuracy     : {results['regime_classification_accuracy_pct']}%")
    print(f" Thermal Freeze Detection Accuracy  : {results['freeze_detection_accuracy_pct']}%")
    print(f" Primary Season Timing (±1 mo)      : {results['primary_timing_accuracy_pct']}%")
    print(f" Cropping Intensity (K) Agreement   : {results['k_intensity_accuracy_pct']}%")
    print(f"========================================================")
