import os, sys, json, ssl, math, urllib.request
import concurrent.futures
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.planetary_benchmark_100 import BENCHMARK_100
from src.seasonal_calendar import UniversalSeasonalSegmenter, MONTH_FULL_NAMES, DAYS_IN_MONTHS
from src.global_env_fetcher import GlobalEnvFetcher

os.makedirs("data/audit_150_batches", exist_ok=True)
cache_file = "data/planetary_150_cache.json"

RAW_150 = [
    # --- BATCH 1: US Heartland & Northern Plains (15) ---
    ("Ames, Story County, Iowa", "USA", "North America", 42.0308, -93.6319, "Central Corn Belt: High-yield corn & soybean"),
    ("Lafayette, Tippecanoe, Indiana", "USA", "North America", 40.4167, -86.8753, "Eastern Corn Belt: Summer corn/soybean, winter wheat"),
    ("Mankato, Blue Earth, Minnesota", "USA", "North America", 44.1636, -93.9994, "Upper Midwest: Cold winter, intensive corn/soybean"),
    ("Lincoln, Lancaster, Nebraska", "USA", "North America", 40.8136, -96.7026, "Western Corn Belt: Rainfed/irrigated corn, grain sorghum"),
    ("Salina, Saline, Kansas", "USA", "North America", 38.8403, -97.6114, "Hard Winter Wheat Belt: Semi-arid, fall-planted wheat"),
    ("Grand Forks, North Dakota", "USA", "North America", 47.9253, -97.0329, "Red River Valley: Spring wheat, sugar beet, dry edible bean"),
    ("Aberdeen, Brown, South Dakota", "USA", "North America", 45.4647, -98.4865, "Northern Plains: Corn, soybean, spring wheat, sunflower"),
    ("Enid, Garfield, Oklahoma", "USA", "North America", 36.3956, -97.8784, "Southern Plains: Hard red winter wheat, double-crop sorghum"),
    ("Jonesboro, Craighead, Arkansas", "USA", "North America", 35.8423, -90.7043, "Mississippi Delta: Intensive irrigated rice, soybean"),
    ("Greenwood, Leflore, Mississippi", "USA", "North America", 33.5162, -90.1795, "Yazoo-Mississippi Delta: Upland cotton, soybean, corn"),
    ("Bowling Green, Warren, Kentucky", "USA", "North America", 36.9685, -86.4808, "Pennyroyal Plateau: Corn, soybean, winter wheat, dark tobacco"),
    ("Modesto, Stanislaus, California", "USA", "North America", 37.6391, -120.9969, "Central Valley: Almonds, walnuts, silage corn, irrigated dairy"),
    ("Moses Lake, Grant, Washington", "USA", "North America", 47.1301, -119.2781, "Columbia Basin: Irrigated potato, sweet corn, alfalfa, wheat"),
    ("Twin Falls, Twin Falls, Idaho", "USA", "North America", 42.5629, -114.4609, "Snake River Plain: Sugar beet, malting barley, potato"),
    ("Las Cruces, Dona Ana, New Mexico", "USA", "North America", 32.3199, -106.7637, "Mesilla Valley: Rio Grande irrigated pecan, green chile, cotton"),

    # --- BATCH 2: Canada & Mexico (15) ---
    ("Brandon, Manitoba", "Canada", "North America", 49.8485, -99.9501, "Canadian Prairies: Canola, spring wheat, oats, field pea"),
    ("Saskatoon, Saskatchewan", "Canada", "North America", 52.1579, -106.6702, "Dark Brown Soil Zone: Lentil, chickpea, canola, wheat capital"),
    ("Red Deer, Alberta", "Canada", "North America", 52.2681, -113.8112, "Aspen Parkland: Malting barley, canola, cool-season forage"),
    ("Chatham-Kent, Ontario", "Canada", "North America", 42.4048, -82.1910, "Lake Erie Granary: Grain corn, soybean, winter wheat, tomato"),
    ("Saint-Hyacinthe, Quebec", "Canada", "North America", 45.6275, -72.9571, "St. Lawrence Lowlands: Grain corn, soybean, dairy silage"),
    ("Charlottetown, Prince Edward Island", "Canada", "North America", 46.2382, -63.1311, "Atlantic Maritime: Red sandy loam seed and table potatoes"),
    ("Hermosillo, Sonora", "Mexico", "North America", 29.0729, -110.9559, "Coast of Hermosillo: Deep well irrigated table grape, wheat, citrus"),
    ("Los Mochis, Sinaloa", "Mexico", "North America", 25.7905, -108.9959, "Valle del Fuerte: Intensive winter irrigated white corn, tomato"),
    ("Delicias, Chihuahua", "Mexico", "North America", 28.1928, -105.4711, "Rio Conchos: Irrigated pecan orchards, chile, alfalfa"),
    ("Zamora, Michoacan", "Mexico", "North America", 19.9856, -102.2839, "Duero Valley: Export strawberry, blackberry, winter wheat"),
    ("Irapuato, Guanajuato", "Mexico", "North America", 20.6767, -101.3563, "El Bajio Granary: Sorghum, maize, irrigated winter barley/broccoli"),
    ("Tehuacan, Puebla", "Mexico", "North America", 18.4627, -97.3928, "Semi-arid valley: Rainfed/irrigated maize, amaranth, onion"),
    ("Tapachula, Chiapas", "Mexico", "North America", 14.9099, -92.2647, "Soconusco Tropical Coast: Banana, mango, cacao, coffee piedmont"),
    ("Merida, Yucatan", "Mexico", "North America", 20.9674, -89.5926, "Yucatan Karst Plain: Citrus, tropical pasture, henequen"),
    ("Torreon, Coahuila", "Mexico", "North America", 25.5428, -103.4068, "Comarca Lagunera: Irrigated forage corn, alfalfa, cotton"),

    # --- BATCH 3: Brazil & Paraguay (15) ---
    ("Lucas do Rio Verde, Mato Grosso", "Brazil", "South America", -13.0500, -55.9100, "Mid-North Cerrado: Safra soy + Safrinha corn double crop"),
    ("Rondonopolis, Mato Grosso", "Brazil", "South America", -16.4674, -54.6360, "Southern Mato Grosso: Soybean, cotton, cattle corridor"),
    ("Rio Verde, Goias", "Brazil", "South America", -17.7925, -50.9192, "Southwestern Goias: Intensive soy, corn, poultry/swine grain"),
    ("Dourados, Mato Grosso do Sul", "Brazil", "South America", -22.2231, -54.8118, "Southern Maracaju: Summer soy + winter corn/wheat"),
    ("Cascavel, Parana", "Brazil", "South America", -24.9578, -53.4595, "Western Parana: Subtropical double-crop soy/wheat and soy/corn"),
    ("Uberaba, Minas Gerais", "Brazil", "South America", -19.7472, -47.9392, "Triangulo Mineiro: Sugarcane, soybean, corn, Zebu genetics"),
    ("Ribeirao Preto, Sao Paulo", "Brazil", "South America", -21.1775, -47.8103, "World Sugarcane Capital: Intensive ethanol/sugar, peanut"),
    ("Cruz Alta, Rio Grande do Sul", "Brazil", "South America", -28.6389, -53.6067, "Highland Gaucho: Winter wheat/barley/canola + summer soy"),
    ("Bage, Rio Grande do Sul", "Brazil", "South America", -31.3314, -54.1069, "Southern Pampas: Irrigated lowland rice, livestock grazing"),
    ("Balsas, Maranhao", "Brazil", "South America", -7.5322, -46.0356, "MATOPIBA Northern Frontier: Single/double-crop cerrado soy"),
    ("Urucui, Piaui", "Brazil", "South America", -7.2289, -44.5561, "Piaui Cerrado Plateau: Highly mechanized rainfed soy and corn"),
    ("Primavera do Leste, Mato Grosso", "Brazil", "South America", -15.5583, -54.2969, "East MT Plateau: High-yield cotton and early-cycle soy"),
    ("Katuete, Canindeyu", "Paraguay", "South America", -24.2483, -54.7578, "Eastern Paraguay: Intensive mechanized soy + Safrinha corn"),
    ("Santa Rita, Alto Parana", "Paraguay", "South America", -25.7867, -55.0867, "Parana Basin: Main grain production center in Paraguay"),
    ("Colonia Independencia, Guaira", "Paraguay", "South America", -25.6833, -56.2667, "Central Valley: Sugarcane, yerba mate, smallholder corn/soy"),

    # --- BATCH 4: Argentina, Andean & Pacific South America (15) ---
    ("Venado Tuerto, Santa Fe", "Argentina", "South America", -33.7456, -61.9688, "Core Humid Pampas: World seed corn capital, soybean, wheat"),
    ("Junin, Buenos Aires", "Argentina", "South America", -34.5838, -60.9431, "Northwest BA Pampas: Wheat/Soy 2da rotation, full-season corn"),
    ("Tandil, Buenos Aires", "Argentina", "South America", -37.3217, -59.1332, "Serrano Pampas: Malting barley, bread wheat, seed potato"),
    ("Marcos Juarez, Cordoba", "Argentina", "South America", -32.6975, -62.1067, "INTA Core Hub: Premier Argentine grain yields (Wheat/Soy, Corn)"),
    ("Rafaela, Santa Fe", "Argentina", "South America", -31.2503, -61.4867, "Argentine Dairy Basin: Alfalfa pastures, corn silage, soybean"),
    ("Parana, Entre Rios", "Argentina", "South America", -31.7319, -60.5238, "Mesopotamia: Rolling Vertisols, wheat, soybean, citrus"),
    ("Roque Saenz Pena, Chaco", "Argentina", "South America", -26.7852, -60.4388, "Dry Chaco Plains: Cotton, sunflower, grain sorghum"),
    ("San Miguel de Tucuman", "Argentina", "South America", -26.8083, -65.2176, "Tucuman Piedmont: World leader in lemon export, sugarcane"),
    ("Rancagua, O'Higgins", "Chile", "South America", -34.1708, -70.7444, "Cachapoal Valley: Irrigated stone fruit, table grapes, hybrid seed"),
    ("Chillan, Nuble", "Chile", "South America", -36.6067, -72.1033, "Central-South Valley: Winter wheat, sugar beet, blueberries"),
    ("Osorno, Los Lagos", "Chile", "South America", -40.5739, -73.1335, "Southern Lake District: Perennial dairy pasture, winter wheat/barley"),
    ("Ica", "Peru", "South America", -14.0678, -75.7286, "Coastal Desert: Drip-irrigated asparagus, table grapes, avocado"),
    ("Chiclayo, Lambayeque", "Peru", "South America", -6.7714, -79.8409, "Northern Coastal Valley: Tinajones canal irrigated rice and sugarcane"),
    ("Espinal, Tolima", "Colombia", "South America", 4.1492, -74.8844, "Upper Magdalena Valley: Bimodal irrigated paddy rice and cotton"),
    ("Monteria, Cordoba", "Colombia", "South America", 8.7479, -75.8814, "Sinu River Valley: Tropical livestock grazing, corn, cotton"),

    # --- BATCH 5: Western & Northern Europe (15) ---
    ("Rennes, Brittany", "France", "Europe", 48.1173, -1.6778, "Armorican Massif: Oceanic dairy forage, winter wheat, maize silage"),
    ("Reims, Champagne", "France", "Europe", 49.2583, 4.0317, "Champagne Chalk Plain: High-yield winter wheat, spring barley, alfalfa"),
    ("Toulouse, Haute-Garonne", "France", "Europe", 43.6047, 1.4442, "Lauragais / Garonne: Durum wheat, sunflower, grain maize"),
    ("Dijon, Bourgogne", "France", "Europe", 47.3220, 5.0415, "Burgundy Plains: Winter rapeseed, winter wheat, malting barley"),
    ("Munster, Westphalia", "Germany", "Europe", 51.9607, 7.6261, "Westphalian Bay: Intensive pork/dairy silage maize, winter barley"),
    ("Magdeburg, Saxony-Anhalt", "Germany", "Europe", 52.1205, 11.6276, "Magdeburger Boerde: Prime chernozem sugar beet and winter wheat"),
    ("Flensburg, Schleswig-Holstein", "Germany", "Europe", 54.7833, 9.4333, "Baltic Coast: High-yielding maritime winter wheat and winter oilseed rape"),
    ("Lincoln, Lincolnshire", "UK", "Europe", 53.2307, -0.5406, "Lincolnshire Fens: Wheat, ware potatoes, brassicas, sugar beet"),
    ("York, Yorkshire", "UK", "Europe", 53.9599, -1.0873, "Vale of York: Winter wheat, spring malting barley, oilseed rape"),
    ("Kilkenny, Leinster", "Ireland", "Europe", 52.6541, -7.2448, "Sunny South East: Spring malting barley, winter wheat, dairy pasture"),
    ("Gent, East Flanders", "Belgium", "Europe", 51.0543, 3.7174, "Flemish Sandy Loam: Processing potatoes, sugar beet, winter cereals"),
    ("Groningen, Groningen", "Netherlands", "Europe", 53.2194, 6.5665, "Veenkolonien: Industrial starch potatoes, sugar beet, winter wheat"),
    ("Odense, Funen", "Denmark", "Europe", 55.4038, 10.4024, "Danish Islands: Winter wheat, spring feed barley, winter rape"),
    ("Uppsala, Uppland", "Sweden", "Europe", 59.8586, 17.6389, "Central Swedish Plain: Spring barley, spring oats, winter wheat"),
    ("Seinajoki, Southern Ostrobothnia", "Finland", "Europe", 62.7903, 22.8403, "Bothnian Lowlands: Subarctic short-season feed barley and oats"),

    # --- BATCH 6: Central, Southern & Eastern Europe (15) ---
    ("Bologna, Emilia-Romagna", "Italy", "Europe", 44.4949, 11.3426, "Po Valley South: Winter wheat, double-crop soy/maize, fruit orchards"),
    ("Foggia, Apulia", "Italy", "Europe", 41.4622, 15.5447, "Tavoliere delle Puglie: Italy's durum wheat capital, processing tomato"),
    ("Zaragoza, Aragon", "Spain", "Europe", 41.6488, -0.8891, "Middle Ebro Valley: Semi-arid, irrigated alfalfa, stone fruit, corn"),
    ("Cordoba, Andalusia", "Spain", "Europe", 37.8882, -4.7794, "Campiña de Cordoba: Dryland olive groves, winter wheat, sunflower"),
    ("Albacete, Castilla-La Mancha", "Spain", "Europe", 38.9943, -1.8585, "La Mancha High Plain: Dryland malting barley, garlic, vineyard"),
    ("Evora, Alentejo", "Portugal", "Europe", 38.5714, -7.9135, "Central Alentejo: Rainfed winter wheat, cork oak montado, olive"),
    ("Karditsa, Thessaly", "Greece", "Europe", 39.3644, 21.9214, "Thessalian Plain: High-yield irrigated cotton, grain maize, wheat"),
    ("Stara Zagora, Thrace", "Bulgaria", "Europe", 42.4258, 25.6345, "Upper Thracian Plain: Winter wheat, sunflower, grain corn"),
    ("Timisoara, Banat", "Romania", "Europe", 45.7537, 21.2257, "Banat Plain: Fertile chernozem winter wheat, corn, sunflower"),
    ("Debrecen, Great Plain", "Hungary", "Europe", 47.5316, 21.6273, "Hajdusag / Alfold: Intensive grain maize, sunflower, wheat"),
    ("Trnava, Danubian Lowland", "Slovakia", "Europe", 48.3774, 17.5883, "Danubian Plain: Sugar beet, malting barley, winter wheat, corn"),
    ("Lublin, Lublin Upland", "Poland", "Europe", 51.2465, 22.5684, "Lublin Loess: Winter wheat, hops, soft berries, sugar beet"),
    ("Vinnytsia, Podolia", "Ukraine", "Europe", 49.2331, 28.4682, "Central Forest-Steppe: Sugar beet capital, corn, winter wheat"),
    ("Dnipro, Steppe", "Ukraine", "Europe", 48.4647, 35.0462, "Southern Black Soil Steppe: Sunflower, winter wheat, corn"),
    ("Novi Sad, Vojvodina", "Serbia", "Europe", 45.2671, 19.8335, "Pannonian Basin: Black soil grain maize, soybean, sunflower"),

    # --- BATCH 7: Sub-Saharan Africa - West & Central (15) ---
    ("Zaria, Kaduna", "Nigeria", "Africa", 11.0855, 7.7199, "Northern Guinea Savanna: Grain corn, soybean, sorghum, cowpea"),
    ("Makurdi, Benue", "Nigeria", "Africa", 7.7322, 8.5391, "Southern Guinea Savanna: Yam, cassava, soybean, sesame"),
    ("Sokoto, Sokoto", "Nigeria", "Africa", 13.0609, 5.2476, "Sudan Savanna: Pearl millet, sorghum, cowpea, garlic"),
    ("Maradi, Maradi", "Niger", "Africa", 13.5000, 7.1000, "Sahelian Savanna: Cowpea hub of West Africa, pearl millet, groundnut"),
    ("Sikasso, Sikasso", "Mali", "Africa", 11.3176, -5.6665, "South Sudanian Savanna: Mali's breadbasket, maize, cotton, mango"),
    ("Koutiala, Sikasso", "Mali", "Africa", 12.3917, -5.4642, "Cotton Basin: White gold capital, sorghum, millet, groundnut"),
    ("Dedougou, Mouhoun", "Burkina Faso", "Africa", 12.4634, -3.4607, "Boucle du Mouhoun: Burkina granary, maize, cotton, sorghum"),
    ("Tamale, Northern", "Ghana", "Africa", 9.4008, -0.8393, "Guinea Savanna: Maize, yam, soybean, rice, groundnut"),
    ("Korhogo, Savanes", "Cote d'Ivoire", "Africa", 9.4580, -5.6296, "Northern Savanna: Cotton, cashew nut, grain corn, groundnut"),
    ("Parakou, Borgou", "Benin", "Africa", 9.3372, 2.6303, "Central Benin Savanna: Cotton, yam, maize, soybean"),
    ("Ngaoundere, Adamawa", "Cameroon", "Africa", 7.3276, 13.5847, "Adamawa Plateau: High-elevation savannas, maize, cattle"),
    ("Maroua, Far North", "Cameroon", "Africa", 10.5956, 14.3247, "Sudano-Sahelian: Rainfed red sorghum (Mouskwari), cotton, cowpea"),
    ("Sarh, Moyen-Chari", "Chad", "Africa", 9.1429, 18.3923, "Southern Chad: Cotton, sorghum, groundnut, rice"),
    ("Bafata, Bafata", "Guinea-Bissau", "Africa", 12.1648, -14.6592, "Geba River Basin: Cashew orchards, upland rice, groundnut"),
    ("Kaolack, Kaolack", "Senegal", "Africa", 14.1500, -16.0833, "Senegalese Groundnut Basin: Peanuts, pearl millet, watermelon"),

    # --- BATCH 8: Sub-Saharan Africa - East & Southern (15) ---
    ("Kitale, Trans-Nzoia", "Kenya", "Africa", 1.0157, 35.0062, "Kenya Maize Granary: High-potential plateau, long-cycle maize, seed beans"),
    ("Nyeri, Central Kenya", "Kenya", "Africa", -0.4197, 36.9476, "Aberdare / Mt Kenya Piedmont: Arabica coffee, tea, dairy, horticulture"),
    ("Morogoro, Morogoro", "Tanzania", "Africa", -6.8278, 37.6591, "Kilombero/Wami Valley: Sugarcane, paddy rice, maize"),
    ("Mbeya, Southern Highlands", "Tanzania", "Africa", -8.9094, 33.4608, "Southern Highlands Granary: Maize, round potatoes, pyrethrum, tea"),
    ("Gulu, Northern", "Uganda", "Africa", 2.7747, 32.2990, "Northern Savanna: Finger millet, sesame, cassava, sunflower"),
    ("Mbarara, Western", "Uganda", "Africa", -0.6072, 30.6545, "Ankole Basin: East African Highland cooking bananas (matooke), dairy"),
    ("Hawassa, Sidama", "Ethiopia", "Africa", 7.0504, 38.4764, "Southern Rift Valley: Enset, haricot bean, maize, coffee"),
    ("Jimma, Oromia", "Ethiopia", "Africa", 7.6734, 36.8344, "Southwestern Highlands: Origin of Arabica coffee, teff, maize"),
    ("Chipata, Eastern", "Zambia", "Africa", -13.6333, 32.6500, "Eastern Plateau: Smallholder maize, groundnut, burley tobacco"),
    ("Mkushi, Central", "Zambia", "Africa", -13.6202, 29.3941, "Mkushi Farm Block: Commercial center for irrigated wheat, summer soy"),
    ("Lilongwe, Central", "Malawi", "Africa", -13.9626, 33.7741, "Lilongwe Plain: Flue-cured tobacco, maize, groundnut, soybean"),
    ("Chimoio, Manica", "Mozambique", "Africa", -19.1167, 33.4833, "Beira Corridor: Maize, macadamia, commercial grain plateau"),
    ("Bethal, Mpumalanga", "South Africa", "Africa", -26.4583, 29.4667, "Eastern Highveld: Commercial dryland maize, sunflower, potato"),
    ("Lichtenburg, North West", "South Africa", "Africa", -26.1520, 26.1594, "Western Maize Triangle: Sandy loam dryland maize, sunflower, groundnut"),
    ("Ceres, Western Cape", "South Africa", "Africa", -33.3700, 19.3100, "Warm Bokkeveld: Mediterranean deciduous pome fruit, winter wheat"),

    # --- BATCH 9: North Africa, Middle East & Central Asia (15) ---
    ("Damanhour, Beheira", "Egypt", "Africa", 31.0425, 30.4689, "Western Nile Delta: Potato export, citrus, winter wheat, summer rice"),
    ("Mansoura, Dakahlia", "Egypt", "Africa", 31.0409, 31.3785, "Eastern Nile Delta: Paddy rice, cotton, winter wheat, berseem clover"),
    ("Meknes, Fes-Meknes", "Morocco", "Africa", 33.8938, -5.5516, "Saiss Plain: Rainfed soft/durum wheat, olive orchards, wine grapes"),
    ("Sidi Bel Abbes, Oran", "Algeria", "Africa", 35.1899, -0.6308, "High Tellian Plateau: Rainfed durum wheat, barley, lentil"),
    ("Beja, Beja", "Tunisia", "Africa", 36.7256, 9.1817, "Medjerda Valley: Tunisia's historic granary, durum wheat, faba bean"),
    ("Sanliurfa, Southeastern Anatolia", "Turkey", "Middle East", 37.1674, 38.7955, "Harran Plain (GAP): World-class irrigated cotton, durum wheat, lentil"),
    ("Tekirdag, Thrace", "Turkey", "Middle East", 40.9833, 27.5167, "Turkish Thrace: Sunflower capital, high-yield winter wheat, canola"),
    ("Irbid, Irbid", "Jordan", "Middle East", 32.5568, 35.8469, "Northern Jordanian Plateau: Rainfed ancient olive groves, winter wheat"),
    ("Zahle, Bekaa", "Lebanon", "Middle East", 33.8463, 35.9020, "Central Bekaa Valley: Irrigated potato, table/wine grapes, winter wheat"),
    ("Gorgan, Golestan", "Iran", "Middle East", 36.8433, 54.4339, "Caspian Subtropical Plain: Soybean, rapeseed, winter wheat, cotton"),
    ("Shiraz, Fars", "Iran", "Middle East", 29.5918, 52.5837, "Southern Zagros Basin: Irrigated wheat, barley, pomegranate, almond"),
    ("Samarkand, Samarkand", "Uzbekistan", "Asia", 39.6542, 66.9597, "Zeravshan Oasis: Irrigated cotton, table grapes, winter wheat"),
    ("Shymkent, Turkistan", "Kazakhstan", "Asia", 42.3417, 69.5901, "Syr Darya Piedmont: Irrigated cotton, melon, winter wheat"),
    ("Kostanay, Kostanay", "Kazakhstan", "Asia", 53.2144, 63.6246, "Virgin Lands Steppe: Spring wheat powerhouse, flax, barley"),
    ("Mary, Mary", "Turkmenistan", "Asia", 37.5938, 61.8317, "Murghab Delta (Karakum): Irrigated cotton, winter wheat, melon"),

    # --- BATCH 10: Asia & Oceania (15) ---
    ("Indore, Madhya Pradesh", "India", "Asia", 22.7196, 75.8577, "Malwa Plateau: Black Vertisol soybean capital, Rabi wheat/chickpea"),
    ("Guntur, Andhra Pradesh", "India", "Asia", 16.3067, 80.4365, "Krishna Delta: World-famous red chilli, cotton, tobacco, rice"),
    ("Mymensingh Sadar", "Bangladesh", "Asia", 24.7471, 90.4203, "Old Brahmaputra Floodplain: Intensive Boro-Aman rice, aquaculture"),
    ("Dinajpur Sadar", "Bangladesh", "Asia", 25.6217, 88.6355, "Himalayan Piedmont: Premier aromatic rice (Kataribhog), litchi, wheat"),
    ("Jessore Sadar", "Bangladesh", "Asia", 23.1667, 89.2167, "Lower Ganges Plain: Winter vegetable granary, floriculture, Boro rice"),
    ("Changchun, Jilin", "China", "Asia", 43.8171, 125.3235, "Northeast Corn Belt: High-yielding single-season grain maize, soy"),
    ("Wuhan, Hubei", "China", "Asia", 30.5928, 114.3055, "Jianghan Plain: Middle Yangtze double-crop rice and winter rapeseed"),
    ("Khon Kaen, Isan", "Thailand", "Asia", 16.4419, 102.8360, "Khorat Plateau: Rainfed cassava, sugarcane, KDML105 jasmine rice"),
    ("Battambang, Battambang", "Cambodia", "Asia", 13.0957, 103.2022, "Tonle Sap Basin: Rice bowl of Cambodia, wet season aromatic rice"),
    ("Davao City, Davao", "Philippines", "Asia", 7.1907, 125.4553, "Southern Mindanao: Year-round Cavendish banana, cacao, coconut"),
    ("Malang, East Java", "Indonesia", "Asia", -7.9666, 112.6326, "Brantas Basin Highland: Upland vegetables, apple, sugarcane, rice"),
    ("Dubbo, Central West NSW", "Australia", "Oceania", -32.2435, 148.6011, "Macquarie Valley: Winter wheat/canola/barley, irrigated cotton"),
    ("Esperance, Western Australia", "Australia", "Oceania", -33.8611, 121.8919, "South Coast Sandplain: Mediterranean winter wheat, canola, barley"),
    ("Palmerston North, Manawatu", "New Zealand", "Oceania", -40.3523, 175.6082, "Manawatu Plains: Perennial rye/clover dairy, maize silage, sheep"),
    ("Invercargill, Southland", "New Zealand", "Oceania", -46.4132, 168.3538, "Southland Plains: Cool maritime, intensive dairy grazing, winter oats")
]

