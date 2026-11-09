# Independent Agronomic Systems & Crop Calendar Audit Report
**Batch 05: Middle East, Central Asia & South Asia (16 Strategic Agricultural Benchmarks)**
**Auditor**: Independent Senior Agronomist & Agro-Meteorological Systems Auditor
**Target Data**: `/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/audit_100_new_batches/batch05_mideast_south_central_asia.json`
**Reference Standards**: ICAR India (All India Coordinated Research Projects on Wheat & Barley, Soybean, Cotton, Millets; CCSHAU Hisar, PAU Ludhiana), PARC Pakistan (Pakistan Agricultural Research Council, Ayub Agricultural Research Institute Faisalabad), BARC Bangladesh (Bangladesh Agricultural Research Council, BRRI, BARI), Turkish Ministry of Agriculture and Forestry (Tarımsal Araştırmalar ve Politikalar Genel Müdürlüğü - TAGEM, Central Anatolian & GAP Agricultural Research Institutes), ICARDA (International Center for Agricultural Research in the Dry Areas), CIMMYT (Global Wheat & Maize Improvement Center), FAO Agro-Ecological Zones (AEZ).

---

## 1. Executive Summary

An exhaustive agro-meteorological and crop phenology audit was performed on the Crop Calendar Deduction Engine for **Batch 05 (Middle East, Central Asia & South Asia)**. This batch comprises 16 pivotal agricultural anchor locations across Turkey, Iran, Iraq, Kazakhstan, Uzbekistan, Pakistan, India, and Bangladesh.

The audit revealed a pronounced regional divergence in engine performance:
1. **West Asia & Mediterranean/Continental Steppe (Turkey, Iran, Iraq, Uzbekistan, Southern Kazakhstan)**: Demonstrated solid agro-climatic alignment. Autumn-sown winter cereal windows (October–May/June) and summer aridity/stubble fallows (June–September) are correctly distinguished across Anatolia, the Zagros mountains, Upper Mesopotamia, and the Talas River basin.
2. **South Asian Monsoonal & Alluvial Basins (Indus Basin & Indo-Gangetic Plains)**: Suffers from **severe architectural defects**, including:
   - **Monsoon Season Inversion in Semi-Arid India**: In Hisar, Haryana, where 77% of annual rain falls during the Southwest Monsoon (June–September, 360.8 mm), the engine hardcoded June–September as `"Summer Aridity & Extreme Heat Fallow"` with reason `"Summer heat and moisture deficit prevent rainfed summer crops."` Conversely, dry winter (108 mm rain over 8 months) was designated as the sole active growing season.
   - **Indus Basin Erasure in Pakistan**: The premier agricultural granaries of the Punjab Canal Colonies (Sahiwal and Bahawalpur) were categorized as `"HYPER_ARID_DESERT"` and relegated to 12 months of year-round fallow, completely erasing both Kharif (cotton/maize/rice) and Rabi (wheat) seasons.
   - **Discontinuous Split-Season Defect**: In monsoonal single-crop India (Aligarh, Ujjain, Amravati), array slicing artifacts generated non-contiguous, disjoint fallow blocks formatted as `"May & October - December (4 Months)"`, sandwiching the monsoonal season between two separated calendar fragments.
   - **Cerrado Terminology Leakage**: In multi-cropping locations in Andhra Pradesh and Bangladesh (Rajahmundry and Bogra), Brazilian Cerrado Portuguese terminology (`"Safra"`, `"Safrinha"`, `"Vazio Sanitario"`) was erroneously applied to the Godavari Delta and Bengal Delta.

### Key Regional Performance Metrics
* **Total Evaluated Locations**: 16
* **Validated (Flawless calendar, exact phenological match)**: 4 locations (25.0%)
* **Acceptable (Agronomically defensible, minor shoulder or terminology artifacts)**: 6 locations (37.5%)
* **Defect (Inverted seasons, year-round fallow erasure, or disjoint split seasons)**: 6 locations (37.5%)
* **Regional Accuracy Score (Validated + Acceptable)**: **62.5% (10 / 16)**
* **Defect Rate**: **37.5% (6 / 16)**

---

## 2. Systemic Architectural Root Causes

Code-level analysis of `src/seasonal_calendar.py` and evaluation against NASA POWER agro-meteorological inputs identified five structural defects in the deduction pipeline:

### Flaw A: Hardcoded Mediterranean Seasonality in `SEMI_ARID_STEPPE` (Lines 279–305)
```python
elif regime == "SEMI_ARID_STEPPE":
    if hemisphere == "Southern":
        s1_months = [4, 5, 6, 7, 8, 9, 10] # May - Nov (7 mo)
    else:
        s1_months = [9, 10, 11, 0, 1, 2, 3, 4] # Oct - May (8 mo)
    dry_months = [m for m in range(12) if m not in s1_months]
    s2_dur = len(dry_months)
    ...
    seasons["season_1"] = SeasonMetadata(
        1, "Cool-Season Rainfed Grain & Canola", ..., "ACTIVE_GROWING", ...
    )
    seasons["season_2"] = SeasonMetadata(
        2, "Summer Aridity & Extreme Heat Fallow", ..., "DROUGHT_DORMANCY", ...
    )
```
* **Mechanism**: When a location satisfies `abs(lat) >= 20.0 and annual_rain < 680.0 and aridity_index < 0.52`, the engine classifies it as `SEMI_ARID_STEPPE` and unconditionally assigns an 8-month cool-season active window (October–May) and a 4-month summer drought fallow (June–September) in the Northern Hemisphere.
* **Failure Mode in South Asia**: This logic correctly models winter-rainfall Mediterranean steppe (e.g., Eskisehir, Diyarbakir, Kermanshah), but **catastrophically fails in monsoonal semi-arid climates**. In Hisar, Haryana (lat 29.15°N, rain 469 mm, AI 0.305), peak precipitation occurs during the June–September Southwest Monsoon (360.8 mm). The engine classifies the monsoon as "Summer Aridity Fallow" and forces active crop production into the dry winter (108 mm rain), inverting agronomic reality.

