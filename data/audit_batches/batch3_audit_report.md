# Independent Agronomic Systems & Crop Calendar Audit Report
**Batch 3: Brazil & Paraguay (15 Strategic Agricultural Benchmarks)**
**Auditor**: Independent Senior Agronomist & Agro-Meteorological Systems Auditor
**Target Data**: `/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/audit_150_batches/batch03_brazil_paraguay.json`
**Reference Standards**: EMBRAPA (Soja, Milho e Sorgo, Trigo, Cerrados, Agropecuária Oeste, Clima Temperado, Pecuária Sul, Meio-Norte), CONAB (Calendário de Safra de Grãos), MAPA (Zoneamento Agrícola de Risco Climático - ZARC, Portarias de Vazio Sanitário), IDR-Paraná / IAPAR (Alerta Geada e Zoneamento), FECOAGRO RS / IRGA, MAG Paraguay (Dirección de Censos y Estadísticas Agropecuarias), SENAVE Paraguay (Pausa Fitosanitaria), CAPECO / INBIO Paraguay.

---

## 1. Executive Summary

An exhaustive, independent agro-ecological and climatological audit was conducted on the Crop Calendar Deduced Engine across 15 agricultural anchor locations in Brazil and Paraguay. The audit evaluated:
1. **Regime Classification Authenticity** (Köppen-Geiger / FAO GAEZ agro-climatic validity).
2. **Primary Growing Season Window Alignment** against documented planting, flowering, and harvest dates (CONAB, EMBRAPA, ZARC, and MAG/SENAVE).
3. **Freeze Dormancy Biological Accuracy** (LGP5 biological zero thresholds and cold tolerance limits).
4. **Cropping Intensity Factor (K)** realism (distinguishing genuine rainfed double-cropping capacity from unviable winter intensification or false fallow states).

### Key Regional Performance Metrics
* **Total Evaluated Locations**: 15
* **Validated (Exact / Near-Exact Match)**: 4 locations (26.7%)
* **Acceptable (Within ±1 Month / Agronomically Defensible Rainfed Window)**: 4 locations (26.7%)
* **Defect (Agronomic Failure, False Regime, Internal Logic Contradiction, or Broken Calendar Window)**: 7 locations (46.7%)
* **Regional Accuracy Score (Validated + Acceptable)**: **53.3% (8 / 15)**

### Regional Breakdown
* **Subtropical Southern Brazil & Southern Paraguay (Paraná, Rio Grande do Sul, Alto Paraná)**: **100% Validated (4/4)** (Cascavel, Cruz Alta, Bagé, Santa Rita). The engine's Humid Subtropical module demonstrates outstanding biological and chronological alignment with real-world summer soy / winter wheat/maize rotations.
* **Cerrado Center-West Grain Belt (Mato Grosso & Goiás)**: **100% Acceptable (4/4)** (Lucas do Rio Verde, Rondonópolis, Rio Verde, Primavera do Leste). The macro-regime (Aw monomodal), freeze dormancy (False), and cropping intensity (K=2) are correctly captured. However, the engine exhibits a systemic 3-month scheduling lag by defining Season 2 as May–July rather than modeling intra-monsoon Safrinha seeding in January/February.
* **MATOPIBA & Northern Transition Frontiers (Maranhão & Piauí)**: **0% Passing (0/2 Defects)** (Balsas, Uruçuí). Inability to model tight semi-arid monsoon boundaries, leading to an impossible May–July rainfed season in Uruçuí and a fatal internal code contradiction in Balsas (deduced_k=2 with Season 2 & 3 both fallow).
* **Center-South Sugarcane & Mixed Grain Belts (Triângulo Mineiro, São Paulo, Mato Grosso do Sul)**: **0% Passing (0/3 Defects)** (Uberaba, Ribeirão Preto, Dourados). Catastrophic misallocation of cropping intensity: impossible rainfed triple-cropping (K=3) in dry-winter savanna zones (Uberaba, Ribeirão Preto) and an inexplicable single-crop (K=1) 10-month lock in Brazil's premier double-cropping hub (Dourados).
* **Eastern Paraguay Subtropical Transition (Canindeyú, Guairá)**: **0% Passing (0/2 Defects)** (Katuete, Colonia Independencia). False classification into `HUMID_TROPICAL_PERENNIAL` at latitudes 24°–25°S, generating overlapping string corruptions and inverting the summer wet season into dry fallow.

