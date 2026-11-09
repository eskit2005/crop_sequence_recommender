import os, sys, json, ssl, math, urllib.request
import concurrent.futures
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.planetary_benchmark_100 import BENCHMARK_100
from scratch.generate_150_batches import RAW_150
from src.seasonal_calendar import UniversalSeasonalSegmenter, MONTH_FULL_NAMES, DAYS_IN_MONTHS
from src.global_env_fetcher import GlobalEnvFetcher

os.makedirs("data/audit_100_new_batches", exist_ok=True)
cache_file = "data/planetary_100_new_cache.json"

RAW_100_NEW = [
    # =========================================================================
    # BATCH 1: North America & Central America / Caribbean (17)
    # =========================================================================
    ("Moose Jaw, Saskatchewan", "Canada", "North America", 50.3933, -105.5344, "Palliser Triangle, durum wheat, pulse crops, summerfallow"),
    ("Dauphin, Manitoba", "Canada", "North America", 51.1494, -100.0494, "Parkland wheat, oats, canola, mixed farming"),
    ("Guelph, Ontario", "Canada", "North America", 43.5448, -80.2482, "Agricultural research hub, dairy, winter wheat, soy"),
    ("Drummondville, Quebec", "Canada", "North America", 45.8833, -72.4833, "St. Lawrence lowland grain, corn silage and dairy"),
    ("Mason City, Iowa", "USA", "North America", 43.1536, -93.2010, "Northern Iowa rich mollisols, corn and soybean"),
    ("Kearney, Nebraska", "USA", "North America", 40.6995, -99.0814, "Central Platte irrigated corn, alfalfa, sorghum"),
    ("Garden City, Kansas", "USA", "North America", 37.9717, -100.8727, "Western Kansas irrigated corn, feedlot beef, winter wheat"),
    ("Watertown, South Dakota", "USA", "North America", 44.8994, -97.1145, "Glacial Lakes corn, soybean, spring wheat"),
    ("Dickinson, North Dakota", "USA", "North America", 46.8792, -102.7896, "Western ND spring wheat, durum, sunflower"),
    ("Victoria, Texas", "USA", "North America", 28.8053, -97.0036, "Gulf Coast grain sorghum, cotton, corn"),
    ("Altamira, Tamaulipas", "Mexico", "North America", 22.3922, -97.9378, "Huasteca coastal plain soybeans, sorghum, citrus"),
    ("Navojoa, Sonora", "Mexico", "North America", 27.0728, -109.4439, "Mayo Valley irrigated winter wheat, safflower, chickpea"),
    ("Guasave, Sinaloa", "Mexico", "North America", 25.5744, -108.4686, "Sinaloa agricultural heartland, white corn, garbanzo, tomato"),
    ("Poza Rica, Veracruz", "Mexico", "North America", 20.5332, -97.4595, "Gulf coastal plain, tropical citrus, vanilla, maize"),
    ("Morelia, Michoacan", "Mexico", "North America", 19.7060, -101.1950, "Tarascan plateau maize, avocado, strawberry"),
    ("La Vega", "Dominican Republic", "North America", 19.2222, -70.5294, "Royal Valley (Valle de la Vega Real) irrigated rice, plantain, sweet potato"),
    ("Santiago de Veraguas", "Panama", "North America", 8.1000, -80.9833, "Central Pacific plains, sugarcane, tropical rice, beef cattle"),

    # =========================================================================
    # BATCH 2: South America (17)
    # =========================================================================
    ("Sinop, Mato Grosso", "Brazil", "South America", -11.8608, -55.5097, "Northern MT soybean and safrinha corn giant"),
    ("Sapezal, Mato Grosso", "Brazil", "South America", -13.5422, -58.8144, "Parecis plateau cotton and soybean capital"),
    ("Jatai, Goias", "Brazil", "South America", -17.8814, -51.7144, "Southwest Goias grains, high-tech soy and corn"),
    ("Maracaju, Mato Grosso do Sul", "Brazil", "South America", -21.6144, -55.1683, "MS central grain belt, soy, safrinha corn"),
    ("Pato Branco, Parana", "Brazil", "South America", -26.2289, -52.6711, "Southwest Parana grain, winter wheat/oats, summer soy"),
    ("Santa Maria, Rio Grande do Sul", "Brazil", "South America", -29.6842, -53.8069, "Central depression, irrigated rice and soybean"),
    ("Barreiras, Western Bahia", "Brazil", "South America", -12.1528, -44.9903, "Rio Grande basin Cerrado, soy, cotton, irrigated maize"),
    ("Caaguazu, Caaguazu", "Paraguay", "South America", -25.4600, -56.0150, "Central eastern soy, wheat, cassava"),
    ("Hohenau, Itapua", "Paraguay", "South America", -27.0767, -55.7533, "United Colonists cooperative, soy, wheat, canola"),
    ("Chivilcoy, Buenos Aires", "Argentina", "South America", -34.8958, -60.0167, "Western Humid Pampas, wheat-soybean double crop, maize"),
    ("Tres Arroyos, Buenos Aires", "Argentina", "South America", -38.3756, -60.2794, "Southern Argentine wheat capital, malting barley, sunflower"),
    ("Villa Maria, Cordoba", "Argentina", "South America", -32.4075, -63.2403, "Central Cordoba dairy basin, alfalfa, corn, soy"),
    ("Trenque Lauquen, Buenos Aires", "Argentina", "South America", -35.9739, -62.7344, "Western Pampas cattle-grain rotation, sunflower, rye"),
    ("San Fernando, Colchagua", "Chile", "South America", -34.5839, -70.9889, "Colchagua Valley world-class wine, fruit orchards, seed crops"),
    ("Los Angeles, Biobio", "Chile", "South America", -37.4697, -72.3536, "Biobio plain, winter wheat, rapeseed, sugar beet, berries"),
    ("Chicama, La Libertad", "Peru", "South America", -7.8444, -79.1469, "Chicama Valley massive irrigated sugarcane and asparagus"),
    ("Anta, Cusco", "Peru", "South America", -13.4611, -72.1478, "Sacred Valley high Andean plateau (3400m), native potato, giant white maize, barley"),

    # =========================================================================
    # BATCH 3: Europe & Mediterranean Basin (17)
    # =========================================================================
    ("Bourges, Cher", "France", "Europe", 47.0810, 2.3988, "Champagne Berrichonne limestone plain, durum wheat, soft wheat, rapeseed"),
    ("Troyes, Aube", "France", "Europe", 48.2973, 4.0744, "Champagne wet/dry plain, winter wheat, malting barley, hemp, sugar beet"),
    ("Agen, Lot-et-Garonne", "France", "Europe", 44.2031, 0.6164, "Garonne Valley prune plum capital, irrigated maize, sunflower, vegetables"),
    ("Halle Saale, Saxony-Anhalt", "Germany", "Europe", 51.4828, 11.9697, "Central German chernozem, sugar beet, winter wheat, rapeseed"),
    ("Landshut, Bavaria", "Germany", "Europe", 48.5369, 12.1522, "Lower Bavaria fertile hill country, winter wheat, malting barley, hops"),
    ("Stralsund, Mecklenburg-Vorpommern", "Germany", "Europe", 54.3122, 13.0928, "Pomeranian coastal plains, winter rape and winter wheat"),
    ("Norwich, Norfolk", "UK", "Europe", 52.6309, 1.2974, "East Anglian loam belt, malting barley, sugar beet, wheat"),
    ("Hereford, Herefordshire", "UK", "Europe", 52.0565, -2.7160, "Wye Valley cider apple orchards, soft fruit, winter wheat, hops"),
    ("Athy, County Kildare", "Ireland", "Europe", 52.9917, -6.9792, "Kildare tillage granary, high-yield spring malting barley, winter wheat"),
    ("Ypres, West Flanders", "Belgium", "Europe", 50.8511, 2.8858, "Westhoek polders and loam, potato processing, cauliflower, wheat"),
    ("Heerenveen, Friesland", "Netherlands", "Europe", 52.9567, 5.9250, "Frisian peat/clay dairy pastures, forage maize, grass seed"),
    ("Viborg, Central Jutland", "Denmark", "Europe", 56.4532, 9.4020, "Jutland moraine, feed barley, winter rye, seed potatoes"),
    ("Linkoping, Ostergotland", "Sweden", "Europe", 58.4108, 15.6214, "Ostgota plain, winter wheat, spring barley, oats, rapeseed"),
    ("Mantua, Lombardy", "Italy", "Europe", 45.1564, 10.7914, "Mincio/Po plain, grain maize, soybean, Grana Padano forage"),
    ("Matera, Basilicata", "Italy", "Europe", 40.6664, 16.6043, "Fossa Bradanica, premier Italian durum wheat for pasta"),
    ("Jaen, Andalusia", "Spain", "Europe", 37.7796, -3.7849, "World capital of olive oil, olive monoculture, winter wheat"),
    ("Badajoz, Extremadura", "Spain", "Europe", 38.8794, -6.9707, "Vegas del Guadiana irrigated processing tomato, rice, corn, olive"),

    # =========================================================================
    # BATCH 4: Sub-Saharan Africa (17)
    # =========================================================================
    ("Kayes, Kayes Region", "Mali", "Africa", 14.4469, -11.4442, "Senegal River basin, groundnut, sorghum, irrigated vegetables"),
    ("Ferkessedougou, Tchologo", "Cote d Ivoire", "Africa", 9.5928, -5.1944, "Northern sugarcane and cotton agro-industrial basin"),
    ("Sunyani, Bono Region", "Ghana", "Africa", 7.3399, -2.3268, "Forest-savanna transition, cocoa, maize, cassava, yam"),
    ("Yendi, Northern Region", "Ghana", "Africa", 9.4428, -0.0099, "Eastern savanna yam and soybean production corridor"),
    ("Bohicon, Zou Department", "Benin", "Africa", 7.1783, 2.0667, "Southern plateau, maize, cowpea, oil palm, cassava"),
    ("Katsina, Katsina State", "Nigeria", "Africa", 12.9908, 7.6018, "Sudan-Sahel cereal belt, millet, sorghum, groundnuts, cowpea"),
    ("Lafia, Nasarawa State", "Nigeria", "Africa", 8.4932, 8.5153, "Middle Belt food crops, yam, sesame, melon seed, cassava"),
    ("Kousseri, Far North", "Cameroon", "Africa", 12.0772, 15.0306, "Lake Chad basin recession sorghum and irrigated onion"),
    ("Bafoussam, West Region", "Cameroon", "Africa", 5.4778, 10.4176, "Western Highlands volcanic soils (1500m), Arabica coffee, Irish potato, maize"),
    ("Nanyuki, Laikipia County", "Kenya", "Africa", 0.0167, 37.0728, "Equatorial leeward high-plateau mixed livestock, wheat, barley, horticulture"),
    ("Embu, Embu County", "Kenya", "Africa", -0.5389, 37.4583, "Eastern slopes of Mt Kenya, bimodal maize, beans, passion fruit, tea"),
    ("Masaka, Central Region", "Uganda", "Africa", -0.3411, 31.7361, "Lake Victoria basin, Robusta coffee, cooking banana, beans, maize"),
    ("Lira, Northern Region", "Uganda", "Africa", 2.2472, 32.9000, "Lango sub-region, sunflower oilseed capital, soya, sesame, pigeonpea"),
    ("Lubango, Huila Province", "Angola", "Africa", -14.9172, 13.4925, "Huila Plateau temperate highland, wheat, maize, fruit orchards"),
    ("Nampula, Nampula Province", "Mozambique", "Africa", -15.1165, 39.2666, "Northern plateau, cashew, cotton, pigeonpea, cassava"),
    ("Kabwe, Central Province", "Zambia", "Africa", -14.4469, 28.4464, "Central commercial farming block, irrigated wheat, rainfed maize, soy"),
    ("Bethlehem, Free State", "South Africa", "Africa", -28.2308, 28.3072, "Eastern Free State wheat and apple capital, cool summer maize"),

    # =========================================================================
    # BATCH 5: Middle East, Central Asia & South Asia (16)
    # =========================================================================
    ("Eskisehir, Central Anatolia", "Turkey", "Asia", 39.7767, 30.5206, "Eskisehir plain, sugar beet, malting barley, wheat"),
    ("Diyarbakir, Southeastern Anatolia", "Turkey", "Asia", 37.9144, 40.2306, "Upper Tigris basin, durum wheat, red lentil, cotton, watermelon"),
    ("Edirne, Thrace", "Turkey", "Europe", 41.6772, 26.5557, "Meric/Tundzha basin, intensive irrigated paddy rice and sunflower"),
    ("Kermanshah, Kermanshah", "Iran", "Asia", 34.3142, 47.0650, "Zagros fertile mountain valley, irrigated wheat, barley, sugar beet, chickpeas"),
    ("Sari, Mazandaran", "Iran", "Asia", 36.5633, 53.0601, "Caspian subtropical lowland, intensive paddy rice, citrus orchards"),
    ("Kirkuk, Kirkuk Governorate", "Iraq", "Asia", 35.4681, 44.3922, "Kirkuk plains rainfed/irrigated wheat, barley, sunflower"),
    ("Taraz, Zhambyl Region", "Kazakhstan", "Asia", 42.9000, 71.3667, "Talas River oasis, sugar beet, winter wheat, onion"),
    ("Bukhara, Bukhara Region", "Uzbekistan", "Asia", 39.7747, 64.4286, "Zeravshan lower delta oasis, Karakul sheep forage, cotton, wheat"),
    ("Sahiwal, Punjab", "Pakistan", "Asia", 30.6682, 73.1114, "Bari Doab, Sahiwal dairy cattle, cotton-wheat, maize-potato double crop"),
    ("Bahawalpur, Punjab", "Pakistan", "Asia", 29.3956, 71.6836, "Sutlej River canal colony, cotton, wheat, sunflower"),
    ("Hisar, Haryana", "India", "Asia", 29.1492, 75.7217, "Western Haryana semi-arid zone, pearl millet (bajra), wheat, mustard, cotton"),
    ("Aligarh, Uttar Pradesh", "India", "Asia", 27.8974, 78.0880, "Doab plain, wheat-rice, sugarcane, potato, mustard"),
    ("Ujjain, Madhya Pradesh", "India", "Asia", 23.1765, 75.7885, "Malwa Plateau black soil (Vertisol), soybean, wheat, chickpea"),
    ("Amravati, Maharashtra", "India", "Asia", 20.9320, 77.7523, "Vidarbha cotton-soybean belt, Nagpur mandarin orange orchards"),
    ("Rajahmundry, Andhra Pradesh", "India", "Asia", 17.0005, 81.8040, "Godavari Delta intensive paddy rice, banana, tobacco"),
    ("Bogra, Rajshahi Division", "Bangladesh", "Asia", 24.8465, 89.3777, "Karatoya river plain, premier potato and Boro rice hub"),

    # =========================================================================
    # BATCH 6: East Asia, Southeast Asia & Oceania (16)
    # =========================================================================
    ("Liaocheng, Shandong", "China", "Asia", 36.4570, 115.9854, "Western Shandong plain, winter wheat, summer maize, greenhouse vegetables"),
    ("Zhumadian, Henan", "China", "Asia", 32.9775, 114.0247, "Southern Henan, China premier sesame and peanut hub, wheat-corn"),
    ("Qiqihar, Heilongjiang", "China", "Asia", 47.3543, 123.9188, "Western Songnen Plain, corn, soybean, dairy cattle"),
    ("Yueyang, Hunan", "China", "Asia", 29.3563, 113.1289, "Dongting Lake mouth, double-crop rice, freshwater aquaculture, ramie"),
    ("Nantong, Jiangsu", "China", "Asia", 32.0140, 120.8943, "Yangtze River Delta north bank, cotton, wheat-soybean, vegetables"),
    ("Obihiro, Tokachi", "Japan", "Asia", 42.9239, 143.1964, "Tokachi Plain Japan food base, sugar beet, potato, wheat, dairy"),
    ("Saga, Kyushu", "Japan", "Asia", 33.2635, 130.3009, "Saga Plain Ariake Sea, high-yield two-crop paddy rice and winter barley"),
    ("Gimje, Jeollabuk-do", "South Korea", "Asia", 35.8036, 126.8808, "Honam Plain granary, rice, barley, potato"),
    ("Phitsanulok, Lower Northern", "Thailand", "Asia", 16.8211, 100.2659, "Nan River basin, irrigated double/triple paddy rice, corn"),
    ("Ubon Ratchathani, Isan", "Thailand", "Asia", 15.2448, 104.8473, "Mun River basin, Hom Mali jasmine rice, cassava, rubber"),
    ("Siem Reap, Siem Reap", "Cambodia", "Asia", 13.3633, 103.8564, "Northern Tonle Sap floodplain, wet-season floating and lowland rice"),
    ("My Tho, Tien Giang", "Vietnam", "Asia", 10.3600, 106.3600, "Upper Mekong Delta, tropical fruit orchards, double/triple-crop rice"),
    ("Teluk Intan, Perak", "Malaysia", "Asia", 4.0259, 101.0213, "Perak River basin, oil palm, irrigated paddy rice, cocoa"),
    ("Karawang, West Java", "Indonesia", "Asia", -6.3054, 107.3006, "National Rice Granary of Indonesia, intensive Citarum irrigated rice"),
    ("Tamworth, New South Wales", "Australia", "Oceania", -31.0927, 150.9320, "New England / Peel Valley, irrigated lucerne, winter wheat, prime lamb"),
    ("Wagga Wagga, Riverina", "Australia", "Oceania", -35.1082, 147.3598, "Eastern Riverina grain-livestock belt, winter wheat, canola, barley")
]

