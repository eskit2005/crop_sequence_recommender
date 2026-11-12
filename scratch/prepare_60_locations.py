import json
import dataclasses
from src.stage3_engine import Stage3Engine

# 60 brand-new, diverse locations across Bangladesh
locations_60 = [
    # -------------------------------------------------------------
    # BATCH 1: Northern Floodplains & Jamuna/Brahmaputra Chars (15 locations)
    # -------------------------------------------------------------
    {"id": "loc_01", "name": "Boda, Panchagarh", "lat": 26.2083, "lon": 88.5917, "land_type": "HL", "zone": "Old Himalayan Piedmont"},
    {"id": "loc_02", "name": "Debiganj, Panchagarh", "lat": 26.1167, "lon": 88.7583, "land_type": "HL", "zone": "Old Himalayan Piedmont"},
    {"id": "loc_03", "name": "Kaharole, Dinajpur", "lat": 25.7917, "lon": 88.6000, "land_type": "HL", "zone": "Old Himalayan Piedmont"},
    {"id": "loc_04", "name": "Nawabganj, Dinajpur", "lat": 25.4167, "lon": 89.0833, "land_type": "MHL", "zone": "Level Barind Tract"},
    {"id": "loc_05", "name": "Dimla, Nilphamari", "lat": 26.1250, "lon": 88.9333, "land_type": "MHL", "zone": "Active Tista Floodplain"},
    {"id": "loc_06", "name": "Jaldhaka, Nilphamari", "lat": 26.0167, "lon": 89.0250, "land_type": "MHL", "zone": "Tista Meander Floodplain"},
    {"id": "loc_07", "name": "Hatibandha, Lalmonirhat", "lat": 26.1167, "lon": 89.1333, "land_type": "MHL", "zone": "Tista Floodplain"},
    {"id": "loc_08", "name": "Aditmari, Lalmonirhat", "lat": 25.9167, "lon": 89.3500, "land_type": "MHL", "zone": "Tista Floodplain"},
    {"id": "loc_09", "name": "Chilmari, Kurigram", "lat": 25.5500, "lon": 89.6667, "land_type": "ML", "zone": "Active Brahmaputra Char"},
    {"id": "loc_10", "name": "Rowmari, Kurigram", "lat": 25.5667, "lon": 89.8500, "land_type": "ML", "zone": "Active Brahmaputra River Char"},
    {"id": "loc_11", "name": "Badarganj, Rangpur", "lat": 25.6750, "lon": 89.0500, "land_type": "MHL", "zone": "Tista Meander Floodplain"},
    {"id": "loc_12", "name": "Palashbari, Gaibandha", "lat": 25.2833, "lon": 89.3500, "land_type": "MHL", "zone": "Tista Meander Floodplain"},
    {"id": "loc_13", "name": "Sariakandi, Bogura", "lat": 24.8833, "lon": 89.5667, "land_type": "ML", "zone": "Active Jamuna River Char"},
    {"id": "loc_14", "name": "Kazipur, Sirajganj", "lat": 24.6667, "lon": 89.6500, "land_type": "ML", "zone": "Jamuna Riverine Char"},
    {"id": "loc_15", "name": "Chauhali, Sirajganj", "lat": 24.2167, "lon": 89.7167, "land_type": "ML", "zone": "Jamuna Active Charland"},

    # -------------------------------------------------------------
    # BATCH 2: Barind Tract & Western Border High Floodplain (15 locations)
    # -------------------------------------------------------------
    {"id": "loc_16", "name": "Paba, Rajshahi", "lat": 24.4333, "lon": 88.6167, "land_type": "HL", "zone": "High Barind Tract"},
    {"id": "loc_17", "name": "Durgapur, Rajshahi", "lat": 24.4583, "lon": 88.7667, "land_type": "HL", "zone": "High Barind Tract"},
    {"id": "loc_18", "name": "Gomastapur, Chapai Nawabganj", "lat": 24.7750, "lon": 88.2833, "land_type": "HL", "zone": "High Barind Drought Tract"},
    {"id": "loc_19", "name": "Shibganj, Chapai Nawabganj", "lat": 24.6833, "lon": 88.1667, "land_type": "HL", "zone": "Ganges Alluvial / Barind"},
    {"id": "loc_20", "name": "Porsha, Naogaon", "lat": 25.0250, "lon": 88.4833, "land_type": "HL", "zone": "High Barind Red Clay"},
    {"id": "loc_21", "name": "Niamatpur, Naogaon", "lat": 24.8583, "lon": 88.5667, "land_type": "HL", "zone": "High Barind Tract"},
    {"id": "loc_22", "name": "Badalgachhi, Naogaon", "lat": 24.9667, "lon": 88.9000, "land_type": "MHL", "zone": "Little Jamuna Floodplain"},
    {"id": "loc_23", "name": "Baraigram, Natore", "lat": 24.3167, "lon": 89.1667, "land_type": "MHL", "zone": "Chalan Beel Terrace Edge"},
    {"id": "loc_24", "name": "Chatmohar, Pabna", "lat": 24.2250, "lon": 89.2833, "land_type": "ML", "zone": "Chalan Beel Depression"},
    {"id": "loc_25", "name": "Sujanagar, Pabna", "lat": 23.9167, "lon": 89.6500, "land_type": "MHL", "zone": "Active Ganges Floodplain"},
    {"id": "loc_26", "name": "Kumarkhali, Kushtia", "lat": 23.8667, "lon": 89.2500, "land_type": "HL", "zone": "High Ganges River Floodplain"},
    {"id": "loc_27", "name": "Alamdanga, Chuadanga", "lat": 23.7583, "lon": 88.9500, "land_type": "HL", "zone": "High Ganges Floodplain"},
    {"id": "loc_28", "name": "Jibannagar, Chuadanga", "lat": 23.4167, "lon": 88.8167, "land_type": "HL", "zone": "Western Border Alluvial"},
    {"id": "loc_29", "name": "Kotchandpur, Jhenaidah", "lat": 23.4000, "lon": 89.0167, "land_type": "MHL", "zone": "High Ganges Meander"},
    {"id": "loc_30", "name": "Bagherpara, Jashore", "lat": 23.2167, "lon": 89.3500, "land_type": "MHL", "zone": "Ganges Tidal / High Floodplain"},

    # -------------------------------------------------------------
    # BATCH 3: Central Delta, Mymensingh & Haor Wetlands (15 locations)
    # -------------------------------------------------------------
    {"id": "loc_31", "name": "Islampur, Jamalpur", "lat": 25.0833, "lon": 89.7833, "land_type": "MHL", "zone": "Old Brahmaputra Alluvial"},
    {"id": "loc_32", "name": "Nakla, Sherpur", "lat": 24.9833, "lon": 90.1833, "land_type": "MHL", "zone": "Old Brahmaputra Floodplain"},
    {"id": "loc_33", "name": "Phulpur, Mymensingh", "lat": 24.9500, "lon": 90.3500, "land_type": "MHL", "zone": "Old Brahmaputra Basin"},
    {"id": "loc_34", "name": "Gaffargaon, Mymensingh", "lat": 24.4333, "lon": 90.5500, "land_type": "MHL", "zone": "Old Brahmaputra Floodplain"},
    {"id": "loc_35", "name": "Bhuapur, Tangail", "lat": 24.4667, "lon": 89.8667, "land_type": "ML", "zone": "Jamuna Riverine Plain"},
    {"id": "loc_36", "name": "Ghatail, Tangail", "lat": 24.5000, "lon": 90.0000, "land_type": "HL", "zone": "Madhupur Red Terrace"},
    {"id": "loc_37", "name": "Sreepur, Gazipur", "lat": 24.2000, "lon": 90.4833, "land_type": "HL", "zone": "Madhupur Tract"},
    {"id": "loc_38", "name": "Raipura, Narsingdi", "lat": 23.9833, "lon": 90.8667, "land_type": "MHL", "zone": "Meghna Floodplain"},
    {"id": "loc_39", "name": "Dharmapasha, Sunamganj", "lat": 25.0833, "lon": 91.0167, "land_type": "VLL", "zone": "Deep Haor Depression (Hakaluki/Tanguar)"},
    {"id": "loc_40", "name": "Shalla, Sunamganj", "lat": 24.6333, "lon": 91.2333, "land_type": "VLL", "zone": "Deep Haor Basin"},
    {"id": "loc_41", "name": "Jagannathpur, Sunamganj", "lat": 24.7667, "lon": 91.5333, "land_type": "LL", "zone": "Sylhet Haor Depression"},
    {"id": "loc_42", "name": "Itna, Kishoreganj", "lat": 24.5333, "lon": 91.0833, "land_type": "VLL", "zone": "Deep Haor Basin"},
    {"id": "loc_43", "name": "Mithamain, Kishoreganj", "lat": 24.4333, "lon": 91.0500, "land_type": "VLL", "zone": "Deep Haor Basin"},
    {"id": "loc_44", "name": "Austagram, Kishoreganj", "lat": 24.2667, "lon": 91.1167, "land_type": "VLL", "zone": "Deep Haor Basin"},
    {"id": "loc_45", "name": "Mohanganj, Netrokona", "lat": 24.8667, "lon": 90.9667, "land_type": "VLL", "zone": "Ganges-Surma Haor Edge"},

    # -------------------------------------------------------------
    # BATCH 4: Coastal Saline, Southern Estuary & Hill Tracts (15 locations)
    # -------------------------------------------------------------
    {"id": "loc_46", "name": "Paikgachha, Khulna", "lat": 22.5833, "lon": 89.3333, "land_type": "LL", "zone": "Coastal Saline Polder / Gher"},
    {"id": "loc_47", "name": "Koyra, Khulna", "lat": 22.3417, "lon": 89.3000, "land_type": "LL", "zone": "Sundarbans Coastal High Saline"},
    {"id": "loc_48", "name": "Assasuni, Satkhira", "lat": 22.5500, "lon": 89.1667, "land_type": "LL", "zone": "Coastal Saline Polder"},
    {"id": "loc_49", "name": "Kaliganj, Satkhira", "lat": 22.4500, "lon": 89.0333, "land_type": "LL", "zone": "Coastal Saline Shrimp Gher"},
    {"id": "loc_50", "name": "Morrelganj, Bagerhat", "lat": 22.4500, "lon": 89.8500, "land_type": "LL", "zone": "Coastal Tidal Mangrove Saline"},
    {"id": "loc_51", "name": "Sarankhola, Bagerhat", "lat": 22.2833, "lon": 89.7833, "land_type": "LL", "zone": "Sundarbans Border Saline Polder"},
    {"id": "loc_52", "name": "Galachipa, Patuakhali", "lat": 22.1667, "lon": 90.4167, "land_type": "MHL", "zone": "Ganges Tidal Floodplain"},
    {"id": "loc_53", "name": "Patharghata, Barguna", "lat": 22.0500, "lon": 89.9667, "land_type": "MHL", "zone": "Coastal Estuarine Coastline"},
    {"id": "loc_54", "name": "Lalmohan, Bhola", "lat": 22.3333, "lon": 90.7333, "land_type": "MHL", "zone": "Lower Meghna Estuary Island"},
    {"id": "loc_55", "name": "Manpura, Bhola", "lat": 22.3000, "lon": 91.0000, "land_type": "MHL", "zone": "Isolated Bay of Bengal Island"},
    {"id": "loc_56", "name": "Hatiya, Noakhali", "lat": 22.3667, "lon": 91.1250, "land_type": "MHL", "zone": "Lower Meghna Delta Island"},
    {"id": "loc_57", "name": "Mirsharai, Chittagong", "lat": 22.7667, "lon": 91.5667, "land_type": "MHL", "zone": "Chittagong Coastal Plain"},
    {"id": "loc_58", "name": "Anwara, Chittagong", "lat": 22.2167, "lon": 91.9167, "land_type": "MHL", "zone": "Karnafuli Estuarine Plain"},
    {"id": "loc_59", "name": "Chakaria, Cox's Bazar", "lat": 21.7833, "lon": 92.0833, "land_type": "MHL", "zone": "Matamuhuri Coastal Delta"},
    {"id": "loc_60", "name": "Khagrachhari Sadar, Khagrachhari", "lat": 23.1167, "lon": 91.9833, "land_type": "HL", "zone": "Chittagong Hill Tracts Valleys"}
]

