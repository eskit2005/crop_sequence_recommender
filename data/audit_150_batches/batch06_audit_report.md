# Independent Agronomic Systems & Crop Calendar Audit Report
**Batch 06: Central, Southern & Eastern Europe (15 Strategic Agricultural Benchmarks)**
**Auditor**: Independent Senior Agronomist & Agro-Meteorological Systems Auditor  
**Target File**: `/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/audit_150_batches/batch06_central_east_europe.json`  
**Official Reference Standards**:
* **Italy**: Consiglio per la ricerca in agricoltura e l'analisi dell'economia agraria (CREA-CI Foggia, CREA Bologna), ARPA Emilia-Romagna, Disciplinare di Produzione Integrata Puglia.
* **Spain**: Ministerio de Agricultura, Pesca y Alimentación (MAPA - ESYRCE), Instituto Técnico Agronómico Provincial de Albacete (ITAP), Red de Alerta e Información Fitosanitaria de Andalucía (RAIF), Centro de Investigación y Tecnología Agroalimentaria de Aragón (CITA).
* **Portugal**: Instituto Nacional de Investigação Agrária e Veterinária (INIAV - Estação de Melhoramento de Plantas de Elvas), Direção-Geral de Agricultura e Desenvolvimento Rural (DGADR), EDIA Alqueva.
* **Greece**: Hellenic Agricultural Organization (ELGO-DIMITRA - Institute of Industrial and Forage Crops, Larissa/Karditsa), Ministry of Rural Development and Food (MRDF).
* **Bulgaria**: Dobrudzha Agricultural Institute (DAI General Toshevo), Agricultural University of Plovdiv, Executive Agency for Variety Testing (IASAS).
* **Romania**: Institutul Național de Cercetare-Dezvoltare Agricolă Fundulea (INCDA Fundulea), Universitatea de Științele Vieții "Regele Mihai I" din Timișoara (USVT).
* **Hungary**: Centre for Agricultural Research (ATK TAKI Martonvásár), University of Debrecen Faculty of Agricultural and Food Sciences.
* **Slovakia**: Národné poľnohospodárske a potravinárske centrum (NPPC - VÚRV Piešťany / Research Institute of Plant Production).
* **Poland**: Instytut Uprawy Nawożenia i Gleboznawstwa - Państwowy Instytut Badawczy (IUNG-PIB Puławy).
* **Ukraine**: APK-Inform Agri-Market Agency, National Academy of Agrarian Sciences of Ukraine (NAAS), State Service of Ukraine on Food Safety and Consumer Protection.
* **Serbia**: Institute of Field and Vegetable Crops, Novi Sad (Institut za ratarstvo i povrtarstvo / NS Seme).

---

## 1. Executive Summary

An exhaustive agro-ecological and crop calendar audit was conducted across 15 agricultural anchor locations in Central, Southern, and Eastern Europe from the Mediterranean basin through the Pannonian Plain, the Carpathian basin, and the Ukrainian Steppe.

### Key Audit Findings
1. **Mediterranean Basin Strengths & Defect**:
   * The engine exhibited high precision in southern Mediterranean winter-rainfall zones (**Foggia, Apulia**, **Córdoba, Andalusia**, and **Évora, Alentejo**), accurately identifying the winter precipitation recharge window (October/November to May/June) and assigning necessary summer fallow periods driven by extreme drought and heat (July–August PET > 150 mm).
   * **Continental Mediterranean Steppe** in **Albacete** (La Mancha) and **Karditsa** (Thessaly) was also properly modeled for rainfed winter cereals (October–June) without artificial freeze halts.
   * **Severe Defect in Zaragoza, Aragon**: The engine misclassified the semi-arid Ebro Depression (annual precipitation 366.8 mm, Köppen *BSk*) as `TEMPERATE_OCEANIC_MARITIME`, and inverted the rainfed crop cycle into a summer window (`March - October`) through the peak of arid summer heat, while declaring winter months fallow when dryland winter barley is actually cultivated.