---

## 2. Master Audit Scorecard

| # | Location | Deduced Regime | Deduced Window (Season 1) | Freeze Dormancy | Deduced K | Real-World Official Calendar & Regime | Rainfed vs Irrigated Status | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **Lucas do Rio Verde, MT** | TROPICAL_MONOMODAL_RAIN | October – April (7 mo) | False | 2 | Cerrado Aw: Safra soy planted Oct–Nov, harvested Jan–Feb; Safrinha corn planted Jan–Feb, harvested Jun–Jul. | Rainfed K=2 standard. S2 (May–Jul) captures drydown but lags planting by 3 mo. | **[ACCEPTABLE]** |
| 2 | **Rondonopolis, MT** | TROPICAL_MONOMODAL_RAIN | October – April (7 mo) | False | 2 | Southern MT: Early soy Oct–Jan; Safrinha corn/cotton Feb–Jun. | Rainfed K=2 standard. Macro-hydrology defensible. | **[ACCEPTABLE]** |
| 3 | **Rio Verde, GO** | TROPICAL_MONOMODAL_RAIN | October – April (7 mo) | False | 2 | Southwest Goiás: Soy Oct–Jan; Safrinha corn/sorghum Feb–Jun. | Rainfed K=2 standard. Macro-hydrology defensible. | **[ACCEPTABLE]** |
| 4 | **Dourados, MS** | TROPICAL_MONOMODAL_RAIN | September – June (10 mo) | False | 1 | Southern Maracaju: Summer soy (Oct–Jan) + Safrinha corn / winter wheat (Feb–Aug). | Rainfed K=2 standard. Engine deduced K=1 with absurd 10-month continuous crop. | **[DEFECT]** |
| 5 | **Cascavel, PR** | HUMID_SUBTROPICAL | September – April (8 mo) | False | 2 | Western Paraná: Summer soy (Oct–Feb) + Safrinha corn/wheat (Feb–Aug). | Rainfed K=2 standard. Flawless subtropical 2-season rotation. | **[VALIDATED]** |
| 6 | **Uberaba, MG** | TROPICAL_MONOMODAL_RAIN | October – April (7 mo) | False | 3 | Triângulo Mineiro: Sugarcane semi-perennial; Soy/corn Oct–Mar. Winter is bone-dry. | Rainfed K=1 or K=2. K=3 impossible rainfed; Season 3 is marked fallow (active K=2). | **[DEFECT]** |
| 7 | **Ribeirao Preto, SP** | TROPICAL_MONOMODAL_RAIN | October – May (8 mo) | False | 3 | Paulista Center: Sugarcane, peanut, soy. Jun–Aug rain < 25 mm/mo. | Rainfed K=3 impossible; June–August active season is unviable. | **[DEFECT]** |
| 8 | **Cruz Alta, RS** | HUMID_SUBTROPICAL | October – April (7 mo) | False | 2 | Planalto Médio RS: Summer soy (Nov–Apr) + Winter wheat/barley/oats (May–Oct). | Rainfed K=2 standard. Flawless match with EMBRAPA Trigo. | **[VALIDATED]** |
| 9 | **Bage, RS** | HUMID_SUBTROPICAL | November – April (6 mo) | False | 2 | Pampa: Lowland rice / soy (Nov–Apr) + Winter pasture/ryegrass/wheat (May–Oct). | Rainfed/irrigated dual cycle K=2. Flawless alignment with IRGA. | **[VALIDATED]** |
| 10 | **Balsas, MA** | TROPICAL_MONOMODAL_RAIN | October – May (8 mo) | False | 2 | MATOPIBA: Soy planted Nov–Dec, harvested Mar–Apr. Safrinha is high risk. | Code contradiction: Deduced K=2, but Seasons 2 & 3 are both fallow (active K=1). | **[DEFECT]** |
| 11 | **Urucui, PI** | TROPICAL_MONOMODAL_RAIN | October – April (7 mo) | False | 2 | Piauí Cerrado (904 mm rain): Single soy crop (Dec–Apr). Winter has 0 mm rain. | Rainfed K=1 strictly. Active May–July season is physically impossible. | **[DEFECT]** |
| 12 | **Primavera do Leste, MT** | TROPICAL_MONOMODAL_RAIN | October – April (7 mo) | False | 2 | East MT: Early soy Oct–Jan; 2nd season cotton/corn Feb–Jul. | Rainfed K=2 standard. Macro-hydrology defensible. | **[ACCEPTABLE]** |
| 13 | **Katuete, Canindeyu (PY)** | HUMID_TROPICAL_PERENNIAL | January – October (6 mo) | False | 2 | Eastern Paraguay: Subtropical Cfa. Soy (Sep–Jan) + Safrinha corn/wheat (Feb–Jul). | Catastrophic regime defect: Tropical at 24°S; overlapping S1/S2; Nov–Dec fallow! | **[DEFECT]** |
| 14 | **Santa Rita, Alto Parana (PY)**| HUMID_SUBTROPICAL | September – April (8 mo) | False | 2 | Alto Paraná: Zafra soy (Sep–Jan) + Zafriña corn/wheat (Feb–Aug). | Rainfed K=2 standard. Superb match with MAG/SENAVE. | **[VALIDATED]** |
| 15 | **Colonia Independencia, Guaira (PY)**| HUMID_TROPICAL_PERENNIAL | January – October (6 mo) | False | 2 | Central Paraguay: Subtropical Cfa. Sugarcane, yerba mate, soy/corn. | Identical failure to Katuete: False regime, overlapping seasons, summer fallow. | **[DEFECT]** |