print(f"Total new locations defined: {len(locations_60)}")
engine = Stage3Engine()

batches = [
    ("Batch 1: Northern Floodplains & Jamuna Chars (loc_01 - loc_15)", locations_60[0:15], "data/scientific_audit_60_batch_1.json"),
    ("Batch 2: Barind Tract & Western Border (loc_16 - loc_30)", locations_60[15:30], "data/scientific_audit_60_batch_2.json"),
    ("Batch 3: Central Delta, Mymensingh & Haor Wetlands (loc_31 - loc_45)", locations_60[30:45], "data/scientific_audit_60_batch_3.json"),
    ("Batch 4: Coastal Saline, Estuary & Hill Tracts (loc_46 - loc_60)", locations_60[45:60], "data/scientific_audit_60_batch_4.json"),
]

for title, batch_locs, outfile in batches:
    results = []
    print(f"\nProcessing {title}...")
    for loc in batch_locs:
        res = engine.get_candidate_pools(loc["lat"], loc["lon"], loc["land_type"])
        rd = res.route_details
        env = res.environmental_metadata
        print(f"  [{loc['id']}] {loc['name']} -> {rd['upazila_name']}, {rd['district_name']} | K={res.cropping_intensity_k} | Haor={env.get('is_haor_wetland')} | Saline={env.get('is_coastal_saline')}")
        results.append({
            "meta": loc,
            "engine_output": dataclasses.asdict(res)
        })
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved {len(results)} locations to {outfile}")

print("\nAll 60 locations successfully generated and saved into 4 batch files!")