2. **Pannonian & Continental Frost Zones Precision & Logic Failure**:
   * Cold continental regions with severe sub-zero winters (**Debrecen**, **Lublin**, **Vinnytsia**, **Dnipro**, **Novi Sad**, and **Stara Zagora**) were accurately captured with appropriate freeze dormancy periods (3 to 5 months with absolute lows from -22°C to -31°C) and viable single-crop summer envelopes (April/May to September/October, K=1).
   * **Catastrophic Disjoint Season Defect in Timișoara, Romania**: The engine deduced `K = 2` by creating a disjoint non-fallow Season 2 spanning `"March & November (2 Months)"` across a 7-month gap (`April - October`). No agronomic crop can be sown in March, suspend growth during summer while another crop occupies the ground, and resume in November. Rainfed Banat farming is strictly `K = 1`.

### Quantitative Audit Metrics
* **Total Benchmark Locations**: 15
* **Validated (Exact / Near-Exact Match)**: 12 locations (80.0%)
* **Acceptable (Minor phenological drift within ±1 month)**: 1 location (6.7%)
* **Defect (Fatal classification, inverted calendar, or disjoint season)**: 2 locations (13.3%)
* **Regional Accuracy Score (Validated + Acceptable)**: **86.7% (13 / 15)**

---

## 2. Master Audit Scorecard

| # | Benchmark Location | Country | Deduced Regime | Deduced Window (Season 1) | Freeze Dormancy | Deduced K | Real-World Agronomic Benchmark | Rainfed / Irrigated Context | Audit Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Bologna, Emilia-Romagna** | Italy | `TEMPERATE_CONTINENTAL_FROST` | April – October (7 mo) | True (Dec–Feb) | 1 | CREA / ARPA: Grain maize/soy/tomato Apr 20–Oct 25; winter wheat Oct 25–Jul 5. Dec–Feb frost pause. | Rainfed K=1. Irrigated double-crop wheat-soybean exists. | **[VALIDATED]** |
| 2 | **Foggia, Apulia** | Italy | `MEDITERRANEAN_WINTER_RAIN` | September – June (10 mo) | False | 1 | CREA-CI Foggia: Durum wheat sown Nov–Dec, harvested early Jun. Summer drought Jul–Aug. | Rainfed K=1 strictly. Durum wheat capital of Italy. | **[VALIDATED]** |
| 3 | **Zaragoza, Aragon** | Spain | `TEMPERATE_OCEANIC_MARITIME` | March – October (8 mo) | True (Nov–Feb) | 1 | MAPA / CITA: Rainfed secano is winter barley/wheat (Nov–Jun). Jul–Aug extreme drought. | **DEFECT**: Arid steppe (366mm) tagged Oceanic. Inverted rainfed calendar. | **[DEFECT]** |
| 4 | **Cordoba, Andalusia** | Spain | `MEDITERRANEAN_WINTER_RAIN` | October – May (8 mo) | False | 1 | MAPA / RAIF: Winter wheat & chickpea sown Nov–Dec, harvest May–Jun. Extreme summer heat >40°C. | Rainfed K=1. True Mediterranean winter cycle. | **[VALIDATED]** |
| 5 | **Albacete, Castilla-La Mancha** | Spain | `MEDITERRANEAN_CONTINENTAL_STEPPE` | October – June (9 mo) | False | 1 | MAPA / ITAP: High plateau barley & purple garlic sown Nov–Dec, harvest Jun–Jul. Summer fallow. | Rainfed K=1. High plateau winter cycle. | **[VALIDATED]** |
| 6 | **Evora, Alentejo** | Portugal | `MEDITERRANEAN_WINTER_RAIN` | October – May (8 mo) | False | 1 | INIAV Elvas / DGADR: Winter cereals (wheat/oats) sown late Oct–Nov, harvested late May–Jun. | Rainfed K=1. Montado & rainfed winter grain. | **[VALIDATED]** |
| 7 | **Karditsa, Thessaly** | Greece | `MEDITERRANEAN_CONTINENTAL_STEPPE` | October – June (9 mo) | False | 1 | ELGO-DIMITRA: Durum & bread wheat sown Oct–Nov, harvested Jun. Rainfed summer fallow. | Rainfed K=1. (Summer cotton strictly irrigated). | **[VALIDATED]** |
| 8 | **Stara Zagora, Thrace** | Bulgaria | `TEMPERATE_CONTINENTAL_FROST` | April – October (7 mo) | True (Dec–Feb) | 1 | DAI / Agro-Plovdiv: Sunflower & maize sown Apr, harvested Aug–Oct. Winter freeze dormancy. | Rainfed K=1. Continental spring row crop cycle. | **[VALIDATED]** |
| 9 | **Timisoara, Banat** | Romania | `TEMPERATE_CONTINENTAL_FROST` | April – October (7 mo) | True (Dec–Feb) | 2 | INCDA Fundulea / USVT: Chernozem maize/sunflower Apr–Oct or winter wheat Oct–Jul. K=1. | **DEFECT**: Season 2 deduced as "March & November" active crop (K=2). Impossible. | **[DEFECT]** |
| 10 | **Debrecen, Great Plain** | Hungary | `TEMPERATE_CONTINENTAL_FROST` | April – October (7 mo) | True (Dec–Feb) | 1 | Debrecen Univ / ATK: Grain maize & sunflower sown mid-Apr, harvested Sep–Oct. Sub-zero winter. | Rainfed K=1. Pannonian black soil anchor cycle. | **[VALIDATED]** |
| 11 | **Trnava, Danubian Lowland** | Slovakia | `TEMPERATE_CONTINENTAL_FROST` | April – September (6 mo) | True (Nov–Mar) | 1 | NPPC-VÚRV: Sugar beet & maize sown Apr, harvested Sep–Nov. Winter freeze Nov–Mar. | Rainfed K=1. Core vegetative window captured. | **[ACCEPTABLE]** |
| 12 | **Lublin, Lublin Upland** | Poland | `TEMPERATE_CONTINENTAL_FROST` | May – September (5 mo) | True (Nov–Mar) | 1 | IUNG-PIB Puławy: Short frost-free window. Spring crops sown late Apr–May, harvest Aug–Sep. | Rainfed K=1. Severe continental winter (-31°C). | **[VALIDATED]** |
| 13 | **Vinnytsia, Podolia** | Ukraine | `TEMPERATE_CONTINENTAL_FROST` | May – September (5 mo) | True (Nov–Mar) | 1 | APK-Inform / NAAS: Corn & sugar beet sown late Apr–May, harvested Sep–Oct. Frost Nov–Mar. | Rainfed K=1. Forest-Steppe summer cash crop window. | **[VALIDATED]** |
| 14 | **Dnipro, Steppe** | Ukraine | `TEMPERATE_CONTINENTAL_FROST` | May – September (5 mo) | True (Nov–Mar) | 1 | APK-Inform: Sunflower sown mid-Apr to May, harvested late Aug–Sep. Severe winter (-31°C). | Rainfed K=1. Southern Steppe summer oilseed cycle. | **[VALIDATED]** |
| 15 | **Novi Sad, Vojvodina** | Serbia | `TEMPERATE_CONTINENTAL_FROST` | April – October (7 mo) | True (Dec–Feb) | 1 | NS Seme: Corn, sunflower, and soybean sown Apr, harvested Sep–Oct. Sub-zero winter halt. | Rainfed K=1. Pannonian basin summer row-crop cycle. | **[VALIDATED]** |

