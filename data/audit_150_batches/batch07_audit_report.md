# Independent Agronomic Systems & Crop Calendar Audit Report
**Batch 07: Sub-Saharan Africa - West & Central (15 Strategic Agricultural Benchmarks)**
**Auditor**: Independent Senior Agronomist & Agro-Meteorological Systems Auditor
**Target Data**: `/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/audit_150_batches/batch07_west_central_africa.json`
**Reference Standards**: FAO Crop Calendar West Africa, FAO-GIEWS, FEWS NET Livelihood Profiles, Agrhymet / CILSS Regional Agrometeorological Bulletins, IITA (International Institute of Tropical Agriculture), NiMet (Nigerian Meteorological Agency - Seasonal Climate Prediction), ICRISAT West & Central Africa, ISRA (Institut Sénégalais de Recherches Agricoles), INRAN (Institut National de la Recherche Agronomique du Niger), IER (Institut d'Économie Rurale du Mali), INERA (Institut de l'Environnement et de Recherches Agricoles, Burkina Faso), CSIR-SARI (Savanna Agricultural Research Institute, Ghana), CNRA (Centre National de Recherche Agronomique, Côte d'Ivoire), INRAB (Institut National des Recherches Agricoles du Bénin), IRAD (Institut de Recherche Agricole pour le Développement, Cameroon), ITRAD (Institut Tchadien de Recherche Agronomique pour le Développement).

---

## 1. Executive Summary

An exhaustive agro-ecological audit was conducted on the Crop Calendar Deduced Engine across 15 agricultural anchor locations spanning West and Central Africa (Nigeria, Niger, Mali, Burkina Faso, Ghana, Côte d'Ivoire, Benin, Cameroon, Chad, Guinea-Bissau, Senegal). The evaluation scrutinized:
1. **Regime Classification Authenticity**: Evaluation of tropical monomodal rainfall regimes against the seasonal migration of the Intertropical Convergence Zone (ITCZ / Intertropical Front - ITF).
2. **Primary Growing Season Window Alignment**: Alignment of Season 1 against documented onset of effective rainfall, sowing windows, flowering, and harvest dates for staple cereals (sorghum, pearl millet, maize, upland/lowland rice) and cash legumes/fibers (cowpea, groundnut, cotton, yam, sesame).
3. **Freeze Dormancy Biological Accuracy**: Verification of low-latitude tropical agro-thermal regimes and confirmation of zero frost risk despite cool Harmattan night spells.
4. **Cropping Intensity Factor (K) Realism**: Evaluation of whether the deduced rainfed water balance can support single (K=1) vs sequential double cropping (K=2), specifically testing whether post-monsoon dry season windows (October–January) are agronomically viable under dryland conditions without supplemental irrigation or hydromorphic floodplains (*fadama*).

### Key Regional Performance Metrics
* **Total Evaluated Locations**: 15
* **Validated (Exact / Near-Exact Match)**: 7 locations (46.7%)
* **Acceptable (Within ±1 Month / Agronomically Defensible Hydromorphic-Residual Window)**: 1 location (6.7%)
* **Defect (Agronomic Failure, False Second Season, or Code Synchronization Bug)**: 7 locations (46.7%)
* **Regional Accuracy Score (Validated + Acceptable)**: **53.3% (8 / 15)**

### Regional Performance Breakdown
* **Sahelian Core & Groundnut Basin (Maradi, Kaolack)**: **100% Passing (2/2 Validated)**. The engine performs flawlessly in short-season Sahelian zones where dry season rainfall is negligible (<10 mm) and LGP < 140 days, correctly triggering single-season rainfed cropping (K=1) with 8-month fallow.
* **South Sudanian & Central/East Savannas (Sikasso, Parakou, Ngaoundere, Sarh, Bafata)**: **100% Passing (5/5 Validated)**. For locations where annual dry season rain sums to <60 mm, the engine correctly rejects post-monsoon cropping and enforces K=1 with flawless S1 windows.
* **Guinea Savanna & Middle Belt (Zaria, Makurdi, Tamale, Korhogo)**: **25% Passing (1/4 Passing: 1 Acceptable, 3 Defect)**. Makurdi passes as Acceptable due to Benue alluvial residual moisture; Zaria fails due to a ghost K=2 code synchronization bug; Tamale and Korhogo fail due to dry-season rain aggregation hallucinating active farming during the Harmattan.
* **Sudan Savanna & Inland Granaries (Sokoto, Koutiala, Dedougou)**: **0% Passing (0/3 Passing: 3 Defect)**. All three suffer from the non-contiguous dry rain summing glitch, falsely declaring October–December as an active growing season with <3 mm of rain in November/December.
* **Sudano-Sahelian Lake Chad Basin (Maroua)**: **0% Passing (0/1 Passing: 1 Defect)**. S1 is accurate, but the engine deduces K=2 while generating two fallow seasons (the ghost season bug).

---

## 2. Master Audit Scorecard

| # | Location | Deduced Regime | Deduced Window (Season 1) | Freeze Dormancy | Deduced K | Real-World Official Calendar & Regime | Rainfed vs Irrigated Status | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **Zaria, Kaduna**, Nigeria | TROPICAL_MONOMODAL_RAIN | April – October (7 mo) | False | 2 | Northern Guinea Savanna: Sowing late May–Jun; Harvest Oct–Nov. Rains May–Oct. | Rainfed K=1 strictly. Internal code bug: K=2 but S2 & S3 both fallow. | **[DEFECT]** |
| 2 | **Makurdi, Benue**, Nigeria | TROPICAL_MONOMODAL_RAIN | April – October (7 mo) | False | 2 | Southern Guinea Savanna (Benue Valley): Rainfed Apr–Oct. S2 Nov–Jan residual moisture cowpea/sesame in alluvium. | Rainfed upland K=1; Lowland/alluvial residual moisture K=2 defensible. | **[ACCEPTABLE]** |
| 3 | **Sokoto, Sokoto**, Nigeria | TROPICAL_MONOMODAL_RAIN | June – September (4 mo) | False | 2 | Sudan Savanna: Rains Jun–Sep (700mm). Sowing Jun–Jul; Harvest Sep–Oct. Dry Oct–May. | Rainfed K=1 strictly. Nov–Dec rain is 0.3mm. S2 active is impossible. | **[DEFECT]** |
| 4 | **Maradi, Maradi**, Niger | TROPICAL_MONOMODAL_RAIN | June – September (4 mo) | False | 1 | Sahelian Savanna: Cowpea hub. Sowing Jun–Jul; Harvest Sep–Oct. 8-mo dry fallow. | Rainfed K=1 strictly. Flawless Sahelian single-cycle calendar. | **[VALIDATED]** |
| 5 | **Sikasso, Sikasso**, Mali | TROPICAL_MONOMODAL_RAIN | May – October (6 mo) | False | 1 | South Sudanian Savanna: Mali breadbasket. Maize/Cotton/Sorghum May–Oct. Nov–Apr dry. | Rainfed K=1 strictly. Dry rain 55mm correctly triggers K=1 fallow. | **[VALIDATED]** |
| 6 | **Koutiala, Sikasso**, Mali | TROPICAL_MONOMODAL_RAIN | May – September (5 mo) | False | 2 | Cotton Basin: Rainfed May–Sep/Oct. Sowing Jun; Harvest Oct–Nov. Nov–Dec rain is 2.7mm. | Rainfed K=1 strictly. Nov–Dec active season is an agronomic defect. | **[DEFECT]** |
| 7 | **Dedougou, Mouhoun**, Burkina Faso | TROPICAL_MONOMODAL_RAIN | May – September (5 mo) | False | 2 | Boucle du Mouhoun: Burkina granary. Sowing Jun; Harvest Oct–Nov. Nov–Dec rain is 2.4mm. | Rainfed K=1 strictly. Nov–Dec active season is an agronomic defect. | **[DEFECT]** |
| 8 | **Tamale, Northern**, Ghana | TROPICAL_MONOMODAL_RAIN | April – October (7 mo) | False | 2 | Guinea Savanna: Single rainy season May–Oct (1074mm). Harvest Oct–Nov. Nov–Mar dry. | Rainfed K=1 strictly. Nov–Jan rain 24mm; cannot sustain active second crop. | **[DEFECT]** |
| 9 | **Korhogo, Savanes**, Côte d'Ivoire | TROPICAL_MONOMODAL_RAIN | April – October (7 mo) | False | 2 | Northern Savanna: Single rainy season May–Oct (995mm). Harvest Oct–Nov. Nov–Mar dry. | Rainfed K=1 strictly. Nov–Jan rain 23mm; cannot sustain active second crop. | **[DEFECT]** |
| 10 | **Parakou, Borgou**, Benin | TROPICAL_MONOMODAL_RAIN | April – October (7 mo) | False | 1 | Central Benin Savanna: Maize/cotton/yam Apr–Oct. Dry season Nov–Mar fallow. | Rainfed K=1 strictly. Flawless match to INRAB/FAO baseline. | **[VALIDATED]** |
| 11 | **Ngaoundere, Adamawa**, Cameroon | TROPICAL_MONOMODAL_RAIN | April – October (7 mo) | False | 1 | Adamawa Plateau (1100m): High-elevation savanna. Rains Apr–Oct. Nov–Mar dry. | Rainfed K=1 strictly. Flawless match to IRAD/FAO baseline. | **[VALIDATED]** |
| 12 | **Maroua, Far North**, Cameroon | TROPICAL_MONOMODAL_RAIN | May – September (5 mo) | False | 2 | Sudano-Sahelian: Rainfed May–Sep. Mouskwari sorghum on vertisols Oct–Jan. | Internal code bug: K=2 deduced, but S2 & S3 both generated as fallow! | **[DEFECT]** |
| 13 | **Sarh, Moyen-Chari**, Chad | TROPICAL_MONOMODAL_RAIN | May – October (6 mo) | False | 1 | Southern Chad Sudanian: Cotton/sorghum/rice May–Oct. Nov–Apr dry season fallow. | Rainfed K=1 strictly. Flawless match to ITRAD/FEWS NET baseline. | **[VALIDATED]** |
| 14 | **Bafata, Bafata**, Guinea-Bissau | TROPICAL_MONOMODAL_RAIN | June – October (5 mo) | False | 1 | Geba River Basin: Heavy monsoonal rain Jun–Oct (1515mm). Nov–May severe dry. | Rainfed K=1 strictly. Flawless match to INPA/FAO baseline. | **[VALIDATED]** |
| 15 | **Kaolack, Kaolack**, Senegal | TROPICAL_MONOMODAL_RAIN | June – October (5 mo) | False | 1 | Groundnut Basin: Hivernage rains Jul–Oct (725mm). Peanut/millet. Nov–Jun dry. | Rainfed K=1 strictly. Flawless match to ISRA/FAO baseline. | **[VALIDATED]** |

---

## 3. Deep-Dive Location Audits

### Location 1: Zaria, Kaduna State, Nigeria
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - October (7 Months)` (active) | S2: `November - December (2 Months)` (fallow) | S3: `January - March (3 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (IITA / NiMet / Ahmadu Bello University - IAR Samaru)**:
  * Agro-Ecological Zone: Northern Guinea Savanna (11.08°N, 7.72°E).
  * Precipitation & Thermal Regime: Annual rainfall 1,129.6 mm. Unimodal rainfall strictly governed by the West African Monsoon (WAM). Effective rains establish in late May or early June; peak rains occur in July–August (250–288 mm/month); rains terminate abruptly in mid-October. Total precipitation from November to March is only 13.8 mm (Nov 4.5 mm, Dec 0.0 mm, Jan 0.3 mm, Feb 0.3 mm, Mar 8.7 mm).
  * Cropping System: Sole or intercropped grain maize, sorghum, soybean, and cowpea. Planting in April is heavily discouraged by NiMet and IAR due to high risk of seedling mortality from early false starts. Land preparation occurs April–May; planting runs late May to June; harvesting takes place October to November.
* **Engine Evaluation & Defect Identification**:
  1. **Fatal Software Contradiction (The Ghost Season Bug)**: The engine recorded `deduced_k: 2`, but generated Season 2 as fallow (`is_fallow: true`, "Severe dryland moisture deficit") and Season 3 as fallow (`is_fallow: true`)! Only Season 1 is active. The engine’s reported cropping intensity K=2 directly contradicts its own seasonal segmentation.
  2. **Agronomic Failure of Rainfed K=2**: In the Northern Guinea Savanna, rainfed upland cropping is strictly unimodal K=1. November through March is the bone-dry Harmattan season with atmospheric relative humidity < 15% and monthly PET > 140 mm. Rainfed double-cropping is impossible.
* **VERDICT**: **[DEFECT]** (Direct code inconsistency and agronomic impossibility).

---

### Location 2: Makurdi, Benue State, Nigeria
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - October (7 Months)` (active) | S2: `November - January (3 Months)` (active: "Residual Soil Moisture / Short Pulses") | S3: `February - March (2 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (Federal University of Agriculture Makurdi / JOSTUM / Benue State MANR / NiMet)**:
  * Agro-Ecological Zone: Southern Guinea Savanna / Middle Belt (Benue River Valley, 7.73°N, 8.54°E).
  * Precipitation Profile: Annual rainfall 1,229.2 mm. Extended unimodal/sub-bimodal rainy season running from April (107.7 mm) through October (153.8 mm), with peak in August–September (201–217 mm). LGP is 249 days (~8.3 months).
  * Cropping System: Primary staple crops (yam, cassava, rainfed rice, soybean, maize) occupy the main pluvial window (April–October). 
  * Dry Season / Post-Monsoon Reality: November receives 31.8 mm, December 2.2 mm, January 4.6 mm. In strictly dry uplands, this moisture is inadequate for new seed germination. However, Makurdi sits directly on the vast alluvial floodplains and hydromorphic depressions (*fadama*) of the River Benue. Agronomic research from JOSTUM (e.g., the *FUAMPEA* cowpea series) and local extension confirm that smallholders extensively exploit late-season residual moisture in lowland/floodplain soils for short-duration cowpea and late sesame (beniseed) planted at the end of the rains (October/November) and harvested in December/January.
* **Engine Evaluation**:
  * Season 1 (April–October, 7 months) is an exact match for the main pluvial season.
  * Season 2 (November–January, active, residual moisture) is agronomically defensible in the Benue riverine and vertic alluvium where stored subsoil moisture and shallow water tables sustain pulse and oilseed maturation. While pure rainfed upland farming is K=1, Makurdi's dominant regional agricultural identity incorporates this post-monsoon niche.
* **VERDICT**: **[ACCEPTABLE]** (Agronomically defensible post-monsoon residual moisture niche; acceptable within regional hydro-climatic context).

---

### Location 3: Sokoto, Sokoto State, Nigeria
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - September (4 Months)` (active) | S2: `October - December (3 Months)` (active: "Residual Soil Moisture / Short Pulses") | S3: `January - May (5 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (Usmanu Danfodiyo University Sokoto / NiMet / FAO GIEWS / ICRISAT)**:
  * Agro-Ecological Zone: Sudan Savanna / Semi-Arid Sahelian Margin (13.06°N, 5.25°E).
  * Precipitation Profile: Annual rainfall 700.3 mm. Unimodal rainfall strictly concentrated between June and September (June 94.5 mm, July 169.6 mm, August 249.9 mm, September 121.2 mm). Rains cease abruptly by late September / early October (October receives 23.2 mm, November 0.3 mm, December 0.0 mm). Total LGP is only 151 days.
  * Cropping System: Pearl millet, drought-tolerant sorghum, and cowpea are sown in June–July and harvested in September–October.
* **Engine Evaluation & Defect Identification**:
  * Season 1 (June–September, 4 months) is flawless.
  * Season 2 (October–December, 3 months, active) is a severe agronomic defect. The engine deduced an active rainfed cropping season during months that receive a cumulative total of only 23.5 mm of rain (and 0.3 mm across November–December combined) under scorching Sahelian temperatures (Tmax 37–40°C) and monthly PET > 160 mm. The sandy soils of the Sudan Savanna have virtually zero water storage capacity.
  * Any winter agricultural production in Sokoto (e.g., irrigated garlic, onions, and wheat) is 100% dependent on capital-intensive irrigation infrastructure from the Bakolori and Goronyo reservoirs along the Sokoto-Rima River Basin. Rainfed K=2 is impossible.
* **VERDICT**: **[DEFECT]** (Severe agronomic defect: false rainfed double-cropping in semi-arid Sudan Savanna).

---

### Location 4: Maradi, Maradi Region, Niger
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - September (4 Months)` (active) | S2: `October - January (4 Months)` (fallow) | S3: `February - May (4 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (INRAN Niger / FAO GIEWS / FEWS NET Livelihood Zone NE05)**:
  * Agro-Ecological Zone: Sahelian Agropastoral Zone (13.50°N, 7.10°E).
  * Precipitation Profile: Annual rainfall 551.8 mm. LGP is 132 days (< 140 days). The monsoon is strictly confined to June–September (Jun 72.9 mm, Jul 144.5 mm, Aug 198.7 mm, Sep 91.2 mm). Dry season rainfall (October–May) totals < 45 mm across 8 months.
  * Cropping System: Maradi is the premier cowpea hub of West Africa. Smallholders intercrop pearl millet and cowpea (over 95% of parcels). Land prep in May; sowing in June with the first soaking rains; flowering in August; harvest in September–October. Once harvested, fields enter an 8-month biological fallow where cowpea haulms and millet stover are grazed by pastoral herds.
* **Engine Evaluation**:
  * Regime correctly identified as `TROPICAL_MONOMODAL_RAIN`.
  * S1 (June–September, 4 months) is an exact match for the Sahelian wet season.
  * Cropping intensity K=1 is strictly enforced (triggered by LGP 132 < 140 days).
  * Off-season properly divided into fallow rest and pre-monsoon land preparation.
* **VERDICT**: **[VALIDATED]** (Flawless Sahelian agro-climatic alignment).

---

### Location 5: Sikasso, Sikasso Region, Mali
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - October (6 Months)` (active) | S2: `November - January (3 Months)` (fallow) | S3: `February - April (3 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (Institut d'Économie Rurale - IER / CMDT / FEWS NET Mali)**:
  * Agro-Ecological Zone: South Sudanian Savanna (11.32°N, -5.67°W). Known as "Mali's Breadbasket."
  * Precipitation Profile: Annual rainfall 1,046.6 mm. Unimodal rainfall running May to October (May 85.9 mm, Jun 141.6 mm, Jul 222.6 mm, Aug 282.1 mm, Sep 193.2 mm, Oct 66.0 mm). Dry season precipitation (November–April) totals 55.2 mm (< 60 mm). LGP is 196 days.
  * Cropping System: Grain maize, cotton, and long-cycle sorghum. Planting begins in late May/June; vegetative development peaks in July–August; harvest of maize begins in September/October; cotton picking and sorghum harvest conclude in November. Fields remain in post-harvest fallow throughout the dry winter.
* **Engine Evaluation**:
  * S1 (May–October, 6 months) accurately captures the entire 196-day LGP.
  * Because dry season rainfall (55.2 mm) is < 60 mm, the engine correctly determined that residual moisture is insufficient for a second rainfed crop, setting K=1 and classifying Season 2 as fallow.
* **VERDICT**: **[VALIDATED]** (Flawless alignment with IER and FEWS NET standards).

---

### Location 6: Koutiala, Sikasso Region, Mali
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - September (5 Months)` (active) | S2: `October - December (3 Months)` (active: "Residual Soil Moisture / Short Pulses") | S3: `January - April (4 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (IER Mali / CMDT - Compagnie Malienne pour le Développement des Textiles)**:
  * Agro-Ecological Zone: Central Cotton Basin (12.39°N, -5.46°W). The historic "Capital of White Gold."
  * Precipitation Profile: Annual rainfall 927.2 mm. Unimodal rainfall peaking July–August (Jul 208.0 mm, Aug 274.3 mm). Monsoon terminates by late September / early October (October receives 47.1 mm, November 2.7 mm, December 0.0 mm). LGP is 158 days (~5.2 months).
  * Cropping System: Cotton, sorghum, and millet rotation. Sowing in June; harvest October–November. Dry season runs November to May with zero precipitation.
* **Engine Evaluation & Defect Identification**:
  * Season 1 (May–September, 5 months) is completely accurate.
  * Season 2 (October–December, 3 months, active) is a major agronomic defect. The engine deduced an active rainfed season spanning November and December, during which total rainfall is 2.7 mm!
  * Why did the engine fail? The engine summed all non-wet months across the entire year (October 47.1 mm + Nov–Apr 35.3 mm = 82.4 mm), saw that 82.4 mm >= 60.0 mm, and erroneously flagged the first 3 dry months (Oct–Dec) as active.
  * In Koutiala, the LGP is 158 days. Season 1 consumes 153 days. There is zero physiological moisture buffer remaining for an active second crop. Upland rainfed K=2 is impossible.
* **VERDICT**: **[DEFECT]** (Algorithmic dry-season summing glitch generating false active season with 2.7 mm rain).

---

### Location 7: Dédougou, Mouhoun Region, Burkina Faso
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - September (5 Months)` (active) | S2: `October - December (3 Months)` (active: "Residual Soil Moisture / Short Pulses") | S3: `January - April (4 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (INERA Burkina Faso / Ministère de l'Agriculture / FEWS NET)**:
  * Agro-Ecological Zone: South Sudanian / Boucle du Mouhoun (12.46°N, -3.46°W). The "Granary of Burkina Faso."
  * Precipitation Profile: Annual rainfall 879.0 mm. Unimodal monsoonal regime: May (61.7 mm), June (114.0 mm), July (197.8 mm), August (270.0 mm), September (154.2 mm). October receives 45.3 mm, November 2.4 mm, December 0.0 mm. LGP is 157 days.
  * Cropping System: High-volume grain maize, rainfed cotton, white sorghum, and cowpea. Planting late May–June; harvest October–November.
* **Engine Evaluation & Defect Identification**:
  * Season 1 (May–September, 5 months) aligns with the pluvial envelope.
  * Season 2 (October–December, 3 months, active) is an agronomic defect identical to Koutiala. November and December receive 2.4 mm total rainfall. Soil moisture in the Mouhoun plateau dries out rapidly following the cessation of the rains in October. Rainfed farming is strictly single-season (K=1).
* **VERDICT**: **[DEFECT]** (False K=2 deduction; impossible rainfed second season in Boucle du Mouhoun).

---

### Location 8: Tamale, Northern Region, Ghana
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - October (7 Months)` (active) | S2: `November - January (3 Months)` (active: "Residual Soil Moisture / Short Pulses") | S3: `February - March (2 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (CSIR-SARI Nyankpala / MoFA Ghana / FEWS NET Ghana)**:
  * Agro-Ecological Zone: Guinea Savanna (9.40°N, -0.84°W).
  * Precipitation Profile: Annual rainfall 1,074.1 mm. Northern Ghana experiences a single unimodal rainy season (unlike Southern Ghana's bimodal regime). Wet season spans April through October (Apr 81.3 mm, May 113.8 mm, Jun 133.5 mm, Jul 169.6 mm, Aug 175.5 mm, Sep 200.1 mm, Oct 121.5 mm). November receives 19.5 mm, December 1.9 mm, January 3.1 mm. LGP is 244 days.
  * Cropping System: Maize, yam, soybean, sorghum, upland rice, and groundnut. Land preparation starts April; planting May–June; main harvests occur September–November. Dry Harmattan season begins in November.
* **Engine Evaluation & Defect Identification**:
  * Season 1 (April–October, 7 months = 214 days) captures the entire rainfed growing period.
  * Season 2 (November–January, 3 months, active) is an agronomic defect. Cumulative rainfall in November–January is only 24.5 mm. Combined with Season 1, the engine proposes 10 consecutive active months (300 days), exceeding the computed LGP of 244 days by nearly two months.
  * CSIR-SARI and MoFA confirm that rainfed cropping in Northern Ghana is strictly unimodal K=1. All dry-season farming is confined to small irrigation dams and dugouts (e.g., Bontanga and Golinga schemes).
* **VERDICT**: **[DEFECT]** (False K=2 rainfed deduction; active season during bone-dry Harmattan).

---

### Location 9: Korhogo, Savanes District, Côte d'Ivoire
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - October (7 Months)` (active) | S2: `November - January (3 Months)` (active: "Residual Soil Moisture / Short Pulses") | S3: `February - March (2 Months)` (fallow) | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (CNRA Côte d'Ivoire / FIRCA / FEWS NET)**:
  * Agro-Ecological Zone: Northern Savanna (9.46°N, -5.63°W).
  * Precipitation Profile: Annual rainfall 995.2 mm. Unimodal rainfall running April to October (Apr 75.9 mm, May 92.4 mm, Jun 119.7 mm, Jul 160.6 mm, Aug 204.9 mm, Sep 165.0 mm, Oct 95.2 mm). November receives 18.0 mm, December 2.2 mm, January 3.1 mm. LGP is 237 days.
  * Cropping System: Cotton (anchor cash crop), cashew orchards, grain maize, groundnut, and yam. Sowing in May–June; harvesting October–November. Dry season spans November to March.
* **Engine Evaluation & Defect Identification**:
  * Season 1 (April–October, 7 months) is agronomically sound.
  * Season 2 (November–January, 3 months, active) suffers from the same defect as Tamale. Total precipitation over the 3-month period is only 23.3 mm. CNRA agronomic guidelines specify that rainfed annual crops cannot be planted in November. Northern Côte d'Ivoire rainfed agriculture is strictly K=1.
* **VERDICT**: **[DEFECT]** (False K=2 deduction; active season generated in dry season with 23 mm rain).

---

### Location 10: Parakou, Borgou Department, Benin
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - October (7 Months)` (active) | S2: `November - December (2 Months)` (fallow) | S3: `January - March (3 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (INRAB Benin / Direction de la Statistique Agricole / FAO GIEWS)**:
  * Agro-Ecological Zone: Central/Northern Benin Savanna (9.34°N, 2.63°E).
  * Precipitation Profile: Annual rainfall 1,096.6 mm. Unimodal rainy season from April to October (Apr 76.5 mm, May 115.6 mm, Jun 140.4 mm, Jul 176.1 mm, Aug 210.5 mm, Sep 205.5 mm, Oct 112.2 mm). Dry season precipitation (November–March) totals 59.8 mm (Nov 11.1 mm, Dec 2.2 mm, Jan 4.6 mm, Feb 9.0 mm, Mar 32.9 mm). LGP is 240 days.
  * Cropping System: Cotton, yam, maize, and soybean. Planting in May–June; harvest September–November.
* **Engine Evaluation**:
  * Because the dry season rainfall (59.8 mm) fell just below the engine's 60.0 mm threshold, the engine correctly rejected a second active season, set K=1, and designated November–March as fallow.
  * S1 (April–October, 7 months) matches the 240-day LGP and official INRAB calendars.
* **VERDICT**: **[VALIDATED]** (Flawless single-season savanna classification).

---

### Location 11: Ngaoundéré, Adamawa Region, Cameroon
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - October (7 Months)` (active) | S2: `November - December (2 Months)` (fallow) | S3: `January - March (3 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (IRAD Cameroon / FAO GIEWS / Ministère de l'Agriculture et du Développement Rural)**:
  * Agro-Ecological Zone: Adamawa High Plateau (7.33°N, 13.58°E, altitude ~1,100 m). High-elevation tropical savanna.
  * Precipitation Profile: Annual rainfall 1,477.7 mm. Abundant unimodal rainfall running April to October (Apr 90.9 mm, May 161.5 mm, Jun 190.8 mm, Jul 280.9 mm, Aug 317.4 mm, Sep 271.8 mm, Oct 131.4 mm). Dry season (November–March) rainfall totals 33.0 mm. LGP is 246 days. Mean annual temperature is cooler (23.0°C).
  * Cropping System: Maize, highland sorghum, yam, and pastoral cattle rangelands. Sowing in April–May; harvesting October–November.
* **Engine Evaluation**:
  * S1 (April–October, 7 months) perfectly bounds the 246-day growing season.
  * Zero frost risk correctly deduced (`has_freeze_dormancy: false`, Tmin reaches 6.6°C in January).
  * K=1 with dry season fallow matches IRAD baseline.
* **VERDICT**: **[VALIDATED]** (Flawless Adamawa plateau agro-climatic alignment).

---

### Location 12: Maroua, Far North Region, Cameroon
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - September (5 Months)` (active) | S2: `October - December (3 Months)` (fallow: "Severe dryland moisture deficit") | S3: `January - April (4 Months)` (fallow: "Peak dry season before monsoon arrival") | Freeze: `False` | Deduced K: `2`.
* **Official Benchmark (IRAD Maroua / SODECOTON / FAO GIEWS)**:
  * Agro-Ecological Zone: Sudano-Sahelian Plain / Lake Chad Basin (10.60°N, 14.32°E).
  * Precipitation Profile: Annual rainfall 750.7 mm. Unimodal rainfall strictly concentrated between May and September (May 56.4 mm, Jun 111.6 mm, Jul 176.1 mm, Aug 218.2 mm, Sep 132.9 mm). October receives 36.9 mm, November 1.5 mm, December 0.0 mm. LGP is 153 days.
  * Cropping Systems:
    1. Rainfed rainy-season crops: White sorghum, cotton, cowpea, and groundnut planted in June–July and harvested September–October.
    2. Post-rainy season vertisol crop (*Mouskwari* / *Berbéré*): Off-season transplant red sorghum cultivated on flooded clay plains (*karal*) from October to January, maturing on deep residual moisture.
* **Engine Evaluation & Defect Identification**:
  * Season 1 (May–September, 5 months) accurately delineates the rainfed pluvial season.
  * **Critical Software Inconsistency Bug (The Ghost Season Bug)**: The engine recorded `deduced_k: 2`, but generated Season 2 as FALLOW (`is_fallow: true`) and Season 3 as FALLOW (`is_fallow: true`)! Thus, only ONE active season exists in the data, directly contradicting the assigned cropping intensity K=2.
  * If the engine intended to capture *Mouskwari* sorghum, it failed by labeling Season 2 as fallow. If it intended pure rainfed cropping, K should be 1. In either case, the output contains a fatal internal contradiction.
* **VERDICT**: **[DEFECT]** (Internal code bug: K=2 assigned while generating zero active secondary seasons).

---

### Location 13: Sarh, Moyen-Chari Region, Chad
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - October (6 Months)` (active) | S2: `November - January (3 Months)` (fallow) | S3: `February - April (3 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (ITRAD Chad / FEWS NET Chad / FAO GIEWS)**:
  * Agro-Ecological Zone: Southern Chad Sudanese Zone (9.14°N, 18.39°E).
  * Precipitation Profile: Annual rainfall 1,055.6 mm. Unimodal rainfall spanning May to October (May 91.1 mm, Jun 163.5 mm, Jul 221.7 mm, Aug 258.2 mm, Sep 196.8 mm, Oct 91.1 mm). Dry season (November–April) precipitation totals 33.2 mm. LGP is 201 days.
  * Cropping System: Cotton (Chad's primary cash crop), penicillaria millet, sorghum, groundnut, and lowland rice along the Chari River basin. Sowing in May–June; harvesting in October–November.
* **Engine Evaluation**:
  * S1 (May–October, 6 months) matches the 201-day LGP.
  * Dry season rainfall (33.2 mm < 60 mm) correctly enforces K=1. Off-season properly segmented into post-harvest fallow and pre-monsoon land preparation.
* **VERDICT**: **[VALIDATED]** (Flawless Southern Chad Sudanese calendar).

---

### Location 14: Bafatá, Bafatá Region, Guinea-Bissau
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - October (5 Months)` (active) | S2: `November - January (3 Months)` (fallow) | S3: `February - May (4 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (INPA Guinea-Bissau / FAO GIEWS / Ministère de l'Agriculture)**:
  * Agro-Ecological Zone: Interior Savanna / Geba River Basin (12.16°N, -14.66°W).
  * Precipitation Profile: Annual rainfall 1,515.2 mm. Highly intense unimodal West African Monsoon concentrated in 5 months: June (155.7 mm), July (370.1 mm), August (468.1 mm), September (323.4 mm), October (151.3 mm). Dry season (November–May) is hyper-dry, totaling only 46.6 mm over 7 months (Dec: 0.0 mm, Feb: 0.3 mm, Mar: 0.6 mm, Apr: 0.6 mm). LGP is 183 days.
  * Cropping System: Upland rice, mangrove/lowland paddy rice, groundnut, and extensive cashew nut agroforestry. Sowing June–July; harvesting October–November. Cashew harvesting occurs in the dry season (March–May).
* **Engine Evaluation**:
  * S1 (June–October, 5 months) precisely bounds the heavy monsoonal pluvial window.
  * The extreme dry season (7 months, <47 mm rain) correctly triggers K=1 and multi-month fallow.
* **VERDICT**: **[VALIDATED]** (Flawless Guinea-Bissau monsoon alignment).

---

### Location 15: Kaolack, Kaolack Region, Senegal
* **Deduced Data**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - October (5 Months)` (active) | S2: `November - January (3 Months)` (fallow) | S3: `February - May (4 Months)` (fallow) | Freeze: `False` | Deduced K: `1`.
* **Official Benchmark (ISRA Senegal / FAO GIEWS / FEWS NET Senegal)**:
  * Agro-Ecological Zone: Senegalese Groundnut Basin (*Bassin Arachidier*, 14.15°N, -16.08°W).
  * Precipitation Profile: Annual rainfall 725.1 mm. The Sahelian monsoon (*hivernage*) is short and intense, running July to October (Jun 50.7 mm, Jul 142.0 mm, Aug 264.1 mm, Sep 203.4 mm, Oct 56.4 mm). November to May is completely dry (8.5 mm total rain over 7 months). LGP is 131 days.
  * Cropping System: Senegal's historic peanut and pearl millet heartland. Sowing begins with the first established rains in late June / July; rapid vegetative growth in August; harvest in October–November. Dry season is devoted to trade, livestock stubble grazing, and off-season petty commerce.
* **Engine Evaluation**:
  * S1 (June–October, 5 months) captures the *hivernage* window.
  * LGP 131 days (< 140 days) correctly enforces K=1. Fallow windows match the severe dryland moisture deficit.
* **VERDICT**: **[VALIDATED]** (Flawless Senegalese Groundnut Basin calendar).

---

## 4. Algorithmic Root-Cause Analysis in `seasonal_calendar.py`

Inspection of `/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/src/seasonal_calendar.py` reveals three distinct algorithmic flaws directly responsible for all 7 defective audits in Batch 07:

### Defect Mechanism 1: Inconsistent Dry Season Rain Thresholds & The "Ghost Season" Bug
* **Code Location**: Lines 191–198 vs Lines 312–321.
* **The Glitch**:
  In lines 191–198, cropping intensity K is determined using:
  ```python
  dry_season_rain = sum(monthly_rain[m] for m in range(12) if monthly_rain[m] < 0.5 * monthly_pet[m])
  if dry_season_rain < 60.0 or lgp_days < 140:
      cropping_intensity_k = 1
  elif lgp_days >= 260 and annual_tmean >= 22.0:
      cropping_intensity_k = 3
  else:
      cropping_intensity_k = 2
  ```
  In lines 300 & 312–315, the actual seasonal generation uses a completely different definition:
  ```python
  wet_months = [m for m in range(12) if monthly_rain[m] >= 50.0]
  dry_months = [m for m in range(12) if m not in wet_months]
  dry_season_rain = sum(monthly_rain[m] for m in dry_months)
  if cropping_intensity_k >= 2 and len(dry_months_cyclic) >= 3 and dry_season_rain >= 60.0:
      # Create active Season 2
  else:
      # Create fallow Season 2! (cropping_intensity_k is NOT updated!)
  ```
* **Impact on Zaria (Kaduna) and Maroua (Cameroon)**:
  * In Zaria, April has 51.9 mm of rain. Its PET is ~115 mm (0.5 * PET = 57.5 mm). Because 51.9 < 57.5, line 192 included April rain in `dry_season_rain`, yielding 65.7 mm >= 60.0 mm $\rightarrow$ `cropping_intensity_k = 2`.
  * However, in line 300, April (51.9 mm >= 50.0 mm) was placed into `wet_months` (Season 1).
  * Consequently, in line 314, April was excluded from `dry_months`. The remaining dry months (Nov–Mar) only totaled 13.8 mm of rain!
  * Thus, line 315 failed (`dry_season_rain < 60.0`), sending Season 2 to the `else` branch where it was generated as **FALLOW** (`is_fallow: True`)!
  * The engine never rolled back `cropping_intensity_k` to 1, leaving `deduced_k: 2` while only generating ONE active season and TWO fallow seasons!

### Defect Mechanism 2: Non-Contiguous Annual Dry Rain Summing Causing Harmattan Season Hallucination
* **Code Location**: Lines 312–317.
* **The Glitch**:
  ```python
  dry_months = [m for m in range(12) if m not in wet_months]
  dry_season_rain = sum(monthly_rain[m] for m in dry_months)
  if cropping_intensity_k >= 2 and len(dry_months_cyclic) >= 3 and dry_season_rain >= 60.0:
      s2_months = dry_months_cyclic[:3]
      # Set s2_months as ACTIVE GROWING (is_fallow: False)
  ```
  `dry_season_rain` sums rainfall across ALL dry months across the entire calendar year—both pre-monsoon (April/May) and post-monsoon (October–December)—regardless of whether they are contiguous!
* **Impact on Sokoto, Koutiala, Dédougou, Tamale, and Korhogo**:
  * In Sokoto, dry months are Oct, Nov, Dec, Jan, Feb, Mar, Apr, May. Total rain across all 8 months is 65.1 mm (mostly falling in May [33.5 mm] and October [23.2 mm]).
  * Because 65.1 mm >= 60.0 mm, the engine took the first 3 cyclic months following the wet season: October, November, December.
  * It declared October–December as an ACTIVE GROWING SEASON (`is_fallow: False`).
  * In reality, November received 0.3 mm and December received 0.0 mm! The engine hallucinated an active growing season during the peak of the bone-dry Harmattan desert winter based on rainfall that actually fell five months later in May!
  * The same error created active second seasons with 2.7 mm rain in Koutiala, 2.4 mm rain in Dédougou, 24 mm rain in Tamale, and 23 mm rain in Korhogo.

### Defect Mechanism 3: Disregard of Length of Growing Period (LGP) Caps on Active Duration
* In Dédougou (LGP = 157 days) and Koutiala (LGP = 158 days), Season 1 spans 5 months (~153 days), absorbing virtually the entire moisture-viable window. Adding a 3-month active Season 2 results in 8 months of active cultivation (244 days), exceeding the agro-climatic moisture capacity by nearly 3 months.

---

## 5. Strategic Recommendations for Engine Remediation

1. **Synchronize K Determination with Seasonal Generation**:
   * If the condition to activate Season 2 in line 315 fails, the engine MUST re-synchronize `cropping_intensity_k`:
     ```python
     if cropping_intensity_k >= 2 and len(dry_months_cyclic) >= 3 and season_2_rain >= 60.0:
         # active season 2
     else:
         cropping_intensity_k = 1  # Revert K to 1 to match active season count!
     ```
2. **Evaluate In-Season Precipitation Rather than Annual Dry Sums**:
   * Replace `dry_season_rain = sum(monthly_rain[m] for m in dry_months)` with the rainfall specifically falling within the prospective Season 2 window:
     ```python
     candidate_s2_months = dry_months_cyclic[:3]
     s2_window_rain = sum(monthly_rain[m] for m in candidate_s2_months)
     if cropping_intensity_k >= 2 and len(candidate_s2_months) >= 3 and s2_window_rain >= 75.0:
         # create active season 2
     ```
   * An active rainfed season must never be created if the rainfall within that specific window is under 60–75 mm.
3. **Enforce Hard LGP Upper Bounds on Cropping Duration**:
   * Total active growing months multiplied by 30 days must not exceed computed LGP by more than 30 days:
     $\sum (\text{Active Season Months} \times 30) \le \text{computed\_lgp\_days} + 30$.
4. **Distinguish Residual Hydromorphic Niches from Upland Rainfed Base**:
   * Allow an explicit agro-system tag `soil_water_retention = "ALLUVIAL_FADAMA"` for river basins like Makurdi (River Benue) or Maroua (Vertisol Karal) to model post-monsoon pulse/sorghum systems without corrupting dryland savanna baselines.

---
**Report Certified by**: Independent Agro-Climatic Audit Subagent  
**Date**: November 2026