### Flaw B: Discontinuous Month Indexing in Monomodal Split Fallow (Lines 606–626)
```python
wet_months = best_wet # e.g. [5, 6, 7, 8] (Jun - Sep)
dry_months = [m for m in range(12) if m not in wet_months]
# dry_months = [0, 1, 2, 3, 4, 9, 10, 11] (natural calendar order)
s2_dur = max(1, len(dry_months) // 2) # 4
s2_months = dry_months[:s2_dur]        # [0, 1, 2, 3] -> Jan - Apr
s3_months = dry_months[s2_dur:]        # [4, 9, 10, 11] -> May & Oct - Dec
```
* **Mechanism**: In `TROPICAL_MONOMODAL_RAIN` with single cropping ($K=1$), non-growing months are gathered via list comprehension from `range(12)`. When monsoon rain occurs in June–September (`[5, 6, 7, 8]`), `dry_months` is ordered `[0, 1, 2, 3, 4, 9, 10, 11]`. Slicing at index 4 assigns January–April to Season 2 and leaves `[4, 9, 10, 11]` (May, October, November, December) to Season 3.
* **Failure Mode**: Season 3 becomes a physically disjointed, non-contiguous block: **"May & October - December (4 Months)"**. A farmer cannot observe a single continuous fallow or cover management window that begins in October, halts for four months of winter in Season 2, re-emerges for one month in May, and terminates before the June monsoon.

### Flaw C: Indus Basin Agro-Economic Erasure under Hyper-Arid Rule (Lines 182–183 & 219–228)
```python
if annual_rain < 120.0 or (aridity_index < 0.20 and annual_tmean >= 14.0):
    regime = "HYPER_ARID_DESERT"
```
* **Mechanism**: Sahiwal (292.9 mm rain, AI 0.183) and Bahawalpur (184.8 mm rain, AI 0.114) exceed 120 mm rainfall, but because high temperatures drive PET to ~1600 mm, their aridity index drops below 0.20. The engine classifies them as `HYPER_ARID_DESERT` and assigns 12 months of `"Pluvial Hyper-Arid Fallow (Year-Round)"` with 0 active cropping windows.
* **Failure Mode**: Sahiwal and Bahawalpur are core districts of the Punjab Canal Colonies, representing one of the most productive agricultural regions in Asia (cotton-wheat and maize-potato rotations). Marking this region as an uncultivated year-round fallow wasteland violates the system's purpose. Furthermore, the reason string contains a hardcoded formatting bug: `f"Hyper-arid pluvial desert ({annual_rain:.1f} mm < 120 mm)"`, printing mathematically contradictory statements like `(292.9 mm < 120 mm)`.

### Flaw D: Brazilian Cerrado Terminology Leakage in South Asia (Lines 534–569)
```python
if len(wet_months) >= 6 and lgp_days >= 210:
    seasons["season_1"] = SeasonMetadata(..., "Primary Wet Season (Safra / Summer Anchor)", ...)
    seasons["season_2"] = SeasonMetadata(..., "Secondary Wet Season (Safrinha / Succession)", ...)
    seasons["season_3"] = SeasonMetadata(..., "Dry Season Fallow / Vazio Sanitario", ...)
```
* **Mechanism**: In high-rainfall tropical monomodal zones ($LGP \ge 210$, wet months $\ge 6$), double-cropping logic hardcodes Portuguese regional terminology (`Safra`, `Safrinha`, `Vazio Sanitario`).
* **Failure Mode**: In Rajahmundry (Godavari Delta, Andhra Pradesh) and Bogra (Karatoya Plain, Bangladesh), the engine outputs Brazilian legal biosecurity concepts ("Vazio Sanitario") and Cerrado succession terminology ("Safrinha Corn") completely foreign to South Asian ICAR and BARC frameworks.

### Flaw E: Neglect of Vertisol Stored-Moisture Rabi Potential (Lines 571–574)
```python
can_double_crop = (candidate_s2_rain >= 75.0 and lgp_days >= 200)
```
* **Mechanism**: Double-cropping in tropical monomodal regimes is prohibited unless post-monsoon rain exceeds 75 mm and LGP exceeds 200 days.
* **Failure Mode**: In the Malwa Plateau (Ujjain, MP), deep black Vertisols hold 200–250 mm of plant-available water. Farmers routinely cultivate a double crop of soybean in Kharif followed by chickpea or durum wheat in Rabi on residual moisture. The rigid meteorological rainfall threshold ignores soil water storage dynamics, forcing a single-crop ($K=1$) classification with an 8-month fallow.

---

## 3. Master Audit Scorecard

