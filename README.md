# 🌾 NASA Crop Sequence Decision Support System (DSS)
### Recommender Engine (Stages 3–5) & Standalone Sequence Evaluator

[![Python Standard Library](https://img.shields.io/badge/Python-3.8%2B%20(Pure%20Stdlib)-blue.svg)](https://www.python.org/)
[![Zero External Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(No%20Pip%20Required)-success.svg)]()
[![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-Field%20Shift-orange.svg)](https://www.spaceappschallenge.org/)
[![Tests](https://img.shields.io/badge/Tests-22%2F22%20Passing%20(100%25)-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Field Shift: Adapting Farms with NASA Earth Observations & Local Agro-Ecological Data**  
> A complete, biophysically grounded Decision Support System (DSS) comprising two decoupled engines:
> 1. **Crop Sequence Recommender:** Synthesizes candidate seasonal crop pools using official Bangladesh Agricultural Research Council (BARC CZIS) matrices and global UN FAO EcoCrop limits.
> 2. **Crop Sequence Evaluator & Diagnostic DSS:** Audits multi-year crop sequences against NASA POWER agro-climatology ($ET_0$ & tipping-bucket water balance), duration-weighted soil organic carbon ($\Delta \text{SOC}$), legume Biological Nitrogen Fixation (BNF, with Nitrogen Harvest Index $NHI = 0.70$), Maas-Hoffman salinity, turnaround temporal feasibility ($T_{\text{wrap}}$), biological disease cycles (*Solanaceae* bacterial wilt / nematode bridge), and generates bilingual KrishiBondhu AI advisory reports with deterministic Smart Swaps.

---

## 📑 Table of Contents
1. [Dual-Engine System Architecture](#dual-engine-system-architecture)
2. [Quick Start (Zero Setup)](#quick-start)
3. [Engine 1: Recommender Engine CLI Usage](#engine-1-recommender-engine-cli-usage)
4. [Engine 2: Evaluator DSS Usage & Reference](#engine-2-evaluator-dss-usage--reference)
5. [20-Location Bangladesh Scientific Verification](#20-location-bangladesh-scientific-verification)
6. [Core Biophysical Models & Equations](#core-biophysical-models--equations)
7. [Running the Automated Test Suite](#running-the-automated-test-suite)
8. [Project File Structure](#project-file-structure)
9. [Citations & References](#citations--references)

---

## 🌍 Dual-Engine System Architecture

```text
                                  FARMER INPUT / GPS COORDINATES
                                                │
                     ┌──────────────────────────┴──────────────────────────┐
                     ▼                                                     ▼
      [ ENGINE 1: RECOMMENDER PIPELINE ]                    [ ENGINE 2: STANDALONE EVALUATOR DSS ]
      "What crops should the farmer grow?"                  "How viable is this specific sequence?"
                     │                                                     │
        2-Tier Jordan Curve PIP Router                        Stage 1: NASA POWER Climatology & ET0
                     │                                                     │
     ┌───────────────┴───────────────┐                        Stage 2: Turnaround Gaps & Hazard Traps
     ▼                               ▼                                     │
Branch A: BARC CZIS        Branch B: Global FAO/NASA          Stage 3: Agro-Hydrological Suitability
(505 Bangladesh Upazilas)  (EcoCrop Cardinal Limits)                       │
     │                               │                        Stage 4: Soil Biogeochem & Disease Audit
     └───────────────┬───────────────┘                        (ΔSOC, BNF NHI=0.70, Salinity, Ralstonia)
                     ▼                                                     │
       Validated Candidate Pools                              Stage 5: Multi-Factor Scoring (0–100)
       (Rabi, Kharif-1, Kharif-2)                             & Deterministic Smart Crop Swaps
                                                                           │
                                                              Stage 6: Bilingual KrishiBondhu AI
                                                              Advisory Report (Bangla & English)
```

> 📖 **Deep Technical Specifications:**
> * **Recommender Engine Blueprint:** [`docs/crop_sequence_recommender_architecture.md`](docs/crop_sequence_recommender_architecture.md)
> * **Evaluator DSS Technical Specification:** [`docs/crop_sequence_evaluator_architecture.md`](docs/crop_sequence_evaluator_architecture.md)

---

## 🚀 Quick Start

Clone and run immediately. **No virtual environment, `pip install`, or environment variables required.** Works on **macOS**, **Linux**, and **Windows (PowerShell / cmd)**.

```bash
# 1. Clone repository
git clone https://github.com/eskit2005/crop_sequence_recommender.git
cd crop_sequence_recommender

# 2. Run Engine 1: Recommender Engine for any coordinate (BARC CZIS + Ray-Casting PIP):
python3 src/stage3_engine.py --lat 24.78 --lon 89.04 --land-type MHL

# 3. Run Engine 2: Evaluator DSS demo (Bogura Solanaceae disease audit & smart swap):
python3 src/evaluate_sequence_cli.py --demo bogura

# 4. Run Engine 2 for Coastal Saline Belt (Satkhira):
python3 src/evaluate_sequence_cli.py --demo satkhira

# 5. Run all 22 automated tests:
python3 -m unittest discover tests
```

---

## 🌾 Engine 1: Recommender Engine CLI Usage

The Recommender Engine generates candidate crop pools for an Upazila or international coordinate:

```bash
# Bangladesh BARC Branch A:
python3 src/stage3_engine.py --lat 24.78 --lon 89.04 --land-type MHL

# Global FAO EcoCrop + NASA POWER Branch B:
python3 src/stage3_engine.py --lat -0.303 --lon 36.08

# JSON Output for Web APIs:
python3 src/stage3_engine.py --lat 24.78 --lon 89.04 --json
```

---

## 🔬 Engine 2: Evaluator DSS Usage & Reference

The Evaluator Decision Support System lives in [`src/evaluator/`](src/evaluator/) and evaluates any user-defined or algorithm-generated multi-year crop sequence against NASA satellite observations, soil biogeochemistry, and agronomic disease dynamics.

---

### 📋 Required & Optional Inputs Reference

The Evaluator DSS ingests four categories of inputs via CLI flags, JSON configuration files, or the Python API:

| Input Category | Field / Parameter | CLI Flag | Required? | Type & Constraints | Description & Real-World Examples |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **1. Geographic Location** | `lat` | `--lat` | **YES** | `float` ($-90.0$ to $90.0$) | Latitude in decimal degrees (e.g. `24.7872` for Adamdighi, Bogura). |
| | `lon` | `--lon` | **YES** | `float` ($-180.0$ to $180.0$) | Longitude in decimal degrees (e.g. `89.0721` for Adamdighi, Bogura). |
| | `upazila` | *(Auto-Resolved)* | **NOT NEEDED** | `string` | **Auto-resolved in <0.3ms** by internal PIP router from `(lat, lon)`. Optional flag `--upazila` exists only as a manual override. |
| | `district` | *(Auto-Resolved)* | **NOT NEEDED** | `string` | **Auto-resolved in <0.3ms** by internal PIP router from `(lat, lon)`. Optional flag `--district` exists only as a manual override. |
| | `division` | *(Auto-Resolved)* | **NOT NEEDED** | `string` | Auto-resolved from `(lat, lon)` by router (e.g. `Rajshahi`, `Khulna`). |
| | `aez` | *(Auto-Resolved)* | **NOT NEEDED** | `int` ($1$ to $30$) | Official Bangladesh Agro-Ecological Zone resolved from database. |
| **2. Field & Soil Conditions** | `land_type` | `--land-type` | **YES** | `string`: `HL`, `MHL`, `MLL`, `LL`, `VLL` | Inundation flood depth class (High Land, Medium High Land, Low Land/Haor). |
| | `soil_salinity_ec_e` | `--salinity` | Optional | `float` ($\ge 0.0$ dS/m, default: `0.80`) | Saturated extract electrical conductivity $EC_e$ for Maas-Hoffman salt audit. |
| | `soil_ph` | `--ph` | Optional | `float` ($3.0$ to $10.0$, default: `6.20`) | Topsoil pH reaction for acidity, aluminum toxicity, and alkaline penalties. |
| | `soil_texture` | *(JSON / API)* | Optional | `string` (default: `"Silt Loam"`) | USDA texture class (`Clay`, `Clay Loam`, `Sandy Loam`, `Silt Loam`). |
| | `soil_organic_carbon_pct` | *(JSON / API)* | Optional | `float` ($\ge 0.0\%$, default: `1.10%`) | Baseline Soil Organic Carbon percentage for annual $\Delta\text{SOC}$ trajectory. |
| | `drainage_condition` | *(JSON / API)* | Optional | `string`: `poor`, `moderate`, `good` | Surface drainage rate impacting waterlogging risk (default: `"moderate"`). |
| | `bulk_density` | *(JSON / API)* | Optional | `float` (default: `1.50` g/cm³) | Soil dry bulk density $\rho_b$ used for volumetric water storage ($S_{\max}$). |
| **3. Farmer Socio-Economics** | `total_budget_bdt` | `--budget` | Optional | `float` (BDT, default: `120000.0`) | Farmer's annual working capital budget across all 3 seasons. |
| | `land_size_ha` | `--area` | Optional | `float` (ha, default: `0.40` ha) | Farm operational size in hectares ($0.40\text{ ha} \approx 1\text{ acre}$). |
| | `irrigation_source` | `--irrigation` | Optional | `string`: `shallow_tubewell`, `deep_tubewell`, `surface_canal`, `rainfed` | Primary irrigation access dictating dry-season drought risk and energy costs. |
| | `water_cost_per_m3_bdt`| *(JSON / API)* | Optional | `float` (default: `3.5` BDT/m³) | Pumping tariff / cost per cubic meter of irrigation water. |
| | `food_security_staple_needed` | *(JSON / API)* | Optional | `bool` (default: `True`) | Whether household prioritizes minimum rice cereal harvest. |
| | `risk_tolerance` | *(JSON / API)* | Optional | `string`: `conservative`, `moderate`, `aggressive` | Farmer financial risk appetite (default: `"moderate"`). |
| **4. Evaluated Sequence** | `crop_name` | `--sequence` | **YES** | `string` | Exact common name of crops in sequence (e.g. `Potato`, `Tomato`, `T. Aman Rice`). |
| | `season` | `--sequence` | **YES** | `string`: `Rabi`, `Kharif-1`, `Kharif-2` | Sequential growing season (inferred automatically or given as `Season:Crop`). |
| | `year` | `--sequence` | **YES** | `int` ($\ge 1$, default: `1`) | Year number in the multi-year rotation sequence. |
| | `cultivar` | *(JSON / API)* | Optional | `string` | Specific variety (e.g. `BRRI dhan88`, `Diamond`, `BARI Mung-6`). |
| | `sowing_date_approx` | *(JSON / API)* | Optional | `string` (`YYYY-MM-DD`) | Target sowing or transplanting date for calendar alignment. |
| | `stover_management` | *(JSON / API)* | Optional | `string`: `incorporated`, `removed`, `grazed` | Residue retention practice dictating legume BNF credit ($NHI=0.70$) & $\Delta\text{SOC}$. |

---

### 🌟 Complete Real-World Example with ALL Inputs Specified

Below are three ways to run an evaluation where all parameters are explicitly defined:

#### 1. Via Command-Line (Clean CLI Execution)
Notice that **no `--upazila` or `--district` flags are passed**; the Ray-Casting PIP router automatically identifies Adamdighi, Bogura from the coordinates in $<0.3\text{ ms}$:

```bash
python3 src/evaluate_sequence_cli.py \
  --lat 24.7872 \
  --lon 89.0721 \
  --sequence "Rabi:Potato;Kharif-1:Tomato;Kharif-2:T. Aman Rice" \
  --land-type "MHL" \
  --salinity 0.80 \
  --ph 6.2 \
  --budget 120000.0 \
  --area 0.40 \
  --irrigation "shallow_tubewell"
```

*(Add `--json` to the command above to get the full machine-readable diagnostic JSON payload).*

#### 2. Via Custom Input Profile File (`--profile`)
You can store the complete farmer profile in a JSON file (a pre-configured copy is available at [`data/farmer_profile_example.json`](data/farmer_profile_example.json)):

```bash
python3 src/evaluate_sequence_cli.py --profile data/farmer_profile_example.json
```

**Contents of `data/farmer_profile_example.json`:**
```json
{
  "location": {
    "lat": 24.7872,
    "lon": 89.0721,
    "upazila": "Adamdighi",
    "district": "Bogura",
    "division": "Rajshahi",
    "aez": 3
  },
  "field_conditions": {
    "land_type": "MHL",
    "soil_texture": "Silt Loam",
    "soil_ph": 6.2,
    "soil_organic_carbon_pct": 1.10,
    "soil_salinity_ec_e": 0.80,
    "drainage_condition": "moderate",
    "bulk_density": 1.50
  },
  "farmer_priorities": {
    "land_size_ha": 0.40,
    "total_budget_bdt": 120000.0,
    "irrigation_source": "shallow_tubewell",
    "water_cost_per_m3_bdt": 3.5,
    "food_security_staple_needed": true,
    "risk_tolerance": "moderate"
  },
  "target_horizon_years": 1,
  "farmer_evaluated_sequence": [
    {
      "year": 1,
      "season": "Rabi",
      "crop_name": "Potato",
      "cultivar": "Diamond (HYV)",
      "sowing_date_approx": "2024-11-15",
      "stover_management": "removed"
    },
    {
      "year": 1,
      "season": "Kharif-1",
      "crop_name": "Tomato",
      "cultivar": "Summer Hybrid",
      "sowing_date_approx": "2025-03-01",
      "stover_management": "incorporated"
    },
    {
      "year": 1,
      "season": "Kharif-2",
      "crop_name": "T. Aman Rice",
      "cultivar": "BRRI dhan49",
      "sowing_date_approx": "2025-07-20",
      "stover_management": "incorporated"
    }
  ],
  "preferences": {
    "language": "bn",
    "tone": "farmer_friendly"
  }
}
```

#### 3. Via Python API (All Dataclasses Populated)
```python
from src.evaluator import (
    EvaluatorEngine,
    FarmerProfile,
    LocationInput,
    FieldConditions,
    FarmerPriorities,
    CropInput
)

# 1. Initialize master 6-stage evaluator engine
engine = EvaluatorEngine()

# 2. Construct complete profile with all real-world inputs
profile = FarmerProfile(
    location=LocationInput(
        lat=24.7872,
        lon=89.0721,
        upazila="Adamdighi",
        district="Bogura",
        division="Rajshahi",
        aez=3
    ),
    field_conditions=FieldConditions(
        land_type="MHL",
        soil_texture="Silt Loam",
        soil_ph=6.2,
        soil_organic_carbon_pct=1.10,
        soil_salinity_ec_e=0.80,
        drainage_condition="moderate",
        bulk_density=1.50
    ),
    farmer_priorities=FarmerPriorities(
        land_size_ha=0.40,
        total_budget_bdt=120000.0,
        irrigation_source="shallow_tubewell",
        water_cost_per_m3_bdt=3.5,
        food_security_staple_needed=True,
        risk_tolerance="moderate"
    ),
    target_horizon_years=1,
    farmer_evaluated_sequence=[
        CropInput(year=1, season="Rabi", crop_name="Potato", cultivar="Diamond (HYV)", sowing_date_approx="2024-11-15", stover_management="removed"),
        CropInput(year=1, season="Kharif-1", crop_name="Tomato", cultivar="Summer Hybrid", sowing_date_approx="2025-03-01", stover_management="incorporated"),
        CropInput(year=1, season="Kharif-2", crop_name="T. Aman Rice", cultivar="BRRI dhan49", sowing_date_approx="2025-07-20", stover_management="incorporated")
    ],
    preferences={"language": "bn", "tone": "farmer_friendly"}
)

# 3. Execute 6-stage scientific evaluation
result = engine.evaluate(profile)

# 4. Access verified biophysical results & KrishiBondhu AI advisory
print(f"Health Score : {result.composite_score:.1f}/100 (Grade: {result.grade})")
print(f"Net ΔSOC     : {result.soc_trajectory['delta_soc_annual_t_c_ha']:.3f} t C/ha/year")
print(f"Net Nitrogen : {result.nitrogen_balance['net_n_balance_annual_kg_ha']:.1f} kg N/ha/year")
print(f"Water Deficit: {result.water_balance['net_water_deficit_mm']:.1f} mm")

# 5. Print KrishiBondhu AI advisory report in Bengali
advisory = result.advisory_report
print("\n🤖 কৃষিবন্ধু এআই পরামর্শ (KrishiBondhu AI):")
print(f"শিরোনাম: {advisory['advisory_summary']['verdict_title']}")
print(f"মূল বার্তা: {advisory['advisory_summary']['one_sentence_takeaway']}")
if advisory.get("targeted_smart_swap"):
    swap = advisory["targeted_smart_swap"]
    print(f"প্রস্তাবিত পরিবর্তন: {swap['problematic_crop']} ➔ {swap['recommended_replacement']}")
    print(f"ফলাফল: স্কোর {result.composite_score:.0f} থেকে বৃদ্ধি পেয়ে {swap['projected_score_after_swap']} হবে!")
```

---

### Ready-to-Run Evaluator Demos

#### Demo A: Bogura Adamdighi (Solanaceae Wilt & Nematode Bridge)
```bash
python3 src/evaluate_sequence_cli.py --demo bogura
```
* **Evaluated Sequence:** Potato (Rabi) $\rightarrow$ Tomato (Kharif-1) $\rightarrow$ T. Aman Rice (Kharif-2).
* **Diagnosis:** Catches *Ralstonia solanacearum* bacterial wilt carryover and *Meloidogyne incognita* nematode bridging across consecutive Solanaceae crops ($S_{\text{bio}} = 5.0$).
* **Smart Swap:** Recommends swapping Tomato with **Mungbean (BARI Mung-6)**, fixing $+40\text{ kg N/ha}$, breaking the pathogen bridge, and elevating rotation score from $59.8\text{ (C)}$ to $95.0\text{ (A)}$.

#### Demo B: Satkhira Shyamnagar (Maas-Hoffman Salinity Mortality)
```bash
python3 src/evaluate_sequence_cli.py --demo satkhira
```
* **Evaluated Sequence:** Lentil (Rabi) $\rightarrow$ Mungbean (Kharif-1) $\rightarrow$ T. Aman Rice (Kharif-2) at $EC_e = 7.8\text{ dS/m}$.
* **Diagnosis:** Triggers dual `CRITICAL_BLOCKER` for fatal pulse salinity mortality ($Y_{\text{rel}} = 0.0\%$, Maas-Hoffman thresholds exceeded). Score capped at $38.0\text{ (D-)}$.
* **Smart Swap:** Replaces Lentil with salt-tolerant **Sunflower (BARI Surjamukhi-2 / Hysun-33)**, raising score to $88.0\text{ (A)}$.

#### Demo C: Rajshahi Godagari (High Barind Aquifer Depletion)
```bash
python3 src/evaluate_sequence_cli.py --demo barind
```
* **Evaluated Sequence:** Boro Rice (Rabi) $\rightarrow$ Fallow (Kharif-1) $\rightarrow$ T. Aman Rice (Kharif-2) on High Land with shallow tubewells.
* **Diagnosis:** Flags extreme groundwater overdraft and seasonal water deficit ($962.6\text{ mm}$).
* **Smart Swap:** Swaps water-guzzling Boro for low-water **Chickpea (BARI Chola-9)** or **Mustard (BARI Sarisha-14)**, preserving groundwater and cutting pumping costs.

### Python API Usage
```python
from src.evaluator import (
    EvaluatorEngine,
    FarmerProfile,
    LocationInput,
    FieldConditions,
    FarmerPriorities,
    CropInput
)

# 1. Initialize master evaluator engine
engine = EvaluatorEngine()

# 2. Define profile
profile = FarmerProfile(
    location=LocationInput(lat=24.785, lon=89.042, upazila="Adamdighi", district="Bogura"),
    field_conditions=FieldConditions(land_type="MHL", soil_ph=6.2, soil_salinity_ec_e=0.8),
    farmer_priorities=FarmerPriorities(land_size_ha=0.40, total_budget_bdt=120000.0, irrigation_source="shallow_tubewell"),
    farmer_evaluated_sequence=[
        CropInput(year=1, season="Rabi", crop_name="Potato"),
        CropInput(year=1, season="Kharif-1", crop_name="Tomato"),
        CropInput(year=1, season="Kharif-2", crop_name="T. Aman Rice")
    ]
)

# 3. Execute 6-stage audit
result = engine.evaluate(profile)
print(f"Rotation Score: {result.composite_score} ({result.grade})")
for issue in result.detected_issues:
    print(f"  [{issue.severity}] {issue.title}: {issue.suggested_action}")
```

---

## 📊 20-Location Bangladesh Scientific Verification

The Evaluator DSS was benchmarked and audited across 20 distinct agro-ecological zones covering every major cropping system in Bangladesh ([`scripts/evaluate_20_bd_locations.py`](scripts/evaluate_20_bd_locations.py)). 

Three autonomous subagents with live web search verified all findings against published literature from BARI, BRRI, SRDI, DAE, CIMMYT, and IRRI:

| # | Location & AEZ | Evaluated Cropping Pattern | Score & Grade | Risk Status | Verified Agronomic Remediation |
| :- | :--- | :--- | :---: | :---: | :--- |
| **01** | **Bogura - Adamdighi (AEZ 3)** | Potato ➔ Tomato ➔ T. Aman Rice | **59.8 (C)** | `HIGH_RISK` | Swap Tomato ➔ **Mungbean (BARI Mung-6)** to break *Ralstonia* wilt. |
| **02** | **Bogura - Shibganj (AEZ 25)** | Potato ➔ Boro Rice ➔ T. Aman Rice | **38.0 (D-)** | `BLOCKER` | Boro-Aman turnaround clash ➔ **Short-Duration T. Aman (BRRI dhan75)**. |
| **03** | **Satkhira - Shyamnagar (AEZ 13)** | Lentil ➔ Mungbean ➔ T. Aman Rice | **38.0 (D-)** | `BLOCKER` | Salinity $7.8\text{ dS/m}$ pulse mortality ➔ **Sunflower (BARI Surjamukhi-2)**. |
| **04** | **Khulna - Dacope (AEZ 13)** | Sunflower ➔ Fallow ➔ T. Aman Rice | **76.0 (B)** | `MODERATE` | Salt-tolerant rotation with Kharif-1 leaching fallow ➔ **Optimal**. |
| **05** | **Rajshahi - Godagari (AEZ 26)** | Boro Rice ➔ Fallow ➔ T. Aman Rice | **71.0 (C+)** | `MODERATE` | Barind aquifer drawdown ➔ **Chickpea / Mustard (BARI Chola-9)**. |
| **06** | **Naogaon - Niamatpur (AEZ 26)** | Chickpea ➔ Aus Rice ➔ T. Aman Rice | **73.6 (C+)** | `MODERATE` | High Barind residual moisture usage ➔ **Chickpea / Barley**. |
| **07** | **Sunamganj - Tahirpur (AEZ 21)** | Boro Rice (Late) ➔ Fallow ➔ Fallow | **38.0 (D-)** | `BLOCKER` | April 15 Meghalaya flash flood ➔ **BRRI dhan88 (Early flash-escape)**. |
| **08** | **Kishoreganj - Nikli (AEZ 21)** | Boro Rice (BRRI dhan88) ➔ Fallow ➔ Fallow | **80.7 (B)** | `MODERATE` | 140-day flash-flood escape cultivar in Haor depression ➔ **Optimal**. |
| **09** | **Rangpur - Mithapukur (AEZ 3)** | Potato ➔ Maize ➔ T. Aman Rice | **73.0 (C+)** | `MODERATE` | Soil nutrient mining ➔ **Short-Duration T. Aman (BRRI dhan75)**. |
| **10** | **Dinajpur - Birganj (AEZ 1)** | Wheat ➔ Mungbean ➔ T. Aman Rice | **70.0 (C+)** | `MODERATE` | Acid soil pH 5.5 & turnaround delay ➔ **Sesbania (Dhaincha)**. |
| **11** | **Mymensingh - Trishal (AEZ 9)** | Boro Rice ➔ Aus Rice ➔ T. Aman Rice | **38.0 (D-)** | `BLOCKER` | Triple rice temporal clash ➔ **Dhaincha (Sesbania aculeata)**. |
| **12** | **Jamalpur - Islampur (AEZ 7)** | Mustard ➔ Jute ➔ T. Aman Rice | **74.5 (C+)** | `MODERATE` | Charland turnaround wrap-around delay ➔ **Mustard (BARI Sarisha-14)**. |
| **13** | **Cumilla - Chandina (AEZ 19)** | 2-Yr Triple Rice & Potato System | **38.0 (D-)** | `BLOCKER` | Overlap & Solanaceae persistence ➔ **Short-Duration T. Aman**. |
| **14** | **Noakhali - Subarnachar (AEZ 18)** | Grass pea ➔ Fallow ➔ T. Aman Rice | **78.8 (B)** | `MODERATE` | Coastal estuarine zero-tillage relay ➔ **Sunflower (Surjamukhi-2)**. |
| **15** | **Barishal - Babuganj (AEZ 12)** | Boro Rice ➔ Aus Rice ➔ T. Aman Rice | **38.0 (D-)** | `BLOCKER` | Triple rice monoculture & Zn/S deficit ➔ **Dhaincha green manure**. |
| **16** | **Patuakhali - Kalapara (AEZ 13)** | Mungbean ➔ Fallow ➔ T. Aman Rice | **38.0 (D-)** | `BLOCKER` | Salinity $6.0\text{ dS/m}$ pulse mortality ➔ **Sunflower (Surjamukhi-2)**. |
| **17** | **Jashore - Jhikargachha (AEZ 11)** | Cauliflower ➔ Jute ➔ T. Aman Rice | **74.5 (C+)** | `MODERATE` | Vegetable turnaround delay ➔ **Mustard (BARI Sarisha-14)**. |
| **18** | **Kushtia - Daulatpur (AEZ 11)** | Tobacco ➔ Sesame ➔ T. Aman Rice | **74.5 (C+)** | `MODERATE` | Tobacco severe nutrient mining & allelopathy ➔ **Mustard**. |
| **19** | **Sylhet - Golapganj (AEZ 20)** | Boro Rice ➔ Fallow ➔ T. Aman Rice | **65.0 (C+)** | `MODERATE` | Acid soil pH 4.8 aluminum toxicity ➔ **Mustard + Dololime (1.5 t/ha)**. |
| **20** | **Bandarban - Sadar (AEZ 29)** | Maize ➔ Fallow ➔ T. Aman Rice | **38.0 (D-)** | `BLOCKER` | Rainfed winter drought & hill slope erosion ➔ **Chickpea / Barley**. |

Full audit data: [`data/evaluator_20_places_audit.json`](data/evaluator_20_places_audit.json)  
Subagent verification reports: [`data/evaluator_audit_cohort_1_north.md`](data/evaluator_audit_cohort_1_north.md), [`data/evaluator_audit_cohort_2_coastal.md`](data/evaluator_audit_cohort_2_coastal.md), [`data/evaluator_audit_cohort_3_special.md`](data/evaluator_audit_cohort_3_special.md).

---

## 📐 Core Biophysical Models & Equations

1. **FAO-56 Hargreaves-Samani Reference Evapotranspiration ($ET_0$):**

   $$
   ET_0 = 0.0023 \cdot R_a \cdot (T_{\text{mean}} + 17.8) \cdot \sqrt{T_{\max} - T_{\min}}
   $$

2. **Two-Step Tipping-Bucket Soil Water Balance:**

   $$
   W_{\text{pot}} = W_{t-1} + P_t + I_t - ET_{\text{c}, t}, \quad D_{\text{deep}} = \max(0, W_{\text{pot}} - S_{\max}), \quad W_t = \max(0, \min(S_{\max}, W_{\text{pot}} - D_{\text{deep}}))
   $$

3. **Duration-Weighted Annual Soil Organic Carbon Trajectory ($\Delta \text{SOC}$):**

   $$
   \Delta \text{SOC}_{\text{yr}} = \sum_{i=1}^N \left( \frac{D_i}{365} \times C_{\text{input}, i} \times h \right) - k_2 \cdot \text{SOC}_0
   $$

4. **Legume Biological Nitrogen Fixation ($NHI = 0.70$):**

   $$
   \Delta \text{N}_{\text{soil}} = \text{BNF} - N_{\text{grain}} = N_{\text{total}} \times (1 - NHI) \ge 0
   $$

5. **Maas-Hoffman Crop Salinity Yield Response:**

   $$
   Y_{\text{rel}} = \max(0, 100 - b \cdot (EC_e - a))
   $$

6. **Hill Dose-Response Pathogen Inoculum Accumulation:**

   $$
   \text{Inoculum}_{t+1} = \text{Inoculum}_t \cdot \left(1 + \frac{R_{\max} \cdot S^h}{K_m^h + S^h}\right) \cdot e^{-\lambda \cdot T_{\text{break}}}
   $$

7. **Multi-Factor Rotation Composite Score (0–100):**

   $$
   S_{\text{total}} = 0.20 S_{\text{climate}} + 0.20 S_{\text{hydro}} + 0.20 S_{\text{biology}} + 0.20 S_{\text{soil}} + 0.20 S_{\text{economics}}
   $$

   *(Any critical blocker strictly caps $S_{\text{total}} < 40.0$ and forces a targeted smart swap).*

---

## 🧪 Running the Automated Test Suite

All 22 unit tests across both the Recommender and Evaluator engines run out-of-the-box:

```bash
python3 -m unittest discover tests
```

### Test Coverage Highlights:
* **`tests/test_stage3.py` (15 tests):** Verifies 2-Tier Jordan Curve spatial routing, BARC matrices, Sys square root scoring, perennial tree exclusions, coastal salinity step-downs, and agro-climatic boundaries.
* **`tests/test_evaluator_stages.py` (7 tests):** Verifies NASA $ET_0$, tipping-bucket water balance, $\Delta \text{SOC}$ trajectories, legume BNF, Maas-Hoffman salinity, turnarounds, Haor flash flood hazard traps, and automated directory structure integrity.

---

## 📁 Project File Structure

```text
crop_sequence_recommender/
├── README.md                                  # Complete project documentation & CLI guide
├── VERSION_LOG.md                             # Version history (v1.0, v2.0, v3.0)
│
├── docs/
│   ├── crop_sequence_recommender_architecture.md  # Master technical specification (Recommender)
│   ├── crop_sequence_recommender_architecture.html# Interactive specification viewer
│   └── crop_sequence_evaluator_architecture.md# Evaluator DSS master technical specification
│
├── src/
│   │   # ─── RECOMMENDER ENGINE (Teammates' Pipeline) ───
│   ├── router.py                              # 2-Tier Jordan Curve Ray-Casting PIP Router
│   ├── stage3_engine.py                       # Recommender unified entrypoint & CLI
│   ├── stage3_barc_selector.py                # BARC CZIS matrix selector with 3-tier bucketer
│   ├── stage3_fao_selector.py                 # FAO EcoCrop fuzzy evaluator & Sys scoring
│   ├── global_env_fetcher.py                  # Keyless NASA POWER & SoilGrids fetcher
│   ├── seasonal_calendar.py                   # Pluvial water balance & calendar model
│   ├── ingest_barc_data.py                    # SQLite database migration utility
│   │
│   │   # ─── EVALUATOR DSS (Standalone 6-Stage Engine) ───
│   ├── evaluator/
│   │   ├── __init__.py                        # Clean module exports & EvaluatorEngine alias
│   │   ├── models.py                          # Dataclasses (FarmerProfile, AuditResult, etc.)
│   │   ├── evaluator_engine.py                # Master 6-Stage Evaluator Orchestrator
│   │   ├── nasa_climate_enricher.py           # Stage 1: NASA ET0 & tipping-bucket water balance
│   │   ├── temporal_turnaround_auditor.py     # Stage 2: Turnarounds, wrap-around & hazards
│   │   ├── biological_disease_auditor.py      # Stage 4: Solanaceae wilt, nematodes & biopores
│   │   ├── soil_biogeochem_auditor.py         # Stage 4: SOC trajectory, BNF, salinity & pH
│   │   ├── sequence_scorer_remediator.py      # Stage 3 & 5: Scoring (0-100) & Smart Swaps
│   │   └── ai_agronomic_advisor.py            # Stage 6: KrishiBondhu AI bilingual advisory
│   │
│   └── evaluate_sequence_cli.py               # Standalone Evaluator CLI tool
│
├── tests/
│   ├── test_stage3.py                         # 15 Recommender unit & integration tests
│   └── test_evaluator_stages.py               # 7 Evaluator DSS unit & structural tests
│
├── scripts/
│   └── evaluate_20_bd_locations.py            # 20-location Bangladesh evaluation benchmark
│
└── data/
    ├── crop_recommender.db                    # Pre-cached BARC CZIS SQLite database
    ├── nasa_power_cache.json                  # Cached NASA POWER agroclimatology
    ├── upazila_polygons.json                  # 505 Upazila MultiPolygon boundary geometries
    ├── upazila_boundaries.csv                 # Bounding box cache for broad-phase router
    ├── evaluator_20_places_audit.json         # Complete audit output for 20 BD scenarios
    ├── evaluator_20_places_summary.md         # Markdown summary table of 20 evaluations
    ├── evaluator_audit_cohort_1_north.md      # Subagent audit: Northern & Barind Tract
    ├── evaluator_audit_cohort_2_coastal.md    # Subagent audit: Coastal Saline Belt
    └── evaluator_audit_cohort_3_special.md    # Subagent audit: Haor, Floodplains & Hill Tracts
```

---

## 📜 Citations & References

1. **NASA Langley Research Center**: [NASA POWER Agroclimatology API](https://power.larc.nasa.gov/).
2. **FAO Irrigation and Drainage Paper No. 56**: Allen, R.G., Pereira, L.S., Raes, D., & Smith, M. (1998). *Crop evapotranspiration: Guidelines for computing crop water requirements*.
3. **Maas, E.V., & Hoffman, G.J. (1977)**: "Crop salt tolerance—current assessment." *Journal of the Irrigation and Drainage Division*, 103(2), 115–134.
4. **Hénin, S., & Dupuis, M. (1945)**: "Essai de bilan de la matière organique du sol." *Annales Agronomiques*, 15, 17–29.
5. **Peoples, M.B., Brockwell, J., Herridge, D.F., et al. (1995)**: "The contribution of nitrogen-fixing crop legumes to the productivity of agricultural systems." *Symbiosis*, 19(1), 89–109.
6. **Chen, G., & Weil, R.R. (2011)**: "Root growth and yield of maize as affected by soil compaction and cover crops." *Soil and Tillage Research*, 117, 110–120.
7. **Bangladesh Agricultural Research Council (BARC)**: [Crop Zoning Information System (CZIS)](http://www.cropzoning.gov.bd/) & *Fertilizer Recommendation Guide (FRG-2018)*.
8. **Nasim, M. et al. (2017/2018)**: "Distribution of Crops and Cropping Patterns in Bangladesh." *Bangladesh Rice Journal*, 21(2), 1–55.

---

## 📄 License
This project is open-source and distributed under the **MIT License**.
