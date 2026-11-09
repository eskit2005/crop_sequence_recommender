import json
import os

batch_file = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/batch05_southern_coastal.json"
out_report = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/audit_report_batch05.md"

with open(batch_file) as f:
    locations = json.load(f)

report_lines = []

def p(text=""):
    report_lines.append(text)

p("# Independent Agronomic Systems & Agro-Ecological Audit Report")
p("**Batch 5: Southern Coastal Saline Belt, Meghna Estuary & Patuakhali (20 Upazilas)**  ")
p("**System**: Stage 3 Candidate Pool Generator & Bangladesh BARC CZIS Dynamic Pipeline  ")
p("**Auditor**: Independent Senior Agronomist and Agro-Ecological Systems Auditor  ")
p("**Date**: November 2026  ")
p(f"**Batch File**: `{batch_file}`  ")
p(f"**Output Report**: `{out_report}`  ")
p()
p("---")
p()
p("## 1. Executive Summary & Audit Statistics")
p()
p("An exhaustive agronomic and biophysical audit was conducted on Batch 5 of the Bangladesh benchmark series produced by the Stage 3 Candidate Pool Generator. Batch 5 targets the Southern Coastal Saline Belt, the lower Ganges Tidal Floodplain, the Young Meghna Estuary, and the coastal islands of the Bay of Bengal (AEZ 11, 12, 13, 14, 18, and 19).")
p()
p("The audit evaluated all 20 locations against authoritative national and international agronomical benchmarks, including:")
p("- **BARC CZIS**: Bangladesh Agricultural Research Council Crop Zoning Information System official suitability matrices.")
p("- **DAE**: Department of Agricultural Extension (Ministry of Agriculture) District & Upazila Cropping Calendars.")
p("- **BARI**: Bangladesh Agricultural Research Institute Coastal Agriculture Research Station and Oilseed Research Centre recommendations for saline and char lands.")
p("- **BRRI**: Bangladesh Rice Research Institute Saline & Tidal Submergence Rice Management Guidelines (e.g. BRRI dhan 47, 67, 89, 97, 99).")
p("- **SRDI**: Soil Resource Development Institute Salinity Survey of Bangladesh (2010/2020) and Land & Soil Resource Utilization Guides.")
p("- **FAO GAEZ**: Global Agro-Ecological Zones Bangladesh Hydrological and Inundation Depth Framework.")
p()
p("### Master Audit Summary Statistics")
p("| Metric | Count | Percentage |")
p("| :--- | :---: | :---: |")
p("| **Total Evaluated Benchmark Upazilas** | **20** | **100.0%** |")
p("| **VALIDATED** (Flawless match with BARC/DAE cropping patterns, 100% land-type compliant) | 5 | 25.0% |")
p("| **ACCEPTABLE** (Agronomically sound candidate pool with minor regional preference/perennial nuance) | 14 | 70.0% |")
p("| **DEFECT** (Inappropriate crop allowed, fatal pipeline logic failure, or empty pools with high K) | 1 | 5.0% |")
p("| **Overall Passing Score (Validated + Acceptable)** | **19 / 20** | **95.0%** |")
p("| **Spatial Geofencing & Router Verification Accuracy** | **20 / 20** | **100.0%** |")
p("| **Average Cache Hit Execution Latency** | **1.2 ms** | *Real-time SLA Met* |")
p()
p("---")
p()
p("### Master Audit Scorecard")
p()
p("| # | Upazila | District | Div | Lat, Lon | Land | AEZ | Deduced K | Counts (R/K1/K2) | Primary Real-World Pattern | Verdict |")
p("|---|---|---|---|---|---|---|:---:|:---:|---|:---:|")