---

## 3. Deep-Dive Location Audits

### Location 1: Lucas do Rio Verde, Mato Grosso, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - April (7 Months)` | S2: `May - July (3 Months, Active)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (CONAB / EMBRAPA Soja / ZARC Mato Grosso)**:
  * Macro-Climate: Köppen Aw (Tropical Savanna with severe dry winter). Annual rainfall is ~1522 mm, concentrated between October and April.
  * Safra de Soja (Primary Summer Crop): Sown immediately after the end of the Vazio Sanitário (after Sept 15 / Oct 1) as rains stabilize; harvested late January to mid-February (cycle: 95–115 days).
  * Safrinha de Milho (Second Crop): Sown sequentially in **January and February**. MAPA/ZARC defines the low-risk climatic window as closing strictly between **February 20 and February 28**. Safrinha flowers in March/April during the tail of the rains, matures on residual subsoil moisture, and is harvested in June/July.
* **Evaluation**:
  * The deduced regime (`TROPICAL_MONOMODAL_RAIN`), freeze status (`False`), and cropping intensity (`K=2`) are 100% accurate.
  * The primary growing window (October–April, 7 months) accurately encompasses the total monsoon pluvial period.
  * **Systemic Limitation**: The engine constructs Season 2 as `May - July (3 Months)`. In Lucas do Rio Verde, rainfall in May is ~20 mm, June is ~5 mm, and July is ~1 mm. An operational crop cannot be sown in May under rainfed conditions. However, the engine designates Season 2 as a "Post-Monsoon Residual Moisture Season", which reflects the late grain-filling and desiccation phase of Safrinha maize sown in February. While operational planting dates exhibit a 3-month lag, the macro-hydrological envelope and K=2 potential are defensible.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 2: Rondonópolis, Mato Grosso, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - April (7 Months)` | S2: `May - July (3 Months, Active)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Soja / IMEA / CONAB)**:
  * Southern Mato Grosso agricultural hub. Rainfall ~1403 mm, marked dry winter (May–September).
  * Commercial System: Early-maturing soybean (October–January) followed immediately by Safrinha corn or second-season cotton (February–June/July).