| # | Location | Country | Deduced Regime | Deduced K | S1 Window (Role) | S2 Window (Role) | S3 Window (Role) | Calendar Integrity (Total Months / Continuity) | Official Extension Benchmark (ICAR / PARC / BARC / Min. Ag) | Audit Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Eskisehir, Central Anatolia** | Turkey | SEMI_ARID_STEPPE | 1 | Oct - May (8 mo, Winter Cereal/Oilseed) | Jun - Sep (4 mo, Summer Fallow) | None (0 mo) | 12 mo (Contiguous 8+4) | TAGEM: Winter wheat drilled Oct, dormant Dec-Feb, harvested Jul. S1 covers vegetative cycle; Jun harvest in S2. | **[ACCEPTABLE]** |
| 2 | **Diyarbakir, SE Anatolia** | Turkey | SEMI_ARID_STEPPE | 1 | Oct - May (8 mo, Winter Cereal/Oilseed) | Jun - Sep (4 mo, Summer Fallow) | None (0 mo) | 12 mo (Contiguous 8+4) | TAGEM/GAP: Durum wheat & red lentil sown Nov, harvested May/early Jun. 96% rain in Oct-May. Perfect match. | **[VALIDATED]** |
| 3 | **Edirne, Thrace** | Turkey | MEDITERRANEAN_CONTINENTAL_STEPPE | 1 | Oct - Jun (9 mo, Winter Grain) | Jul (1 mo, Post-Harvest Stubble) | Aug - Sep (2 mo, Summer Drought Fallow) | 12 mo (Contiguous 9+1+2) | TAGEM Thrace: Winter wheat Oct-Jun, harvest late Jun/Jul. Sunflower Apr-Aug. Rainfed grain calendar flawless. | **[VALIDATED]** |
| 4 | **Kermanshah, Zagros** | Iran | SEMI_ARID_STEPPE | 1 | Oct - May (8 mo, Winter Cereal/Oilseed) | Jun - Sep (4 mo, Summer Fallow) | None (0 mo) | 12 mo (Contiguous 8+4) | AREEO/DARI: Zagros dryland winter wheat, barley & chickpea sown Oct/Nov, harvest May. 99% rain in Oct-May. | **[VALIDATED]** |
| 5 | **Sari, Mazandaran** | Iran | MEDITERRANEAN_CONTINENTAL_STEPPE | 1 | Oct - Apr (7 mo, Winter Grain) | May - Jun (2 mo, Post-Harvest Stubble) | Jul - Sep (3 mo, Summer Drought Fallow) | 12 mo (Contiguous 7+2+3) | AREEO Mazandaran: Rainfed uplands winter wheat/canola Oct-May. Lowland paddy irrigated. Rainfed window sound. | **[ACCEPTABLE]** |
| 6 | **Kirkuk, Kirkuk Gov.** | Iraq | MEDITERRANEAN_CONTINENTAL_STEPPE | 1 | Oct - Apr (7 mo, Winter Grain) | May - Jun (2 mo, Post-Harvest Stubble) | Jul - Sep (3 mo, Summer Drought Fallow) | 12 mo (Contiguous 7+2+3) | Iraqi Min. Ag/FAO: Northern plains rainfed winter wheat/barley sown Nov/Dec, harvest Apr/May. Summer dry (3 mm). | **[VALIDATED]** |
| 7 | **Taraz, Zhambyl** | Kazakhstan | SEMI_ARID_STEPPE | 1 | Oct - May (8 mo, Winter Cereal/Oilseed) | Jun - Sep (4 mo, Summer Fallow) | None (0 mo) | 12 mo (Contiguous 8+4) | KazAgro/KazSRIWG: Southern KZ winter wheat sown Oct, harvest Jun. Sub-zero winter dormant; S1 bounds cycle. | **[ACCEPTABLE]** |
| 8 | **Bukhara, Zeravshan** | Uzbekistan | HYPER_ARID_DESERT | 1 | Jan - Dec (12 mo, Pluvial Hyper-Arid Fallow) | None (0 mo) | None (0 mo) | 12 mo (Contiguous 12) | Uzbek Min. Ag: Kyzylkum desert (138 mm rain, AI 0.10). Rainfed farming impossible. String formatting bug. | **[ACCEPTABLE]** |
| 9 | **Sahiwal, Punjab** | Pakistan | HYPER_ARID_DESERT | 1 | Jan - Dec (12 mo, Pluvial Hyper-Arid Fallow) | None (0 mo) | None (0 mo) | 12 mo (Contiguous 12) | PARC/AARI: Bari Doab canal colony. Double crop cotton-wheat, maize-potato. Year-round fallow is fatal mismatch. | **[DEFECT]** |
| 10 | **Bahawalpur, Punjab** | Pakistan | HYPER_ARID_DESERT | 1 | Jan - Dec (12 mo, Pluvial Hyper-Arid Fallow) | None (0 mo) | None (0 mo) | 12 mo (Contiguous 12) | PARC/RARI: Sutlej canal colonies, premier cotton-wheat belt. Categorized as 100% fallow wasteland. | **[DEFECT]** |
| 11 | **Hisar, Haryana** | India | SEMI_ARID_STEPPE | 1 | Oct - May (8 mo, Winter Cereal/Oilseed) | Jun - Sep (4 mo, Summer Drought Fallow) | None (0 mo) | 12 mo (Contiguous 8+4) | CCSHAU/ICAR: 77% rain (361 mm) in Jun-Sep (Kharif bajra/cotton/pulses). Flagged as drought fallow! INVERTED. | **[DEFECT]** |
| 12 | **Aligarh, Uttar Pradesh** | India | TROPICAL_MONOMODAL_RAIN | 1 | Jun - Sep (4 mo, Monsoonal Wet) | Jan - Apr (4 mo, Dry Season Dormancy) | May & Oct - Dec (4 mo, Disjoint Fallow) | 12 mo (**Disjoint Non-Contiguous S3**) | ICAR-IIPR/Doab: Rice-wheat/mustard belt. S3 split into disjoint fragments (May & Oct-Dec). Rabi wheat omitted. | **[DEFECT]** |
| 13 | **Ujjain, Madhya Pradesh** | India | TROPICAL_MONOMODAL_RAIN | 1 | Jun - Sep (4 mo, Monsoonal Wet) | Jan - Apr (4 mo, Dry Season Dormancy) | May & Oct - Dec (4 mo, Disjoint Fallow) | 12 mo (**Disjoint Non-Contiguous S3**) | ICAR-IISR: Malwa Vertisols support Kharif soy + Rabi chickpea/durum on residual moisture. S3 disjoint fragment bug. | **[DEFECT]** |
| 14 | **Amravati, Maharashtra** | India | TROPICAL_MONOMODAL_RAIN | 1 | Jun - Sep (4 mo, Monsoonal Wet) | Jan - Apr (4 mo, Dry Season Dormancy) | May & Oct - Dec (4 mo, Disjoint Fallow) | 12 mo (**Disjoint Non-Contiguous S3**) | Dr. PDKV/ICAR-CICR: Vidarbha cotton spans Jun-Dec (150-180 d). Cut off at Sep. S3 non-contiguous split bug. | **[DEFECT]** |
| 15 | **Rajahmundry, Andhra P.** | India | TROPICAL_MONOMODAL_RAIN | 2 | May - Aug (4 mo, SW Monsoon) | Sep - Dec (4 mo, NE Monsoon / Succession) | Jan - Apr (4 mo, Dry Season Fallow) | 12 mo (Contiguous 4+4+4) | ANGRAU: Godavari Delta Kharif (Sarva) & Rabi (Dalwa). Correct K=2 separation; Brazilian Cerrado naming bug. | **[ACCEPTABLE]** |
| 16 | **Bogra, Rajshahi** | Bangladesh | TROPICAL_MONOMODAL_RAIN | 2 | Apr - Jul (4 mo, Aus Pre-Monsoon) | Aug - Nov (4 mo, T. Aman Monsoon) | Dec - Mar (4 mo, Boro Dry Season) | 12 mo (Contiguous 4+4+4) | BARC/BRRI: Premier potato & Boro hub. Aus (Apr-Jul) & Aman (Aug-Nov) separated cleanly. Brazilian naming bug. | **[ACCEPTABLE]** |