---

## 3. Deep-Dive Location Audits

### Location 1: Bologna, Emilia-Romagna, Italy
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `April - October (7 Months)` | Freeze: `True` (Dec–Feb, down to -9.0°C) | K: `1`.
* **Institutional Ground Truth (CREA / ARPA Emilia-Romagna)**:
  * In the southern Po Valley, spring-sown row crops (maize, sorghum, processing tomato, full-season soybean) are seeded from mid-April through early May and harvested from September through late October.
  * Winter wheat (*Triticum aestivum*) is sown in late October to November and harvested in late June to early July.
  * Overwintering conditions: In December through February, recurrent sub-zero nocturnal frosts and cold air pooling halt vegetative growth.
  * Cropping Intensity: Rainfed farming is restricted to single-crop production (K=1) due to summer moisture deficits. Irrigated sectors (via Canale Emiliano-Romagnolo) occasionally perform wheat-soybean double cropping, but K=1 is the true agro-climatic rainfed baseline.
* **Audit Evaluation**: While Bologna is classified under Köppen as *Cfa* (Humid Subtropical), agronomically it is situated in the sub-continental Po plain with winter frost dormancy. The April–October envelope accurately matches the full-season summer economic anchor crop.
* **VERDICT**: **[VALIDATED]**

---

### Location 2: Foggia, Apulia, Italy
* **Engine Output**: Regime: `MEDITERRANEAN_WINTER_RAIN` | S1: `September - June (10 Months)` | Freeze: `False` | K: `1`.
  * S2: `July (1 Month, Fallow)` | S3: `August (1 Month, Fallow)`.