* **Evaluation**: Identical behavior to Lucas do Rio Verde. Macro-regime, frost freedom, and K=2 intensity are solid. Season 1 spans the pluvial window. Season 2 represents the desiccation/harvest of Safrinha rather than a true May planting window.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 3: Rio Verde, Goiás, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - April (7 Months)` | S2: `May - July (3 Months, Active)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Arroz e Feijão / CONAB Goiás)**:
  * Southwestern Goiás mega-production zone. Rainfall ~1250 mm.
  * Commercial System: Rainfed soybean sown October–November, harvested January–February; followed immediately by Safrinha corn, grain sorghum, or sunflower sown in February. ZARC window closes early March.
* **Evaluation**: Captures the Aw monomodal regime and K=2 potential. Exhibits the same post-monsoon shoulder lag for Season 2, but remains acceptable at the macro-agroecological level.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 4: Dourados, Mato Grosso do Sul, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `September - June (10 Months)` | S2: `July (1 Month, Fallow)` | S3: `August (1 Month, Fallow)` | Freeze: `False` | K: `1`.
* **Official Benchmark (EMBRAPA Agropecuária Oeste - Dourados, MS)**:
  * Agro-Ecological Reality: Dourados sits in the highly productive Maracaju plateau. Rainfall is ~1298 mm, and computed LGP is 334 days.
  * Commercial Reality: Dourados is one of the premier double-cropping centers of Brazil!
    * Summer: Soja de verão sown late September to November; harvested January–February.
    * Autumn/Winter: Milho safrinha sown February–March (harvested July–August) OR Trigo (wheat) sown April–May (harvested August–September).
  * Engine Defect: The engine deduced **`K=1`** and locked the region into an **absurd 10-month continuous single growing season (September–June)**! No rainfed field crop in Dourados occupies the field continuously from September to June. Squeezing a famous double-crop powerhouse into K=1 represents a severe agronomic failure caused by flawed dry-season rainfall filtering.
* **VERDICT**: **[DEFECT]**

---

