import json
import dataclasses
from src.stage3_engine import Stage3Engine

locations = [
    # Batch 1: Northern Granary, Piedmont & Tista (loc_01 to loc_08)
    {"id": "loc_01", "name": "Panchagarh Sadar, Panchagarh", "lat": 26.3353, "lon": 88.5583, "land_type": "HL", "aez": "AEZ-1 Old Himalayan Piedmont"},
    {"id": "loc_02", "name": "Birganj, Dinajpur", "lat": 25.8569, "lon": 88.6639, "land_type": "HL", "aez": "AEZ-1 Old Himalayan Piedmont"},
    {"id": "loc_03", "name": "Patgram, Lalmonirhat", "lat": 26.3533, "lon": 89.0167, "land_type": "MHL", "aez": "AEZ-2 Active Tista Floodplain"},
    {"id": "loc_04", "name": "Nageshwari, Kurigram", "lat": 25.9667, "lon": 89.6833, "land_type": "ML", "aez": "AEZ-2 Active Brahmaputra Floodplain"},
    {"id": "loc_05", "name": "Pirgachha, Rangpur", "lat": 25.5806, "lon": 89.4000, "land_type": "MHL", "aez": "AEZ-3 Tista Meander Floodplain"},
    {"id": "loc_06", "name": "Gobindaganj, Gaibandha", "lat": 25.1333, "lon": 89.3833, "land_type": "MHL", "aez": "AEZ-3 Tista Meander Floodplain"},
    {"id": "loc_07", "name": "Panchbibi, Joypurhat", "lat": 25.1958, "lon": 89.0208, "land_type": "MHL", "aez": "AEZ-25 Level Barind Tract"},
    {"id": "loc_08", "name": "Ranisankail, Thakurgaon", "lat": 25.8708, "lon": 88.2542, "land_type": "HL", "aez": "AEZ-1 Old Himalayan Piedmont"},

    # Batch 2: Barind Tract, Chalan Beel & Western Ganges (loc_09 to loc_16)
    {"id": "loc_09", "name": "Tanore, Rajshahi", "lat": 24.5833, "lon": 88.5833, "land_type": "HL", "aez": "AEZ-26 High Barind Tract"},
    {"id": "loc_10", "name": "Nachole, Chapai Nawabganj", "lat": 24.7292, "lon": 88.4167, "land_type": "HL", "aez": "AEZ-26 High Barind Tract"},
    {"id": "loc_11", "name": "Manda, Naogaon", "lat": 24.7833, "lon": 88.6667, "land_type": "ML", "aez": "AEZ-5 Lower Atrai Basin"},
    {"id": "loc_12", "name": "Gurudaspur, Natore", "lat": 24.3667, "lon": 89.2500, "land_type": "VLL", "aez": "AEZ-5 Chalan Beel Basin"},
    {"id": "loc_13", "name": "Santhia, Pabna", "lat": 24.0625, "lon": 89.5333, "land_type": "MHL", "aez": "AEZ-11 High Ganges Floodplain"},
    {"id": "loc_14", "name": "Bheramara, Kushtia", "lat": 24.0167, "lon": 88.9833, "land_type": "HL", "aez": "AEZ-11 Active Ganges Floodplain"},
    {"id": "loc_15", "name": "Damurhuda, Chuadanga", "lat": 23.6167, "lon": 88.7833, "land_type": "HL", "aez": "AEZ-11 High Ganges Floodplain"},
    {"id": "loc_16", "name": "Kaliganj, Jhenaidah", "lat": 23.4083, "lon": 89.1333, "land_type": "MHL", "aez": "AEZ-11 High Ganges Floodplain"},

    # Batch 3: Central Delta, Brahmaputra & Red Terrace (loc_17 to loc_24)
    {"id": "loc_17", "name": "Melandaha, Jamalpur", "lat": 24.9667, "lon": 89.8333, "land_type": "MHL", "aez": "AEZ-9 Old Brahmaputra Floodplain"},
    {"id": "loc_18", "name": "Nalitabari, Sherpur", "lat": 25.0833, "lon": 90.1833, "land_type": "MHL", "aez": "AEZ-22 Northern Piedmont Plain"},
    {"id": "loc_19", "name": "Muktagachha, Mymensingh", "lat": 24.7583, "lon": 90.2667, "land_type": "MHL", "aez": "AEZ-9 Old Brahmaputra Floodplain"},
    {"id": "loc_20", "name": "Belkuchi, Sirajganj", "lat": 24.2917, "lon": 89.7000, "land_type": "ML", "aez": "AEZ-10 Jamuna Floodplain"},
    {"id": "loc_21", "name": "Mirzapur, Tangail", "lat": 24.1000, "lon": 90.1000, "land_type": "HL", "aez": "AEZ-28 Madhupur Tract edge"},
    {"id": "loc_22", "name": "Kapasia, Gazipur", "lat": 24.1000, "lon": 90.5667, "land_type": "HL", "aez": "AEZ-28 Madhupur Red Terrace"},
    {"id": "loc_23", "name": "Shibchar, Madaripur", "lat": 23.3500, "lon": 90.1667, "land_type": "ML", "aez": "AEZ-12 Low Ganges Floodplain"},
    {"id": "loc_24", "name": "Bhanga, Faridpur", "lat": 23.3833, "lon": 89.9833, "land_type": "MHL", "aez": "AEZ-12 Low Ganges Floodplain"},

    # Batch 4: Haor Basin Wetlands & NE Hills (loc_25 to loc_32)
    {"id": "loc_25", "name": "Derai, Sunamganj", "lat": 24.7833, "lon": 91.3500, "land_type": "VLL", "aez": "AEZ-21 Deep Haor Basin"},
    {"id": "loc_26", "name": "Nikli, Kishoreganj", "lat": 24.3167, "lon": 90.9333, "land_type": "VLL", "aez": "AEZ-21 Central Haor Basin"},
    {"id": "loc_27", "name": "Khaliajuri, Netrokona", "lat": 24.7000, "lon": 91.1333, "land_type": "VLL", "aez": "AEZ-21 Deep Haor Wetland"},
    {"id": "loc_28", "name": "Nabiganj, Habiganj", "lat": 24.5667, "lon": 91.5167, "land_type": "LL", "aez": "AEZ-20 Kushiyara Floodplain"},
    {"id": "loc_29", "name": "Golapganj, Sylhet", "lat": 24.8667, "lon": 92.0167, "land_type": "MHL", "aez": "AEZ-20 Surma High Floodplain"},
    {"id": "loc_30", "name": "Kulaura, Moulvibazar", "lat": 24.5167, "lon": 92.0333, "land_type": "MHL", "aez": "AEZ-20 Hakaluki Haor edge"},
    {"id": "loc_31", "name": "Kamalganj, Moulvibazar", "lat": 24.3667, "lon": 91.8667, "land_type": "HL", "aez": "AEZ-29 Eastern Hilly Valley"},
    {"id": "loc_32", "name": "Durgapur, Netrokona", "lat": 25.1250, "lon": 90.6875, "land_type": "HL", "aez": "AEZ-22 Susang Piedmont Plain"},

    # Batch 5: Coastal Saline, Estuary & Hill Tracts (loc_33 to loc_40)
    {"id": "loc_33", "name": "Dacope, Khulna", "lat": 22.5722, "lon": 89.5111, "land_type": "LL", "aez": "AEZ-13 Coastal Saline Polder"},
    {"id": "loc_34", "name": "Shyamnagar, Satkhira", "lat": 22.3306, "lon": 89.1028, "land_type": "LL", "aez": "AEZ-13 Coastal High Saline"},
    {"id": "loc_35", "name": "Kalapara, Patuakhali", "lat": 21.9861, "lon": 90.2417, "land_type": "MHL", "aez": "AEZ-13 Kuakata Coastal Belt"},
    {"id": "loc_36", "name": "Amtali, Barguna", "lat": 22.1278, "lon": 90.2306, "land_type": "MHL", "aez": "AEZ-13 Coastal Tidal Floodplain"},
    {"id": "loc_37", "name": "Char Fasson, Bhola", "lat": 22.1833, "lon": 90.7167, "land_type": "MHL", "aez": "AEZ-18 Lower Meghna Estuary Island"},
    {"id": "loc_38", "name": "Subarnachar, Noakhali", "lat": 22.6500, "lon": 91.1333, "land_type": "MHL", "aez": "AEZ-18 Young Meghna Saline Char"},
    {"id": "loc_39", "name": "Hathazari, Chittagong", "lat": 22.5083, "lon": 91.8083, "land_type": "MHL", "aez": "AEZ-23 Chittagong Coastal Plain"},
    {"id": "loc_40", "name": "Teknaf, Cox's Bazar", "lat": 20.8667, "lon": 92.3000, "land_type": "HL", "aez": "AEZ-23/29 Southern Coastal Peninsular Hills"}
]

