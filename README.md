# 🌾 NASA Crop Sequence Recommender Engine (Stages 3–5)

[![Python Standard Library](https://img.shields.io/badge/Python-3.8%2B%20(Pure%20Stdlib)-blue.svg)](https://www.python.org/)
[![Zero External Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(No%20Pip%20Required)-success.svg)]()
[![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-Field%20Shift-orange.svg)](https://www.spaceappschallenge.org/)
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing%20(100%25)-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Field Shift: Adapting Farms with NASA Earth Observations & Local Agro-Ecological Data**  
> An agro-ecological decision-support system and crop sequence recommendation engine. Integrates NASA POWER satellite agroclimatology, UN FAO EcoCrop cardinal limits, ISRIC SoilGrids 2.0 pedometrics, and official Bangladesh Agricultural Research Council (BARC CZIS) regional matrices.

---

## 📑 Table of Contents
1. [Overview & Architecture](#-overview--architecture)
2. [Quick Start (GitHub Clone & Run)](#-quick-start)
3. [CLI Usage & Arguments Reference](#-cli-usage--arguments-reference)
4. [Ready-to-Run Examples](#-ready-to-run-examples)
5. [What is NOT Needed (Zero-Friction Boundary)](#-what-is-not-needed)
6. [Core Algorithms & Guardrails](#-core-algorithms--guardrails)
7. [Running the Automated Test Suite](#-running-the-automated-test-suite)
8. [Project Structure](#-project-structure)
9. [Citations & Acknowledgments](#-citations--acknowledgments)

---

## 🌍 Overview & Architecture

The recommendation engine features a **Dual-Pipeline Spatial Router** that dynamically selects the optimal agro-ecological model based on coordinate location:

```
                                Farmer GPS (Lat, Lon)
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │ 2-Tier Jordan Curve Spatial Router    │
                     │ (Pure-Python Ray-Casting PIP in <0.3ms│
                     └───────────────────┬───────────────────┘
                                         │
                    Is inside Bangladesh?│
                    ┌────────────────────┴───────────────────┐
                    │ YES                                    │ NO
                    ▼                                        ▼
      ┌───────────────────────────┐            ┌───────────────────────────┐
      │ Branch A: Bangladesh BARC │            │ Branch B: Global FAO/NASA │
      ├───────────────────────────┤            ├───────────────────────────┤
      │ • BARC CZIS SQLite Cache  │            │ • NASA POWER Climatology  │
      │ • EffArea = VS + 0.70×S   │            │ • ISRIC SoilGrids 2.0     │
      │ • Monsoonal Flood Rules   │            │ • FAO Tipping-Bucket LGP  │
      │ • Perennial Tree Purge    │            │ • Sys et al. 1991 Sqrt    │
      │ • 3-Tier Dynamic Bucketer │            │ • Trapezoidal Fuzzy Epsilon│
      └─────────────┬─────────────┘            └─────────────┬─────────────┘
                    │                                        │
                    └────────────────────┬───────────────────┘
                                         ▼
                      ┌────────────────────────────────────┐
                      │ Stage 3 Output Contract Schema     │
                      │ (Validated Candidate Seasonal Pools│
                      └────────────────────────────────────┘
```

---

## 🚀 Quick Start

Clone this repository and run immediately. **No virtual environment, `pip install`, or environment variables required.** Works out-of-the-box across **Windows (Command Prompt / PowerShell)**, **macOS**, and **Linux**.

```bash
# 1. Clone the repository
git clone https://github.com/eskit2005/crop_sequence_recommender.git

# 2. Enter the directory
cd crop_sequence_recommender

# 3. Run for any coordinate in Bangladesh (Formatted Terminal Output):
python3 src/stage3_engine.py --lat 24.78 --lon 89.04 --land-type MHL
# On Windows PowerShell / cmd:
# python src/stage3_engine.py --lat 24.78 --lon 89.04 --land-type MHL

# 4. Run for an International Coordinate (Global FAO EcoCrop + NASA POWER):
python3 src/stage3_engine.py --lat -0.303 --lon 36.08

# 5. Output Machine-Readable JSON for Web APIs:
python3 src/stage3_engine.py --lat 24.78 --lon 89.04 --json
```

---

## 🛠 CLI Usage & Arguments Reference

```
usage: python3 src/stage3_engine.py [-h] --lat LAT --lon LON [--land-type LAND_TYPE] [--json]
```

### Argument Details

| Flag | Required | Type | Default | Description & Allowed Values |
| :--- | :---: | :---: | :---: | :--- |
| **`--lat`** | **YES** | `float` | *None* | Geographic Latitude in decimal degrees (e.g. `24.7946`, `50.1109`). |
| **`--lon`** | **YES** | `float` | *None* | Geographic Longitude in decimal degrees (e.g. `89.0657`, `8.6821`). |
| **`--land-type`** | Optional | `string` | `"MHL"` | Monsoonal flood water depth classification (Used for Bangladesh Branch A):<br>• **`HL`** (High Land, 0 cm flood — purges flooded Boro paddy)<br>• **`MHL`** (Medium High Land, 0–90 cm flood — standard triple-crop rotation)<br>• **`MLL`** (Medium Low Land, 90–180 cm flood — caps double cropping $K=2$)<br>• **`LL`** or **`VLL`** (Low Land / Haor Wetland, 180–300+ cm flood — single-season Boro, caps $K=1$) |
| **`--json`** | Optional | `flag` | `False` | Outputs machine-readable JSON adhering to the Stage 3 output contract schema. |
| **`-h`, `--help`** | Optional | `flag` | `False` | Displays the help menu and exits. |

---

## 💡 Ready-to-Run Examples

### Example 1: Northern Granary Commercial Hub (Bogura / Naogaon, Bangladesh)
```bash
python3 src/stage3_engine.py --lat 24.78 --lon 89.04 --land-type MHL
```
* **Engine Action:** Resolves to Raninagar Upazila (`506485`). Evaluates $VS + 0.70S$ hectarage and outputs $K=3$ candidate pools featuring category champions across 5 functional guilds: **Potato**, **Linseed**, **Maize**, **Coriander**, **Cowpea**, **Sesame**, and **T. Aman rice**.

### Example 2: Deep Haor Wetland Monoculture (Sunamganj, Bangladesh)
```bash
python3 src/stage3_engine.py --lat 25.05 --lon 91.56 --land-type LL
```
* **Engine Action:** Resolves to Dowarabazar Upazila (`609033`). Enforces the Haor Monoculture Relaxation: $K=1$, Rabi contains `['Boro dhan']`, and Kharif-1 / Kharif-2 safely backfill `['Fallow']`.

### Example 3: Barind Drought-Prone Terrace (Rajshahi, Bangladesh)
```bash
python3 src/stage3_engine.py --lat 24.28 --lon 88.75 --land-type HL
```
* **Engine Action:** Resolves to Charghat Upazila (`508134`). High Land purges flooded Boro rice; perennial orchard trees (Date Palm, Palmyra Palm, Guava) are 100% eliminated, elevating drought-hardy annual field crops (**Sesame**, **Jute**, **Maize**).

### Example 4: Coastal Saline Belt Dynamic Step-Down (Mongla, Bangladesh)
```bash
python3 src/stage3_engine.py --lat 22.1532 --lon 89.6591 --land-type MHL
```
* **Engine Action:** Resolves to Mongla Upazila (`400158`). Dry-season soil salinity dynamically steps down $K$ from 3 to $K=1$, outputting **Fallow – Fallow – T. Aman dhan** with zero downstream Cartesian sequence collapse.

### Example 5: Global Rift Valley Montane Highlands (Nakuru, Kenya)
```bash
python3 src/stage3_engine.py --lat -0.303 --lon 36.08
```
* **Engine Action:** Automatically diverts to `GLOBAL_FAO_ECOCROP`. Fetches keyless NASA POWER climatology and ISRIC SoilGrids data. Evaluates LGP ($275\text{ days}, K=3$) and ranks cool-season highland crops (**Potato**, **Wheat**, **Cabbage**).

---

## 🛡 What is NOT Needed (Zero-Friction Boundary)

This codebase is specifically engineered to run out-of-the-box in air-gapped environments, edge devices, and serverless containers:

* ❌ **NO `pip install` required:** Uses 100% pure Python standard library (`math`, `urllib`, `sqlite3`, `json`, `argparse`, `dataclasses`, `time`).
* ❌ **NO external GIS C-binaries (NO GDAL, NO GEOS, NO Shapely):** Ray-casting Jordan Curve algorithm is implemented in pure Python.
* ❌ **NO API keys or paid accounts:**
  - **NASA POWER Climatology:** Keyless, open-access public API.
  - **ISRIC SoilGrids 2.0:** Public REST API with automatic mirror failover (`pixelgust.com`).
  - **BARC CZIS:** Bundled pre-cached local SQLite database (`data/crop_recommender.db`).
* ❌ **NO manual administrative codes:** The user never needs to supply BBS Upazila codes or district IDs; raw `(lat, lon)` coordinates are resolved in $< 0.3\text{ ms}$.

---

## 🔬 Core Algorithms & Guardrails

1. **Pure-Python Jordan Curve Point-in-Polygon (PIP):**
   Horizontal ray-casting counts boundary crossings against 505 Upazila MultiPolygon rings. Odd crossings = inside; even = outside. Average routing latency: **$0.128\text{ ms}$**.
2. **Effective Commercial Area Formula:**
   $$\mathbf{\text{EffArea}} = \text{VerySuitable (VS)} + \left(0.70 \times \text{Suitable (S)}\right)$$
   Weighting `S` at 0.70 reflects economic yield parity while preventing marginal (`MS`) false-positive inflation.
3. **Continuous Trapezoidal Fuzzy Logic with $\epsilon$-Guards:**
   Evaluates cardinal thermal, rainfall, and pH limits with $10^{-6}$ epsilon guards against ZeroDivisionError on cliff-edge plateaus.
4. **Sys et al. (1991) Square Root Land Evaluation Method:**
   $$S_{\text{total}} = S_{\min} \times \sqrt{\prod_{i \ne \min} S_i}$$
   Preserves Liebig’s Law of the Minimum ($S_{\min} = 0 \implies 0$) while eliminating Storie index multiplicative compounding decay.
5. **3-Tier Dynamic Bucketer with Category Champions:**
   Harvests Category Champions ($\text{EffArea} \ge 300\text{ ha}$) across 6 distinct functional plant guilds (`Pulses`, `Tubers`, `Oilseeds`, `Fibers`, `Cereals`, `Vegetables`) to ensure agronomic rotation diversity.
6. **Perennial Orchard Blacklist Filter:**
   Purges 19 permanent tree taxa (Date Palm, Palmyra Palm, Guava, Mango, Golden Apple, Coconut, etc.) from seasonal rotations.
7. **Dynamic Cropping Intensity $K$ & Fallow Backfill:**
   $$K = \max\left(1, \min(K_{\text{land}}, \text{active\_pools\_count})\right)$$
   Guarantees non-empty candidate lists by backfilling explicit `Fallow` objects (`crop_id: 999`), preventing Cartesian product collapse in Stage 4.

---

## 🧪 Running the Automated Test Suite

The test suite covers spatial routing, mathematical guards, haor monoculture relaxation, perennial tree exclusions, coastal salinity guards, and global agro-climatology:

```bash
python3 -m unittest tests/test_stage3.py
# On Windows:
# python -m unittest tests/test_stage3.py
```

### Expected Output:
```
test_barc_land_type_exclusions .......................................... ok
test_dynamic_k_coastal_empty_pool_guard ................................. ok
test_engine_bangladesh_pipeline ......................................... ok
test_engine_haor_pipeline ............................................... ok
test_engine_international_pipeline ...................................... ok
test_fao_zero_intensity_desert .......................................... ok
test_perennial_orchard_exclusion ........................................ ok
test_spatial_router_international_envelope_rejection .................... ok
test_spatial_router_known_points ........................................ ok
test_sys_square_root_scoring ............................................ ok
test_trapezoidal_fuzzy_epsilon_guards ................................... ok
test_usda_texture_classification ........................................ ok

----------------------------------------------------------------------
Ran 12 tests in ~8.0s - OK (100% PASS)
```

---

## 📁 Project Structure

```
crop_sequence_recommender/
├── README.md                               # Project documentation & GitHub quick start
├── .gitignore                              # Comprehensive Python & OS ignore rules
├── crop_sequence_recommender_architecture.md   # Master technical specification (Stages 3–5)
├── crop_sequence_recommender_architecture.html # Standalone interactive specification
├── src/
│   ├── router.py                           # 2-Tier Jordan Curve ray-casting spatial router
│   ├── stage3_engine.py                    # Unified engine API & CLI entry point
│   ├── stage3_barc_selector.py             # BARC CZIS selector with 3-tier bucketer
│   ├── stage3_fao_selector.py              # FAO EcoCrop fuzzy evaluator & Sys scoring
│   ├── global_env_fetcher.py               # Keyless NASA POWER & SoilGrids fetcher
│   ├── seasonal_calendar.py                # Pluvial water balance & calendar model
│   └── ingest_barc_data.py                 # SQLite database schema migration utility
├── tests/
│   └── test_stage3.py                      # 12 automated unit and integration tests
└── data/
    ├── crop_recommender.db                 # SQLite database of official BARC CZIS matrices
    ├── upazila_polygons.json               # 505 Upazila MultiPolygon boundary geometries
    ├── upazila_boundaries.csv              # Bounding box cache for broad-phase router
    └── bd_100_batches/                     # 100 benchmark locations across Bangladesh
```

---

## 📜 Citations & Acknowledgments

1. **NASA Langley Research Center**: [NASA POWER Agroclimatology API](https://power.larc.nasa.gov/) (30-year historical climate normals).
2. **UN Food and Agriculture Organization (FAO)**: EcoCrop Database (2,568 cultivated taxa) and *Land Evaluation Framework* (Sys et al., 1991).
3. **ISRIC - World Soil Information**: [SoilGrids 2.0](https://www.isric.org/explore/soilgrids) (250m global soil property predictions).
4. **Bangladesh Agricultural Research Council (BARC)**: [Crop Zoning Information System (CZIS)](http://www.cropzoning.gov.bd/).
5. **Nasim, M. et al. (2017/2018)**: "Distribution of Crops and Cropping Patterns in Bangladesh." *Bangladesh Rice Journal*, 21(2), 1–55.

---

## 📄 License
This project is open-source and distributed under the **MIT License**.
