# Independent Agronomic Systems & Crop Calendar Audit Report
**Batch 02: Canada & Mexico (15 Strategic Agricultural Benchmarks)**
**Auditor**: Independent Senior Agronomist & Agro-Meteorological Systems Auditor
**Target Data**: `/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/audit_150_batches/batch02_canada_mexico.json`
**Reference Standards**: Agriculture & Agri-Food Canada (AAFC), Canola Council of Canada, Manitoba Agriculture & MASC, Saskatchewan Ministry of Agriculture & SCIC, Alberta Agriculture & Forestry (AFSC), OMAFRA (Ontario), MAPAQ & CRAAQ (Quebec), Prince Edward Island Potato Board, INIFAP Mexico (CEBAJ, CENEB, Costa de Hermosillo, Rosario Izapa, Delicias, La Laguna), SIAP Mexico (SADER), CONAGUA (Distritos de Riego 005, 011, 017, 075).

---

## 1. Executive Summary

An exhaustive agro-ecological audit was conducted on the Crop Calendar Deduced Engine across 15 agricultural anchor locations in Canada and Mexico (Batch 02). The evaluation scrutinized:
1. **Regime Classification Authenticity** (Köppen-Geiger / FAO GAEZ agro-climatic validity).
2. **Primary Growing Season Window Alignment** against documented planting, flowering, and harvest dates.
3. **Freeze Dormancy Biological Accuracy** (LGP5 biological zero thresholds and cold tolerance limits).
4. **Cropping Intensity Factor (K)** realism (distinguishing true rainfed water-balance capacity from artificial irrigation infrastructure).

### Key Performance Metrics
* **Total Evaluated Locations**: 15
* **Validated (Exact / Near-Exact Match)**: 7 locations (46.7%)
* **Acceptable (Agronomically Defensible Rainfed Window / Minor Boundary Delta)**: 2 locations (13.3%)
* **Defect (Agronomic Failure, False Regime, or Fatal Code Artifact)**: 6 locations (40.0%)
* **Overall Regional Accuracy Score (Validated + Acceptable)**: **60.0% (9 / 15)**

### Regional Breakdown
* **Canada (AAFC / Prairies, Great Lakes, St. Lawrence, Atlantic Maritime)**: **100% Passing** (6/6 Validated: Brandon, Saskatoon, Red Deer, Chatham-Kent, Saint-Hyacinthe, Charlottetown). The cold-climate temperate continental engine demonstrates flawless fidelity across Canadian latitudes.
* **Mexico (INIFAP / SIAP / CONAGUA)**: **33.3% Passing** (1 Validated: Tapachula; 2 Acceptable: Los Mochis, Torreon; 6 Defects: Hermosillo, Delicias, Zamora, Irapuato, Tehuacan, Merida). The engine suffers severe systemic defects in subtropical arid oasis zones, karst terrain, and dry-winter monsoon double-cropping heuristics.

---

## 2. Master Audit Scorecard