---

## 4. Deep-Dive Location Audits

### Location 1: Eskisehir, Central Anatolia, Turkey
* **Deduced Engine Output**: Regime: `SEMI_ARID_STEPPE` | S1: `October - May (8 Months)` [Active, Rain: 382.8 mm, Tmean: 6.8°C, Tmin: -20.2°C] | S2: `June - September (4 Months)` [Fallow, Rain: 114.0 mm, Tmean: 20.6°C] | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (TAGEM Central Anatolia / Eskisehir Agricultural Research Institute)**:
  * Agro-Ecology: Anatolian Plateau semi-arid steppe ($BSk$), elevation 788 m, annual rainfall 496.8 mm, mean temperature 11.4°C.
  * Cropping System: Rainfed winter wheat (*Triticum aestivum*) and malting barley (*Hordeum vulgare*); irrigated sugar beet and sunflower.
  * Crop Calendar: Winter cereals drilled in October; crop enters semi-dormancy in December–February (freezing temperatures with snow cover); vegetative surge in March–April; heading and grain filling in May; harvesting takes place in late June to mid-July.
* **Audit Critique**:
  * S1 (October–May) covers the foundation of the winter cereal vegetative and reproductive cycle.
  * Placing June into Season 2 summer fallow cuts off the maturity/harvest period, but is agronomically defensible as an 8-month active grain cycle.
  * The calendar satisfies 12-month conservation ($8 + 4 = 12$).
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 2: Diyarbakir, Southeastern Anatolia, Turkey
* **Deduced Engine Output**: Regime: `SEMI_ARID_STEPPE` | S1: `October - May (8 Months)` [Active, Rain: 478.5 mm, Tmean: 9.1°C, Tmin: -21.7°C] | S2: `June - September (4 Months)` [Fallow, Rain: 22.0 mm, Tmean: 28.0°C] | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (TAGEM GAP International Agricultural Research Institute)**:
  * Agro-Ecology: Upper Tigris basin, Mediterranean-continental steppe ($Csa/BSk$), annual rain 500.5 mm, mean temp 15.4°C. Precipitation is strongly winter-dominant: 478.5 mm (95.6%) falls between October and May, while June–September receives only 22.0 mm against PET of 656 mm.
  * Cropping System: Rainfed durum wheat (*Triticum durum*) and red lentils (*Lens culinaris*); irrigated cotton and watermelon in the GAP canal zones.
  * Crop Calendar: Red lentils and durum wheat sown in late October/November; harvested in May (lentils) and late May/early June (durum wheat). Summer is blisteringly hot (July/August mean >30°C, max >42°C) and completely dry.
* **Audit Critique**:
  * S1 (October–May) matches the local rainfed winter grain/lentil vegetative window.
  * S2 (June–September) captures the hyper-arid, extreme summer heat stubble fallow.
  * Flawless representation of Southeastern Anatolian dryland agronomy.
* **VERDICT**: **[VALIDATED]**

---

### Location 3: Edirne, Thrace, Turkey
* **Deduced Engine Output**: Regime: `MEDITERRANEAN_CONTINENTAL_STEPPE` | S1: `October - June (9 Months)` [Active, Rain: 513.6 mm, Tmean: 10.2°C, Tmin: -23.4°C] | S2: `July (1 Month)` [Fallow, Rain: 36.6 mm, Tmean: 25.9°C] | S3: `August - September (2 Months)` [Fallow, Rain: 63.3 mm, Tmean: 23.2°C] | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (TAGEM Thrace Agricultural Research Institute / Trakya University)**:
  * Agro-Ecology: Meric/Tundzha basin, transition Mediterranean-continental climate ($Cfa/Csa$), annual rainfall 613.5 mm, mean temp 13.6°C.
  * Cropping System: High-yielding rainfed winter soft wheat, oilseed sunflower, and irrigated paddy rice.
  * Crop Calendar: Winter wheat sown in October–November; overwintering with moderate chill; grain fill in May; harvested late June to early July.
* **Audit Critique**:
  * S1 (October–June, 9 months) incorporates the full growth and harvesting window of Thracian winter wheat.
  * S2 (July post-harvest rest) and S3 (August–September drought fallow) conserve 12 continuous months ($9 + 1 + 2 = 12$).
* **VERDICT**: **[VALIDATED]**

---

### Location 4: Kermanshah, Kermanshah, Iran
* **Deduced Engine Output**: Regime: `SEMI_ARID_STEPPE` | S1: `October - May (8 Months)` [Active, Rain: 342.8 mm, Tmean: 8.1°C, Tmin: -19.8°C] | S2: `June - September (4 Months)` [Fallow, Rain: 4.3 mm, Tmean: 25.4°C] | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (AREEO Dryland Agricultural Research Institute - DARI / Kermanshah Center)**:
  * Agro-Ecology: Zagros Mountain highland valley, Mediterranean semi-arid ($BSk/Csa$), elevation 1350 m, annual rainfall 347.1 mm, mean temp 13.8°C. Virtually all rainfall (342.8 mm out of 347.1 mm, 98.8%) occurs during October–May; June–September receives a negligible 4.3 mm total.
  * Cropping System: Rainfed bread wheat, feed barley, and cold-tolerant Kabuli chickpeas.
  * Crop Calendar: Autumn-sown cereals drilled in October–November; dormant in January; harvested in late May to June.
* **Audit Critique**:
  * Perfect match for Zagros winter-rainfall rainfed cereals.
  * Summer fallow (June–September) reflects the extreme 4.3 mm moisture deficit. Full 12-month conservation.
* **VERDICT**: **[VALIDATED]**

---

