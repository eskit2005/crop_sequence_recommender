import json
import os
import sys
import dataclasses

from src.stage3_engine import Stage3Engine

batch_a_locations = [
    {"id": "loc_01", "name": "Thakurgaon Sadar, Thakurgaon", "lat": 26.0302, "lon": 88.4690, "land_type": "HL", "zone": "Dinajpur Piedmont Plain"},
    {"id": "loc_02", "name": "Domar, Nilphamari", "lat": 26.1000, "lon": 88.8333, "land_type": "MHL", "zone": "Tista Floodplain / North Maize-Tobacco"},
    {"id": "loc_03", "name": "Shibganj, Bogura", "lat": 24.9833, "lon": 89.3167, "land_type": "MHL", "zone": "Karatoya-Bangali / Vegetable-Potato Hub"},
    {"id": "loc_04", "name": "Godagari, Rajshahi", "lat": 24.4667, "lon": 88.3300, "land_type": "HL", "zone": "High Barind Tract"},
    {"id": "loc_05", "name": "Singra, Natore", "lat": 24.5000, "lon": 89.1500, "land_type": "VLL", "zone": "Chalan Beel Deep Wetland"},
    {"id": "loc_06", "name": "Ishwardi, Pabna", "lat": 24.1292, "lon": 89.0667, "land_type": "HL", "zone": "Active Ganges Floodplain"},
    {"id": "loc_07", "name": "Meherpur Sadar, Meherpur", "lat": 23.7667, "lon": 88.6333, "land_type": "MHL", "zone": "Meander Floodplain / Winter Veg"},
    {"id": "loc_08", "name": "Jashore Sadar, Jashore", "lat": 23.1667, "lon": 89.2167, "land_type": "MHL", "zone": "Commercial Flower & Veg Belt"},
    {"id": "loc_09", "name": "Kushtia Sadar, Kushtia", "lat": 23.9000, "lon": 89.1200, "land_type": "HL", "zone": "Ganges High Floodplain"},
    {"id": "loc_10", "name": "Sirajganj Sadar, Sirajganj", "lat": 24.4577, "lon": 89.7081, "land_type": "ML", "zone": "Jamuna Riverine Charlands"},
]

batch_b_locations = [
    {"id": "loc_11", "name": "Singair, Manikganj", "lat": 23.8167, "lon": 90.1500, "land_type": "MHL", "zone": "Dhaleshwari / Peri-urban Vegetable"},
    {"id": "loc_12", "name": "Madhupur, Tangail", "lat": 24.6167, "lon": 90.0333, "land_type": "HL", "zone": "Madhupur Tract (Red Soil)"},
    {"id": "loc_13", "name": "Trishal, Mymensingh", "lat": 24.5833, "lon": 90.4000, "land_type": "MHL", "zone": "Old Brahmaputra Alluvial"},
    {"id": "loc_14", "name": "Tahirpur, Sunamganj", "lat": 25.0833, "lon": 91.1833, "land_type": "VLL", "zone": "Deep Haor Wetland (Tanguar)"},
    {"id": "loc_15", "name": "Sreemangal, Moulvibazar", "lat": 24.3069, "lon": 91.7333, "land_type": "HL", "zone": "Northern & Eastern Hills / Valley"},
    {"id": "loc_16", "name": "Dumuria, Khulna", "lat": 22.8083, "lon": 89.4250, "land_type": "ML", "zone": "Coastal Saline Gher Dyke"},
    {"id": "loc_17", "name": "Mongla, Bagerhat", "lat": 22.4833, "lon": 89.6000, "land_type": "LL", "zone": "Coastal Saline Polder"},
    {"id": "loc_18", "name": "Bhola Sadar, Bhola", "lat": 22.6858, "lon": 90.6433, "land_type": "MHL", "zone": "Lower Meghna Estuary Island"},
    {"id": "loc_19", "name": "Babuganj, Barishal", "lat": 22.8000, "lon": 90.3167, "land_type": "MHL", "zone": "Non-saline Tidal Floodplain"},
    {"id": "loc_20", "name": "Bandarban Sadar, Bandarban", "lat": 22.1953, "lon": 92.2184, "land_type": "HL", "zone": "Chittagong Hill Tracts"},
]

def run_batch(engine, locations, output_file):
    results = []
    for loc in locations:
        res = engine.get_candidate_pools(loc["lat"], loc["lon"], loc["land_type"])
        results.append({
            "meta": loc,
            "engine_output": dataclasses.asdict(res)
        })
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} locations to {output_file}")

engine = Stage3Engine()
run_batch(engine, batch_a_locations, "data/web_audit_batch_a.json")
run_batch(engine, batch_b_locations, "data/web_audit_batch_b.json")