### Location 5: Cascavel, Paraná, Brazil
* **Deduced Data**: Regime: `HUMID_SUBTROPICAL` | S1: `September - April (8 Months)` | S2: `May - August (4 Months, Active)` | S3: `None (0 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (IDR-Paraná / IAPAR / EMBRAPA Soja)**:
  * Western Paraná: Subtropical climate (Köppen Cfa) with rainfall distributed year-round (~1584 mm) and moderate winter temperatures.
  * Production System:
    * Summer Cash Crop: Soybeans planted late September through October; harvested January through March.
    * Winter Second Crop: Safrinha corn sown January–February OR Winter Wheat / White Oats sown April–May and harvested August–September.
* **Evaluation**:
  * Regime (`HUMID_SUBTROPICAL`) and Cropping Intensity (`K=2`) are 100% correct.
  * Season 1 (September–April) perfectly captures the summer cash grain cycle.
  * Season 2 (May–August) accurately captures the winter cereal and late safrinha cycle.
  * Freeze Dormancy `False` is correct under LGP5 biological zero standards (monthly mean temperature never drops below 5°C, despite occasional light radiation frosts).
  * *Note: A minor cyclic index serialization artifact causes `start_month` to read "January" and `end_month` "December", but the formatted window string `September - April (8 Months)` is flawlessly displayed.*
* **VERDICT**: **[VALIDATED]**

---

### Location 6: Uberaba, Minas Gerais, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - April (7 Months)` | S2: `May - July (3 Months, Active)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `3`.
* **Official Benchmark (EPAMIG Triângulo Mineiro / EMBRAPA Cerrados)**:
  * Triângulo Mineiro: Tropical Savanna (Aw). Rainfall ~1331 mm with an intense 5-month winter drought (May–September total rain < 80 mm).
  * Commercial Reality: Dominated by sugarcane (12–18 month semi-perennial cycle) and grain rotations (Soybean + Safrinha Sorghum/Corn).
  * **Critical Engine Defects**:
    1. **Impossible Cropping Intensity**: The engine assigned `K=3`. Triple-cropping under rainfed conditions in an Aw climate with 5 rainless months is physically impossible. Triple cropping in Uberaba is restricted to center-pivot irrigation (Soybean -> Corn -> Dry Edible Beans).
    2. **Internal Code Contradiction**: While `deduced_k` is 3, the engine generated Season 1 (active), Season 2 (active), and Season 3 (**fallow**). The number of active seasons is only 2! The engine contradicts its own intensity assignment.
    3. Active Season 2 in May–July under dryland conditions is agronomically unviable.
* **VERDICT**: **[DEFECT]**

---

### Location 7: Ribeirão Preto, São Paulo, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - May (8 Months)` | S2: `June - August (3 Months, Active)` | S3: `September (1 Month, Fallow)` | Freeze: `False` | K: `3`.
* **Official Benchmark (IAC - Instituto Agronômico de Campinas / APTA)**:
  * World Capital of Sugarcane. Tropical/Subtropical with dry winter (Cwa/Aw). Annual rain ~1316 mm.
  * Commercial System: Semi-perennial sugarcane, peanuts in sugarcane renovation (November–March), and summer soybeans.
  * **Critical Engine Defects**:
    1. Identical defect to Uberaba: Engine assigned **`K=3`** under rainfed conditions!
    2. S2 is placed squarely in **June - August (3 Months)**. In Ribeirão Preto, June, July, and August are the coldest, driest months of the year (July rainfall averages 17 mm). No annual rainfed crop can be planted in June and harvested in August.
    3. Severe internal contradiction: `deduced_k: 3` with Season 3 marked fallow.
* **VERDICT**: **[DEFECT]**

---

### Location 8: Cruz Alta, Rio Grande do Sul, Brazil
* **Deduced Data**: Regime: `HUMID_SUBTROPICAL` | S1: `October - April (7 Months)` | S2: `May - September (5 Months, Active)` | S3: `None (0 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Trigo / FECOAGRO RS / ZARC RS)**:
  * Planalto Médio Gaúcho: Humid Subtropical (Cfa). Rainfall ~1737 mm, well distributed year-round.
  * Double-Cropping Standard:
    * Summer: Soybeans sown late October through November; harvested March through April.
    * Winter: Wheat, barley, canola, and black oats sown May through June; harvested October through November.
* **Evaluation**:
  * Flawless agro-climatic alignment.
  * Season 1 (October–April, 7 mo) matches the summer soybean cycle with precision.
  * Season 2 (May–September, 5 mo) captures the winter cereal cycle with textbook accuracy.
  * Freeze Dormancy `False` is correct (LGP5 biological threshold is not breached).
* **VERDICT**: **[VALIDATED]**

---

### Location 9: Bagé, Rio Grande do Sul, Brazil
* **Deduced Data**: Regime: `HUMID_SUBTROPICAL` | S1: `November - April (6 Months)` | S2: `May - October (6 Months, Active)` | S3: `None (0 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Pecuária Sul / IRGA)**:
  * Pampa Biome (Campanha Gaúcha). Subtropical maritime-influenced climate (Cfa). Rain ~1479 mm.
  * Agricultural Cycle:
    * Summer: Lowland irrigated rice (arroz irrigado) and upland soybeans sown late October through November; harvested March through April.
    * Winter: Cool-season pastures (annual ryegrass / azevém, oats) and winter wheat sown May–June; grazed/harvested through October.
* **Evaluation**:
  * S1 (November–April, 6 mo) precisely reflects the delayed spring planting window of southern Rio Grande do Sul.
  * S2 (May–October, 6 mo) matches the 6-month winter cereal and pasture cycle.
  * K=2 captures the universal crop-livestock integration (ILP) or rice-pasture rotation.
* **VERDICT**: **[VALIDATED]**

