# Crop Sequence Recommender: System Version Log

## [Version 1.0 - Planetary Benchmark & Universal Climate Engine] (Git Tag: `v1.0-planetary`)
**Date:** November 7, 2026  
**Commit:** `45d11a4`

### Architectural Scope
* **Universal Agro-Meteorological Segmentation Engine**: Implemented in [`src/seasonal_calendar.py`](src/seasonal_calendar.py) and [`src/global_env_fetcher.py`](src/global_env_fetcher.py).
* **NASA POWER Climatology Integration**: Automated ingestion of 30-year daily radiation, precipitation rate (`PRECTOTCORR`), and temperatures ($T_{\min}, T_{\max}, T_{\text{mean}}$) converted to monthly water balance.
* **FAO GAEZ v4 Daily Tipping-Bucket Model**: Reference soil water storage capacity ($S_{\max} = 100\text{ mm}$), daily Hargreaves PET, and daily moisture sufficiency tracking ($P_d + W_{t-1} \ge 0.5 \times PET_d$ and $T_{\text{mean}} \ge 5.0^\circ\text{C}$).
* **10 Global Agro-Climatic Regimes**:
  1. `TROPICAL_HIGHLAND_VALLEY` (Highland radiation freeze & Andean staples)
  2. `HYPER_ARID_DESERT` (Rainless desert drought dormancy, $K=0$)
  3. `MEDITERRANEAN_WINTER_RAIN` (Mild winter active, summer aridity fallow)
  4. `MEDITERRANEAN_CONTINENTAL_STEPPE` (Continental winter cereal with spring heading)
  5. `TEMPERATE_CONTINENTAL_FROST` (High-latitude spring/summer cereal, sub-zero freeze pause, and Huang-Huai-Hai double cropping $K=2$)
  6. `SEMI_ARID_STEPPE` (Summer monsoon vs winter rain dynamically branched)
  7. `TEMPERATE_OCEANIC_MARITIME` (Mild maritime double cropping / rice-wheat rotation)
  8. `HUMID_SUBTROPICAL` (Cfa basin summer cash crop + winter cover/small grain)
  9. `HUMID_TROPICAL_PERENNIAL` (Year-round pluvial equatorial tropics)
  10. `TROPICAL_MONOMODAL_RAIN` / `BIMODAL` (Equatorial monsoons)

### Verification History
* **Benchmark Iteration 1**: 100 global grain baskets audited (98% validated).
* **Benchmark Iteration 2**: 150 diverse agro-ecological zones audited across 10 regional subagents (96% validated).
* **Benchmark Iteration 3**: 100 brand-new worldwide coordinates audited across 6 regional subagents (82% pre-remediation $\to$ 100% verified resolved post-remediation).
* **Cumulative Milestone**: 350 distinct global coordinates validated against USDA NASS, AAFC, EMBRAPA, INTA, SIAP, CAAS, ICAR, and FAO guidelines.
* **Preservation**: Fully committed and tagged as `v1.0-planetary`.

---

## [Version 2.0 - Bangladesh Production Core & Dual-Branch Architecture] (Current Main)
**Date:** November 9, 2026  
**Reference Blueprint:** [`docs/crop_sequence_recommender_architecture.md`](docs/crop_sequence_recommender_architecture.md)

### Architectural Scope
* **Focus Re-Alignment**: Prioritizing the hackathon end-to-end user experience, ultra-low latency, and agronomic rotation intelligence (Stages 3, 4, and 5).
* **Branch A (Bangladesh Local Authority Pipeline)**:
  - Official Bangladesh Agricultural Research Council (BARC) Crop Zoning Information System (CZIS) suitability data.
  - 505 Upazilas across all 64 districts resolved via a 2-Tier pure-Python spatial router (`src/router.py`) in $< 0.15\text{ ms}$.
  - Write-through SQLite local cache (`data/crop_recommender.db`) serving candidate pools in $< 3\text{ ms}$.
  - Inundation level rules (`HL`, `MHL`, `MLL`, `LL`) preventing rhizosphere anoxia and haor monoculture deadlocks.
  - Dynamic 3-Tier bucketing yielding 7 Rabi, 5 Kharif-1, and 3 Kharif-2 crops.
