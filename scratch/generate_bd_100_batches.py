"""
scratch/generate_bd_100_batches.py
Generates 100 representative agricultural test locations across Bangladesh,
distributed across 5 regional cohorts (20 locations each, exactly 2 per district).
Gracefully handles government API 500 gaps by selecting neighboring upazilas in the same district.
"""

import os
import sys
import json
import csv
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.router import SpatialRouter
from src.stage3_engine import Stage3Engine

def select_upazilas_for_cohort(target_districts: List[str], count: int, land_type_rules: Dict[str, str], engine: Stage3Engine) -> List[Dict[str, Any]]:
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "upazila_boundaries.csv")
    with open(csv_path) as f:
        all_upazilas = list(csv.DictReader(f))

    router = SpatialRouter.get_instance()
    
    # Group upazilas by district
    dist_map = {}
    for u in all_upazilas:
        d_name = u["district_name"].lower()
        if d_name not in dist_map:
            dist_map[d_name] = []
        dist_map[d_name].append(u)

    selected_results = []
    
    # We want count = 20 upazilas. With 10 districts, that is 2 per district.
    per_district_target = max(1, count // len(target_districts))
    
    for dist in target_districts:
        d_candidates = dist_map.get(dist.lower(), [])
        dist_selected = 0
        ltype = land_type_rules.get(dist.lower(), "MHL")
        
        for u in d_candidates:
            if dist_selected >= per_district_target and len(selected_results) + (len(target_districts) - target_districts.index(dist) - 1) >= count:
                break
            c_lat = round((float(u["min_lat"]) + float(u["max_lat"])) / 2.0, 4)
            c_lon = round((float(u["min_lon"]) + float(u["max_lon"])) / 2.0, 4)
            route = router.route(c_lat, c_lon)
            if not (route.is_bangladesh and route.upazila_code == u["upazila_code"]):
                continue

            try:
                # Test candidate pool generation (triggers write-through cache if not yet cached)
                res = engine.get_candidate_pools(latitude=c_lat, longitude=c_lon, land_type=ltype)
                selected_results.append({
                    "upazila_code": u["upazila_code"],
                    "upazila_name": u["upazila_name"],
                    "district_name": u["district_name"],
                    "division_name": u["division_name"],
                    "lat": c_lat,
                    "lon": c_lon,
                    "land_type": ltype,
                    "pipeline": res.pipeline,
                    "cropping_intensity_k": res.cropping_intensity_k,
                    "candidate_counts": res.candidate_counts,
                    "latency_ms": res.total_execution_ms,
                    "seasons": {
                        s_name: [
                            {
                                "crop_name": c["crop_name"],
                                "botanical_family": c.get("botanical_family"),
                                "is_legume": c.get("is_legume"),
                                "duration_days": c.get("duration_days"),
                                "effective_area_ha": c.get("effective_area"),
                                "suitability_tier": c.get("suitability_tier")
                            }
                            for c in c_list
                        ]
                        for s_name, c_list in res.seasons.items()
                    }
                })
                dist_selected += 1
                print(f"  [{u['district_name']}] {u['upazila_name']} ({ltype}) -> K={res.cropping_intensity_k}, Rabi={res.candidate_counts.get('rabi', 0)}, Kharif1={res.candidate_counts.get('kharif1', 0)}, Kharif2={res.candidate_counts.get('kharif2', 0)} ({res.total_execution_ms:.2f} ms)")
            except Exception as e:
                print(f"  [SKIP] {u['district_name']} - {u['upazila_name']} failed ({e}), trying next upazila in district...")
                continue
                
            if len(selected_results) >= count:
                break
        if len(selected_results) >= count:
            break

    # If we still need more to hit exactly count:
    if len(selected_results) < count:
        existing_codes = {x["upazila_code"] for x in selected_results}
        for dist in target_districts:
            d_candidates = dist_map.get(dist.lower(), [])
            ltype = land_type_rules.get(dist.lower(), "MHL")
            for u in d_candidates:
                if u["upazila_code"] in existing_codes:
                    continue
                c_lat = round((float(u["min_lat"]) + float(u["max_lat"])) / 2.0, 4)
                c_lon = round((float(u["min_lon"]) + float(u["max_lon"])) / 2.0, 4)
                route = router.route(c_lat, c_lon)
                if not (route.is_bangladesh and route.upazila_code == u["upazila_code"]):
                    continue
                try:
                    res = engine.get_candidate_pools(latitude=c_lat, longitude=c_lon, land_type=ltype)
                    selected_results.append({
                        "upazila_code": u["upazila_code"],
                        "upazila_name": u["upazila_name"],
                        "district_name": u["district_name"],
                        "division_name": u["division_name"],
                        "lat": c_lat,
                        "lon": c_lon,
                        "land_type": ltype,
                        "pipeline": res.pipeline,
                        "cropping_intensity_k": res.cropping_intensity_k,
                        "candidate_counts": res.candidate_counts,
                        "latency_ms": res.total_execution_ms,
                        "seasons": {
                            s_name: [
                                {
                                    "crop_name": c["crop_name"],
                                    "botanical_family": c.get("botanical_family"),
                                    "is_legume": c.get("is_legume"),
                                    "duration_days": c.get("duration_days"),
                                    "effective_area_ha": c.get("effective_area"),
                                    "suitability_tier": c.get("suitability_tier")
                                }
                                for c in c_list
                            ]
                            for s_name, c_list in res.seasons.items()
                        }
                    })
                    existing_codes.add(u["upazila_code"])
                    print(f"  [Backfill] [{u['district_name']}] {u['upazila_name']} ({ltype}) -> K={res.cropping_intensity_k}")
                    if len(selected_results) >= count:
                        break
                except Exception as e:
                    continue
            if len(selected_results) >= count:
                break

    return selected_results[:count]


def main():
    print("Generating 100 Bangladesh Agricultural Benchmark Locations across 5 Cohorts...")

    cohorts = {
        "batch01_northern_granary": {
            "title": "Batch 1: Northern Granary & Rangpur/Dinajpur Piedmont (AEZ 1, 2, 3)",
            "districts": ["Dinajpur", "Bogura", "Rangpur", "Panchagarh", "Thakurgaon", "Joypurhat", "Gaibandha", "Nilphamari", "Kurigram", "Lalmonirhat"],
            "land_types": {
                "panchagarh": "HL",
                "thakurgaon": "HL",
                "dinajpur": "HL",
                "joypurhat": "MHL",
                "bogura": "MHL",
                "rangpur": "MHL",
                "gaibandha": "MLL",
                "kurigram": "MLL",
                "lalmonirhat": "MHL",
                "nilphamari": "MHL"
            }
        },
        "batch02_northwest_barind": {
            "title": "Batch 2: Northwest Barind Tract & Western Floodplain (AEZ 11, 25, 26, 27)",
            "districts": ["Rajshahi", "Naogaon", "Nawabganj", "Natore", "Pabna", "Sirajganj", "Kushtia", "Meherpur", "Chuadanga", "Jhenaidah"],
            "land_types": {
                "rajshahi": "HL",
                "naogaon": "HL",
                "nawabganj": "HL",
                "natore": "MLL",
                "pabna": "MHL",
                "sirajganj": "MLL",
                "kushtia": "HL",
                "meherpur": "HL",
                "chuadanga": "HL",
                "jhenaidah": "MHL"
            }
        },
        "batch03_central_delta": {
            "title": "Batch 3: Central Alluvial Delta & Brahmaputra/Jamuna (AEZ 8, 9, 12, 28)",
            "districts": ["Dhaka", "Gazipur", "Manikganj", "Munshiganj", "Narayanganj", "Narsingdi", "Tangail", "Mymensingh", "Jamalpur", "Sherpur"],
            "land_types": {
                "dhaka": "MHL",
                "gazipur": "HL",
                "manikganj": "MHL",
                "munshiganj": "MLL",
                "narayanganj": "MHL",
                "narsingdi": "MHL",
                "tangail": "HL",
                "mymensingh": "MHL",
                "jamalpur": "MHL",
                "sherpur": "MHL"
            }
        },
        "batch04_northeast_haor": {
            "title": "Batch 4: Northeast Wetland Haor Basin & Surma-Kushiyara (AEZ 20, 21, 22)",
            "districts": ["Sunamganj", "Netrokona", "Kishoreganj", "Habiganj", "Sylhet", "Moulvibazar", "Brahmanbaria"],
            "land_types": {
                "sunamganj": "LL",
                "netrokona": "LL",
                "kishoreganj": "LL",
                "habiganj": "LL",
                "sylhet": "MHL",
                "moulvibazar": "MHL",
                "brahmanbaria": "MLL"
            }
        },
        "batch05_southern_coastal": {
            "title": "Batch 5: Southern Coastal Saline Belt, Meghna Estuary & Chittagong (AEZ 13, 18, 19, 23)",
            "districts": ["Khulna", "Satkhira", "Bagerhat", "Barishal", "Bhola", "Patuakhali", "Pirojpur", "Jhalakathi", "Barguna", "Noakhali"],
            "land_types": {
                "khulna": "MHL",
                "satkhira": "MHL",
                "bagerhat": "MHL",
                "barishal": "MHL",
                "bhola": "MLL",
                "patuakhali": "MLL",
                "pirojpur": "MHL",
                "jhalakathi": "MHL",
                "barguna": "MLL",
                "noakhali": "MLL"
            }
        }
    }

    engine = Stage3Engine.get_instance()
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bd_100_batches")
    os.makedirs(out_dir, exist_ok=True)

    total_generated = 0
    for batch_id, c_data in cohorts.items():
        print(f"\nProcessing {c_data['title']} (Target: 20 upazilas)...")
        upazila_entries = select_upazilas_for_cohort(c_data["districts"], 20, c_data["land_types"], engine)
        assert len(upazila_entries) == 20, f"Expected 20 upazilas for {batch_id}, got {len(upazila_entries)}"

        out_path = os.path.join(out_dir, f"{batch_id}.json")
        with open(out_path, "w") as f:
            json.dump(upazila_entries, f, indent=2)
        print(f"Successfully saved {len(upazila_entries)} locations to {out_path}")
        total_generated += len(upazila_entries)

    print(f"\nAll {total_generated} Bangladesh benchmark locations generated, verified, and cached!")

if __name__ == "__main__":
    main()
