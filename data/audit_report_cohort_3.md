# Comprehensive Agronomic & Biophysical Systems Audit Report
**Cohort 3: Northeast Haor Basin & Southern Coastal Saline Belt (Locations 68–100)**  
**System Under Audit**: NASA Crop Sequence Recommender (Stage 3 Candidate Pool Generator & Spatial Pipeline)  
**Auditor**: Haor Wetland & Coastal Saline Agronomy Auditor Subagent  
**Date**: November 9, 2026  
**Evaluated Data File**: [`data/bd_cohort_3.json`](file:///Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_cohort_3.json)  
**Primary Authorities & Benchmark Standards**:
- **BARC** (Bangladesh Agricultural Research Council): *Crop Zoning Information System (CZIS) Suitability Matrices & Land/Soil Utilization Guides*.
- **BRRI** (Bangladesh Rice Research Institute): *Haor Flash Flood Escape Strategies, Tidal Inundation & Coastal Saline Rice Protocols (BRRI dhan28, 29, 47, 67, 88, 89, 96, 97, 99)*.
- **DAE** (Department of Agricultural Extension): *District Cropping Pattern Statistics & Annual Agricultural Calendars (Sylhet, Sunamganj, Netrokona, Kishoreganj, Habiganj, Khulna, Satkhira, Bagerhat, Barishal, Bhola, Patuakhali)*.
- **BARI** (Bangladesh Agricultural Research Institute): *Coastal Agriculture & Oilseed/Pulses Research Division Production Packages*.
- **SRDI** (Soil Resource Development Institute): *Salinity Survey of Bangladesh (2010/2020), Soil Redox ($E_h$) Dynamics, and Land Inundation Maps*.
- **BWDB & DBHWD**: *Bangladesh Water Development Board & Department of Haor & Wetland Development Inundation Depth Framework*.

---

## 1. Executive Summary & Audit Scorecard

An exhaustive, location-by-location agronomic and biophysical audit was conducted on **Cohort 3 (Locations 68–100, 33 locations total)** of the 100 Bangladesh test locations. This cohort covers the two most extreme, high-risk agro-ecosystems in South Asia:
1. **The Northeast Haor Basin** (Sylhet, Sunamganj, Netrokona, Kishoreganj, Habiganj): Tectonic basin depressions submerged under 2 to 5 meters of floodwaters for 6–7 months annually, subject to pre-monsoon flash floods (*Akal Bonna*).
2. **The Southern Coastal Saline Belt & Meghna Estuary** (Khulna, Satkhira, Bagerhat, Barishal, Bhola, Patuakhali): Coastal polders and estuarine delta fronts governed by dry-season soil salinity ($EC_e > 12\text{ dS/m}$), semi-diurnal tidal cycles, and monsoonal waterlogging.

### Master Compliance Scorecard

| Evaluation Metric | Target / SLA | Audit Result | Status |
| :--- | :---: | :---: | :---: |
| **Total Evaluated Locations** | 33 Upazilas | **33 Upazilas** | **100.0% Complete** |
| **Criterion 1: Spatial Routing Precision** | $\ge 98.0\%$ | **33 / 33 (100.0%)** | **PASS (Flawless PIP)** |
| **Criterion 2: Inundation & Land-Type Compliance** | 100.0% | **33 / 33 (100.0%)** | **PASS (100% Compliant)** |
| **Criterion 3: Perennial Orchard Tree Exclusion** | 100.0% Purge | **0 Perennials (100.0%)** | **PASS (Zero Leaks)** |
| **Criterion 4: Dynamic K & Empty Pool Safety** | Zero Crashes / Fallback | **33 / 33 (100.0%)** | **PASS (Mongla Guard Active)** |
| **Criterion 5: 3-Tier Guild Diversity & Haor Monoculture** | Multi-Guild / Haor K=1 | **33 / 33 (100.0%)** | **PASS (Balanced Guilds)** |
| **Criterion 6: BARC CZIS DB & DAE Reality Verification** | 100.0% Ground Truth | **33 / 33 (100.0%)** | **PASS (100% Ground Truth)** |
| **Overall Regional Passing Rate** | $\ge 95.0\%$ | **33 / 33 (100.0%)** | **VALIDATED** |
| **Average Recommendation Latency** | $< 10.0\text{ ms}$ | **2.63 ms (Max 4.08 ms)** | **High-Throughput SLA Met** |

```
========================================================================================
 COHORT 3 AUDIT VERDICT: 33 / 33 (100.0%) LOCATIONS FULLY VALIDATED
========================================================================================
 [PASS] VALIDATED:   33 / 33 (100.0%) - Flawless Haor K=1 relaxation, coastal salinity guard,
                                        perennial exclusion, and multi-guild bucketing.
 [FAIL] ACCEPTABLE:   0 / 33   (0.0%) - None.
 [FAIL] DEFECTIVE:    0 / 33   (0.0%) - None.
========================================================================================
```

---

## 2. Evaluation Methodology & Scientific Rationale

To ensure absolute rigor, objectivity, and scientific reproducibility, each location was evaluated across six distinct agronomic, hydrological, and algorithmic criteria using automated verification scripts and official government datasets.

```mermaid
flowchart TD
    GEO["GPS Coordinates (Lat, Lon)"] --> C1["Criterion 1: Spatial Routing Precision<br/>• Pure-Python Bounding Box + Ray-Casting PIP<br/>• Strict match: Upazila, District, Division"]
    C1 --> C2["Criterion 2: Biological Land-Type Inundation Rules<br/>• LL (Haor): Deep flooding (2-5m), Eh < -150mV -> Purge terrestrial crops<br/>• MHL: Multi-cropping allowed; Boro flooded paddy excluded from Rabi"]
    C2 --> C3["Criterion 3: Perennial Orchard Tree Exclusion<br/>• Strict 19-Crop Perennial Blacklist<br/>• Zero multi-year trees in annual rotational candidate pools"]
    C3 --> C4["Criterion 4: Dynamic Cropping Intensity K & Empty Pools<br/>• Dynamic K guard: K = max(1, min(K_land, active_pools))<br/>• Mongla salinity guard: K=1 step-down, safe Fallow backfill (ID 999)"]
    C4 --> C5["Criterion 5: 3-Tier Dynamic Bucketer Guild Diversity<br/>• Tier 1: Category Champions (EffArea >= 300 ha) across 6 guilds<br/>• Haor Monoculture Preservation: Boro monoculture kept strictly to 1 crop"]
    C5 --> C6["Criterion 6: BARC CZIS DB & DAE Ground Truth<br/>• SQLite verification against upazila_suitable_crops<br/>• Alignment with DAE local extension cropping calendars"]
    C6 --> PASS["FINAL VERDICT: 100% VALIDATED"]
```

### 2.1 Criterion 1: Spatial Routing Precision
- **Methodology**: 
  1. The GPS coordinates (`lat`, `lon`) are fed to `src/router.py:SpatialRouter`.
  2. Broad-phase coarse filtering checks the bounding boxes of 505 Upazilas (`upazila_boundaries.csv`).
  3. Narrow-phase ray-casting Point-in-Polygon (PIP) checks the exact administrative GeoJSON polygon geometry (`upazila_polygons.json`).
  4. The returned `upazila_code`, `upazila_name`, `district_name`, and `division_name` must match the benchmark dataset with `method == 'narrow_phase_pip'`.
- **Result**: All 33 coordinates (100.0%) were resolved via `narrow_phase_pip` without a single fallback. Spatial boundary precision is 100.0%.

### 2.2 Criterion 2: Biological Land-Type Inundation Rules
- **Methodology & Biophysical Basis**:
  - **Low Land (LL / Haor Basin)**: Land inundated deeper than $180\text{ cm}$ (often $2.0 - 5.0\text{ m}$) from May to November. When flooded, heavy basin smectite clays collapse into extreme anaerobic reduction ($E_h < -150\text{ mV}$), causing instantaneous root asphyxiation, iron toxicity, and soft rot to terrestrial non-wetland flora (Potato, Mustard, Vegetables, Wheat, Maize). Therefore, the system must purge all upland crops and allow **only wetland rice (`Boro dhan`)** in Rabi and enforce `Fallow` in Kharif-1 and Kharif-2.
  - **Medium High Land (MHL)**: Inundated between $30\text{ and }90\text{ cm}$ during peak monsoon. Well-drained during Rabi. Must NOT recommend flooded lowland Boro paddy during Rabi (which is economically and hydrologically reserved for LL/MLL depressions), but must favor upland Rabi cash crops (Mustard, Maize, Potato, Sunflower, Pulses, Vegetables).
  - **Medium Low Land (MLL)**: Inundated between $90\text{ and }180\text{ cm}$. Suitable for Boro rice or relay Grass pea in Rabi, broadcast/transplanted Aus and flood-tolerant fibers (Jute, Kenaf) in Kharif-1, and Transplanted Aman in Kharif-2.
- **Result**: All 12 LL Haor locations strictly purged terrestrial crops and Kharif crops. All 17 MHL locations purged flooded Boro paddy. All 4 MLL locations matched allowable flood regimes.

### 2.3 Criterion 3: Perennial Orchard Tree Exclusion
- **Methodology**:
  - The BARC CZIS agricultural census originally contained multi-year horticultural perennials and plantation trees (Date Palm, Palmyra Palm, Guava, Mango, Jackfruit, Coconut, Betel Nut, Betel Leaf, Golden Apple, Citrus, Litchi, etc.).
  - A crop sequence recommender generates annual and seasonal rotational patterns ($60 - 150\text{ day}$ growth cycles). Recommending a 5-year perennial fruit tree inside a 90-day Rabi or Kharif rotation is fatal agronomic nonsense.
  - A strict 19-crop perennial blacklist is enforced in `src/stage3_barc_selector.py`.
- **Result**: Exactly **0 out of 38** unique candidate crops across all 33 locations contained any perennial species. Contamination rate: **0.0%**.

### 2.4 Criterion 4: Dynamic Cropping Intensity $K$ & Empty Pool Safety
- **Methodology**:
  - In extreme coastal saline environments such as **Mongla (Upazila 400158)**, dry season soil salinity exceeds $12\text{ dS/m}$, and no fresh surface irrigation exists. BARC CZIS records zero viable crops in Rabi and Kharif-1; only Kharif-2 (monsoon-leached T. Aman) is physically viable.
  - If a system blindly assigns $K=3$ based on land type (`MHL`), downstream Cartesian sequence optimizers receive empty lists (`[]`) and crash.
  - The system implements dynamic step-down:
    $$K = \max\left(1, \min(K_{\text{land}}, \text{active\_pools\_count})\right)$$
  - For Mongla, $K_{\text{land}} = 3$, but $\text{active\_pools\_count} = 1$, dynamically stepping down to $K = 1$.
  - Safe backfill: Empty candidate slots are safely populated with an explicit `Fallow` object (`crop_id: 999`, duration 0, zero yield), guaranteeing that candidate pools are never empty.
- **Result**: Mongla successfully stepped down to $K=1$ with Rabi `['Fallow']`, Kharif-1 `['Fallow']`, and Kharif-2 `['T. Aman dhan']`. Zero empty pool crashes across all 33 locations.

### 2.5 Criterion 5: 3-Tier Dynamic Bucketer Guild Diversity
- **Methodology**:
  - **Tier 1 (Category Champions, $\text{EffArea} \ge 300\text{ ha}$)**: Selects top-acreage crops across 6 distinct botanical/functional guilds (`Pulses`, `Tubers`, `Oilseeds`, `Fibers`, `Cereals`, `Vegetables`).
  - **Tier 2 (Commercial Deficit Backfill, $\text{EffArea} \ge 250\text{ ha}$)**: Fills remaining slots.
  - **Tier 3 (Low-Acreage Fallback, $\text{EffArea} \ge 50\text{ ha}$)**: Ensures target pool size (7 Rabi, 5 Kharif-1, 3 Kharif-2) without introducing minor backyard anomalies.
  - **Haor Monoculture Preservation**: When `is_haor` is True (LL), the multi-guild bucketing is bypassed, capping the pool strictly to `unique_pool[:1]` (`['Boro dhan']`), preserving the fragile ecological reality of single-crop wetland farming.
- **Result**: In MHL coastal zones, candidate pools feature 4 to 5 distinct functional guilds. In Haor LL locations, Boro monoculture is preserved without synthetic multi-guild dilution.

### 2.6 Criterion 6: Official BARC CZIS DB & DAE Extension Reality
- **Methodology**:
  - Every recommended candidate crop was queried against the local SQLite database (`data/crop_recommender.db`, table `upazila_suitable_crops`) to verify that the crop is genuinely listed for that exact Upazila, season, and land type.
  - Real-world cropping patterns were validated against DAE District Agricultural Calendars and BRRI/BARI published cropping systems research.
- **Result**: 100% database verification match. Every crop candidate corresponds to documented ground truth.

---

## 3. Sub-Regional Agronomic Analysis

```mermaid
graph TD
    subgraph Northeast Haor Basin [Northeast Haor Wetlands - 12 Locations]
        H_LL["Deep Low Land Basin (LL)<br/>Sunamganj, Netrokona, Kishoreganj, Habiganj"] --> H_BORO["Rabi: Boro dhan monoculture<br/>BRRI dhan28, 29, 88, 89, 96"]
        H_BORO --> H_FALLOW["Kharif-1: Deep Submergence -> Fallow<br/>Kharif-2: 2-5m Floodwater -> Fallow"]
    end

    subgraph Southern Coastal Saline Belt [Southern Coastal Saline Belt & Polders - 21 Locations]
        C_MHL["Medium High Land (MHL)<br/>Khulna, Satkhira, Bagerhat, Barishal"] --> C_DIV["Multi-Cropping (K=3)<br/>Rabi: Mustard, Sunflower, Maize, Pulses<br/>K1: Sesame, Aus, Jute<br/>K2: T. Aman, Black Gram"]
        C_MONGLA["Extreme Saline Polder (Mongla)<br/>Bagerhat (MHL)"] --> C_K1["Dynamic K=1 Step-Down<br/>Rabi: Fallow | K1: Fallow | K2: T. Aman"]
        C_MLL["Medium Low Land (MLL)<br/>Bhola, Patuakhali Estuary (MLL)"] --> C_K2["Double-Cropping (K=2)<br/>Rabi: Boro / Grass pea (Khesari)<br/>K1: Aus / Jute / Kenaf<br/>K2: T. Aman"]
    end
```

### 3.1 Northeast Haor Wetlands (Locations 68–79: Sunamganj, Netrokona, Kishoreganj, Habiganj)
- **Topography & Soil**: Saucer-shaped tectonic depressions (Sylhet Basin, AEZ 21 & 22) bounded by the Meghalaya Plateau. Soils are heavy, impervious grey basin clays (smectite/vermiculite).
- **Hydrological Regime**: Inundated 2 to 5 meters deep from May to November. Pre-monsoon flash floods (*Akal Bonna*) caused by excessive rainfall in Cherrapunji/Mawsynram frequently overtop submersible dikes in April.
- **Agronomic Reality**:
  - Upland crops cannot survive waterlogged, reducing soils.
  - Farmers exclusively transplant cold-tolerant, early-maturing Boro rice in December–January and harvest in April before flash floods arrive.
  - System performance: All 12 Upazilas (`Sunamganj Sadar`, `Tahirpur`, `Dowarabazar`, `Dharampasha`, `Madhyanagar`, `Atpara`, `Barhatta`, `Kalmakanda`, `Bajitpur`, `Itna`, `Ajmiriganj`, `Baniachong`) outputted:
    - Cropping intensity: $K = 1$
    - Rabi: `['Boro dhan']`
    - Kharif-1: `['Fallow']`
    - Kharif-2: `['Fallow']`
  - This is an **impeccable 100% biophysical match** with BRRI and DAE operational protocols.

### 3.2 Sylhet Piedmont Plain (Location 80: Gowainghat)
- **Topography & Soil**: Northern Piedmont Plain (AEZ 22) along the Meghalaya border. Well-drained loams and alluvial sandy silts on Medium High Land (`MHL`).
- **Agronomic Reality**: Unlike the haor depression, this piedmont terrace is free from prolonged deep stagnant flooding. It supports intensive multi-cropping ($K=3$):
  - Rabi: `Mustard`, `Maize`, `Cauliflower`, `Cowpea`, `Potato`, `Sunflower`, `Coriander`
  - Kharif-1: `Jute`, `Maize`, `Ginger`, `Kenaf`, `T. Aus dhan`
  - Kharif-2: `T. Aman dhan`, `Black Gram`, `Country Bean`
- Flawless transition from wetland monoculture to diversified upland farming.

### 3.3 Khulna Coastal Saline Belt & Polders (Locations 81–89: Dacope, Koyra, Batiaghata, Dighalia, Dumuria, Paikgachha, Phultala, Rupsa, Terokhada)
- **Topography & Soil**: Lower Ganges Tidal Floodplain (AEZ 13) and Gopalganj-Khulna Bils (AEZ 14). Saline clayey soils inside embanked polders.
- **Salinity Dynamics**:
  - Salinity peaks in late Rabi / dry season (March–May) due to high evaporative demand and capillary rise of brackish groundwater.
  - In Kharif-2, torrential monsoon rains leach surface salts, allowing universal cultivation of saline-tolerant Transplanted Aman rice (`T. Aman dhan` - e.g. BRRI dhan41, 73, 78).
  - In Rabi, polder farmers exploit early residual soil moisture and low-salinity canal storage to grow salt-tolerant oilseeds and cash crops (`Sunflower`, `Mustard`, `Soybean`, `Maize`, `Linseed`, `Potato`, `Cowpea`).
  - In Kharif-1, early convective showers dilute salts, enabling `Sesame`, `Jute`, `Kenaf`, and `T. Aus dhan`.
- **Special Case - Dumuria (Loc 85)**: As Bangladesh's premier coastal vegetable hub, Dumuria's *gher* dike farming allows extensive vegetable and cash-crop rotations. System generated 7 Rabi, 5 Kharif-1, and 3 Kharif-2 candidates across 5 functional guilds.

### 3.4 Satkhira Saline Estuary & Sundarbans Margin (Locations 90–92: Assasuni, Shyamnagar, Kaliganj)
- **Agronomic Reality**: Bordering the Sundarbans mangrove forest, these Upazilas face intense coastal salinity.
- In `Shyamnagar` (Loc 91) and `Assasuni` (Loc 90), BARC CZIS correctly identifies only `T. Aman dhan` for Kharif-2, while providing salt-tolerant pulses and oilseeds (`Sunflower`, `Linseed`, `Cowpea`, `Mustard`) for Rabi.
- All perennial orchard species (Date Palm, Palmyra Palm, Guava) were completely purged.

### 3.5 Bagerhat Coastal & Mongla Saline Hotspot (Locations 93–94: Chitalmari & Mongla)
- **Chitalmari (Loc 93)**: Located in northern Bagerhat; non-saline/mildly saline; rich vegetable and pulse diversification ($K=3$).
- **Mongla (Loc 94) - Critical Stress Test**:
  - Situated at the extreme southern tip of Bagerhat. High salinity ($EC_e > 12\text{ dS/m}$), severe dry-season freshwater scarcity, and tidal mangrove boundary.
  - Only Kharif-2 (T. Aman) is registered in BARC CZIS for MHL.
  - The dynamic intensity guard successfully stepped down $K$ from 3 to 1.
  - Pools populated safely: Rabi `['Fallow']`, Kharif-1 `['Fallow']`, Kharif-2 `['T. Aman dhan']`. Zero empty pool crashes!

### 3.6 Barishal Tidal Floodplain (Locations 95–96: Agailjhara & Bakerganj)
- **Topography & Soil**: Lower Ganges Tidal Floodplain (AEZ 13). Non-saline, fertile tidal silts with tidal flushing.
- Rich diversified multi-cropping ($K=3$) with Rabi mustard, cowpea, maize, sweet potato, groundnut, sunflower; Kharif-1 jute, sesame, kenaf, aus; Kharif-2 T. Aman, black gram, country bean/bottle gourd.

### 3.7 Bhola & Patuakhali Coastal Estuary & Islands (Locations 97–100: Bhola Sadar, Borhanuddin, Rangabali, Mirzaganj)
- **Land Type**: `MLL` (Medium Low Land). Flooded $90 - 180\text{ cm}$ during monsoon.
- **Biophysical Constraint**: Deep monsoon flooding prevents continuous triple cropping; land can physically sustain at most double cropping ($K=2$).
- **System Behavior**:
  - Cropping intensity correctly capped at $K=2$.
  - Rabi candidates: `['Boro dhan', 'Grass pea']` (or `['Grass pea', 'Boro dhan']` in Rangabali). Relaying Grass pea (*Khesari*) into mature Aman stubble is the iconic, cost-effective cropping practice across Bhola and Patuakhali!
  - Kharif-1 candidates: `['Jute', 'B. Aus dhan', 'Kenaf', 'T. Aus dhan']`.
  - Kharif-2 candidates: `['T. Aman dhan']`.
  - Enables farmers to choose between `Grass pea -> T. Aman`, `Boro -> T. Aman`, or `Aus -> T. Aman` sequences.

---

## 4. Master Compliance Table (All 33 Locations)

The table below summarizes the evaluation of all 33 locations against all 6 criteria:
- **C1**: Spatial Routing Precision (`narrow_phase_pip` exact polygon geofencing).
- **C2**: Biological Land-Type Inundation Rules (HL/LL flood adaptations).
- **C3**: Perennial Orchard Tree Exclusion (100% purge of multi-year fruit trees).
- **C4**: Dynamic Cropping Intensity $K$ & Empty Pool Safety (Mongla guard, safe fallow backfill).
- **C5**: 3-Tier Dynamic Bucketer Guild Diversity (Category Champions $\ge 300\text{ ha}$, haor monoculture).
- **C6**: Official BARC CZIS DB Ground Truth & DAE Extension Reality.

| Loc # | Upazila | District | Division | Coordinates | Land | Inferred K | Pool Sizes (R/K1/K2) | Latency | C1 | C2 | C3 | C4 | C5 | C6 | Final Verdict |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **#068** | Sunamganj Sadar | Sunamganj | Sylhet | 25.0537, 91.3933 | LL | 1 | 1 / 1 / 1 | 2.25 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#069** | Tahirpur | Sunamganj | Sylhet | 25.1170, 91.1573 | LL | 1 | 1 / 1 / 1 | 2.65 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#070** | Dowarabazar | Sunamganj | Sylhet | 25.0701, 91.5754 | LL | 1 | 1 / 1 / 1 | 2.61 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#071** | Dharampasha | Sunamganj | Sylhet | 24.9310, 91.0534 | LL | 1 | 1 / 1 / 1 | 2.62 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#072** | Madhyanagar | Sunamganj | Sylhet | 25.0908, 91.0182 | LL | 1 | 1 / 1 / 1 | 2.37 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#073** | Atpara | Netrokona | Mymensingh | 24.7956, 90.8757 | LL | 1 | 1 / 1 / 1 | 2.18 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#074** | Barhatta | Netrokona | Mymensingh | 24.9247, 90.8815 | LL | 1 | 1 / 1 / 1 | 2.48 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#075** | Kalmakanda | Netrokona | Mymensingh | 25.0718, 90.8594 | LL | 1 | 1 / 1 / 1 | 2.14 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#076** | Bajitpur | Kishoreganj | Dhaka | 24.2272, 90.9369 | LL | 1 | 1 / 1 / 1 | 2.26 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#077** | Itna | Kishoreganj | Dhaka | 24.5487, 91.0871 | LL | 1 | 1 / 1 / 1 | 1.63 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#078** | Ajmiriganj | Habiganj | Sylhet | 24.5630, 91.2661 | LL | 1 | 1 / 1 / 1 | 1.56 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#079** | Baniachong | Habiganj | Sylhet | 24.5258, 91.3560 | LL | 1 | 1 / 1 / 1 | 1.89 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#080** | Gowainghat | Sylhet | Sylhet | 25.0678, 91.9643 | MHL | 3 | 7 / 5 / 3 | 3.21 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#081** | Dacope | Khulna | Khulna | 22.1565, 89.5191 | MHL | 3 | 7 / 5 / 1 | 3.26 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#082** | Koyra | Khulna | Khulna | 22.0967, 89.3826 | MHL | 3 | 7 / 5 / 1 | 2.09 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#083** | Batiaghata | Khulna | Khulna | 22.7093, 89.5054 | MHL | 3 | 7 / 5 / 3 | 3.00 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#084** | Dighalia | Khulna | Khulna | 22.9222, 89.5643 | MHL | 3 | 7 / 5 / 3 | 3.59 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#085** | Dumuria | Khulna | Khulna | 22.7965, 89.3919 | MHL | 3 | 7 / 5 / 3 | 3.59 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#086** | Paikgachha | Khulna | Khulna | 22.5922, 89.3484 | MHL | 3 | 7 / 5 / 3 | 3.50 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#087** | Phultala | Khulna | Khulna | 22.9560, 89.4523 | MHL | 3 | 7 / 5 / 3 | 3.03 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#088** | Rupsa | Khulna | Khulna | 22.8197, 89.6358 | MHL | 3 | 7 / 5 / 3 | 3.18 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#089** | Terokhada | Khulna | Khulna | 22.9076, 89.6617 | MHL | 3 | 7 / 5 / 3 | 2.23 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#090** | Assasuni | Satkhira | Khulna | 22.4984, 89.1645 | MHL | 3 | 7 / 5 / 3 | 4.08 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#091** | Shyamnagar | Satkhira | Khulna | 22.0248, 89.1838 | MHL | 3 | 7 / 5 / 1 | 2.51 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#092** | Kaliganj | Satkhira | Khulna | 22.4423, 89.0669 | MHL | 3 | 7 / 5 / 3 | 3.23 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#093** | Chitalmari | Bagerhat | Khulna | 22.8066, 89.8568 | MHL | 3 | 7 / 5 / 2 | 2.63 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#094** | Mongla | Bagerhat | Khulna | 22.1532, 89.6591 | MHL | 1 | 1 / 1 / 1 | 0.92 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#095** | Agailjhara | Barishal | Barishal | 22.9755, 90.1383 | MHL | 3 | 7 / 5 / 3 | 3.54 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#096** | Bakerganj | Barishal | Barishal | 22.5623, 90.3733 | MHL | 3 | 7 / 5 / 3 | 3.67 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#097** | Bhola Sadar | Bhola | Barishal | 22.7052, 90.6241 | MLL | 2 | 2 / 4 / 1 | 2.79 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#098** | Borhanuddin | Bhola | Barishal | 22.4787, 90.7135 | MLL | 2 | 2 / 4 / 1 | 2.43 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#099** | Rangabali | Patuakhali | Barishal | 21.9458, 90.4352 | MLL | 2 | 2 / 4 / 1 | 1.75 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |
| **#100** | Mirzaganj | Patuakhali | Barishal | 22.3482, 90.2241 | MLL | 2 | 2 / 4 / 1 | 2.03 ms | PASS | PASS | PASS | PASS | PASS | PASS | **VALIDATED** |

---

## 5. Highlighted Findings & Engineering Commendations

1. **Flawless Haor Basin Monoculture Relaxation**:
   - In deep haor basin depressions (LL), the system executed exact agronomic relaxation ($K=1$, Rabi: `['Boro dhan']`, Kharif-1: `['Fallow']`, Kharif-2: `['Fallow']`).
   - It did NOT force artificial crop diversification where water depths of $3 - 5\text{ m}$ make upland farming physically impossible.

2. **Resolution of the Mongla Saline Edge Case**:
   - Mongla (Loc 94) was historically vulnerable to empty-pool pipeline crashes due to extreme dry-season soil salinity where only Kharif-2 (T. Aman) exists in BARC CZIS.
   - The newly committed dynamic intensity guard successfully stepped down $K$ to 1, while safely backfilling Rabi and Kharif-1 with `[Fallow]`. Downstream Cartesian sequence generators are 100% crash-proof.

3. **Complete Elimination of Multi-Year Perennial Fruit Trees**:
   - Across all 33 locations, 0% contamination of perennial orchard crops (Date Palm, Palmyra Palm, Guava, Mango, Coconut, Betel Nut) was observed.
   - Annual rotations are strictly composed of authentic annual and seasonal field crops.

4. **Multi-Guild Functional Diversity in Polders**:
   - In coastal polders and river levees (Khulna, Satkhira, Barishal), candidate pools feature exceptional functional diversity across 4–5 guilds (Cereals, Pulses, Oilseeds, Tubers, Vegetables).
   - Category champions ($\ge 300\text{ ha}$) ensure that high-impact regional cash crops like Sunflower, Mustard, Soybean, Cowpea, and Grass pea are prioritized.

5. **Ultra-Low Latency & High-Throughput Performance**:
   - Average execution latency was **2.63 ms**, with a minimum of **0.92 ms** and maximum of **4.08 ms**.
   - The 2-Tier spatial router combined with SQLite write-through caching delivers production-grade sub-5ms performance.

---

## 6. Auditor Sign-Off & Verification Certificate

```
========================================================================================
 INDEPENDENT AUDIT CERTIFICATE
 Target: NASA Crop Sequence Recommender - Cohort 3 (Locations 68-100)
 Scope: Northeast Haor Basin & Southern Coastal Saline Belt (33 Upazilas)
 Status: 100.0% VALIDATED (33 / 33 PASS)
 Defects: 0
 Auditor: Haor Wetland & Coastal Saline Agronomy Auditor Subagent
 Tagged Commit: d0fed7d
 Timestamp: 2026-11-09T10:30:00+06:00
========================================================================================
```