* **Institutional Ground Truth (CREA-CI Foggia / Regione Puglia)**:
  * The *Tavoliere delle Puglie* is Italy's premier durum wheat production basin. Under rainfed conditions, sowing occurs in November to early December following the first soaking autumn rains. Flowering occurs in April/May, and harvest is completed in June.
  * July and August represent the core Mediterranean summer drought (rainfall < 20 mm/month, PET > 150 mm/month), making rainfed cropping impossible.
  * The deduced 10-month window (`September - June`) encapsulates the entire rainfed winter cereal lifecycle from early field preparation through harvest.
* **Audit Evaluation**: Exceptional alignment with the Mediterranean winter-rainfall agronomic regime.
* **VERDICT**: **[VALIDATED]**

---

### Location 3: Zaragoza, Aragon, Spain
* **Engine Output**: Regime: `TEMPERATE_OCEANIC_MARITIME` | S1: `March - October (8 Months)` | Freeze: `True` (Nov–Feb) | K: `1`.
* **Institutional Ground Truth (MAPA / CITA Aragón)**:
  * **Agro-Climatic Reality**: Zaragoza is situated in the Middle Ebro Valley (Depresión del Ebro), characterized by a cold semi-arid steppe climate (Köppen *BSk*) with severe rain-shadow effects from the Pyrenees and Iberian mountain ranges. Annual precipitation is merely 366.8 mm, with extreme summer aridity and frequent desiccating *Cierzo* winds.
  * **Rainfed Cropping System (*Secano Cerealista*)**: Dryland farming is strictly winter-cereal based (malting barley and bread wheat). Sowing takes place in October–November; vegetative development relies on winter/spring rainfall; harvesting concludes in May–June.
  * **Irrigation (*Regadío*)**: Summer crops (alfalfa, grain maize, stone fruit) can **only** be grown with extensive river/canal irrigation from the Ebro and Canal Imperial de Aragón.
* **Audit Critique**:
  1. **Fatal Regime Error**: Classifying an arid/semi-arid interior steppe with 366 mm rainfall as `TEMPERATE_OCEANIC_MARITIME` is a severe geographic and climatological defect. Oceanic maritime climates (Köppen *Cfb*, e.g., Galicia, Cantabria, Brittany) have high, year-round precipitation without dry seasons.
  2. **Inverted Cropping Calendar**: The engine forced rainfed Season 1 into `March - October (8 Months)` through the peak of extreme summer drought (July–August), while classifying the actual rainfed growing period (November–February) as fallow due to "low radiation and cool temperatures"!
* **VERDICT**: **[DEFECT]** (Regime classification failure and completely inverted rainfed crop calendar).

---

### Location 4: Cordoba, Andalusia, Spain
* **Engine Output**: Regime: `MEDITERRANEAN_WINTER_RAIN` | S1: `October - May (8 Months)` | Freeze: `False` | K: `1`.
  * S2: `June (1 Month, Fallow)` | S3: `July - September (3 Months, Fallow)`.
* **Institutional Ground Truth (MAPA / RAIF Andalucía)**:
  * In the Campiña de Córdoba (Guadalquivir basin), rainfed winter cereals (durum wheat) and winter legumes (chickpeas, faba beans) are sown from mid-November to mid-December and harvested in May through early June.
  * Summer is characterized by extreme heat (regularly exceeding 40°C in July and August) and total lack of rain, enforcing mandatory fallow from June through September.
* **Audit Evaluation**: Flawless representation of the Andalusian dryland winter-crop season and summer drought dormancy.
* **VERDICT**: **[VALIDATED]**

---