### Location 5: Sari, Mazandaran, Iran
* **Deduced Engine Output**: Regime: `MEDITERRANEAN_CONTINENTAL_STEPPE` | S1: `October - April (7 Months)` [Active, Rain: 408.6 mm, Tmean: 12.0°C] | S2: `May - June (2 Months)` [Fallow, Rain: 31.4 mm, Tmean: 23.6°C] | S3: `July - September (3 Months)` [Fallow, Rain: 95.1 mm, Tmean: 26.5°C] | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (AREEO Rice Research Institute of Iran - Amol / Mazandaran Center)**:
  * Agro-Ecology: Caspian southern coastal plain, Humid Subtropical / Sub-Mediterranean border ($Cfa/Csa$), annual rainfall 535.1 mm, mean temp 17.5°C.
  * Cropping System: Alluvial plain is dominated by intensive irrigated paddy rice (transplanted April/May, harvested August), followed by ratoon rice, winter canola, or vegetables. Rainfed foothills produce winter wheat and barley.
* **Audit Critique**:
  * For pure rainfed production, October–April (408.6 mm) accurately captures the winter cereal cycle.
  * Summer (June–August) has a severe moisture deficit under non-irrigated conditions (PET > 165 mm/month vs rain ~20 mm).
  * While the engine misses the irrigated summer rice economy of the Caspian coast, its rainfed cereal calendar is defensible.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 6: Kirkuk, Kirkuk Governorate, Iraq
* **Deduced Engine Output**: Regime: `MEDITERRANEAN_CONTINENTAL_STEPPE` | S1: `October - April (7 Months)` [Active, Rain: 260.9 mm, Tmean: 13.7°C, Tmin: -5.3°C] | S2: `May - June (2 Months)` [Fallow, Rain: 18.5 mm, Tmean: 28.9°C] | S3: `July - September (3 Months)` [Fallow, Rain: 3.4 mm, Tmean: 33.6°C] | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (Ministry of Agriculture Baghdad / FAO Iraq Cereal Assessment)**:
  * Agro-Ecology: Northern Iraqi undulating plain / Zagros piedmont, semi-arid steppe ($BSh/BWh$), annual rain 282.8 mm, mean temp 21.2°C. Rain is concentrated entirely between November and April; July–September is desiccating (3.4 mm rain, mean temp 34°C, max >45°C).
  * Cropping System: Rainfed and supplemental irrigated winter wheat and two-row barley.
  * Crop Calendar: Winter cereals drilled after first soaking rains in November–December; harvested in April to early May.
* **Audit Critique**:
  * S1 (October–April, 7 months) cleanly frames the winter wheat growing season.
  * S2 and S3 correctly map post-harvest desiccation and hyper-arid summer dormancy.
* **VERDICT**: **[VALIDATED]**

---

### Location 7: Taraz, Zhambyl Region, Kazakhstan
* **Deduced Engine Output**: Regime: `SEMI_ARID_STEPPE` | S1: `October - May (8 Months)` [Active, Rain: 301.4 mm, Tmean: 6.2°C, Tmin: -25.9°C] | S2: `June - September (4 Months)` [Fallow, Rain: 53.5 mm, Tmean: 24.3°C] | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (Kazakh National Agrarian University / Kazakh Research Institute of Agriculture and Plant Growing)**:
  * Agro-Ecology: Talas River oasis, Northern Tian Shan foothills, continental semi-arid steppe ($BSk$), annual rain 354.9 mm, mean temp 12.3°C.
  * Winter Severity: Dec, Jan, and Feb means are sub-zero (-1.8°C, -2.4°C, -0.3°C), with extreme minimums dropping to -25.9°C.
  * Cropping System: Southern Kazakhstan is the primary zone in the country cultivating autumn-sown winter wheat (*озимая пшеница*), unlike the vast spring wheat belts of Northern Kazakhstan (Kostanay, Akmola). Irrigated onions and sugar beets occupy river flats.
  * Crop Calendar: Winter wheat sown in late September–October; overwinters in dormancy under snow cover; vegetative surge in March–April; harvested in June.
* **Audit Critique**:
  * Correctly identifies autumn-sown winter wheat rather than spring wheat.
  * June–September summer aridity fallow (53.5 mm rain, PET 630 mm) matches dryland stubble realities.
  * Minor limitation: The engine marks October–May as continuous active growth without segmenting deep winter freeze dormancy (Dec–Feb). However, the crop remains in the ground throughout this period.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 8: Bukhara, Bukhara Region, Uzbekistan
* **Deduced Engine Output**: Regime: `HYPER_ARID_DESERT` | S1: `January - December (12 Months)` [Drought Fallow, Rain: 138.7 mm, Tmean: 15.9°C, Tmin: -17.8°C] | S2: `None` | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (Ministry of Agriculture Republic of Uzbekistan / ICARDA Central Asia)**:
  * Agro-Ecology: Kyzylkum Desert / lower Zeravshan River basin, cold desert ($BWk$), annual rain 138.7 mm, PET 1315.7 mm (Aridity Index 0.105).
  * Cropping System: 100% of crop production (cotton, winter wheat, fodder maize) is dependent on large-scale canal irrigation from the Amu Darya and Zeravshan rivers. Zero rainfed agriculture is viable.
* **Audit Critique**:
  * Correctly determines that rainfed crop production is impossible, designating a year-round fallow / irrigation mandatory status.
  * Code Bug: The fallow reason string hardcodes `(138.7 mm < 120 mm)`, creating a false inequality statement because the desert threshold was triggered via aridity index ($AI < 0.20$), not rainfall $< 120$ mm.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 9: Sahiwal, Punjab, Pakistan
* **Deduced Engine Output**: Regime: `HYPER_ARID_DESERT` | S1: `January - December (12 Months)` [Drought Fallow, Rain: 292.9 mm, Tmean: 27.1°C, Tmin: -0.6°C] | S2: `None` | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (PARC Pakistan / Ayub Agricultural Research Institute Faisalabad)**:
  * Agro-Ecology: Bari Doab canal irrigated alluvial plain, hot semi-arid/desert border ($BWh/BSh$), annual rainfall 292.9 mm, PET 1599.1 mm.
  * Cropping System: One of the most productive multi-cropping agricultural hubs in South Asia:
    * **Kharif Season (May–October)**: Cotton, grain maize, basmati rice, forage sorghum.
    * **Rabi Season (November–April)**: High-yielding wheat, autumn potato, mustard, winter fodder (berseem).