| # | Location | Deduced Regime | Deduced Window (Season 1) | Freeze Dormancy | Deduced K | Real-World Official Calendar & Regime | Rainfed vs Irrigated Status | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **Brandon, MB** (CAN) | TEMPERATE_CONTINENTAL_FROST | May – September (5 mo) | True (Oct–Apr) | 1 | Aspen Parkland / Black Soil: Frost-free ~106d (May 27–Sep 10). Spring wheat/canola seeded May; harvest Aug–Sep. | Rainfed K=1 strictly. Sub-zero winter halt. | **[VALIDATED]** |
| 2 | **Saskatoon, SK** (CAN) | TEMPERATE_CONTINENTAL_FROST | May – September (5 mo) | True (Oct–Apr) | 1 | Dark Brown Soil Zone: Frost-free ~115d (May 21–Sep 15). Lentil/chickpea/canola/wheat seeded May; harvest Aug–Sep. | Rainfed K=1 strictly. Severe winter dormancy. | **[VALIDATED]** |
| 3 | **Red Deer, AB** (CAN) | TEMPERATE_CONTINENTAL_FROST | May – September (5 mo) | True (Oct–Apr) | 1 | Central Alberta Aspen Parkland: Frost-free ~107d (May 25–Sep 9). Barley/canola seeded May; harvest Aug–Sep. | Rainfed K=1 strictly. Deep winter freeze. | **[VALIDATED]** |
| 4 | **Chatham-Kent, ON** (CAN) | TEMPERATE_CONTINENTAL_FROST | May – October (6 mo) | True (Nov–Mar) | 1 | Lake Erie Granary: Frost-free late Apr–late Oct. 3,400 CHU. Full-season corn/soybean seeded May; harvest Oct–Nov. | Rainfed K=1 strictly. Full-season row crop anchor. | **[VALIDATED]** |
| 5 | **Saint-Hyacinthe, QC** (CAN) | TEMPERATE_CONTINENTAL_FROST | May – September (5 mo) | True (Nov–Mar) | 1 | St. Lawrence Lowlands: Frost-free mid-May–late Sep. Grain corn/soybean/dairy silage seeded May; harvest Sep–Oct. | Rainfed K=1 strictly. Extreme winter freeze. | **[VALIDATED]** |
| 6 | **Charlottetown, PE** (CAN) | TEMPERATE_CONTINENTAL_FROST | June – October (5 mo) | True (Nov–Apr) | 1 | Atlantic Maritime: Frost-free May 10–Oct 14 (~130d). Seed/table potatoes planted May–Jun; harvest Sep–Oct. | Rainfed K=1 strictly. Late cool spring captures bulking. | **[VALIDATED]** |
| 7 | **Hermosillo, SON** (MEX) | TROPICAL_MONOMODAL_RAIN | July – September (3 mo) | False | 1 | Sonoran Arid Desert (BWh): 381mm rain, PET 1563mm. O-I wheat seeded Nov–Dec, harvest Apr–May; table grapes May–Jun. | Rainfed summer impossible (49°C heat blast). Winter commercial cycle marked fallow! | **[DEFECT]** |
| 8 | **Los Mochis, SIN** (MEX) | TROPICAL_MONOMODAL_RAIN | July – September (3 mo) | False | 1 | Valle del Fuerte (BSh): Rainfed temporal monsoon Jul–Sep (422mm rain). Irrigated O-I white corn seeded Nov, harvest May. | Rainfed K=1 valid for monsoon temporal; Irrigated commercial granary relies on dams. | **[ACCEPTABLE]** |
| 9 | **Delicias, CHIH** (MEX) | HUMID_SUBTROPICAL | April – October (7 mo) | False | 1 | Chihuahuan Desert (BWk/BSh): 328mm rain. Pecan orchards, alfalfa, chile jalapeño, silage corn (100% DR-005 irrigation). | Regime absurdly misclassified as HUMID; April (4mm rain) rainfed crop impossible. | **[DEFECT]** |
| 10 | **Zamora, MICH** (MEX) | TROPICAL_MONOMODAL_RAIN | June – October (5 mo) [S2: Nov–Jan (3 mo)] | False | 2 | Duero Valley: Summer maize rainfed Jun–Oct. Winter Nov–Jan has only 30mm rain; PET >120mm/mo. Export berries 100% drip. | Rainfed K=2 impossible due to bone-dry winter (30mm rain). Second crop fails without irrigation. | **[DEFECT]** |
| 11 | **Irapuato, GTO** (MEX) | TROPICAL_MONOMODAL_RAIN | June – September (4 mo) [S2: Oct–Dec (3 mo)] | False | 2 | El Bajío: P-V maize/sorghum rainfed Jun–Sep. O-I wheat/barley/broccoli Nov–Apr is 100% deep-well/canal irrigated. | Rainfed K=2 impossible. Oct–Dec has only 61mm rain; winter has zero rain. Mirrors Celaya defect. | **[DEFECT]** |
| 12 | **Tehuacan, PUE** (MEX) | TROPICAL_MONOMODAL_RAIN | May – October (6 mo) [S2: Nov–Jan (3 mo)] | False | 2 | Semi-arid valley: Rainfed milpa & amaranth May–Oct (816mm rain). Dry winter Nov–Jan has only 48mm rain. | Rainfed K=2 unviable. Dry winter requires valley spring irrigation for onions/vegetables. | **[DEFECT]** |
| 13 | **Tapachula, CHIS** (MEX) | TROPICAL_MONOMODAL_RAIN | April – November (8 mo) | False | 1 | Soconusco Tropical Coast: 2,570mm rain. Wet season Apr–Nov. Annual crops (maize/soy) single P-V cycle due to rust/pests. | Rainfed K=1 validated for annual crops; dry winter break required. Perennials dominate. | **[VALIDATED]** |
| 14 | **Merida, YUC** (MEX) | TROPICAL_MONOMODAL_RAIN | May – November (7 mo) [S2: Dec–Feb (3 mo)] | False | 2 | Yucatan Karst Plain: Thin calcareous soils (tzek'\''el) have 0 water retention. Milpa Maya strictly P-V temporal. | Rainfed K=2 impossible on porous karst; Dec–Feb has only 95mm rain with high PET. | **[DEFECT]** |
| 15 | **Torreon, COAH** (MEX) | HYPER_ARID_DESERT | Jan – Dec (12 mo Fallow, Mandatory Irrig) | False | 1 | Comarca Lagunera: 274mm rain, PET 1470mm. Forage corn, alfalfa, cotton 100% dependent on Nazas dams & aquifers. | Rainfed LGP=0 validated (commercial rainfed farming impossible). Cosmetic string glitch noted. | **[ACCEPTABLE]** |