print(f"Total locations defined: {len(locations)}")
engine = Stage3Engine()

batches = [
    ("Batch 1: Northern Granary & Tista (loc_01 - loc_08)", locations[0:8], "data/scientific_audit_batch_1.json"),
    ("Batch 2: Barind Tract & Western Ganges (loc_09 - loc_16)", locations[8:16], "data/scientific_audit_batch_2.json"),
    ("Batch 3: Central Delta & Red Terrace (loc_17 - loc_24)", locations[16:24], "data/scientific_audit_batch_3.json"),
    ("Batch 4: Haor Basin Wetlands & NE Hills (loc_25 - loc_32)", locations[24:32], "data/scientific_audit_batch_4.json"),
    ("Batch 5: Coastal Saline, Estuary & Hill Tracts (loc_33 - loc_40)", locations[32:40], "data/scientific_audit_batch_5.json"),
]

for title, batch_locs, outfile in batches:
    results = []
    print(f"\nProcessing {title}...")
    for loc in batch_locs:
        res = engine.get_candidate_pools(loc["lat"], loc["lon"], loc["land_type"])
        rd = res.route_details
        print(f"  [{loc['id']}] {loc['name']} -> {rd['upazila_name']}, {rd['district_name']} | K={res.cropping_intensity_k}")
        results.append({
            "meta": loc,
            "engine_output": dataclasses.asdict(res)
        })
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved {len(results)} locations to {outfile}")

print("\nAll 5 batches successfully processed and saved!")