* **Audit Critique**:
  * **Critical Engine Failure**: The engine classifies Sahiwal as an uncultivated desert fallow for 365 days of the year, erasing both the monsoon Kharif and winter Rabi seasons.
  * Root cause: Aridity index $292.9 / 1599.1 = 0.183 < 0.20$ triggered `HYPER_ARID_DESERT`.
  * The reason string outputs the contradiction: `"Hyper-arid pluvial desert (292.9 mm < 120 mm)"`.
* **VERDICT**: **[DEFECT]**

---

### Location 10: Bahawalpur, Punjab, Pakistan
* **Deduced Engine Output**: Regime: `HYPER_ARID_DESERT` | S1: `January - December (12 Months)` [Drought Fallow, Rain: 184.8 mm, Tmean: 27.7°C, Tmin: 0.6°C] | S2: `None` | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (PARC Pakistan / Regional Agricultural Research Institute Bahawalpur)**:
  * Agro-Ecology: Sutlej River canal colony / Cholistan desert margin ($BWh$), annual rainfall 184.8 mm, PET 1613.8 mm.
  * Cropping System: Intensive canal-fed cotton-wheat cropping system:
    * **Kharif (May–October)**: Bt cotton, sunflower, cluster bean (guar).
    * **Rabi (November–April)**: Bread wheat, chickpea, canola/mustard.
* **Audit Critique**:
  * Identical failure to Sahiwal: Relegated to 100% year-round fallow, wiping out Pakistan's core cotton-wheat belt from the calendar engine.
  * Fallow reason displays the false statement `(184.8 mm < 120 mm)`.
* **VERDICT**: **[DEFECT]**

---

### Location 11: Hisar, Haryana, India
* **Deduced Engine Output**: Regime: `SEMI_ARID_STEPPE` | S1: `October - May (8 Months)` [Active, Rain: 108.2 mm, Tmean: 22.8°C, Tmin: 0.2°C] | S2: `June - September (4 Months)` [Fallow, Rain: 360.8 mm, Tmean: 33.0°C] | S3: `None` | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (ICAR / CCS Haryana Agricultural University - CCSHAU Hisar)**:
  * Agro-Ecology: Western Haryana semi-arid zone ($BSh$), annual rainfall 469.0 mm, PET 1538.4 mm.
  * Seasonal Rainfall Distribution:
    * **Monsoon (June–September)**: **360.8 mm** (76.9% of annual total).
    * **Winter/Spring (October–May)**: **108.2 mm** (23.1% over 8 months, averaging 13.5 mm/month).
  * Cropping System:
    * **Kharif Season (June/July–October)**: The primary rainfed production window! Pearl millet (*bajra*), cluster bean (*guar*), green gram (*mung*), cowpea, and cotton.
    * **Rabi Season (November–April)**: Wheat, Indian mustard (*raya*), chickpea, irrigated via Western Yamuna and Bhakra canal systems.
* **Audit Critique**:
  * **Complete Seasonal Inversion (Severe Defect)**:
    1. The wet monsoon season (June–September, 360.8 mm rain) is classified as `"Summer Aridity & Extreme Heat Fallow"` with reason `"Summer heat and moisture deficit prevent rainfed summer crops."`
    2. The dry winter (October–May, 108.2 mm rain) is designated as the sole active growing season and labeled `"Cool-Season Rainfed Grain & Canola"`.
  * Forcing dryland farmers to leave the monsoon fallow while attempting rainfed broadacre cropping during the dry winter is an agro-climatological inversion.
* **VERDICT**: **[DEFECT]**

---

### Location 12: Aligarh, Uttar Pradesh, India
* **Deduced Engine Output**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - September (4 Months)` [Active, Rain: 615.4 mm, Tmean: 31.5°C] | S2: `January - April (4 Months)` [Fallow, Rain: 61.7 mm, Tmean: 21.7°C, Tmin: -1.0°C] | S3: `May & October - December (4 Months)` [Fallow, Rain: 52.3 mm, Tmean: 24.0°C] | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (ICAR-Indian Institute of Farming Systems Research / Aligarh Muslim University Ag. Faculty)**:
  * Agro-Ecology: Central Ganga-Yamuna Doab alluvial plain ($Cwa$), annual rainfall 729.4 mm, mean temp 25.7°C.
  * Cropping System: High-intensity double cropping:
    * **Kharif (June–October)**: Basmati and non-basmati rice, grain maize, pearl millet, pigeonpea.
    * **Rabi (November–April)**: Bread wheat, Indian mustard, autumn potato, sugarcane.
    * **Zaid (April–June)**: Spring mungbean, cucurbits, forage.
* **Audit Critique**:
  * **Discontinuous Split Season Bug**: Season 3 is split into non-contiguous months: `"May & October - December (4 Months)"`.
  * **Rabi Omission**: The engine sets $K=1$, leaving October through May as an unbroken 8-month fallow, ignoring North India's premier wheat-mustard Rabi season.
* **VERDICT**: **[DEFECT]**

---

### Location 13: Ujjain, Madhya Pradesh, India
* **Deduced Engine Output**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - September (4 Months)` [Active, Rain: 859.2 mm, Tmean: 27.0°C] | S2: `January - April (4 Months)` [Fallow, Rain: 18.7 mm, Tmean: 24.2°C] | S3: `May & October - December (4 Months)` [Fallow, Rain: 49.2 mm, Tmean: 24.5°C] | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (ICAR-Indian Institute of Soybean Research Indore / RVSKVV Gwalior)**:
  * Agro-Ecology: Malwa Plateau, semi-arid tropical monsoon ($Aw/Cwa$), annual rainfall 927.2 mm (92.7% in June–September). Deep black soils (Vertisols) with exceptionally high water-holding capacity (available water capacity 200–250 mm/m).
  * Cropping System:
    * **Kharif (June–September)**: Soybean capital of India, plus maize and blackgram.
    * **Rabi (October–March)**: Chickpea (*desi* and *kabuli*) and Malwi durum wheat grown on stored Vertisol residual moisture without supplemental summer irrigation.