---

### Location 10: Balsas, Maranhão, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - May (8 Months)` | S2: `June - July (2 Months, Fallow)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Meio-Norte / Fapcen MATOPIBA)**:
  * Southern Maranhão Cerrado: Aw regime. Rainfall ~1205 mm, strictly bounded between late October and April.
  * Commercial Reality: Soybeans sown November–December; harvested March–April. The abrupt end of rains in April makes commercial Safrinha maize extremely risky; farmers typically grow cover crops (milheto/crotalária) or single-crop soy (K=1).
  * **Critical Engine Defects**:
    1. **Fatal Internal Logic Contradiction**: The engine outputs `deduced_k: 2`. However, Season 1 is active, Season 2 is marked **`is_fallow: true`** ("Severe dryland moisture deficit"), and Season 3 is marked **`is_fallow: true`** ("Peak dry season before monsoon arrival"). The total number of active seasons is 1! Assigning K=2 while generating 2 fallow seasons is a direct software logic error.
    2. Season 1 spanning 8 months (October–May) is artificially prolonged for MATOPIBA, where the rainfed cycle rarely exceeds 120 days.
* **VERDICT**: **[DEFECT]**

---

### Location 11: Uruçuí, Piauí, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - April (7 Months)` | S2: `May - July (3 Months, Active)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Meio-Norte - Bom Jesus / Uruçuí)**:
  * Piauí Cerrado Plateau: Semi-arid transition. Annual rainfall is only **903.8 mm**, characterized by erratic rainfall and severe mid-season dry spells (veranicos).
  * Seasonality: The dry season begins aggressively in May. Average rainfall in May is ~15 mm, June < 3 mm, July 0 mm, August 0 mm.
  * Agronomic Evaluation: Rainfed agriculture in Uruçuí is strictly **single-crop (K=1)** (Soybean sown December–January, harvested April). Designating Season 2 (May–July) as an active growing season (`is_fallow: false`) with 900 mm total rainfall and zero winter rain is an agronomic impossibility. Any rainfed crop planted in May will die.
* **VERDICT**: **[DEFECT]**

---