print(f"Total candidate locations: {len(RAW_100_NEW)}")
assert len(RAW_100_NEW) == 100, f"Expected 100, got {len(RAW_100_NEW)}"

# 1. Overlap Check against Benchmark 100 and Raw 150
existing_100_names = set(b.name.lower() for b in BENCHMARK_100)
existing_100_coords = [(round(b.lat, 2), round(b.lon, 2), b.name) for b in BENCHMARK_100]

existing_150_names = set(b[0].lower() for b in RAW_150)
existing_150_coords = [(round(b[3], 2), round(b[4], 2), b[0]) for b in RAW_150]

for name, country, cont, lat, lon, desc in RAW_100_NEW:
    n_clean = name.lower()
    coord = (round(lat, 2), round(lon, 2))
    if n_clean in existing_100_names:
        raise ValueError(f"Duplicate name in BENCHMARK_100: {name}")
    if n_clean in existing_150_names:
        raise ValueError(f"Duplicate name in RAW_150: {name}")
    for ex_lat, ex_lon, ex_name in existing_100_coords:
        if abs(ex_lat - coord[0]) < 0.20 and abs(ex_lon - coord[1]) < 0.20:
            raise ValueError(f"Coordinate collision with BENCHMARK_100: {name} ({coord}) vs {ex_name} ({ex_lat}, {ex_lon})")
    for ex_lat, ex_lon, ex_name in existing_150_coords:
        if abs(ex_lat - coord[0]) < 0.20 and abs(ex_lon - coord[1]) < 0.20:
            raise ValueError(f"Coordinate collision with RAW_150: {name} ({coord}) vs {ex_name} ({ex_lat}, {ex_lon})")

