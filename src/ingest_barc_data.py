"""
Data Ingestion & Local Database Builder for Crop Sequence Recommender (Step 1)
-----------------------------------------------------------------------------
Harvests official agricultural boundaries and crop suitability data from BARC
(dashboard.cropzoning.gov.bd) and builds an offline SQLite database and CSV files.
"""

import urllib.request
import json
import sqlite3
import csv
import os
import ssl
import sys

# SSL context for government endpoints
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://dashboard.cropzoning.gov.bd"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}

# Agronomic metadata mapping for major Bangladesh crops
CROP_AGRONOMIC_METADATA = {
    "potato":       {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 90,  "yield_ton_ha": 25.0, "land_types": "HL,MHL"},
    "sweet potato": {"family": "Convolvulaceae", "root": "shallow",        "is_legume": False, "duration": 120, "yield_ton_ha": 18.0, "land_types": "HL,MHL"},
    "mustard":      {"family": "Brassicaceae",   "root": "medium_tap",     "is_legume": False, "duration": 80,  "yield_ton_ha": 1.5,  "land_types": "HL,MHL"},
    "lentil":       {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 105, "yield_ton_ha": 1.2,  "land_types": "HL,MHL"},
    "grass pea":    {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 110, "yield_ton_ha": 1.3,  "land_types": "HL,MHL,MLL"},
    "khesari":      {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 110, "yield_ton_ha": 1.3,  "land_types": "HL,MHL,MLL"},
    "chickpea":     {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 115, "yield_ton_ha": 1.4,  "land_types": "HL,MHL"},
    "wheat":        {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 110, "yield_ton_ha": 4.0,  "land_types": "HL,MHL"},
    "maize":        {"family": "Poaceae",        "root": "deep_fibrous",   "is_legume": False, "duration": 130, "yield_ton_ha": 7.5,  "land_types": "HL,MHL"},
    "boro dhan":    {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 145, "yield_ton_ha": 6.5,  "land_types": "MLL,LL"},
    "brinjal":      {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 120, "yield_ton_ha": 20.0, "land_types": "HL,MHL"},
    "tomato":       {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 100, "yield_ton_ha": 35.0, "land_types": "HL,MHL"},
    "chilli":       {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 110, "yield_ton_ha": 2.2,  "land_types": "HL,MHL"},
    "cabbage":      {"family": "Brassicaceae",   "root": "shallow",        "is_legume": False, "duration": 85,  "yield_ton_ha": 30.0, "land_types": "HL,MHL"},
    "cauliflower":  {"family": "Brassicaceae",   "root": "shallow",        "is_legume": False, "duration": 85,  "yield_ton_ha": 25.0, "land_types": "HL,MHL"},
    "broccoli":     {"family": "Brassicaceae",   "root": "shallow",        "is_legume": False, "duration": 80,  "yield_ton_ha": 18.0, "land_types": "HL,MHL"},
    "onion":        {"family": "Amaryllidaceae", "root": "shallow",        "is_legume": False, "duration": 100, "yield_ton_ha": 12.0, "land_types": "HL,MHL"},
    "garlic":       {"family": "Amaryllidaceae", "root": "shallow",        "is_legume": False, "duration": 120, "yield_ton_ha": 7.0,  "land_types": "HL,MHL"},
    "coriander":    {"family": "Apiaceae",       "root": "shallow",        "is_legume": False, "duration": 70,  "yield_ton_ha": 1.5,  "land_types": "HL,MHL"},
    "linseed":      {"family": "Linaceae",       "root": "medium_tap",     "is_legume": False, "duration": 95,  "yield_ton_ha": 1.0,  "land_types": "HL,MHL"},
    "sunflower":    {"family": "Asteraceae",     "root": "deep_tap",       "is_legume": False, "duration": 100, "yield_ton_ha": 2.0,  "land_types": "HL,MHL"},
    "jute":         {"family": "Malvaceae",      "root": "deep_tap",       "is_legume": False, "duration": 115, "yield_ton_ha": 3.2,  "land_types": "HL,MHL,MLL"},
    "kenaf":        {"family": "Malvaceae",      "root": "deep_tap",       "is_legume": False, "duration": 120, "yield_ton_ha": 3.5,  "land_types": "HL,MHL,MLL"},
    "mungbean":     {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 65,  "yield_ton_ha": 1.4,  "land_types": "HL,MHL"},
    "sesame":       {"family": "Pedaliaceae",    "root": "medium_tap",     "is_legume": False, "duration": 90,  "yield_ton_ha": 1.1,  "land_types": "HL,MHL"},
    "t. aus":       {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 105, "yield_ton_ha": 3.5,  "land_types": "HL,MHL"},
    "b. aus":       {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 100, "yield_ton_ha": 2.8,  "land_types": "MHL,MLL"},
    "t. aman":      {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 127, "yield_ton_ha": 6.5,  "land_types": "MHL,MLL"},
    "b. aman":      {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 180, "yield_ton_ha": 2.5,  "land_types": "MLL,LL"},
    "black gram":   {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 70,  "yield_ton_ha": 1.0,  "land_types": "HL,MHL"},
    "mashkalai":    {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 70,  "yield_ton_ha": 1.0,  "land_types": "HL,MHL"},
    "cotton":       {"family": "Malvaceae",      "root": "deep_tap",       "is_legume": False, "duration": 160, "yield_ton_ha": 2.5,  "land_types": "HL,MHL"},
    "ash gourd":    {"family": "Cucurbitaceae",  "root": "shallow",        "is_legume": False, "duration": 90,  "yield_ton_ha": 22.0, "land_types": "HL,MHL"},
    "pumpkin":      {"family": "Cucurbitaceae",  "root": "shallow",        "is_legume": False, "duration": 110, "yield_ton_ha": 25.0, "land_types": "HL,MHL"}
}