* **Audit Critique**:
  * **Discontinuous Split Season Bug**: Season 3 suffers from the same array-slicing defect: `"May & October - December (4 Months)"`.
  * **Vertisol Double-Cropping Blindness**: The engine restricts Ujjain to single cropping ($K=1$) and designates October–May as fallow, ignoring the standard soybean-chickpea/durum wheat double-crop sequence enabled by Vertisol moisture retention.
* **VERDICT**: **[DEFECT]**

---

### Location 14: Amravati, Maharashtra, India
* **Deduced Engine Output**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `June - September (4 Months)` [Active, Rain: 830.3 mm, Tmean: 27.4°C] | S2: `January - April (4 Months)` [Fallow, Rain: 46.1 mm, Tmean: 26.9°C] | S3: `May & October - December (4 Months)` [Fallow, Rain: 71.5 mm, Tmean: 25.8°C] | K: `1` | Freeze Dormancy: `False`.
* **Official Benchmark (Dr. Panjabrao Deshmukh Krishi Vidyapeeth - PDKV Akola / ICAR-CICR Nagpur)**:
  * Agro-Ecology: Vidarbha black soil belt, tropical monomodal ($Aw$), annual rainfall 947.9 mm (87.6% in June–September).
  * Cropping System: Rainfed cotton (*Gossypium hirsutum*) intercropped with pigeonpea (*Cajanus cajan*), and soybean followed by post-monsoon chickpea.
* **Audit Critique**:
  * **Cotton Phenological Truncation**: Vidarbha cotton is a long-duration crop requiring 150–180 days (June to November/December). The engine forces S1 to terminate abruptly after 4 months in September, leaving the boll development and picking stages stranded in a declared fallow period.
  * **Discontinuous Split Season Bug**: S3 is fragmented into `"May & October - December (4 Months)"`.
* **VERDICT**: **[DEFECT]**

---

### Location 15: Rajahmundry, Andhra Pradesh, India
* **Deduced Engine Output**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `May - August (4 Months)` [Active, Rain: 611.4 mm, Tmean: 29.3°C] | S2: `September - December (4 Months)` [Active, Rain: 512.4 mm, Tmean: 25.2°C] | S3: `January - April (4 Months)` [Fallow, Rain: 49.4 mm, Tmean: 27.7°C] | K: `2` | Freeze Dormancy: `False`.
* **Official Benchmark (Acharya N.G. Ranga Agricultural University - ANGRAU / ICAR-CTRI Rajahmundry)**:
  * Agro-Ecology: Godavari Delta coastal alluvial plain ($Aw$), annual rainfall 1173.3 mm, computed LGP 218 days. The region receives both Southwest Monsoon (June–September) and substantial Northeast Monsoon / retreating cyclone rains (October–November, 289.7 mm).
  * Cropping System: Two distinct cropping seasons ($K=2$):
    * **Kharif (Sarva)**: Long-duration paddy rice (June/July–November).
    * **Rabi (Dalwa)**: Short-duration rice, blackgram, groundnut, or maize (December/January–April).
* **Audit Critique**:
  * **Sound Seasonal Architecture**: Correctly deduces $K=2$ and segments two active 4-month windows (May–August and September–December), capturing the bi-monsoonal pluvial surge, followed by a continuous 4-month dry fallow (January–April). Full 12 continuous months ($4 + 4 + 4 = 12$).
  * **Terminology Defect**: S1 is named `"Safra / Summer Anchor"`, S2 is named `"Safrinha / Succession"`, and S3 is named `"Vazio Sanitario"`. These Brazilian Cerrado concepts are inappropriate for the Godavari Delta.
* **VERDICT**: **[ACCEPTABLE]**

---

### Location 16: Bogra, Rajshahi Division, Bangladesh
* **Deduced Engine Output**: Regime: `TROPICAL_MONOMODAL_RAIN` | S1: `April - July (4 Months)` [Active, Rain: 991.3 mm, Tmean: 29.8°C] | S2: `August - November (4 Months)` [Active, Rain: 742.8 mm, Tmean: 26.1°C] | S3: `December - March (4 Months)` [Fallow, Rain: 57.9 mm, Tmean: 20.4°C] | K: `2` | Freeze Dormancy: `False`.
* **Official Benchmark (BARC / Bangladesh Rice Research Institute - BRRI / BARI Bogra Station)**:
  * Agro-Ecology: Karatoya floodplain / Barind Tract margin ($Cwa/Aw$), annual rainfall 1792.0 mm, computed LGP 259 days. Seven consecutive months receive $>100$ mm rainfall (April–October).
  * Cropping System:
    * **Aus (Pre-Monsoon)**: Broadcast/transplanted rice, jute (April–July).
    * **Aman (Monsoon)**: Transplanted Aman rice (*Ropa Aman*) (August–November/December).
    * **Boro (Winter)**: Irrigated Boro rice, premier potato belt, mustard, maize (December–April).
* **Audit Critique**:
  * S1 (April–July, 991 mm rain) cleanly aligns with the pre-monsoonal Aus cycle.
  * S2 (August–November, 743 mm rain) matches the main monsoonal Aman rice cycle.
  * S3 (December–March, 58 mm rain) represents the dry winter season (rainfed fallow; irrigated Boro/potato).
  * Full 12 continuous months ($4 + 4 + 4 = 12$). Brazilian terminology artifact present, but agronomic calendar structure is robust.
* **VERDICT**: **[ACCEPTABLE]**

---

## 5. Synthesis of Auditor Verification Queries

### Query 1: Anatolia, Iran & Central Asia (Eskisehir, Kermanshah, Taraz)
> *Are autumn-sown winter wheat vs summer heat aridity fallow properly recognized?*

* **Auditor Finding**: **YES, PROPERLY RECOGNIZED.**
* **Agro-Meteorological Evidence**:
  * In Eskisehir, Diyarbakir, Edirne, Kermanshah, and Kirkuk, rainfall is winter-dominant (October–May precipitation comprises $>85\%$ of annual totals). The engine assigns an 8-to-9 month active window (October–May/June) dedicated to broadacre winter cereals, accompanied by a 3-to-4 month summer heat and moisture deficit fallow (June/July–September).
  * In Taraz (Kazakhstan), the engine correctly avoids classifying the location as spring wheat (as occurs in northern Kazakhstan) and assigns the autumn-sown winter cereal cycle (October–May). Although sub-zero ground freeze in December–February is unsegmented, the crop resides in the soil across this window.