### Location 12: Primavera do Leste, Mato Grosso, Brazil
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `October - April (7 Months)` | S2: `May - July (3 Months, Active)` | S3: `August - September (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (EMBRAPA Algodão / EMBRAPA Soja / IMEA)**:
  * Eastern Mato Grosso Plateau (~630m elev). Rainfall ~1507 mm.
  * Commercial System: Global powerhouse of ultra-intensive double-cropping: Early Soybeans (sown late Sept–Oct, harvested Jan) followed by Second-Crop Cotton (algodão 2ª safra) or Safrinha Corn sown in January/February.
* **Evaluation**: Identical to Lucas do Rio Verde. Macro-regime, frost freedom, and K=2 intensity are solid. Season 2 acts as a desiccation/maturation phase for the February-planted second crop rather than a true May seeding window. Defensible at the regional agro-climatic level.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 13: Katueté, Canindeyú, Paraguay
* **Deduced Data**: Regime: `HUMID_TROPICAL_PERENNIAL` | S1: `January - October (6 Months)` | S2: `June - September (4 Months, Active)` | S3: `November - December (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (MAG Paraguay / SENAVE / CAPECO)**:
  * Climatology: Latitude -24.25°S (Subtropical, south of the Tropic of Capricorn). Köppen Cfa (Humid Subtropical). Annual rain ~1489 mm. Winter incurs cold southern polar fronts (*surazos*) with temperatures dropping to 2°–5°C.
  * Commercial Reality: Mechanized grain production:
    * Zafra de Soja: Sown September 1 to November; harvested January to March.
    * Zafriña (Maíz / Soja / Trigo): Sown January to March (maize/soy) or May to June (wheat); harvested June to October.
  * **Catastrophic Engine Defects**:
    1. **False Regime**: Classified as `HUMID_TROPICAL_PERENNIAL` at latitude 24.25°S because rainfall was >= 60 mm in 10 months, ignoring latitude and thermal boundaries.
    2. **Corrupted Season String**: Season 1 is labeled `January - October (6 Months)`—a 10-month span labeled as 6 months due to index truncation!
    3. **Overlapping Active Windows**: Season 2 (`June - September`) is nested entirely inside Season 1 (`January - October`)!
    4. **Inverted Fallow Season**: Season 3 marks **November - December (2 Months)** as fallow ("Dry season soil moisture rest"). In Paraguay, November and December are the peak summer rainy season when soybeans are in full vegetative growth! Marking summer as dry fallow is an agronomic catastrophe.
* **VERDICT**: **[DEFECT]**

---

### Location 14: Santa Rita, Alto Paraná, Paraguay
* **Deduced Data**: Regime: `HUMID_SUBTROPICAL` | S1: `September - April (8 Months)` | S2: `May - August (4 Months, Active)` | S3: `None (0 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (MAG Paraguay / INBIO / SENAVE)**:
  * Alto Paraná Grain Heartland: Latitude -25.79°S. Humid Subtropical (Cfa). Rainfall ~1650 mm.
  * Production System:
    * Zafra de Soja (Summer Anchor): Sown September through October; harvested January through March.
    * Zafriña de Maíz / Trigo (Winter Cycle): Safrinha corn sown February–March (harvested July–August); Wheat sown May–June (harvested September–October).
* **Evaluation**:
  * Regime (`HUMID_SUBTROPICAL`) and Cropping Intensity (`K=2`) are 100% accurate.
  * S1 (September–April) perfectly captures the primary summer zafra window.
  * S2 (May–August) matches the winter wheat and late zafriña maturation window.
  * Unlike Katueté, Santa Rita correctly triggered the `HUMID_SUBTROPICAL` branch because its mean temperature was 21.5°C (< 22.0°C).
* **VERDICT**: **[VALIDATED]**

---

### Location 15: Colonia Independencia, Guairá, Paraguay
* **Deduced Data**: Regime: `HUMID_TROPICAL_PERENNIAL` | S1: `January - October (6 Months)` | S2: `June - September (4 Months, Active)` | S3: `November - December (2 Months, Fallow)` | Freeze: `False` | K: `2`.
* **Official Benchmark (MAG Paraguay - Dirección de Extensión Agraria)**:
  * Central Paraguay: Latitude -25.68°S. Subtropical climate (Cfa). Major production center for sugarcane, yerba mate, smallholder maize, and beans.
  * Evaluation: Suffers from the exact same catastrophic failure mode as Katueté. Classified as `HUMID_TROPICAL_PERENNIAL` at latitude 25.7°S, resulting in corrupted overlapping calendar strings (June–Sept inside Jan–Oct) and inverting the summer pluvial period (Nov–Dec) into dry fallow.
* **VERDICT**: **[DEFECT]**

---

## 4. Systemic Findings & Root Cause Analysis

### 1. The "Tropical Perennial" Latitude Bypass Bug
* **Location in Code**: `src/seasonal_calendar.py`, lines 160–163:
  ```python
  elif annual_tmean < 22.0 and min_monthly_tmean >= 4.0 and abs(lat) >= 23.0:
      regime = "HUMID_SUBTROPICAL"
  elif sum(1 for m in range(12) if monthly_rain[m] >= 60.0) >= 10 and annual_rain >= 1400:
      regime = "HUMID_TROPICAL_PERENNIAL"
  ```
* **Mechanism**: To qualify for `HUMID_SUBTROPICAL`, a location must have `annual_tmean < 22.0°C`. Katueté (22.4°C) and Colonia Independencia (22.2°C) narrowly missed this threshold despite being at latitudes 24.2°S and 25.7°S. They fell into `HUMID_TROPICAL_PERENNIAL`, which completely lacks latitude gating!
* **Consequence**: Subtropical Paraguayan latitudes were subjected to an equatorial monsoon calendar builder that sliced arbitrary 6-month wet chunks, generated overlapping season windows (`June-Sept` inside `Jan-Oct`), and marked the summer pluvial season (`Nov-Dec`) as dry fallow.

### 2. Monomodal Wet-Season Splitting Blindness
* **Location in Code**: `src/seasonal_calendar.py`, lines 300–324.
* **Mechanism**: In `TROPICAL_MONOMODAL_RAIN`, the engine lumps **all** months with precipitation >= 50 mm into a single monolithic `Season 1` (typically 7 to 8 months, Oct–Apr). When `K >= 2`, it carves `Season 2` out of the first 3 **dry months** (May–July).
* **Agronomic Failure**: In the Brazilian Cerrado, farmers achieve K=2 not by planting in the dry season (May), but by sequentially squeezing two rapid cycles (100-day early soy + 120-day safrinha corn/cotton) **inside the 7-month wet season plus tail moisture**. Sowing in May is an agronomic death sentence.

### 3. Fallow Contradiction with Deduced K
* **Location in Code**: `src/seasonal_calendar.py`, lines 192–198 and 318–324.
* **Mechanism**: In Balsas, MA, `cropping_intensity_k` was deduced as 2. However, because dry season rainfall was < 60 mm, Season 2 fell into the fallback branch and was forced to `is_fallow: True`. Season 3 was also hardcoded to `is_fallow: True`.
* **Result**: The JSON output reported `deduced_k: 2`, but contained only **1 active season and 2 fallow seasons**. In Uberaba and Ribeirão Preto, `deduced_k: 3` was assigned, but Season 3 was hardcoded to fallow, leaving only 2 active seasons.

### 4. Flawed Dry-Season Filter Locking High-LGP Zones into K=1
* **Location in Code**: `src/seasonal_calendar.py`, lines 192–194:
  ```python
  dry_season_rain = sum(monthly_rain[m] for m in range(12) if monthly_rain[m] < 0.5 * monthly_pet[m])
  if dry_season_rain < 60.0 or lgp_days < 140:
      cropping_intensity_k = 1
  ```
* **Mechanism**: In Dourados, MS, LGP is 334 days. However, because the few dry months received < 60 mm, the engine forced `cropping_intensity_k = 1` and generated a 10-month continuous single growing season. An LGP of 334 days with 1300 mm rain can easily support two crops; conditioning K=2 on dry-season rainfall rather than total pluvial duration is fundamentally flawed.

---

## 5. Actionable Architectural Recommendations

1. **Fix `HUMID_SUBTROPICAL` Boundary & Guard Tropical Perennial**:
   * Raise the temperature ceiling for `HUMID_SUBTROPICAL` from 22.0°C to **23.5°C** if `abs(lat) >= 23.0°`.
   * Enforce a strict latitude check on `HUMID_TROPICAL_PERENNIAL`: `abs(lat) < 23.0°`.
2. **Implement Intra-Monsoon Double-Crop Segmentation for Cerrado**:
   * For `TROPICAL_MONOMODAL_RAIN` with `lgp_days >= 220` and `cropping_intensity_k == 2`:
     * Split the pluvial window into:
       * **Season 1 (Safra / Summer Anchor)**: Month 0 to Month 3.5 (e.g., October – January, 4 Months).
       * **Season 2 (Safrinha / Succession)**: Month 3.5 to Month 8 (e.g., February – June, 5 Months, maturing on residual moisture).
       * **Season 3 (Dry Fallow / Vazio Sanitário)**: July – September (3 Months, Fallow).
3. **Synchronize `deduced_k` with Generated Non-Fallow Seasons**:
   * Ensure that `cropping_intensity_k = sum(1 for s in seasons.values() if not s.is_fallow)`. Never output a K value that exceeds the count of active seasons.
4. **Decouple K=2 from Dry-Season Rainfall in High-LGP Tropical Zones**:
   * If `lgp_days >= 240` and `annual_rain >= 1200 mm`, K=2 should be permitted regardless of dry-season precipitation, reflecting sequential double cropping during the extended rainy season.