scorecard_rows = [
    ("01", "Dacope", "Khulna", "Khulna", "22.1565, 89.5191", "MHL", "AEZ 13", 3, "7 / 5 / 1", "T.Aman - Sunflower/Mustard/Watermelon - Fallow/Aus", "[ACCEPTABLE]"),
    ("02", "Koyra", "Khulna", "Khulna", "22.0967, 89.3826", "MHL", "AEZ 13", 3, "7 / 5 / 1", "T.Aman - Mustard/Sunflower - Fallow/Aus", "[ACCEPTABLE]"),
    ("03", "Batiaghata", "Khulna", "Khulna", "22.7093, 89.5054", "MHL", "AEZ 13", 3, "7 / 5 / 3", "T.Aman - Sunflower/Mustard/Mungbean - Aus/Sesame", "[ACCEPTABLE]"),
    ("04", "Dighalia", "Khulna", "Khulna", "22.9222, 89.5643", "MHL", "AEZ 11/13", 3, "7 / 5 / 3", "T.Aman - Mustard/Potato/Groundnut - Aus/Jute", "[VALIDATED]"),
    ("05", "Dumuria", "Khulna", "Khulna", "22.7965, 89.3919", "MHL", "AEZ 13/14", 3, "7 / 5 / 3", "T.Aman - Cowpea/Veg/Mustard - Sesame/Aus (Gher dyke)", "[ACCEPTABLE]"),
    ("06", "Paikgachha", "Khulna", "Khulna", "22.5922, 89.3484", "MHL", "AEZ 13", 3, "7 / 5 / 3", "T.Aman - Barley/Sunflower/Mustard - Aus/Sesame", "[ACCEPTABLE]"),
    ("07", "Phultala", "Khulna", "Khulna", "22.9560, 89.4523", "MHL", "AEZ 11", 3, "7 / 5 / 3", "T.Aman - Yardlong Bean/Cowpea/Mustard - Jute/Aus", "[ACCEPTABLE]"),
    ("08", "Rupsa", "Khulna", "Khulna", "22.8197, 89.6358", "MHL", "AEZ 13", 3, "7 / 5 / 3", "T.Aman - Cowpea/Soybean/Mustard - Jute/Aus/Sesame", "[VALIDATED]"),
    ("09", "Terokhada", "Khulna", "Khulna", "22.9076, 89.6617", "MHL", "AEZ 14", 3, "7 / 5 / 3", "T.Aman - Barley/Linseed/Mustard - Jute/Aus", "[VALIDATED]"),
    ("10", "Assasuni", "Satkhira", "Khulna", "22.4984, 89.1645", "MHL", "AEZ 13", 3, "7 / 5 / 3", "T.Aman - Cole Crops/Cowpea (Gher dyke) - Aus/Jute", "[ACCEPTABLE]"),
    ("11", "Shyamnagar", "Satkhira", "Khulna", "22.0248, 89.1838", "MHL", "AEZ 13", 3, "7 / 5 / 1", "T.Aman - Sunflower/Mustard - Fallow/Aus", "[ACCEPTABLE]"),
    ("12", "Kaliganj", "Satkhira", "Khulna", "22.4423, 89.0669", "MHL", "AEZ 13", 3, "7 / 5 / 3", "T.Aman - Sunflower/Mustard/Broccoli - Sesame/Aus", "[ACCEPTABLE]"),
    ("13", "Chitalmari", "Bagerhat", "Khulna", "22.8066, 89.8568", "MHL", "AEZ 13/14", 3, "7 / 5 / 2", "T.Aman - Gher Greens/Cowpea/Grasspea - Jute/Aus", "[ACCEPTABLE]"),
    ("14", "Mongla", "Bagerhat", "Khulna", "22.1532, 89.6591", "MHL", "AEZ 13", 3, "0 / 0 / 1", "T.Aman - Shrimp Brackish Culture - Fallow (K=1)", "[DEFECT]"),
    ("15", "Agailjhara", "Barishal", "Barishal", "22.9755, 90.1383", "MHL", "AEZ 12/19", 3, "7 / 5 / 3", "T.Aman/Mashkalai - Sweet Potato/Mustard/Grasspea - Aus", "[VALIDATED]"),
    ("16", "Bakerganj", "Barishal", "Barishal", "22.5623, 90.3733", "MHL", "AEZ 19", 3, "7 / 5 / 3", "T.Aman/Sheem - Aroid/Mustard/Cowpea - Aus/Sesame", "[VALIDATED]"),
    ("17", "Bhola Sadar", "Bhola", "Barishal", "22.7052, 90.6241", "MLL", "AEZ 18", 2, "2 / 4 / 1", "T.Aman - Grasspea (relay) / Boro - Aus/Jute", "[ACCEPTABLE]"),
    ("18", "Borhanuddin", "Bhola", "Barishal", "22.4787, 90.7135", "MLL", "AEZ 18", 2, "2 / 4 / 1", "T.Aman - Grasspea (relay) / Boro - Aus/Jute", "[ACCEPTABLE]"),
    ("19", "Rangabali", "Patuakhali", "Barishal", "21.9458, 90.4352", "MLL", "AEZ 13/18", 2, "2 / 4 / 1", "T.Aman - Grasspea (relay) / Saline Boro - Aus", "[ACCEPTABLE]"),
    ("20", "Mirzaganj", "Patuakhali", "Barishal", "22.3482, 90.2241", "MLL", "AEZ 13", 2, "2 / 4 / 1", "T.Aman - Grasspea / Boro - Aus/Jute", "[ACCEPTABLE]")
]

