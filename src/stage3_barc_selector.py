"""
stage3_barc_selector.py - Stage 3 Candidate Pool Generator for Bangladesh
Retrieves BARC CZIS suitability matrices with Option A write-through SQLite caching,
applies biological land-type anoxia exclusions, and runs 3-Tier dynamic bucketing.
"""

import sqlite3
import urllib.request
import ssl
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Agronomic metadata mapping for Bangladesh crops
CROP_AGRONOMIC_METADATA = {
    "potato":       {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 90,  "yield_ton_ha": 25.0, "land_types": ["HL", "MHL"]},
    "sweet potato": {"family": "Convolvulaceae", "root": "shallow",        "is_legume": False, "duration": 120, "yield_ton_ha": 18.0, "land_types": ["HL", "MHL"]},
    "mustard":      {"family": "Brassicaceae",   "root": "medium_tap",     "is_legume": False, "duration": 80,  "yield_ton_ha": 1.5,  "land_types": ["HL", "MHL"]},
    "lentil":       {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 105, "yield_ton_ha": 1.2,  "land_types": ["HL", "MHL"]},
    "grass pea":    {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 110, "yield_ton_ha": 1.3,  "land_types": ["HL", "MHL", "MLL"]},
    "khesari":      {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 110, "yield_ton_ha": 1.3,  "land_types": ["HL", "MHL", "MLL"]},
    "chickpea":     {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 115, "yield_ton_ha": 1.4,  "land_types": ["HL", "MHL"]},
    "wheat":        {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 110, "yield_ton_ha": 4.0,  "land_types": ["HL", "MHL"]},
    "maize":        {"family": "Poaceae",        "root": "deep_fibrous",   "is_legume": False, "duration": 130, "yield_ton_ha": 7.5,  "land_types": ["HL", "MHL"]},
    "boro dhan":    {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 145, "yield_ton_ha": 6.5,  "land_types": ["MLL", "LL", "VLL"]},
    "brinjal":      {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 120, "yield_ton_ha": 20.0, "land_types": ["HL", "MHL"]},
    "tomato":       {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 100, "yield_ton_ha": 35.0, "land_types": ["HL", "MHL"]},
    "chilli":       {"family": "Solanaceae",     "root": "shallow",        "is_legume": False, "duration": 110, "yield_ton_ha": 2.2,  "land_types": ["HL", "MHL"]},
    "cabbage":      {"family": "Brassicaceae",   "root": "shallow",        "is_legume": False, "duration": 85,  "yield_ton_ha": 30.0, "land_types": ["HL", "MHL"]},
    "cauliflower":  {"family": "Brassicaceae",   "root": "shallow",        "is_legume": False, "duration": 85,  "yield_ton_ha": 25.0, "land_types": ["HL", "MHL"]},
    "broccoli":     {"family": "Brassicaceae",   "root": "shallow",        "is_legume": False, "duration": 80,  "yield_ton_ha": 18.0, "land_types": ["HL", "MHL"]},
    "onion":        {"family": "Amaryllidaceae", "root": "shallow",        "is_legume": False, "duration": 100, "yield_ton_ha": 12.0, "land_types": ["HL", "MHL"]},
    "garlic":       {"family": "Amaryllidaceae", "root": "shallow",        "is_legume": False, "duration": 120, "yield_ton_ha": 7.0,  "land_types": ["HL", "MHL"]},
    "coriander":    {"family": "Apiaceae",       "root": "shallow",        "is_legume": False, "duration": 70,  "yield_ton_ha": 1.5,  "land_types": ["HL", "MHL"]},
    "linseed":      {"family": "Linaceae",       "root": "medium_tap",     "is_legume": False, "duration": 95,  "yield_ton_ha": 1.0,  "land_types": ["HL", "MHL"]},
    "sunflower":    {"family": "Asteraceae",     "root": "deep_tap",       "is_legume": False, "duration": 100, "yield_ton_ha": 2.0,  "land_types": ["HL", "MHL"]},
    "jute":         {"family": "Malvaceae",      "root": "deep_tap",       "is_legume": False, "duration": 115, "yield_ton_ha": 3.2,  "land_types": ["HL", "MHL", "MLL"]},
    "kenaf":        {"family": "Malvaceae",      "root": "deep_tap",       "is_legume": False, "duration": 120, "yield_ton_ha": 3.5,  "land_types": ["HL", "MHL", "MLL"]},
    "mungbean":     {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 65,  "yield_ton_ha": 1.4,  "land_types": ["HL", "MHL"]},
    "sesame":       {"family": "Pedaliaceae",    "root": "medium_tap",     "is_legume": False, "duration": 90,  "yield_ton_ha": 1.1,  "land_types": ["HL", "MHL"]},
    "t. aus":       {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 105, "yield_ton_ha": 3.5,  "land_types": ["HL", "MHL", "MLL"]},
    "aus dhan":     {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 105, "yield_ton_ha": 3.5,  "land_types": ["HL", "MHL", "MLL"]},
    "t. aman":      {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 135, "yield_ton_ha": 4.5,  "land_types": ["MHL", "MLL"]},
    "aman dhan":    {"family": "Poaceae",        "root": "shallow_fibrous","is_legume": False, "duration": 135, "yield_ton_ha": 4.5,  "land_types": ["MHL", "MLL"]},
    "blackgram":    {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 75,  "yield_ton_ha": 1.2,  "land_types": ["HL", "MHL"]},
    "black gram":   {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 75,  "yield_ton_ha": 1.2,  "land_types": ["HL", "MHL"]},
    "cotton":       {"family": "Malvaceae",      "root": "deep_tap",       "is_legume": False, "duration": 150, "yield_ton_ha": 2.2,  "land_types": ["HL", "MHL"]},
    "bottle gourd": {"family": "Cucurbitaceae",  "root": "medium_tap",     "is_legume": False, "duration": 110, "yield_ton_ha": 25.0, "land_types": ["HL", "MHL"]},
    "groundnut":    {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 130, "yield_ton_ha": 2.2,  "land_types": ["HL", "MHL"]},
    "soybean":      {"family": "Fabaceae",       "root": "nodulated",      "is_legume": True,  "duration": 100, "yield_ton_ha": 2.0,  "land_types": ["HL", "MHL"]},
    "fallow":       {"family": "None",           "root": "none",           "is_legume": False, "duration": 0,   "yield_ton_ha": 0.0,  "land_types": ["HL", "MHL", "MLL", "LL", "VLL"]},
}