print("Verified: 0% overlap with both previous 100 and 150 benchmarks (250 prior points)!")

# 2. Cache management
cache = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r") as f:
            cache = json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")

fetcher = GlobalEnvFetcher()

def fetch_point(loc):
    name, country, cont, lat, lon, desc = loc
    key = f"{lat:.4f}_{lon:.4f}"
    if key in cache:
        return key, cache[key]
    
    print(f"Fetching NASA POWER for {name} ({lat}, {lon})...")
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,T2M_MIN,T2M_MAX,PRECTOTCORR&community=AG&longitude={lon:.4f}&latitude={lat:.4f}&format=JSON"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=fetcher.ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        params = data["properties"]["parameter"]
        months_str = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        monthly_tmean = [params["T2M"][m] for m in months_str]
        monthly_tmin = [params["T2M_MIN"][m] for m in months_str]
        monthly_tmax = [params["T2M_MAX"][m] for m in months_str]
        days_per_month = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        monthly_rain = [params["PRECTOTCORR"][m] * days_per_month[i] for i, m in enumerate(months_str)]
        
        lgp_days, k = fetcher.compute_daily_lgp_and_k(monthly_tmean, monthly_tmin, monthly_tmax, monthly_rain, lat=lat)
        
        result = {
            "name": name,
            "country": country,
            "continent": cont,
            "lat": lat,
            "lon": lon,
            "description": desc,
            "monthly_tmean": monthly_tmean,
            "monthly_tmin": monthly_tmin,
            "monthly_tmax": monthly_tmax,
            "monthly_rain": monthly_rain,
            "lgp_days": lgp_days,
            "k_prelim": k
        }
        return key, result