print(f"Total candidate locations: {len(RAW_150)}")

# Check duplicate with BENCHMARK_100
existing_coords = set((round(loc.lat, 2), round(loc.lon, 2)) for loc in BENCHMARK_100)
for item in RAW_150:
    c = (round(item[3], 2), round(item[4], 2))
    assert c not in existing_coords, f"Duplicate coordinate found: {item[0]}"
print("Verified: 0% overlap with the previous 100 benchmark locations!")

# Load or fetch climate cache
cache = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r") as f:
            cache = json.load(f)
    except Exception:
        cache = {}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

uncached = [item for item in RAW_150 if f"{item[3]:.4f}_{item[4]:.4f}" not in cache]
print(f"Locations needing NASA POWER fetch: {len(uncached)}")

def fetch_pt(item):
    lat, lon = item[3], item[4]
    key = f"{lat:.4f}_{lon:.4f}"
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,T2M_MIN,T2M_MAX,PRECTOTCORR&community=AG&latitude={lat:.4f}&longitude={lon:.4f}&format=JSON"
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/2.0-Audit150"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    params = data.get("properties", {}).get("parameter", {})
    tmean = [float(params.get("T2M", {}).get(m, 20.0)) for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]]
    tmin = [float(params.get("T2M_MIN", {}).get(m, 15.0)) for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]]
    tmax = [float(params.get("T2M_MAX", {}).get(m, 25.0)) for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]]
    prec_rate = [float(params.get("PRECTOTCORR", {}).get(m, 2.0)) for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]]
    rain = [round(prec_rate[i] * DAYS_IN_MONTHS[i], 1) for i in range(12)]
    return key, {
        "monthly_tmean": tmean,
        "monthly_tmin": tmin,
        "monthly_tmax": tmax,
        "monthly_rain": rain
    }