### Query 2: Indus Basin & Indo-Gangetic Plains (Sahiwal, Bahawalpur, Hisar, Aligarh, Ujjain, Amravati, Rajahmundry, Bogra)
> *Are monsoon Kharif and winter Rabi seasons properly separated?*

* **Auditor Finding**: **NO, SYSTEMATICALLY FAILED AND DEFECTIVE (6 out of 8 locations fail).**
* **Agro-Meteorological Evidence**:
  1. **Indus Basin (Sahiwal & Bahawalpur)**: **Zero seasonal separation.** Erased completely under a year-round 365-day hyper-arid desert fallow.
  2. **Indo-Gangetic Margin (Hisar)**: **Inverted.** Kharif monsoon (361 mm rain) is labeled summer drought fallow; Rabi winter is designated active rainfed cereal.
  3. **Gangetic Alluvium & Central Vertisols (Aligarh, Ujjain, Amravati)**: **Rabi erased.** Only Kharif is designated active ($K=1$), and non-monsoon months are broken into an invalid non-contiguous split season (`May & October - December`).
  4. **Deltaic Double-Crop Exceptions (Rajahmundry & Bogra)**: **Properly separated**, successfully bounding Southwest/Northeast monsoons in Andhra Pradesh and Aus/Aman seasons in Bangladesh ($K=2$), though burdened by Brazilian Cerrado naming artifacts.

---

## 6. Comprehensive Remediation Blueprint

To eliminate the 6 defects identified in Batch 05, the following surgical code updates must be applied to `src/seasonal_calendar.py`:

### Fix 1: Monsoonal Precipitation Check in `SEMI_ARID_STEPPE`
Prevent summer monsoon inversion by inspecting the rainfall ratio before assigning season months:
```python
elif regime == "SEMI_ARID_STEPPE":
    summer_rain_total = sum(monthly_rain[m] for m in ([5, 6, 7, 8] if hemisphere == "Northern" else [11, 0, 1, 2]))
    winter_rain_total = sum(monthly_rain[m] for m in ([11, 0, 1, 2] if hemisphere == "Northern" else [5, 6, 7, 8]))
    
    if hemisphere == "Northern" and summer_rain_total > 1.25 * winter_rain_total:
        # Monsoonal Semi-Arid (e.g. Haryana, Rajasthan, Sahelian margins)
        s1_months = [5, 6, 7, 8, 9] # June - October (Kharif Monsoon)
        s2_months = [10, 11, 0, 1, 2, 3, 4] # November - May (Post-Monsoon / Rabi Fallow)
        s1_start, s1_end = get_run_start_end(s1_months)
        s2_start, s2_end = get_run_start_end(s2_months)
        seasons["season_1"] = SeasonMetadata(
            1, "Monsoonal Kharif Rainfed Season", s1_start, s1_end, len(s1_months),
            format_cyclic_window(s1_months), "ACTIVE_GROWING", ...,
            "Primary Rainfed Monsoon Grain & Pulse (Bajra, Guar, Cotton, Sorghum)"
        )
        seasons["season_2"] = SeasonMetadata(
            2, "Dry Cool Season / Rabi Rest", s2_start, s2_end, len(s2_months),
            format_cyclic_window(s2_months), "DROUGHT_DORMANCY", ...,
            "Post-Monsoon Stubble & Dryland Rest (Irrigated Rabi Wheat/Mustard Niche)"
        )
    else:
        # Standard Mediterranean Winter-Rainfall Steppe (Anatolia, Zagros, Levant)
        ...
```

### Fix 2: Cyclic Contiguity for Monomodal Dry Months
Replace linear range slicing with modular cyclical indexing to eliminate discontinuous split seasons (`May & October - December`):
```python
# Construct dry months cyclically starting immediately after wet_months end
wet_end = wet_months[-1]
num_dry = 12 - len(wet_months)
dry_months_cyclic = [(wet_end + 1 + i) % 12 for i in range(num_dry)]

s2_dur = max(1, num_dry // 2)
s2_months = dry_months_cyclic[:s2_dur]
s3_months = dry_months_cyclic[s2_dur:]

s2_start, s2_end = get_run_start_end(s2_months)
s3_start, s3_end = get_run_start_end(s3_months)
```
*Effect*: For June–September wet months, `dry_months_cyclic` becomes `[9, 10, 11, 0, 1, 2, 3, 4]` (October–May). S2 cleanly becomes October–January (Post-Monsoon/Early Rabi), and S3 becomes February–May (Hot Dry Season Pre-Monsoon Rest). Both seasons are 100% contiguous.

### Fix 3: Regionalized Nomenclature for Tropical Double Cropping
Replace hardcoded Portuguese Cerrado strings with agro-climatically generalized or regionalized designations:
```python
if abs(lat) <= 30.0 and (60.0 <= lon <= 95.0): # South Asia
    s1_name = "Primary Kharif / Monsoon Season"
    s2_name = "Secondary Rabi / Post-Monsoon Season"
    s3_name = "Zaid / Hot Dry Season Fallow"
    s1_role = "Monsoon Cash Crop & Cereals (Rice, Cotton, Maize, Soybean)"
    s2_role = "Post-Monsoon Residual Moisture Grain & Oilseed (Wheat, Mustard, Pulses)"
    s3_role = "Summer Field Rest & Land Preparation"
else:
    s1_name = "Primary Wet Season (Summer Anchor)"
    s2_name = "Secondary Wet Season (Succession)"
    s3_name = "Dry Season Sanitary Fallow"
    ...
```

### Fix 4: Hyper-Arid String Formatting Correction
Correct the string output logic in `regime == "HYPER_ARID_DESERT"`:
```python
reason_str = (
    f"Hyper-arid pluvial desert ({annual_rain:.1f} mm < 120 mm). Rainfed crops cannot survive; requires irrigation."
    if annual_rain < 120.0 else
    f"Hyper-arid moisture deficit (Aridity Index {aridity_index:.2f} < 0.20). Rainfed crops cannot survive; requires irrigation."
)
```