---

## 3. Deep-Dive Location Audits

### Location 1: Brandon, Manitoba, Canada
* **Deduced Data**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | S2: `October (1 Month, Fallow)` | S3: `October - April (7 Months, Freeze Fallow)` | Freeze: `True` (Tmin down to -45.2°C) | K: `1`.
* **Official Benchmark (Agriculture & Agri-Food Canada / Manitoba Agriculture & MASC)**:
  * Agro-Climatic Zone: Aspen Parkland / Black Chernozem Soil Zone.
  * Thermal Window: Average last spring frost occurs May 27; average first fall frost occurs September 10 (mean frost-free period: 106 days).
  * Crop Calendars: Canola and Canadian Western Red Spring (CWRS) wheat are seeded May 1–25 as soil warms to ≥5°C; MASC seeding deadlines run June 10–15. Harvest runs late August through late September.
  * Cold Halt: Sub-zero air and soil freeze halts all biological division from October to April.
* **Evaluation**: The May–September window (5 months) perfectly frames the agronomic lifecycle. Single cropping (K=1) is strictly enforced by climate.
* **VERDICT**: **[VALIDATED]**

---

### Location 2: Saskatoon, Saskatchewan, Canada
* **Deduced Data**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | S2: `October (1 Month, Fallow)` | S3: `October - April (7 Months, Freeze Fallow)` | Freeze: `True` (Tmin down to -44.9°C) | K: `1`.
* **Official Benchmark (Saskatchewan Ministry of Agriculture / SCIC / University of Saskatchewan)**:
  * Agro-Climatic Zone: Dark Brown Soil Zone (semi-arid prairie transition).
  * Thermal Window: Average last spring frost is May 21–22; average first fall frost is September 15 (frost-free period: ~115 days).
  * Crop Calendars: Saskatchewan pulse capital (red/green lentils, chickpeas, field peas) and canola/wheat. Seeding commences late April to mid-May once soil hits 3°C–5°C; SCIC final insurance seeding cutoff is June 20. Harvest wraps up in September.
  * Winter Freeze: Deep continental freeze with extreme minimums dropping below -40°C.
* **Evaluation**: Deduced parameters represent a textbook match with Saskatchewan agronomy.
* **VERDICT**: **[VALIDATED]**

---

### Location 3: Red Deer, Alberta, Canada
* **Deduced Data**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | S2: `October (1 Month, Fallow)` | S3: `October - April (7 Months, Freeze Fallow)` | Freeze: `True` (Tmin down to -40.3°C) | K: `1`.
* **Official Benchmark (Alberta Agriculture and Irrigation / AFSC / Lacombe Field Research)**:
  * Agro-Climatic Zone: Central Alberta Aspen Parkland (Zone 3b).
  * Thermal Window: Average last spring frost is May 25; average first fall frost is September 9 (frost-free period: 107 days).
  * Crop Calendars: Malting barley and Argentine canola. Optimum seeding window is May 1–20 to ensure heading before July heat and maturity before early September frost. Harvest occurs August 25–September 30.
* **Evaluation**: Flawless calibration of the short-season Canadian Parkland growing window.
* **VERDICT**: **[VALIDATED]**

---