def get_agronomic_info(crop_name):
    clean = crop_name.lower().split("(")[0].strip()
    for key, val in CROP_AGRONOMIC_METADATA.items():
        if key in clean:
            return val
    return {
        "family": "Other",
        "root": "medium",
        "is_legume": False,
        "duration": 100,
        "yield_ton_ha": 5.0,
        "land_types": "HL,MHL"
    }

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def init_database(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS upazila_boundaries (
        upazila_code VARCHAR(10) PRIMARY KEY,
        upazila_name VARCHAR(100),
        district_name VARCHAR(100),
        division_name VARCHAR(100),
        min_lat REAL,
        max_lat REAL,
        min_lon REAL,
        max_lon REAL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS upazila_suitable_crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upazila_code VARCHAR(10),
        crop_id INTEGER,
        crop_name VARCHAR(100),
        season VARCHAR(20),
        very_suitable_ha REAL,
        suitable_ha REAL,
        mod_suitable_ha REAL,
        effective_area REAL,
        suitability_tier VARCHAR(20),
        allowable_land_types VARCHAR(50),
        botanical_family VARCHAR(50),
        root_type VARCHAR(30),
        is_legume BOOLEAN,
        duration_days INTEGER,
        yield_ton_ha REAL,
        source VARCHAR(50) DEFAULT 'BARC_CZIS_GOV',
        UNIQUE(upazila_code, crop_id, season)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_crop_upz ON upazila_suitable_crops (upazila_code, season);")
    conn.commit()
    conn.close()

def extract_bbox_from_geometry(geom):
    coords = geom.get("coordinates", [])
    all_lons = []
    all_lats = []
    
    def recurse(pt_list):
        if len(pt_list) == 2 and isinstance(pt_list[0], (int, float)) and isinstance(pt_list[1], (int, float)):
            all_lons.append(pt_list[0])
            all_lats.append(pt_list[1])
        elif isinstance(pt_list, list):
            for sub in pt_list:
                recurse(sub)
                
    recurse(coords)
    if not all_lons:
        return 0.0, 0.0, 0.0, 0.0
    return min(all_lats), max(all_lats), min(all_lons), max(all_lons)

def harvest_upazila_boundaries(db_path, csv_path):
    print("[1/2] Harvesting official Upazila boundary GIS polygons from BARC...")
    url = f"{BASE_URL}/api/dashboard/polygon-list/3"
    data = fetch_json(url)
    features = data.get("features", [])
    print(f"      Successfully downloaded {len(features)} Upazila boundary polygons.")
    
    rows = []
    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {})
        code = str(props.get("geocode") or props.get("area_code") or props.get("upz_code") or props.get("id") or "")
        name = props.get("upazila") or props.get("name") or "Unknown"
        dist = props.get("district") or props.get("dist_name") or "Unknown"
        div = props.get("division") or props.get("div_name") or "Unknown"
        
        min_lat, max_lat, min_lon, max_lon = extract_bbox_from_geometry(geom)
        
        rows.append({
            "upazila_code": code,
            "upazila_name": name,
            "district_name": dist,
            "division_name": div,
            "min_lat": round(min_lat, 4),
            "max_lat": round(max_lat, 4),
            "min_lon": round(min_lon, 4),
            "max_lon": round(max_lon, 4)
        })
        
    # Write to CSV
    fields = ["upazila_code", "upazila_name", "district_name", "division_name", "min_lat", "max_lat", "min_lon", "max_lon"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"      Saved {len(rows)} boundary bounding boxes to: {csv_path}")
    
    # Save to SQLite
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for r in rows:
        cur.execute("""
            INSERT OR REPLACE INTO upazila_boundaries 
            (upazila_code, upazila_name, district_name, division_name, min_lat, max_lat, min_lon, max_lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (r["upazila_code"], r["upazila_name"], r["district_name"], r["division_name"], r["min_lat"], r["max_lat"], r["min_lon"], r["max_lon"]))
    conn.commit()
    conn.close()
    return rows

def harvest_crop_suitability_batch(upazila_codes, db_path, csv_path):
    print(f"[2/2] Harvesting official crop suitability records for {len(upazila_codes)} target Upazilas...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    all_cleaned = []
    
    for code in upazila_codes:
        url = f"{BASE_URL}/czis/suitable/area/upazila/{code}"
        try:
            raw_suit = fetch_json(url)
        except Exception as e:
            print(f"      Warning: Upazila {code} query failed: {e}")
            continue
            
        print(f"      Upazila {code}: Received {len(raw_suit)} crop assessments.")
        
        for r in raw_suit:
            vs = float(r.get("vs") or 0)
            s = float(r.get("s") or 0)
            ms = float(r.get("ms") or 0)
            
            eff_area = round(vs + (0.70 * s), 1)
            if eff_area == 0 and ms == 0:
                continue
                
            tier = "Ideal" if vs > 0 else ("Suitable" if s > 0 else "Marginal")
            cname = r.get("crop_name", "").split("(")[0].strip()
            agro = get_agronomic_info(cname)
            
            rec = {
                "upazila_code": str(code),
                "crop_id": r.get("crop_id"),
                "crop_name": cname,
                "season": r.get("crop_season"),
                "very_suitable_ha": vs,
                "suitable_ha": s,
                "mod_suitable_ha": ms,
                "effective_area": eff_area,
                "suitability_tier": tier,
                "allowable_land_types": agro["land_types"],
                "botanical_family": agro["family"],
                "root_type": agro["root"],
                "is_legume": 1 if agro["is_legume"] else 0,
                "duration_days": agro["duration"],
                "yield_ton_ha": agro["yield_ton_ha"],
                "source": "BARC_CZIS_GOV"
            }
            all_cleaned.append(rec)
            
            cur.execute("""
                INSERT OR REPLACE INTO upazila_suitable_crops 
                (upazila_code, crop_id, crop_name, season, very_suitable_ha, suitable_ha, mod_suitable_ha, 
                 effective_area, suitability_tier, allowable_land_types, botanical_family, root_type, 
                 is_legume, duration_days, yield_ton_ha, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec["upazila_code"], rec["crop_id"], rec["crop_name"], rec["season"],
                rec["very_suitable_ha"], rec["suitable_ha"], rec["mod_suitable_ha"],
                rec["effective_area"], rec["suitability_tier"], rec["allowable_land_types"],
                rec["botanical_family"], rec["root_type"], rec["is_legume"],
                rec["duration_days"], rec["yield_ton_ha"], rec["source"]
            ))
            
    conn.commit()
    conn.close()
    
    # Export master CSV
    fields = [
        "upazila_code", "crop_id", "crop_name", "season", "very_suitable_ha", "suitable_ha",
        "mod_suitable_ha", "effective_area", "suitability_tier", "allowable_land_types",
        "botanical_family", "root_type", "is_legume", "duration_days", "yield_ton_ha", "source"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_cleaned)
        
    print(f"      Saved {len(all_cleaned)} total crop records to: {csv_path}")
    print(f"      SQLite Database updated: {db_path}")

def run_step1(output_dir):
    data_dir = os.path.join(output_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    db_file = os.path.join(data_dir, "crop_recommender.db")
    boundary_csv = os.path.join(data_dir, "upazila_boundaries.csv")
    crops_csv = os.path.join(data_dir, "suitable_crops_master.csv")
    
    init_database(db_file)
    harvest_upazila_boundaries(db_file, boundary_csv)
    
    # Initial seed harvest of diverse representative Upazilas across Bangladesh:
    # Manikganj (Central), Adamdighi (Bogura), Agailjhara (Barishal),
    # Shyamnagar (Satkhira Saline), Rowmari (Kurigram Char), Dacope (Khulna), Dowarabazar (Sunamganj)
    sample_upazilas = ["305646", "501006", "100602", "408786", "554977", "404730", "609033"]
    harvest_crop_suitability_batch(sample_upazilas, db_file, crops_csv)
    
    print("\n✅ STEP 1 COMPLETED SUCCESSFULLY!")
    print(f"• Boundaries CSV: {boundary_csv}")
    print(f"• Master Crops CSV: {crops_csv}")
    print(f"• SQLite Database: {db_file}")

if __name__ == "__main__":
    project_root = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender"
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    run_step1(project_root)