### Location 5: Albacete, Castilla-La Mancha, Spain
* **Engine Output**: Regime: `MEDITERRANEAN_CONTINENTAL_STEPPE` | S1: `October - June (9 Months)` | Freeze: `False` | K: `1`.
* **Institutional Ground Truth (MAPA / ITAP Albacete)**:
  * Located on the southern high plateau (*La Mancha*, ~700 m a.s.l.), Albacete has a Mediterranean-continental climate (*Csa/BSk* transition) with cold winters and very hot, dry summers (annual rainfall 348.6 mm).
  * Major rainfed crops are dryland malting barley (*cebada cervecera*), winter wheat, and purple garlic (*Ajo Morado de Las Pedroñeras*). Winter cereals and garlic are planted in autumn (October–December) and harvested in June to early July.
  * While Albacete records ~50 frost days, average monthly temperatures do not drop below 0°C (January mean is ~5°C), which allows winter cereals to overwinter without complete biological dormancy halts.
* **Audit Evaluation**: The deduced regime `MEDITERRANEAN_CONTINENTAL_STEPPE` and 9-month window (`October - June`) precisely mirror the high-plateau cereal/garlic vegetative cycle.
* **VERDICT**: **[VALIDATED]**

---

### Location 6: Evora, Alentejo, Portugal
* **Engine Output**: Regime: `MEDITERRANEAN_WINTER_RAIN` | S1: `October - May (8 Months)` | Freeze: `False` | K: `1`.
* **Institutional Ground Truth (INIAV Elvas / DGADR)**:
  * Central Alentejo is the historical cereal breadbasket of Portugal. Rainfed winter wheat, triticale, and oats are seeded following early autumn rains in late October through November, with optimal grain yield achieved from early November drillings.
  * Ripening occurs in May, and combining finishes by early June before the intense Mediterranean summer drought (July–September).
* **Audit Evaluation**: Exact match with INIAV agronomic guidelines and the Alentejo rainfed winter cereal calendar.
* **VERDICT**: **[VALIDATED]**

---

### Location 7: Karditsa, Thessaly, Greece
* **Engine Output**: Regime: `MEDITERRANEAN_CONTINENTAL_STEPPE` | S1: `October - June (9 Months)` | Freeze: `False` | K: `1`.
* **Institutional Ground Truth (ELGO-DIMITRA / Institute of Industrial and Forage Crops)**:
  * In the Thessalian Plain, rainfed durum wheat and barley are sown in October–November and harvested in June.
  * Summer field crops such as cotton and grain maize are intensively grown from April to October but are **100% dependent on artificial irrigation** from local groundwater and reservoirs.
  * For the natural rainfed agro-climatic baseline, the productive window is October through June, followed by extreme summer drought fallow in July–September.
* **Audit Evaluation**: Properly captures the rainfed winter cereal cycle and rejects unassisted summer cropping.
* **VERDICT**: **[VALIDATED]**

---

### Location 8: Stara Zagora, Thrace, Bulgaria
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `April - October (7 Months)` | Freeze: `True` (Dec–Feb, down to -22.2°C) | K: `1`.
* **Institutional Ground Truth (Dobrudzha Agricultural Institute / Agro-Plovdiv)**:
  * In the Upper Thracian Plain, sunflower is sown from late March to early April and harvested in late August–September. Grain maize is sown in April and harvested in September–October.
  * Winter temperatures regularly drop below freezing (extreme continental lows down to -22°C), inducing strict vegetative dormancy from December through February.
* **Audit Evaluation**: April–October (7 months) perfectly bounds the spring row-crop cycle, and freeze dormancy Dec–Feb reflects the Balkan continental winter.
* **VERDICT**: **[VALIDATED]**

---

### Location 9: Timisoara, Banat, Romania
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `April - October (7 Months)` | S2: `March & November (2 Months, Non-Fallow)` | Freeze: `True` (Dec–Feb, down to -23.5°C) | K: `2`.
* **Institutional Ground Truth (INCDA Fundulea / USVT Timișoara)**:
  * In the fertile chernozem plains of Banat, farming systems are strictly single-crop per calendar year (`K = 1`): either full-season spring row crops (grain maize, sunflower, soybean) planted in April and harvested in September–October, OR winter cereals (winter wheat, winter barley, oilseed rape) sown in October and harvested in late June–July.
  * Double-cropping without irrigation is agronomically unfeasible.