### Location 4: Chatham-Kent, Ontario, Canada
* **Deduced Data**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - October (6 Months)` | S2: `November (1 Month, Fallow)` | S3: `November - March (5 Months, Freeze Fallow)` | Freeze: `True` (Tmin down to -26.8°C) | K: `1`.
* **Official Benchmark (OMAFRA / Grain Farmers of Ontario / Ridgetown Campus)**:
  * Agro-Climatic Zone: Lake Erie Granary / Southwestern Ontario Carolinian Zone.
  * Thermal Window: Moderated by Lakes Erie and St. Clair. Average last spring frost is late April (~April 27); first fall frost is mid-to-late October. Accumulates Ontario's highest thermal units (3,300 to 3,500+ CHUs).
  * Crop Calendars: Full-season grain corn (Maturity Groups 100–115 CRM) and soybeans (MG 2.5–3.2). Planted late April through May; harvested late October through November.
* **Evaluation**: May–October (6 months) captures the full-season grain corn and soybean physiological cycle before killing freezes in November. K=1 is strictly correct for full-season cash crops.
* **VERDICT**: **[VALIDATED]**

---

### Location 5: Saint-Hyacinthe, Quebec, Canada
* **Deduced Data**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | S2: `October (1 Month, Fallow)` | S3: `November - March (5 Months, Freeze Fallow)` | Freeze: `True` (Tmin down to -40.4°C) | K: `1`.
* **Official Benchmark (MAPAQ Montérégie / CRAAQ / Agrométéo Québec)**:
  * Agro-Climatic Zone: St. Lawrence Lowlands / Vallée du Richelieu.
  * Thermal Window: Last spring frost occurs mid-May (May 10–15); first fall frost occurs late September to early October.
  * Crop Calendars: Grain corn, high-protein soybean, and dairy silage maize. Seeded May 5–25; harvest runs September into October. Winter freeze is absolute from November to March (Tmin -40°C).
* **Evaluation**: Exact alignment with the agro-climatic calendar of southern Quebec.
* **VERDICT**: **[VALIDATED]**

---

### Location 6: Charlottetown, Prince Edward Island, Canada
* **Deduced Data**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `June - October (5 Months)` | S2: `November (1 Month, Fallow)` | S3: `November - April (6 Months, Freeze Fallow)` | Freeze: `True` (Tmin down to -23.6°C) | K: `1`.
* **Official Benchmark (PEI Department of Agriculture / PEI Potato Board / AAFC Harrington)**:
  * Agro-Climatic Zone: Atlantic Maritime Climate Zone.
  * Thermal Window: Spring warming is delayed by cold waters of the Gulf of St. Lawrence (May mean temp is only 8.1°C). Last spring frost is ~May 10; first fall frost is ~October 14.
  * Crop Calendars: World-renowned seed and processing potatoes (Russet Burbank, Shepody, Superior). Field preparation and planting occur mid-to-late May into early June; primary tuber bulking occurs July–August; bulk harvest ramps up in September and must finish by late October before sub-zero soil freezes rot tubers.
* **Evaluation**: The deduced June–October window accurately identifies that the thermal threshold for rapid vegetative canopy development (Tmean ≥ 10°C) is reached in June, concluding with the critical October potato harvest. Fits PEI maritime realities.
* **VERDICT**: **[VALIDATED]**

---

### Location 7: Hermosillo, Sonora, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `July - September (3 Months)` | S2: `October - January (4 Months, Fallow)` | S3: `February - June (5 Months, Fallow)` | Freeze: `False` | K: `1`.
* **Official Benchmark (INIFAP Campo Experimental Costa de Hermosillo / SIAP / SADER)**:
  * Real Agro-Ecological Zone: Sonoran Arid Desert (Köppen BWh). Annual rainfall is only 381.6 mm, while annual PET is 1562.8 mm (Aridity Index 0.244). Latitude is 29.07°N.
  * Commercial Reality: Costa de Hermosillo is a high-technology, deep-well irrigated desert oasis. **The primary economic cycle is Otoño-Invierno (O-I) and Spring Perennials!**
    * Trigo cristalino / durum: Planted November 25 – December 31; harvested April – May.
    * Uva de mesa (Table Grapes): Pruning in December–January; rapid spring growth; export harvest runs late May through June.
    * Citrus & Pecans: Year-round drip irrigation.
  * Summer Climatology: In June, July, and August, maximum temperatures consistently reach **46°C to 49°C**! Rainfed field crop production during July–September is virtually non-existent because extreme heat blast aborts flowers, and vapor pressure deficits overwhelm seedling transpiration.
  * Glaring Algorithmic Defects:
    1. Labeled `TROPICAL_MONOMODAL_RAIN` at 29°N in the Sonoran Desert.
    2. The entire real-world economic growing season (November through June) is marked as FALLOW.
    3. Designated July–September as active rainfed anchor under unlivable 49°C desert heat.
* **VERDICT**: **[DEFECT]** (Catastrophic inversion of the agricultural cycle, false regime, and disregard of lethal summer heat).

---

### Location 8: Los Mochis, Sinaloa, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `July - September (3 Months)` | S2: `October - January (4 Months, Fallow)` | S3: `February - June (5 Months, Fallow)` | Freeze: `False` | K: `1`.
* **Official Benchmark (INIFAP Valle del Fuerte / SIAP / Asociación de Agricultores del Río Fuerte Poniente - AARFS)**:
  * Real Agro-Ecological Dynamics:
    * **Rainfed ("Temporal") Perspective**: Rainfall is concentrated almost exclusively in the North American Monsoon: July (140.4 mm), August (153.5 mm), September (127.8 mm) provide 421.7 mm (78.7% of annual rainfall). Under pure rainfed conditions, smallholders can only sow during July–September (sesame, grain sorghum, drought-tolerant beans). October through June receives virtually no rain (<15 mm/month).
    * **Commercial Irrigated Perspective**: Valle del Fuerte is Mexico's premier white corn granary. Commercial production is conducted in the **Otoño-Invierno (O-I)** cycle under irrigation from the Presa Miguel Hidalgo and Presa Huites: white corn is planted October 25 to November 30 and harvested May to June.
* **Evaluation**: From a purely rainfed agro-hydrological perspective, the engine's identification of July–September (3 months) with K=1 is hydrology-consistent. However, because commercial agriculture is overwhelmingly irrigated winter white corn, the audit must document this divergence. Following the precedent of Culiacán in Batch 1, it is acceptable for rainfed physics.
* **VERDICT**: **[ACCEPTABLE]** (Hydrologically valid for rainfed temporal; note commercial reliance on winter irrigation infrastructure).

---

### Location 9: Delicias, Chihuahua, Mexico
* **Deduced Data**: Regime: `HUMID_SUBTROPICAL` | S1: `April - October (7 Months)` | S2: `November - March (5 Months, Fallow)` | S3: `None` | Freeze: `False` | K: `1`.
* **Official Benchmark (INIFAP Campo Experimental Delicias / Distrito de Riego 005 - Conchos / SIAP)**:
  * Real Agro-Ecological Zone: Chihuahuan Desert / Semi-Arid Steppe (Köppen BWk/BSh). Annual rainfall is only **328.9 mm**, while annual PET is 1418.2 mm (Aridity Index 0.232).
  * Real Agricultural Infrastructure: Agriculture in Delicias is 100% dependent on **Distrito de Riego 005 (DR-005)** fed by Presa La Boquilla and Presa Las Vírgenes on the Río Conchos. Major crops are drip/gravity irrigated pecan orchards (nogal pecanero), multi-cut alfalfa for dairy basins, chile jalapeño, and hybrid silage corn.
  * Egregious Algorithmic Defects:
    1. **False Classification as "HUMID"**: Delicias receives only 328 mm of rain, yet the engine classified it as `HUMID_SUBTROPICAL`! This was caused by an unchecked heuristic in `seasonal_calendar.py` line 160 (`elif annual_tmean < 22.0 and min_monthly_tmean >= 4.0 and abs(lat) >= 23.0`) which lacked any precipitation or aridity threshold!
    2. **Unviable Rainfed Window**: The engine declared an active rainfed growing season of `April - October (7 Months)` for "Soybean, Maize, Peanut, Cotton". In April, Delicias receives **4.5 mm of rain**; in May, **11.2 mm**; while PET exceeds 200 mm/month. Any rainfed seed planted in April would immediately desiccate and die.
* **VERDICT**: **[DEFECT]** (Severe code defect: desert classified as humid subtropical; physical impossibility of rainfed April planting).

---

### Location 10: Zamora, Michoacan, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - October (5 Months)` | S2: `November - January (3 Months, Active Growing)` | S3: `February - May (4 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (INIFAP / El Colegio de Michoacán / SIAP / Sistema Producto Fresa)**:
  * Agro-Climatic Zone: Duero Valley / Trans-Mexican Volcanic Belt (Köppen Cwb/Aw). Annual rainfall is 741.3 mm, with 646.2 mm (87.2%) falling between June and October.
  * Real Agricultural Calendars:
    * Primavera-Verano (P-V): June to October rainfed maize and sorghum coincide with the pluvial monsoon.
    * Otoño-Invierno (O-I): Zamora is Mexico's strawberry and berry export capital. Berries, winter wheat, and vegetables grown in November–March require intensive pressurized drip irrigation from deep wells and the Duero River.
  * Engine Defect on Rainfed Double-Cropping:
    * The engine assigned **K = 2** and declared **November - January (3 Months)** as an ACTIVE GROWING season (`is_fallow: false`) on "residual soil moisture".
    * In reality, rainfall in November is 15.0 mm, December is 6.2 mm, and January is 9.6 mm (total 30.8 mm over 3 months!). Monthly PET in Nov–Jan exceeds 100 mm/month.
    * Under rainfed conditions, 30 mm of precipitation cannot support crop germination, vegetative growth, and grain fill. K=2 is an unviable artifact.
* **VERDICT**: **[DEFECT]** (Invalid rainfed double-cropping K=2; November–January active season with 30 mm rainfall is agronomically unsupportable).

---

### Location 11: Irapuato, Guanajuato, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - September (4 Months)` | S2: `October - December (3 Months, Active Growing)` | S3: `January - May (5 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (INIFAP Campo Experimental Bajío - CEBAJ / Distrito de Riego 011 / SIAP)**:
  * Agro-Climatic Zone: El Bajío Granary (Köppen BSk/Cwb). Annual rainfall is 721.7 mm.
  * Real Agricultural Calendars:
    * Primavera-Verano (P-V, June–October): Maize and sorghum grown under rainfed (temporal) or irrigation. S1 (June–September) matches this window.
    * Otoño-Invierno (O-I, November–April): Wheat, malting barley, broccoli, and garlic. INIFAP CEBAJ agronomic manuals state unequivocally that **O-I production is 100% dependent on irrigation**. Rainfall in winter is near zero (Nov: 13 mm, Dec: 5 mm, Jan: 10 mm).
  * Identical Defect to Celaya (Batch 1):
    * The engine deduced **K = 2** and declared October–December as an active growing season. Total rainfall in Oct–Dec is only 61 mm, followed by bone-dry winter months. Rainfed double-cropping cannot mature in El Bajío.
* **VERDICT**: **[DEFECT]** (Exact replica of Batch 1 Celaya defect: ungrounded rainfed K=2 based on phantom winter moisture).

---

### Location 12: Tehuacan, Puebla, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - October (6 Months)` | S2: `November - January (3 Months, Active Growing)` | S3: `February - April (3 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (INIFAP / Colegio de Postgraduados / SIAP Puebla)**:
  * Agro-Climatic Zone: Tehuacán-Cuicatlán Biosphere Valley (Köppen BSh/Cwb). Annual rainfall is 919.9 mm, with 816.5 mm falling between May and October.
  * Real Agricultural Calendars:
    * S1 (May–October, 6 months): Accurately captures the primary monomodal temporal rainy season for traditional milpa (maize, beans) and drought-hardy amaranth.
    * S2 (November–January, 3 months): Total rainfall across Nov–Jan is only 48.1 mm (Nov 25.2 mm, Dec 10.5 mm, Jan 12.4 mm). Commercial winter crops (onions, garlic, tomatoes) are grown exclusively under spring/well irrigation.
  * Defect: The engine assigned K=2 with an active non-fallow Season 2. Even drought-resistant pulses cannot complete a commercial cycle under rainfed conditions with 48 mm total rainfall.
* **VERDICT**: **[DEFECT]** (False rainfed K=2; dry winter cannot support an active second crop).

---

### Location 13: Tapachula, Chiapas, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - November (8 Months)` | S2: `December - January (2 Months, Fallow)` | S3: `February - March (2 Months, Fallow)` | Freeze: `False` | K: `1`.
* **Official Benchmark (INIFAP Campo Experimental Rosario Izapa / SIAP / Asociación Agrícola de Productores de Soya del Soconusco)**:
  * Agro-Climatic Zone: Soconusco Tropical Coast (Köppen Aw/Am). Annual rainfall is **2,570.4 mm**.
  * Seasonality: Single massive monomodal monsoon. Rains begin in April (73 mm), surge in May (307 mm), peak in September (474 mm), and taper off in November (82 mm). December through March constitutes a sharp dry season (total 54 mm).
  * Crop Calendars:
    * Annual Field Crops: Soybeans and tropical maize are cultivated strictly in the **Primavera-Verano (P-V)** cycle (June to November). INIFAP Rosario Izapa research explicitly warns against an Otoño-Invierno second crop under temporal due to high risk of Asian soybean rust (*Phakopsora pachyrhizi*), pest explosions, and rapid topsoil desiccation during the rainless winter months.
    * Perennials: Commercial economy is anchored by perennial plantations (mango Ataulfo, Cavendish bananas, cacao, oil palm, robusta coffee in piedmont).