def get_agronomic_info(crop_name: str) -> Dict[str, Any]:
    c_lower = crop_name.lower().strip()
    # Sort keys by length descending so multi-word keys ("sweet potato") match before substrings ("potato")
    for key in sorted(CROP_AGRONOMIC_METADATA.keys(), key=len, reverse=True):
        if key in c_lower:
            return CROP_AGRONOMIC_METADATA[key]
    return {
        "family": "Unknown",
        "root": "medium",
        "is_legume": False,
        "duration": 100,
        "yield_ton_ha": 3.0,
        "land_types": ["HL", "MHL"]
    }


@dataclass
class CropCandidate:
    crop_id: int
    crop_name: str
    season: str
    botanical_family: str
    root_type: str
    is_legume: bool
    duration_days: int
    yield_ton_ha: float
    effective_area_ha: float
    suitability_tier: str
    suitability_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BARCCandidateSelector:
    """
    Candidate Selector for Bangladesh Upazilas using official BARC CZIS data.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "crop_recommender.db")
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _fetch_from_barc_api(self, upazila_code: str) -> List[Dict[str, Any]]:
        """Option A Write-Through: Fetch from official BARC CZIS endpoint if cache miss."""
        url = f"https://dashboard.cropzoning.gov.bd/czis/suitable/area/upazila/{upazila_code}"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        conn = self._get_connection()
        cur = conn.cursor()
        cleaned = []
        for r in data:
            vs = float(r.get("vs") or 0)
            s = float(r.get("s") or 0)
            ms = float(r.get("ms") or 0)
            eff_area = round(vs + (0.70 * s), 1)
            if eff_area == 0 and ms == 0:
                continue

            tier = "Ideal" if vs > 0 else ("Suitable" if s > 0 else "Marginal")
            cname = r.get("crop_name", "").split("(")[0].strip()
            agro = get_agronomic_info(cname)
            land_types_str = ",".join(agro["land_types"])

            cur.execute("""
                INSERT OR REPLACE INTO upazila_suitable_crops 
                (upazila_code, crop_id, crop_name, season, very_suitable_ha, suitable_ha, mod_suitable_ha, 
                 effective_area, suitability_tier, allowable_land_types, botanical_family, root_type, 
                 is_legume, duration_days, yield_ton_ha, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'BARC_CZIS_GOV')
            """, (
                str(upazila_code), r.get("crop_id"), cname, r.get("crop_season"),
                vs, s, ms, eff_area, tier, land_types_str, agro["family"],
                agro["root"], 1 if agro["is_legume"] else 0, agro["duration"],
                agro["yield_ton_ha"]
            ))
            cleaned.append({
                "crop_id": r.get("crop_id"),
                "crop_name": cname,
                "season": r.get("crop_season"),
                "very_suitable_ha": vs,
                "suitable_ha": s,
                "mod_suitable_ha": ms,
                "effective_area": eff_area,
                "suitability_tier": tier,
                "allowable_land_types": land_types_str,
                "botanical_family": agro["family"],
                "root_type": agro["root"],
                "is_legume": bool(agro["is_legume"]),
                "duration_days": agro["duration"],
                "yield_ton_ha": agro["yield_ton_ha"]
            })
        conn.commit()
        conn.close()
        return cleaned

    def get_crops_for_upazila(self, upazila_code: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT * FROM upazila_suitable_crops WHERE upazila_code = ?",
            (str(upazila_code),)
        ).fetchall()
        conn.close()

        if rows:
            return [dict(r) for r in rows]

        # Cache miss: fetch live write-through
        return self._fetch_from_barc_api(upazila_code)

    def select_candidate_pools(
        self,
        upazila_code: str,
        land_type: str = "MHL"
    ) -> Dict[str, Any]:
        """
        Filters and buckets crops into target candidate pools:
        - Rabi (Season 1): Target 7 crops
        - Kharif-1 (Season 2): Target 5 crops
        - Kharif-2 (Season 3): Target 3 crops
        """
        raw_crops = self.get_crops_for_upazila(upazila_code)
        norm_land = land_type.upper().strip()

        # Step 1: Biological Land Type Filtering
        rabi_candidates: List[CropCandidate] = []
        kharif1_candidates: List[CropCandidate] = []
        kharif2_candidates: List[CropCandidate] = []

        is_haor = norm_land in ["LL", "VLL"]

        for c in raw_crops:
            cname = c["crop_name"]
            c_season = str(c["season"]).strip().title()
            eff_area = float(c["effective_area"] or 0)
            vs = float(c["very_suitable_ha"] or 0)
            tier = c["suitability_tier"]
            allowed_lands = [l.strip() for l in c.get("allowable_land_types", "").split(",")]

            # Land type eligibility check
            if norm_land not in allowed_lands:
                continue

            # Hard Biological Exclusions:
            # High Land (HL): Purge flooded paddy rice (Boro)
            if norm_land == "HL" and "boro" in cname.lower():
                continue

            # Low Land (LL/VLL): Purge terrestrial crops prone to root rot / anoxia
            if is_haor and not ("boro" in cname.lower() or "aman" in cname.lower() or "deepwater" in cname.lower() or "fallow" in cname.lower()):
                continue

            # Calculate normalized suitability score [0.0 - 1.0] based on effective area
            # Using logarithmic or min-max scaling relative to max upazila area (~20,000 ha)
            score = round(min(1.0, max(0.2, (eff_area / 5000.0) if vs > 0 else (eff_area / 10000.0))), 3)

            cand = CropCandidate(
                crop_id=int(c.get("crop_id") or 0),
                crop_name=cname,
                season=c_season,
                botanical_family=c.get("botanical_family") or "Unknown",
                root_type=c.get("root_type") or "medium",
                is_legume=bool(c.get("is_legume")),
                duration_days=int(c.get("duration_days") or 90),
                yield_ton_ha=float(c.get("yield_ton_ha") or 2.0),
                effective_area_ha=eff_area,
                suitability_tier=tier,
                suitability_score=score
            )

            if "Rabi" in c_season:
                rabi_candidates.append(cand)
            elif "Kharif-1" in c_season or "Kharif 1" in c_season:
                kharif1_candidates.append(cand)
            elif "Kharif-2" in c_season or "Kharif 2" in c_season:
                kharif2_candidates.append(cand)

        # Step 2: 3-Tier Dynamic Bucketer with Diversity & Fallback Guards
        def bucket_season(
            pool: List[CropCandidate],
            target_count: int,
            season_name: str
        ) -> List[CropCandidate]:
            # Sort by effective area descending, then duration
            sorted_pool = sorted(pool, key=lambda x: (x.effective_area_ha, -x.duration_days), reverse=True)
            
            # De-duplicate by crop_name
            seen = set()
            unique_pool: List[CropCandidate] = []
            for cp in sorted_pool:
                if cp.crop_name.lower() not in seen:
                    seen.add(cp.crop_name.lower())
                    unique_pool.append(cp)

            # If pool meets or exceeds target
            if len(unique_pool) >= target_count:
                return unique_pool[:target_count]

            # If pool is below target (e.g. LL haor basin where only Boro survives)
            # Add Fallow to fill slots without causing deadlocks in Stage 4
            result = list(unique_pool)
            if is_haor:
                # In haor wetland, single crop monoculture with fallow is the ecological reality
                fallow_cand = CropCandidate(
                    crop_id=999,
                    crop_name="Fallow",
                    season=season_name,
                    botanical_family="None",
                    root_type="none",
                    is_legume=False,
                    duration_days=0,
                    yield_ton_ha=0.0,
                    effective_area_ha=10000.0,
                    suitability_tier="Ideal",
                    suitability_score=1.0
                )
                if not result:
                    result.append(fallow_cand)
                return result

            # For non-haor, if still short, keep all available unique candidates
            return result

        final_rabi = bucket_season(rabi_candidates, 7, "Rabi")
        final_kharif1 = bucket_season(kharif1_candidates, 5, "Kharif-1")
        final_kharif2 = bucket_season(kharif2_candidates, 3, "Kharif-2")

        # Determine Cropping Intensity K
        # K = 3 if 3 non-fallow seasons feasible, 2 if 2, 1 for deep haor
        if is_haor:
            k = 1
        elif norm_land == "MLL":
            k = 2
        else:
            k = 3

        return {
            "region_type": "BANGLADESH_BARC",
            "upazila_code": upazila_code,
            "land_type": norm_land,
            "cropping_intensity_k": k,
            "is_haor_wetland": is_haor,
            "seasons": {
                "rabi": [c.to_dict() for c in final_rabi],
                "kharif1": [c.to_dict() for c in final_kharif1],
                "kharif2": [c.to_dict() for c in final_kharif2]
            },
            "candidate_counts": {
                "rabi": len(final_rabi),
                "kharif1": len(final_kharif1),
                "kharif2": len(final_kharif2)
            }
        }