* **Audit Critique**:
  1. **Disjoint Non-Fallow Season 2**: The engine deduced Season 2 as `"March & November (2 Months)"` and tagged it as `is_fallow: false`, thereby generating an erroneous `deduced_k = 2`.
  2. **Physical Impossibility**: March (early spring ground thaw, frequent night frosts) and November (late autumn frost, decaying photoperiod) are disjoint shoulder months separated by the 7-month summer cycle. No crop can germinate in March, pause during the entire summer, and mature in November.
  3. This defect replicates the logic failure identified in Champaign, IL (Batch 01).
* **VERDICT**: **[DEFECT]** (Unviable K=2 and biologically impossible disjoint non-fallow season).

---

### Location 10: Debrecen, Great Plain, Hungary
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `April - October (7 Months)` | Freeze: `True` (Dec–Feb, down to -26.6°C) | K: `1`.
* **Institutional Ground Truth (University of Debrecen / ATK TAKI)**:
  * In the *Hajdúság* / Eastern Alföld, grain maize and sunflower are drilled mid-to-late April once soil temperatures reach 10°C, with harvest spanning September through late October.
  * Winter freeze dormancy from December through February is absolute, with minimum temperatures dropping below -25°C.
* **Audit Evaluation**: Flawless delineation of the Pannonian continental summer grain season. K=1 is strictly appropriate.
* **VERDICT**: **[VALIDATED]**

---

### Location 11: Trnava, Danubian Lowland, Slovakia
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `April - September (6 Months)` | Freeze: `True` (Nov–Mar, 5 months, down to -24.2°C) | K: `1`.
* **Institutional Ground Truth (NPPC - VÚRV Piešťany)**:
  * In the Danubian Lowland (*Podunajská nížina*), sugar beet, malting barley, and grain maize are primary crops. Sowing occurs in April (late March for early barley/beet), with harvest occurring in September for silage maize and early barley, extending into October/November for sugar beet and grain maize.
  * Biological freeze halts are extensive, running from November through March.
* **Audit Evaluation**: The 6-month window (`April - September`) captures the core frost-free vegetative growth period. While sugar beet and grain maize field drying can stretch into October, the deduced window is well within the acceptable ±1 month envelope of the active thermal season.
* **VERDICT**: **[ACCEPTABLE]** (Solid frost-free envelope; note that sugar beet harvest extends through October).

---

### Location 12: Lublin, Lublin Upland, Poland
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | Freeze: `True` (Nov–Mar, 5 months, down to -31.3°C) | K: `1`.
* **Institutional Ground Truth (IUNG-PIB Puławy)**:
  * In the Lublin Voivodeship (mean annual temperature 8.4°C), the frost-free growing season is short. Spring crops (spring barley, maize, soft fruits, hops) are established in late April to May, and harvested in late August to September.
  * Winter is severe and prolonged, with soil freeze depths exceeding 50 cm and minimum temperatures plunging to -31°C, enforcing an absolute 5-month biological halt from November through March.
* **Audit Evaluation**: Exact alignment with IUNG agrotechnical guidelines for eastern Poland.
* **VERDICT**: **[VALIDATED]**

---

### Location 13: Vinnytsia, Podolia, Ukraine
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | Freeze: `True` (Nov–Mar, 5 months, down to -30.1°C) | K: `1`.
* **Institutional Ground Truth (APK-Inform / NAAS Ukraine)**:
  * In the central Ukrainian Forest-Steppe, Vinnytsia is the national capital of sugar beet production and a major grain corn belt. Sowing occurs from mid-April to early May; active vegetative development occurs May–August; harvest runs September to October.
  * Deep winter dormancy is enforced from November through March, with freezing temperatures down to -30°C.
* **Audit Evaluation**: The 5-month window (`May - September`) accurately delineates the frost-free active growth cycle for summer cash crops.
* **VERDICT**: **[VALIDATED]**

---

### Location 14: Dnipro, Steppe, Ukraine
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `May - September (5 Months)` | Freeze: `True` (Nov–Mar, 5 months, down to -31.2°C) | K: `1`.
* **Institutional Ground Truth (APK-Inform)**:
  * In the southern Ukrainian Steppe, sunflower and grain maize are sown from mid-April to early May to exploit spring soil moisture reserves before severe summer heatwaves. Sunflower harvesting initiates in late August and peaks in September.
  * Hard continental winter halts vegetation from November through March, with sub-zero extremes below -31°C.
