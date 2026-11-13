"""
evaluate_20_bd_locations.py - Evaluates 20 Diverse Agricultural Scenarios Across Bangladesh
Runs the 6-stage Crop Sequence Evaluator Decision Support System (DSS) across all 8 divisions,
different AEZs, hydrological conditions, and real smallholder cropping sequences.
"""

import os
import sys
import json

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator.models import FarmerProfile
from src.evaluator.evaluator_engine import CropSequenceEvaluatorEngine


SCENARIOS_20 = [
    {
        "id": "LOC_01_BOGURA_ADAMDIGHI",
        "name": "Bogura - Adamdighi (Tista Meander Floodplain, AEZ 3)",
        "location": {"lat": 24.80, "lon": 89.05, "upazila": "Adamdighi", "district": "Bogura", "division": "Rajshahi", "aez": 3},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silt Loam", "soil_ph": 6.2, "soil_organic_carbon_pct": 1.10, "soil_salinity_ec_e": 0.8},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 120000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Potato", "cultivar": "Diamond"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Tomato", "cultivar": "Summer Hybrid"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice", "cultivar": "BRRI dhan49"}
        ]
    },
    {
        "id": "LOC_02_BOGURA_SHIBGANJ",
        "name": "Bogura - Shibganj (Level Barind / Tista Floodplain, AEZ 3 & 25)",
        "location": {"lat": 24.98, "lon": 89.33, "upazila": "Shibganj", "district": "Bogura", "division": "Rajshahi", "aez": 25},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silt Loam", "soil_ph": 6.4, "soil_organic_carbon_pct": 1.15, "soil_salinity_ec_e": 0.7},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 140000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Potato"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_03_SATKHIRA_SHYAMNAGAR",
        "name": "Satkhira - Shyamnagar (Coastal Saline Belt, AEZ 13)",
        "location": {"lat": 22.33, "lon": 89.15, "upazila": "Shyamnagar", "district": "Satkhira", "division": "Khulna", "aez": 13},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Clay Loam", "soil_ph": 7.4, "soil_organic_carbon_pct": 0.95, "soil_salinity_ec_e": 7.8},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 100000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Lentil"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Mungbean"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_04_KHULNA_DACOPE",
        "name": "Khulna - Dacope (Ganges Tidal Floodplain Saline, AEZ 13)",
        "location": {"lat": 22.57, "lon": 89.51, "upazila": "Dacope", "district": "Khulna", "division": "Khulna", "aez": 13},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silty Clay", "soil_ph": 7.2, "soil_organic_carbon_pct": 1.05, "soil_salinity_ec_e": 6.5},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 90000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Sunflower"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice", "cultivar": "BRRI dhan73"}
        ]
    },
    {
        "id": "LOC_05_RAJSHAHI_GODAGARI",
        "name": "Rajshahi - Godagari (High Barind Tract, AEZ 26)",
        "location": {"lat": 24.46, "lon": 88.33, "upazila": "Godagari", "district": "Rajshahi", "division": "Rajshahi", "aez": 26},
        "field_conditions": {"land_type": "HL", "soil_texture": "Clay Loam", "soil_ph": 5.8, "soil_organic_carbon_pct": 0.85, "soil_salinity_ec_e": 0.5},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 110000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_06_NAOGAON_NIAMATPUR",
        "name": "Naogaon - Niamatpur (High Barind Drought Belt, AEZ 26)",
        "location": {"lat": 24.86, "lon": 88.56, "upazila": "Niamatpur", "district": "Naogaon", "division": "Rajshahi", "aez": 26},
        "field_conditions": {"land_type": "HL", "soil_texture": "Silt Loam", "soil_ph": 6.0, "soil_organic_carbon_pct": 0.90, "soil_salinity_ec_e": 0.5},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 95000.0, "irrigation_source": "rainfed_only", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Gram / Chickpea"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Aus Rice"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_07_SUNAMGANJ_TAHIRPUR",
        "name": "Sunamganj - Tahirpur (Haor Basin Wetland, AEZ 21)",
        "location": {"lat": 25.09, "lon": 91.17, "upazila": "Tahirpur", "district": "Sunamganj", "division": "Sylhet", "aez": 21},
        "field_conditions": {"land_type": "LL", "soil_texture": "Clay", "soil_ph": 5.2, "soil_organic_carbon_pct": 1.60, "soil_salinity_ec_e": 0.4},
        "farmer_priorities": {"land_size_ha": 0.60, "total_budget_bdt": 80000.0, "irrigation_source": "surface_canal", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice", "cultivar": "Late HYV"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "Fallow"}
        ]
    },
    {
        "id": "LOC_08_KISHOREGANJ_NIKLI",
        "name": "Kishoreganj - Nikli (Haor Basin Wetland, AEZ 21)",
        "location": {"lat": 24.32, "lon": 90.95, "upazila": "Nikli", "district": "Kishoreganj", "division": "Dhaka", "aez": 21},
        "field_conditions": {"land_type": "LL", "soil_texture": "Clay Loam", "soil_ph": 5.4, "soil_organic_carbon_pct": 1.50, "soil_salinity_ec_e": 0.4},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 75000.0, "irrigation_source": "surface_canal", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice", "cultivar": "BRRI dhan88 (Early)"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "Fallow"}
        ]
    },
    {
        "id": "LOC_09_RANGPUR_MITHAPUKUR",
        "name": "Rangpur - Mithapukur (Tista Meander Floodplain, AEZ 3)",
        "location": {"lat": 25.58, "lon": 89.28, "upazila": "Mithapukur", "district": "Rangpur", "division": "Rangpur", "aez": 3},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Sandy Loam", "soil_ph": 5.9, "soil_organic_carbon_pct": 1.00, "soil_salinity_ec_e": 0.5},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 135000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Potato"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Maize"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_10_DINAJPUR_BIRGANJ",
        "name": "Dinajpur - Birganj (Old Himalayan Piedmont Plain, AEZ 1)",
        "location": {"lat": 25.86, "lon": 88.66, "upazila": "Birganj", "district": "Dinajpur", "division": "Rangpur", "aez": 1},
        "field_conditions": {"land_type": "HL", "soil_texture": "Sandy Loam", "soil_ph": 5.5, "soil_organic_carbon_pct": 1.20, "soil_salinity_ec_e": 0.4},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 90000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Wheat"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Mungbean"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_11_MYMENSINGH_TRISHAL",
        "name": "Mymensingh - Trishal (Old Brahmaputra Floodplain, AEZ 9)",
        "location": {"lat": 24.58, "lon": 90.39, "upazila": "Trishal", "district": "Mymensingh", "division": "Mymensingh", "aez": 9},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silt Loam", "soil_ph": 6.5, "soil_organic_carbon_pct": 1.25, "soil_salinity_ec_e": 0.6},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 120000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Aus Rice"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_12_JAMALPUR_ISLAMPUR",
        "name": "Jamalpur - Islampur (Active Brahmaputra Charland, AEZ 7)",
        "location": {"lat": 25.08, "lon": 89.79, "upazila": "Islampur", "district": "Jamalpur", "division": "Mymensingh", "aez": 7},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Sandy Silt", "soil_ph": 6.6, "soil_organic_carbon_pct": 0.70, "soil_salinity_ec_e": 0.5},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 85000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Mustard"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Jute"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_13_CUMILLA_CHANDINA",
        "name": "Cumilla - Chandina (Old Meghna Estuarine Floodplain, AEZ 19)",
        "location": {"lat": 23.48, "lon": 91.00, "upazila": "Chandina", "district": "Cumilla", "division": "Chattogram", "aez": 19},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silt Loam", "soil_ph": 6.3, "soil_organic_carbon_pct": 1.15, "soil_salinity_ec_e": 0.7},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 220000.0, "irrigation_source": "deep_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 2,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Potato"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"},
            {"year": 2, "season": "Rabi", "crop_name": "Potato"},
            {"year": 2, "season": "Kharif-1", "crop_name": "Boro Rice"},
            {"year": 2, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_14_NOAKHALI_SUBARNACHAR",
        "name": "Noakhali - Subarnachar (Young Meghna Estuarine Coastal Plain, AEZ 18)",
        "location": {"lat": 22.65, "lon": 91.08, "upazila": "Subarnachar", "district": "Noakhali", "division": "Chattogram", "aez": 18},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silty Clay Loam", "soil_ph": 7.0, "soil_organic_carbon_pct": 1.10, "soil_salinity_ec_e": 5.2},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 90000.0, "irrigation_source": "rainfed_only", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Grass pea"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_15_BARISHAL_BABUGANJ",
        "name": "Barishal - Babuganj (Ganges Tidal Floodplain Non-Saline, AEZ 12)",
        "location": {"lat": 22.83, "lon": 90.31, "upazila": "Babuganj", "district": "Barishal", "division": "Barishal", "aez": 12},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Silt Loam", "soil_ph": 6.8, "soil_organic_carbon_pct": 1.30, "soil_salinity_ec_e": 1.5},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 105000.0, "irrigation_source": "surface_canal", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Aus Rice"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_16_PATUAKHALI_KALAPARA",
        "name": "Patuakhali - Kalapara (Ganges Tidal Saline Coastal Belt, AEZ 13)",
        "location": {"lat": 21.98, "lon": 90.23, "upazila": "Kalapara", "district": "Patuakhali", "division": "Barishal", "aez": 13},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Clay", "soil_ph": 7.1, "soil_organic_carbon_pct": 1.20, "soil_salinity_ec_e": 6.0},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 85000.0, "irrigation_source": "rainfed_only", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Mungbean"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_17_JASHORE_JHIKARGACHHA",
        "name": "Jashore - Jhikargachha (High Ganges River Floodplain, AEZ 11)",
        "location": {"lat": 23.10, "lon": 89.13, "upazila": "Jhikargachha", "district": "Jashore", "division": "Khulna", "aez": 11},
        "field_conditions": {"land_type": "HL", "soil_texture": "Silt Loam", "soil_ph": 7.2, "soil_organic_carbon_pct": 1.05, "soil_salinity_ec_e": 0.8},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 125000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Cauliflower"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Jute"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_18_KUSHTIA_DAULATPUR",
        "name": "Kushtia - Daulatpur (High Ganges Floodplain Commercial, AEZ 11)",
        "location": {"lat": 24.02, "lon": 88.87, "upazila": "Daulatpur", "district": "Kushtia", "division": "Khulna", "aez": 11},
        "field_conditions": {"land_type": "HL", "soil_texture": "Sandy Loam", "soil_ph": 7.5, "soil_organic_carbon_pct": 0.80, "soil_salinity_ec_e": 0.6},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 130000.0, "irrigation_source": "shallow_tubewell", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Tobacco"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Sesame"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_19_SYLHET_GOLAPGANJ",
        "name": "Sylhet - Golapganj (Surma-Kushiyara Floodplain Acid Soil, AEZ 20)",
        "location": {"lat": 24.86, "lon": 91.97, "upazila": "Golapganj", "district": "Sylhet", "division": "Sylhet", "aez": 20},
        "field_conditions": {"land_type": "MHL", "soil_texture": "Clay Loam", "soil_ph": 4.8, "soil_organic_carbon_pct": 1.40, "soil_salinity_ec_e": 0.4},
        "farmer_priorities": {"land_size_ha": 0.40, "total_budget_bdt": 95000.0, "irrigation_source": "surface_canal", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    },
    {
        "id": "LOC_20_BANDARBAN_SADAR",
        "name": "Bandarban - Sadar (Chittagong Hill Tracts Upland Slope, AEZ 29)",
        "location": {"lat": 22.20, "lon": 92.22, "upazila": "Bandarban Sadar", "district": "Bandarban", "division": "Chattogram", "aez": 29},
        "field_conditions": {"land_type": "HL", "soil_texture": "Sandy Loam", "soil_ph": 5.2, "soil_organic_carbon_pct": 1.10, "soil_salinity_ec_e": 0.3},
        "farmer_priorities": {"land_size_ha": 0.50, "total_budget_bdt": 90000.0, "irrigation_source": "rainfed_only", "food_security_staple_needed": True},
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {"year": 1, "season": "Rabi", "crop_name": "Maize"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    }
]


def run_20_evaluations():
    engine = CropSequenceEvaluatorEngine()
    results = []

    print(f"Executing evaluations across {len(SCENARIOS_20)} diverse Bangladesh agro-ecosystems...")

    for i, scen in enumerate(SCENARIOS_20, 1):
        profile = FarmerProfile.from_dict(scen)
        res = engine.evaluate(profile)

        res_dict = res.to_dict()
        res_dict["scenario_id"] = scen["id"]
        res_dict["scenario_name"] = scen["name"]
        results.append(res_dict)

        top_swap = res.smart_swaps[0].recommended_replacement if res.smart_swaps else "None needed"
        print(
            f"[{i:02d}/20] {scen['name'][:42]:<42} | "
            f"Score: {res.overall_health_score:4.1f} ({res.grade:<2}) | "
            f"Status: {res.risk_category:<24} | "
            f"Swap: {top_swap}"
        )

    # Save complete JSON
    out_json = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "evaluator_20_places_audit.json"
    )
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved complete evaluation results to {out_json}")

    # Save Markdown Summary
    out_md = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "evaluator_20_places_summary.md"
    )
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Scientific Evaluation Audit Across 20 Diverse Bangladesh Scenarios\n\n")
        f.write("| # | Location & Agro-Ecological Zone | Evaluated Crop Sequence | Score | Grade | Diagnostic Risk Status | Key Agronomic Finding & Targeted Smart Swap |\n")
        f.write("| :- | :--- | :--- | :-: | :-: | :--- | :--- |\n")
        for i, r in enumerate(results, 1):
            seq_str = " ➔ ".join([c["crop_name"] for c in r["farmer_profile"]["farmer_evaluated_sequence"]])
            swap_str = r["smart_swaps"][0]["recommended_replacement"] if r["smart_swaps"] else "Optimal (No swap required)"
            top_issue = r["detected_issues"][0]["title"] if r["detected_issues"] else "Zero severe issues"
            f.write(
                f"| **{i:02d}** | **{r['scenario_name']}** | {seq_str} | **{r['overall_health_score']:.1f}** | "
                f"`{r['grade']}` | {r['risk_category']} | **Issue:** {top_issue}<br>**Swap:** {swap_str} |\n"
            )
    print(f"✓ Saved markdown table summary to {out_md}")


if __name__ == "__main__":
    run_20_evaluations()