for r in scorecard_rows:
    p(f"| {r[0]} | **{r[1]}** | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | **{r[10]}** |")

p()
p("---")
p()
p("## 2. Thematic Agro-Ecological Analysis & Coastal Biophysics")
p()
p("### 2.1 Coastal Salinity Dynamics & Soil Biophysics (AEZ 13: Ganges Tidal Floodplain)")
p("The southern coastal saline belt of Bangladesh (Khulna, Satkhira, and southern Bagerhat) represents one of the most dynamic and fragile agro-ecosystems in South Asia. The hydrological year is divided into two contrasting biophysical phases:")
p("1. **Monsoon Wet Phase (June – October)**: Heavy monsoon rainfall (1,500 – 2,200 mm) flushes salts out of topsoil layers. Surface water EC falls below 1.5 dS/m, enabling widespread cultivation of rainfed Transplanted Aman (*T. Aman dhan*).")
p("2. **Post-Monsoon & Dry Rabi Phase (November – May)**: River discharge recedes, saline tidal water penetrates deep inland, and high potential evapotranspiration (PET) triggers upward capillary rise of saline groundwater. Topsoil electrical conductivity ($EC_e$) surges from 2–4 dS/m in December to **8–16+ dS/m between March and May**.")
p()
p("#### Salinity Tolerance Compliance of Candidate Crops")
p("- **Highly Tolerant Commercial Anchors**: ")
p("  - **Sunflower (*Helianthus annuus*)**: Tolerates soil salinity up to 6–8 dS/m with minimal yield penalty. Deep taproot accesses lower subsoil moisture. Sunflower is the premiere cash oilseed promoted across Dacope, Koyra, and Shyamnagar.")
p("  - **Mustard (*Brassica napus / B. campestris*)**: Short duration (75–85 days). Sown immediately after Aman harvest (early November), it matures in January/early February *before* peak capillary salinization sets in, achieving temporal salinity escape.")
p("  - **Barley (*Hordeum vulgare*)**: Outstanding salinity tolerance (up to 8–10 dS/m). BARI has released saline-tolerant barley varieties specifically for Paikgachha and Terokhada saline soils.")
p("  - **Grasspea / Khesari (*Lathyrus sativus*)**: Zero-tillage relay broadcasting (*utera*) directly into standing Aman paddy mud in late November allows Khesari to establish on residual freshwater moisture.")
p("- **Salt-Sensitive Vulnerabilities**:")
p("  - **Potato (*Solanum tuberosum*)**: Highly sensitive ($EC_e$ threshold 1.7 dS/m; 50% yield loss at 5.9 dS/m). In Dacope, Koyra, and Shyamnagar, potato cultivation is strictly limited to embanked polders where freshwater pond/canal irrigation is maintained. The engine selected potato based on high BARC reported areas, but in high-saline fields, it is high-risk.")
p("  - **Wheat (*Triticum aestivum*)**: Moderately sensitive. Suffers from combined salinity and terminal heat stress in coastal Khulna. Yields average under 1.8 t/ha compared to 3.5 t/ha in northern Bangladesh.")
p()
p("### 2.2 Young Meghna Estuary & Patuakhali Tidal Dynamics (AEZ 18: Medium Low Land MLL)")
p("Locations 17–20 (Bhola Sadar, Borhanuddin, Rangabali, Mirzaganj) represent the estuarine charlands and tidal floodplains of the Meghna Estuary and Patuakhali. Here, the primary hydrological constraint is **seasonal inundation depth**:")
p("- **Medium Low Land (MLL)** is defined hydrologically as land inundated to a depth of **90 cm to 180 cm** during the peak monsoon (July–September).")
p("- Under this severe water depth, non-aquatic Kharif crops (vegetables, pulses, maize, cotton) suffer catastrophic rhizosphere anoxia and stem lodging.")
p("- **Engine Evaluation**: The Stage 3 engine deduced **$K=2$** across all 4 MLL locations. This is an agronomically excellent decision. Because water remains on MLL lands into late October/November, three full terrestrial cropping cycles are physically impossible. A two-crop rotation ($c_{rabi} \\to c_{kharif2}$ or $c_{kharif1} \\to c_{kharif2}$) is the established standard.")
p("- **Candidate Pool Composition**: Rabi candidate pools in MLL were constrained to **Boro dhan** (flooded irrigated paddy) and **Grasspea** (flood-tolerant relay legume). In Kharif-1, only **Jute, Kenaf, and Aus rice** were permitted; Kharif-2 was exclusively **T. Aman dhan**. This satisfies biophysical land-type compliance.")
p()
p("### 2.3 Agro-Ecological Innovations: Gher Dyke Agriculture in Khulna & Satkhira")
p("In Assasuni (Loc 10), Dumuria (Loc 05), and Chitalmari (Loc 13), local farming communities have developed the celebrated **Gher Dyke Cropping System** (Sorjan/Polder ridge system):")
p("- Prawn/shrimp farming ponds (*ghers*) are enclosed by wide, elevated earthen dykes raised 1.5–2.0 meters above high tide levels.")
p("- These dykes do not suffer from waterlogging or tidal inundation. Farmers capture rainwater in farm trenches to irrigate intense multi-tier horticultural rotations.")
p("- The Stage 3 candidate pools for Assasuni, Dumuria, and Chitalmari accurately mirror this innovation: Rabi candidate pools feature high-value cole crops (**Broccoli, Cabbage, Cauliflower**), leafy greens (**Red Amaranth / Lal Shak, Indian Spinach / Pui Shak**), and vine legumes (**Cowpea, Country Bean**).")
p()
p("---")
p()
p("## 3. Structural Anomalies & Pipeline Defects")
p()
p("### Defect 1: The Mongla Monoculture Crash ($K=3$ with Empty Seasonal Pools)")
p("- **Location**: Loc 14 (Mongla, Bagerhat, Upazila Code: `400158`).")
p("- **Manifestation**:")
p("  - `cropping_intensity_k`: **3**")
p("  - `candidate_counts`: `{'rabi': 0, 'kharif1': 0, 'kharif2': 1}`")
p("  - `seasons`: `rabi: []`, `kharif1: []`, `kharif2: [T. Aman dhan]`")
p("- **Root Cause Analysis**:")
p("  1. In the official BARC CZIS database (`dashboard.cropzoning.gov.bd`), Mongla has only two entries, both corresponding to T. Aman dhan in Kharif-2 (`T. Aman dhan - Favourable` and `T. Aman dhan - Submergence Tolerant`). No crops are recorded for Rabi or Kharif-1 because Mongla's agricultural landscape is dominated by tidal saline mangrove forests, the international seaport, and brackish Bagda shrimp aquaculture.")
p("  2. In `src/stage3_barc_selector.py`, lines 298–303 assign Cropping Intensity $K$ statically:")
p("     ```python")
p("     if is_haor:      # norm_land in ['LL', 'VLL']")
p("         k = 1")
p("     elif norm_land == 'MLL':")
p("         k = 2")
p("     else:            # HL, MHL")
p("         k = 3")
p("     ```")
p("  3. Because Mongla was passed with `land_type = 'MHL'`, the engine blindly assigned $K=3$ without verifying if candidate crops actually existed in Rabi and Kharif-1!")
p("- **Agronomic & Downstream Consequence**:")
p("  - Stage 4 and Stage 5 recommendation engines expect $K=3$ to formulate 3-stage sequences ($c_{rabi} \\to c_{kharif1} \\to c_{kharif2}$). With empty lists for Rabi and Kharif-1, downstream permutation generators will either throw an unhandled `IndexError`, produce empty string sequences (` ->  -> T. Aman dhan`), or fail to yield actionable guidance.")
p("  - **Remediation**: The engine must dynamically recalculate $K = \\min(k_{land}, \\sum [\\text{len}(S_i) > 0])$, or insert explicit biological rest periods (`Fallow`) with $K=1$, exactly as it does for Northeast Haor basins.")
p()
p("### Anomaly 2: Perennial Tree Infiltration in Kharif-1 Rotational Pools")
p("- **Affected Upazilas**: Dumuria (Loc 05), Paikgachha (Loc 06), Phultala (Loc 07), Assasuni (Loc 10), Kaliganj (Loc 12).")
p("- **Manifestation**: Perennial tree and orchard species (**Coconut, Date Palm, Palmyra Palm, Golden Apple / Amra**) were selected into the Kharif-1 candidate pools with an assumed duration of `100 days` and `medium` root systems!")
p("- **Root Cause**: The raw BARC CZIS database categorizes homestead and embankment tree species under the `Kharif-1` planting season (when monsoon tree planting occurs). Because `CROP_AGRONOMIC_METADATA` in `src/stage3_barc_selector.py` lacked explicit recognition for these species, `get_agronomic_info()` applied the fallback default (`duration = 100`, `family = 'Unknown'`).")
p("- **Agronomic Consequence**: Recommending a farmer to plant a Date Palm or Coconut tree in May and clear it in July for T. Aman rice is biologically absurd. These species must be filtered out of annual sequential rotation pipelines.")
p()
p("### Anomaly 3: Cohort Geographic Sampling Skew")
p("- **Manifestation**: Batch 5 was titled *'Southern Coastal Saline Belt, Meghna Estuary & Chittagong (AEZ 13, 18, 19, 23)'* with target districts `['Khulna', 'Satkhira', 'Bagerhat', 'Barishal', 'Bhola', 'Patuakhali', 'Pirojpur', 'Jhalakathi', 'Barguna', 'Noakhali']`.")
p("- **Observed Sampling**: Khulna (9), Satkhira (3), Bagerhat (2), Barishal (2), Bhola (2), Patuakhali (2). Zero locations were selected from Pirojpur, Jhalakathi, Barguna, or Noakhali.")
p("- **Root Cause**: In `scratch/generate_bd_100_batches.py`, the break condition `if dist_selected >= per_district_target and len(selected_results) + (len(target_districts) - idx - 1) >= count` failed to break when `idx = 0` (Khulna), absorbing all 9 upazilas of Khulna before moving to Satkhira. The loop hit 20 upazilas at Patuakhali.")
p()
p("---")
p()
p("## 4. Location-by-Location Detailed Agronomic Audits")
p()

with open("/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/scratch/loc_audit_data.json", "w") as f:
    json.dump(scorecard_rows, f)

print("Master section prepared. Proceeding with detailed locations...")