* **Audit Evaluation**: Accurate characterization of the Steppe oilseed summer window under continental freeze constraints.
* **VERDICT**: **[VALIDATED]**

---

### Location 15: Novi Sad, Vojvodina, Serbia
* **Engine Output**: Regime: `TEMPERATE_CONTINENTAL_FROST` | S1: `April - October (7 Months)` | Freeze: `True` (Dec–Feb, down to -25.0°C) | K: `1`.
* **Institutional Ground Truth (Institute of Field and Vegetable Crops - NS Seme)**:
  * In the Pannonian Basin chernozem zone of Vojvodina, grain maize, sunflower, and soybean are sown in April and harvested from September through October.
  * Sub-zero ground frost and freezing air from December through February halt cell division.
* **Audit Evaluation**: Perfect agronomic fidelity to the Pannonian summer row-crop cycle documented by NS Seme.
* **VERDICT**: **[VALIDATED]**

---

## 4. Root Cause Analysis of Detected Defects

### Defect 1: Zaragoza, Aragon, Spain (Regime Classification & Calendar Inversion)
* **Underlying Logic Flaw**: The engine's regime decision tree failed to incorporate precipitation threshold checks against atmospheric evaporative demand (PET) in Mediterranean interior basins. Because winter temperatures drop near freezing, the classifier defaulted to `TEMPERATE_OCEANIC_MARITIME` (or misattributed the thermal profile without checking maritime rainfall distribution).
* **Consequence**: An arid continental steppe (366 mm) was treated like a humid oceanic maritime zone. Consequently, the crop calendar was erroneously inverted into a summer window (`March - October`), ignoring the fact that rainfed crops in Zaragoza cannot survive July and August without irrigation.
* **Required Engine Fix**:
  * Add a check: If `annual_rain_mm < 400` and `summer_PET >> summer_rain` in southern Europe, classify as `MEDITERRANEAN_CONTINENTAL_STEPPE` or `SEMI_ARID_STEPPE`.
  * In semi-arid Mediterranean/steppe regimes, enforce the rainfed primary season as autumn-sown winter cereal (`October/November - May/June`).

### Defect 2: Timișoara, Banat, Romania (Disjoint Non-Fallow Season & Spurious K=2)
* **Underlying Logic Flaw**: When Season 1 was assigned as `April - October (7 Months)` and Freeze Dormancy was assigned as `December - February (3 Months)`, the remaining two months in the calendar year were `March` and `November`. A code defect merged these non-contiguous months into a single composite string (`"March & November (2 Months)"`) and inadvertently flagged `is_fallow: false`, which subsequently triggered `deduced_k = 2`.
* **Consequence**: Creation of an agronomically impossible cropping season where a commercial crop allegedly grows across disjoint months flanking the entire summer.
* **Required Engine Fix**:
  * Add an invariant assertion: Any non-fallow season **must be temporally contiguous** within a circular calendar year.
  * Residual shoulder months (`March`, `November`) in temperate continental frost regimes must default to transitional fallow (`is_fallow: true`, "Insufficient thermal units / vernalization transition") unless part of a continuous overwintering cycle. Enforce `K = 1` for rainfed temperate continental climates.

---

## 5. Regional Synthesis & Systemic Recommendations

1. **Overall Engine Health**:
   * **Pannonian & Eastern European Continental Frost Engine**: **90.0% Passing** (9/10 passing, 8 Validated, 1 Acceptable, 1 Defect). The engine handles freeze dormancy and spring-summer row crops across Central and Eastern Europe with high fidelity.
   * **Mediterranean Winter Rain Engine**: **100% Passing** (3/3 Validated: Foggia, Córdoba, Évora). Flawless handling of winter rains and summer drought.
   * **Continental Steppe Engine**: **66.7% Passing** (2/3 passing: Albacete and Karditsa Validated; Zaragoza Defect).
2. **Systemic Code Patches Needed**:
   * Patch the disjoint shoulder-month bug that caused spurious `K = 2` in Timișoara (and previously in Champaign, IL).
   * Rectify the Köppen *BSk* arid basin classification logic in the Iberian peninsula to prevent semi-arid valleys from being labeled oceanic maritime.