* **Evaluation**: The deduced regime `TROPICAL_MONOMODAL_RAIN` is 100% climatically authentic. The 8-month April–November window captures the entire pluvial season. For annual field crops, enforcing K=1 with a 4-month dry season fallow accurately reflects regional agronomic constraints.
* **VERDICT**: **[VALIDATED]**

---

### Location 14: Merida, Yucatan, Mexico
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - November (7 Months)` | S2: `December - February (3 Months, Active Growing)` | S3: `March - April (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (INIFAP Campo Experimental Mocochá / CICY / UADY / SIAP Yucatan)**:
  * Agro-Climatic Zone: Northern Yucatan Karst Plain (Köppen Aw). Annual rainfall is 1044.9 mm.
  * Geological & Edafic Reality: The Yucatan platform is characterized by **shallow, highly porous, permeable limestone karst (tzek'el / leptosols)** with no surface rivers and virtually **zero soil moisture retention capacity**.
  * Agricultural Dynamics:
    * S1 (May–November, 7 months): Perfectly frames the rainy season (883 mm) for the traditional Milpa Maya (maíz nativo xmejen-nal, ibes/frijol, calabaza) and citrus.
    * S2 (December–February, 3 months): Rainfall in Dec–Feb is only 95.9 mm (Dec 34 mm, Jan 33 mm, Feb 28 mm), while PET is high (>120 mm/mo).
    * Agronomic Defect: Because karstic limestone dries out immediately after rain stops, **no rainfed second crop can survive in December–February**. The Milpa Maya is universally known as a single-cycle temporal system (K=1). The engine's heuristic deduced K=2 and marked Season 2 as active growing, completely disregarding karstic edaphic physics.
* **VERDICT**: **[DEFECT]** (Rainfed K=2 is impossible on porous karst soils; Milpa Maya is strictly K=1).

---

### Location 15: Torreon, Coahuila, Mexico
* **Deduced Data**: Regime: `HYPER_ARID_DESERT` | S1: `January - December (12 Months, Drought Fallow - Irrigation Mandatory)` | S2: `None` | S3: `None` | Freeze: `False` | K: `1`.
* **Official Benchmark (INIFAP Campo Experimental La Laguna / CENID-RASPA / CONAGUA DR-017)**:
  * Agro-Climatic Zone: Comarca Lagunera / Bolsón de Mapimí (Köppen BWh). Annual rainfall is **274.8 mm**, annual PET is 1469.5 mm (Aridity Index 0.187).
  * Real Agricultural Infrastructure: The Comarca Lagunera is Mexico's premier dairy basin. Over 80% of cropland is dedicated to forage corn, alfalfa, and forage sorghum, alongside historical cotton.
  * Rainfed Feasibility: INIFAP La Laguna and CONAGUA explicitly confirm that **rainfed agriculture is economically and agronomically impossible** due to hyper-aridity. Rainfed LGP is 0 days. All production is 100% dependent on irrigation from the Río Nazas (Presa Lázaro Cárdenas) and deep aquifer pumping.
  * Evaluation: The engine's deduced regime `HYPER_ARID_DESERT`, computed LGP = 0, and determination that Season 1 is a 12-month mandatory irrigation fallow is 100% physically and agronomically accurate!
  * Cosmetic Glitch: The generated fallow reason contains a formatting string bug: `"Hyper-arid pluvial desert (274.8 mm < 120 mm)"`. The condition was triggered by `aridity_index < 0.20`, but the template text hardcoded `< 120 mm`. Because the agronomic decision is correct, this is acceptable.
* **VERDICT**: **[ACCEPTABLE]** (Agronomically validated rainfed 0-LGP; cosmetic string artifact noted).

---

## 4. Systemic Engine Bugs & Root Causes

The audit of Batch 02 uncovered four critical algorithmic defects in `UniversalSeasonalSegmenter`:

1. **The "Humid Subtropical Aridity Bypass" (Delicias, Chihuahua)**:
   * **Code Bug (`src/seasonal_calendar.py:160`)**:
     ```python
     elif annual_tmean < 22.0 and min_monthly_tmean >= 4.0 and abs(lat) >= 23.0:
         regime = "HUMID_SUBTROPICAL"
     ```
   * **Root Cause**: This classification rule lacks any precipitation, PET, or aridity index constraint. Any dry desert or steppe location in northern Mexico (or globally) with latitude ≥ 23° and mean temperature < 22°C that escapes the strict hyper-arid check gets classified as `HUMID_SUBTROPICAL`. As a result, Delicias (328 mm rain) was branded humid subtropical and assigned an active rainfed crop in April (4.5 mm rain).

2. **The "Phantom Dry-Season Moisture K=2" Bug (Zamora, Irapuato, Tehuacan, Merida)**:
   * **Code Bug (`src/seasonal_calendar.py:192-198 & 315-317`)**:
     ```python
     dry_season_rain = sum(monthly_rain[m] for m in dry_months)
     if cropping_intensity_k >= 2 and len(dry_months_cyclic) >= 3 and dry_season_rain >= 60.0:
         s2_months = dry_months_cyclic[:3]
         seasons["season_2"] = SeasonMetadata(..., is_fallow=False, ...)
     ```
   * **Root Cause**: The engine calculates `dry_season_rain` across ALL dry months (which can span 6–7 months). If the aggregate across 7 months reaches 60 mm (an average of <9 mm/month!), and LGP ≥ 140 days, the engine declares Season 2 (`dry_months_cyclic[:3]`, e.g., Nov–Jan) as an **ACTIVE GROWING** season. In reality, 30–50 mm of rain over 3 months under high subtropical PET results in acute drought death for field crops. Furthermore, it ignores shallow karstic soil hydrology (Merida's porous limestone).

3. **The Sonoran Desert Monsoon vs. Winter Inversion Bug (Hermosillo, Sonora)**:
   * **Root Cause**: With 381 mm rain and PET 1563 mm, Hermosillo's aridity index is 0.244, just barely exceeding the 0.20 hyper-arid threshold. Lacking a warm desert/steppe rule, it falls through to `TROPICAL_MONOMODAL_RAIN`. This forces an active rainfed season in July–September under lethal **46°C–49°C** summer temperatures, while inverting the actual commercial growing season (O-I wheat and table grapes, November–June) into a 9-month fallow!

4. **Cosmetic String Formatter Glitch in Hyper-Arid Desert (Torreon, Coahuila)**:
   * **Code Bug (`src/seasonal_calendar.py:203`)**:
     ```python
     f"Hyper-arid pluvial desert ({annual_rain:.1f} mm < 120 mm)."
     ```
   * **Root Cause**: When a location triggers `HYPER_ARID_DESERT` via `aridity_index < 0.20 and annual_tmean >= 15.0` rather than `annual_rain < 120`, the string output prints an untrue mathematical statement (e.g. `274.8 mm < 120 mm`).

---

## 5. Remediation Roadmap

1. **Add Aridity Guard to `HUMID_SUBTROPICAL`**:
   Require `annual_rain >= 700.0 and aridity_index >= 0.65` before classifying any location as `HUMID_SUBTROPICAL`. Locations failing this threshold should be routed to `SEMI_ARID_STEPPE` or `SUBTROPICAL_ARID_DESERT`.
2. **Fix Second Season Moisture Threshold for Monomodal Tropics**:
   Instead of checking aggregate rain across the entire 7-month dry season (`dry_season_rain >= 60`), require that the specific 3 months of Season 2 have at least **150 mm of rainfall** (or `monthly_rain >= 40 mm` in each month) and a soil water-holding capacity factor before permitting `is_fallow = False` (K=2).
3. **Incorporate Lethal Temperature Checks for Summer Monsoon**:
   In desert/semi-arid zones where summer maximum temperatures exceed 42°C (e.g., Sonora, Sinaloa), suppress rainfed summer crop windows unless specialized thermal-hardy crops are designated, and incorporate winter irrigated cycles (Otoño-Invierno).
4. **Fix Hyper-Arid String Formatter**:
   Update line 203 to dynamically reflect the trigger: `if annual_rain < 120: f"... {annual_rain:.1f} mm < 120 mm"` else `f"... Aridity Index {aridity_index:.2f} < 0.20"`.