to_fetch = [loc for loc in RAW_100_NEW if f"{loc[3]:.4f}_{loc[4]:.4f}" not in cache]
print(f"Locations needing NASA POWER fetch: {len(to_fetch)}")

if to_fetch:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_point, loc): loc for loc in to_fetch}
        for future in concurrent.futures.as_completed(futures):
            key, res = future.result()
            cache[key] = res
            
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)

# 3. Partition into 6 batches
batches = {
    "batch01_north_central_america": RAW_100_NEW[0:17],    # 17
    "batch02_south_america": RAW_100_NEW[17:34],            # 17
    "batch03_europe_mediterranean": RAW_100_NEW[34:51],     # 17
    "batch04_subsaharan_africa": RAW_100_NEW[51:68],        # 17
    "batch05_mideast_south_central_asia": RAW_100_NEW[68:84], # 16
    "batch06_east_seasia_oceania": RAW_100_NEW[84:100]      # 16
}

for b_name, b_locs in batches.items():
    b_data = []
    for loc in b_locs:
        key = f"{loc[3]:.4f}_{loc[4]:.4f}"
        raw = cache[key]
        
        cal = UniversalSeasonalSegmenter.segment_calendar(
            lat=raw["lat"],
            lon=raw["lon"],
            monthly_tmean=raw["monthly_tmean"],
            monthly_tmin=raw["monthly_tmin"],
            monthly_tmax=raw["monthly_tmax"],
            monthly_rain=raw["monthly_rain"],
            lgp_days=raw["lgp_days"]
        )
        
        has_freeze_dormancy = any(s.regime_type == "FREEZE_DORMANCY" for s in cal.seasons.values())
        
        pt_entry = {
            "name": raw["name"],
            "country": raw["country"],
            "continent": raw["continent"],
            "lat": raw["lat"],
            "lon": raw["lon"],
            "description": raw["description"],
            "annual_rain_mm": round(sum(raw["monthly_rain"]), 1),
            "annual_mean_temp_c": round(sum(raw["monthly_tmean"])/12.0, 1),
            "computed_lgp_days": cal.lgp_days,
            "deduced_regime": cal.regime_classification,
            "deduced_k": cal.cropping_intensity_k,
            "has_freeze_dormancy": has_freeze_dormancy,
            "season_1": {
                "name": cal.seasons["season_1"].name,
                "window": cal.seasons["season_1"].calendar_window,
                "duration_months": cal.seasons["season_1"].duration_months,
                "regime_type": cal.seasons["season_1"].regime_type,
                "is_fallow": cal.seasons["season_1"].is_fallow,
                "mean_temp_c": cal.seasons["season_1"].mean_temp_c,
                "min_temp_c": cal.seasons["season_1"].min_temp_c,
                "rain_mm": cal.seasons["season_1"].total_rain_mm,
                "role": cal.seasons["season_1"].role,
                "fallow_reason": cal.seasons["season_1"].fallow_reason
            },
            "season_2": {
                "name": cal.seasons["season_2"].name,
                "window": cal.seasons["season_2"].calendar_window,
                "duration_months": cal.seasons["season_2"].duration_months,
                "regime_type": cal.seasons["season_2"].regime_type,
                "is_fallow": cal.seasons["season_2"].is_fallow,
                "mean_temp_c": cal.seasons["season_2"].mean_temp_c,
                "min_temp_c": cal.seasons["season_2"].min_temp_c,
                "rain_mm": cal.seasons["season_2"].total_rain_mm,
                "role": cal.seasons["season_2"].role,
                "fallow_reason": cal.seasons["season_2"].fallow_reason
            },
            "season_3": {
                "name": cal.seasons["season_3"].name,
                "window": cal.seasons["season_3"].calendar_window,
                "duration_months": cal.seasons["season_3"].duration_months,
                "regime_type": cal.seasons["season_3"].regime_type,
                "is_fallow": cal.seasons["season_3"].is_fallow,
                "mean_temp_c": cal.seasons["season_3"].mean_temp_c,
                "min_temp_c": cal.seasons["season_3"].min_temp_c,
                "rain_mm": cal.seasons["season_3"].total_rain_mm,
                "role": cal.seasons["season_3"].role,
                "fallow_reason": cal.seasons["season_3"].fallow_reason
            }
        }
        b_data.append(pt_entry)
        
    out_path = f"data/audit_100_new_batches/{b_name}.json"
    with open(out_path, "w") as f:
        json.dump(b_data, f, indent=2)
    print(f"Generated {out_path} ({len(b_data)} locations)")

print("\nAll 100 brand-new locations processed and partitioned into 6 audit batches!")