* **Branch B (Global Climate Adaptation Proof-of-Concept)**:
  - Global FAO EcoCrop + NASA POWER Earth observations for international coordinates.
* **100-Location Comprehensive Bangladesh Audit**:
  - 100 diverse agricultural locations sampled across all major Bangladesh Agro-Ecological Zones (AEZs).
  - Evaluated by 5 independent agronomic subagents covering Northern Granary, Barind Tract, Central Delta, Northeast Haor Basin, and Southern Coastal Saline Belt.

---

## [Version 3.0 - Standalone Evaluator Decision Support System & KrishiBondhu AI]
**Date:** November 13, 2026  
**Reference Blueprint:** [`docs/crop_sequence_evaluator_architecture.md`](docs/crop_sequence_evaluator_architecture.md)

### Architectural Scope
* **Decoupled Evaluator Decision Support System (DSS)**:
  - Built as a standalone, production-ready Python package in `src/evaluator/` with zero external dependencies.
  - Implements all 6 evaluation stages:
    1. **NASA Climate Enricher**: FAO-56 Hargreaves-Samani $ET_0$, solar radiation geometry $R_a$, and two-step tipping-bucket water balance.
    2. **Temporal & Turnaround Feasibility**: Monotonic day offsets, dynamic turnaround gaps $T_{\text{gap}}$, circular multi-year wrap-around loop $T_{\text{wrap}}$, and regional hazard cut-offs (Haor flash flood April 15, Bogura late Nor'wester March 10, Aman transplanting August 15).
    3. **Agro-Hydrological Compatibility**: Land-type flood inundation depths, Barind aquifer depletion checks, and rainfed winter drought deficit.
    4. **Biological Disease & Soil Health**: Duration-weighted $\Delta \text{SOC}$ trajectory (Hénin-Dupuis/ICBM/Lal), net legume BNF with $NHI = 0.70$, Maas-Hoffman salinity response, 24–36 month *Solanaceae* non-host rule (*Ralstonia solanacearum* and *Meloidogyne incognita*), maize nematode host bridging, and root biopore stratigraphy.
    5. **Multi-Factor Scoring & Targeted Remediation**: 5 sub-scores ($S_{\text{climate}}, S_{\text{hydro}}, S_{\text{biology}}, S_{\text{soil}}, S_{\text{economics}}$), critical blocker caps ($<40.0$), and deterministic Smart Crop Swaps.
    6. **KrishiBondhu AI Explainability**: Generates structured, empathetic bilingual advisory reports in Bengali and English.
* **CLI & Tooling**:
  - `src/evaluate_sequence_cli.py`: Interactive CLI with built-in demos (`--demo bogura`, `--demo satkhira`, `--demo barind`), custom sequence evaluation, and JSON output.
  - Comprehensive Input Matrix & Example Profile: Added complete 4-domain input specification (Location, Field Biophysics, Farmer Socio-Economics, Crop Sequence) and verified all-arguments working example in `README.md`, `docs/crop_sequence_recommender_architecture.md`, and `docs/crop_sequence_evaluator_architecture.md`, bundled with a ready-to-run template profile in `data/farmer_profile_example.json`.
* **Empirical Verification Across 20 Diverse Bangladesh Locations**:
  - Benchmarked across 20 distinct agro-ecological scenarios (`scripts/evaluate_20_bd_locations.py`, `data/evaluator_20_places_audit.json`, `data/evaluator_20_places_summary.md`).
  - Fact-checked and verified by 3 autonomous subagents with live web search against BARI, BRRI, SRDI, DAE, CIMMYT, and IRRI literature.
* **Automated Unit Testing & Verification**:
  - 22/22 unit tests passing across both Recommender and Evaluator modules (`python3 -m unittest discover tests`), including directory structure integrity assertions.
* **Repository-Wide Mathematical Equations & LaTeX KaTeX Compatibility Audit**:
  - Scanned all 44 repository markdown files (`README.md`, `VERSION_LOG.md`, `docs/*`, `data/*`).
  - Automated CI audit harness in `scripts/audit_latex_equations.py` validating 100% GFM isolation, delimiter balance, macro validity, and strict KaTeX rendering (0 errors remaining across all repository files).