if uncached:
    print(f"Fetching {len(uncached)} points in parallel (max_workers=10)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(fetch_pt, uncached)
        for key, clim in results:
            cache[key] = clim
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)
    print("Cache updated and saved!")

fetcher = GlobalEnvFetcher()

# Build 10 batches of 15 locations each
batches_def = [
    ("batch01_us_heartland", RAW_150[0:15]),
    ("batch02_canada_mexico", RAW_150[15:30]),
    ("batch03_brazil_paraguay", RAW_150[30:45]),
    ("batch04_argentina_andean", RAW_150[45:60]),
    ("batch05_west_north_europe", RAW_150[60:75]),
    ("batch06_central_east_europe", RAW_150[75:90]),
    ("batch07_west_central_africa", RAW_150[90:105]),
    ("batch08_east_south_africa", RAW_150[105:120]),
    ("batch09_mideast_northafrica_centralasia", RAW_150[120:135]),
    ("batch10_asia_oceania", RAW_150[135:150]),
]

for b_id, items in batches_def:
    batch_records = []
    for item in items:
        name, country, continent, lat, lon, desc = item
        key = f"{lat:.4f}_{lon:.4f}"
        clim = cache[key]
        calc_lgp, _ = fetcher.compute_daily_lgp_and_k(
            clim["monthly_tmean"], clim["monthly_tmin"], clim["monthly_tmax"], clim["monthly_rain"],
            lat=lat
        )
        cal = UniversalSeasonalSegmenter.segment_calendar(
            lat, lon,
            clim["monthly_tmean"], clim["monthly_tmin"], clim["monthly_tmax"], clim["monthly_rain"],
            lgp_days=calc_lgp
        )
        s1 = cal.seasons["season_1"]
        s2 = cal.seasons["season_2"]
        s3 = cal.seasons["season_3"]

        batch_records.append({
            "name": name,
            "country": country,
            "continent": continent,
            "lat": lat,
            "lon": lon,
            "description": desc,
            "annual_rain_mm": round(sum(clim["monthly_rain"]), 1),
            "annual_mean_temp_c": round(sum(clim["monthly_tmean"]) / 12.0, 1),
            "computed_lgp_days": calc_lgp,
            "deduced_regime": cal.regime_classification,
            "deduced_k": cal.cropping_intensity_k,
            "has_freeze_dormancy": any(s.regime_type == "FREEZE_DORMANCY" for s in cal.seasons.values()),
            "season_1": {
                "window": s1.calendar_window,
                "start_month": MONTH_FULL_NAMES[s1.start_month],
                "end_month": MONTH_FULL_NAMES[s1.end_month],
                "duration_months": s1.duration_months,
                "is_fallow": s1.is_fallow,
                "role": s1.role
            },
            "season_2": {
                "window": s2.calendar_window,
                "duration_months": s2.duration_months,
                "is_fallow": s2.is_fallow,
                "fallow_reason": s2.fallow_reason
            },
            "season_3": {
                "window": s3.calendar_window,
                "duration_months": s3.duration_months,
                "is_fallow": s3.is_fallow,
                "fallow_reason": s3.fallow_reason
            }
        })
    out_path = f"data/audit_150_batches/{b_id}.json"
    with open(out_path, "w") as f:
        json.dump(batch_records, f, indent=2)
    print(f"Generated {out_path} ({len(batch_records)} locations)")

print("\nAll 150 brand-new locations processed and partitioned into 10 audit batches!")
