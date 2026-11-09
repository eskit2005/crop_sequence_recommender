"""
router.py - 2-Tier Spatial Geofencing & Upazila Resolution Router
Zero external C-dependencies (pure standard library: json, math, time).
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any

# National Bounding Box Geofence for Bangladesh
BD_MIN_LAT = 20.50
BD_MAX_LAT = 26.70
BD_MIN_LON = 88.00
BD_MAX_LON = 92.70


@dataclass
class RouteDecision:
    is_bangladesh: bool
    upazila_code: Optional[str]
    upazila_name: Optional[str]
    district_name: Optional[str]
    division_name: Optional[str]
    method: str
    candidates_count: int
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_bangladesh": self.is_bangladesh,
            "upazila_code": self.upazila_code,
            "upazila_name": self.upazila_name,
            "district_name": self.district_name,
            "division_name": self.division_name,
            "method": self.method,
            "candidates_count": self.candidates_count,
            "latency_ms": round(self.latency_ms, 3)
        }


def point_in_ring(lat: float, lon: float, ring: List[List[float]]) -> bool:
    """
    Pure-Python Ray-Casting algorithm implementing the Jordan Curve Theorem.
    ring: List of [lon, lat] coordinate pairs.
    """
    inside = False
    n = len(ring)
    if n < 3:
        return False
    
    p1x, p1y = ring[0][0], ring[0][1]
    for i in range(1, n + 1):
        p2x, p2y = ring[i % n][0], ring[i % n][1]
        if min(p1y, p2y) < lat <= max(p1y, p2y):
            if lon <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                else:
                    xinters = p1x
                if p1x == p2x or lon <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def point_in_polygon(lat: float, lon: float, poly: List[List[List[float]]]) -> bool:
    """
    Checks if (lat, lon) is inside a single polygon (exterior ring minus interior rings/holes).
    poly: [exterior_ring, interior_ring1, interior_ring2, ...]
    """
    if not poly or not poly[0]:
        return False
    # Must be inside the exterior ring
    if not point_in_ring(lat, lon, poly[0]):
        return False
    # Must NOT be inside any interior ring (holes)
    for hole in poly[1:]:
        if point_in_ring(lat, lon, hole):
            return False
    return True


class SpatialRouter:
    """
    Two-Tier Spatial Router:
    - Tier 1: Fast Axis-Aligned Bounding Box (AABB) broad-phase filter.
    - Tier 2: Pure-Python Ray-Casting narrow-phase point-in-polygon resolution.
    """
    _instance = None

    def __init__(self, geojson_path: Optional[str] = None):
        if geojson_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            geojson_path = os.path.join(base_dir, "data", "upazila_polygons.json")
        self.geojson_path = geojson_path
        self.upazilas: List[Dict[str, Any]] = []
        self._load_polygons()

    @classmethod
    def get_instance(cls, geojson_path: Optional[str] = None) -> "SpatialRouter":
        if cls._instance is None:
            cls._instance = cls(geojson_path)
        return cls._instance

    def _extract_bbox(self, coords: Any) -> Tuple[float, float, float, float]:
        lons: List[float] = []
        lats: List[float] = []
        
        def rec(pt: Any):
            if isinstance(pt, (list, tuple)) and len(pt) == 2 and isinstance(pt[0], (int, float)):
                lons.append(float(pt[0]))
                lats.append(float(pt[1]))
            elif isinstance(pt, (list, tuple)):
                for sub in pt:
                    rec(sub)
        
        rec(coords)
        if not lats or not lons:
            return 0.0, 0.0, 0.0, 0.0
        return min(lats), max(lats), min(lons), max(lons)

    def _load_polygons(self):
        if not os.path.exists(self.geojson_path):
            raise FileNotFoundError(f"Upazila GeoJSON not found at: {self.geojson_path}")
        
        with open(self.geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        features = data.get("features", [])
        for f in features:
            props = f.get("properties", {})
            geom = f.get("geometry", {})
            gtype = geom.get("type")
            coords = geom.get("coordinates", [])
            
            code = str(props.get("geocode") or props.get("id") or "")
            name = props.get("upazila") or "Unknown"
            district = props.get("district") or ""
            division = props.get("division") or ""
            
            min_lat, max_lat, min_lon, max_lon = self._extract_bbox(coords)
            
            # Normalize to list of Polygons: List[List[List[Tuple[float, float]]]]
            polys = []
            if gtype == "Polygon":
                polys.append(coords)
            elif gtype == "MultiPolygon":
                polys = coords
                
            self.upazilas.append({
                "code": code,
                "name": name,
                "district": district,
                "division": division,
                "bbox": (min_lat, max_lat, min_lon, max_lon),
                "polygons": polys
            })

    def route(self, lat: float, lon: float) -> RouteDecision:
        t0 = time.perf_counter()
        
        # Tier 0: Fast National Envelope Geofence
        if not (BD_MIN_LAT <= lat <= BD_MAX_LAT and BD_MIN_LON <= lon <= BD_MAX_LON):
            latency = (time.perf_counter() - t0) * 1000.0
            return RouteDecision(
                is_bangladesh=False,
                upazila_code=None,
                upazila_name=None,
                district_name=None,
                division_name=None,
                method="national_envelope_rejection",
                candidates_count=0,
                latency_ms=latency
            )

        # Tier 1 (Broad-Phase): Axis-Aligned Bounding Box (AABB) Filter
        candidates = []
        for u in self.upazilas:
            min_lat, max_lat, min_lon, max_lon = u["bbox"]
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                candidates.append(u)

        if not candidates:
            # Inside national envelope, but in water body or border enclave not enclosed by any upazila AABB
            latency = (time.perf_counter() - t0) * 1000.0
            return RouteDecision(
                is_bangladesh=False,
                upazila_code=None,
                upazila_name=None,
                district_name=None,
                division_name=None,
                method="aabb_empty_rejection",
                candidates_count=0,
                latency_ms=latency
            )

        # Tier 2 (Narrow-Phase): Pure-Python Ray-Casting across candidate polygons
        for cand in candidates:
            for poly in cand["polygons"]:
                if point_in_polygon(lat, lon, poly):
                    latency = (time.perf_counter() - t0) * 1000.0
                    return RouteDecision(
                        is_bangladesh=True,
                        upazila_code=cand["code"],
                        upazila_name=cand["name"],
                        district_name=cand["district"],
                        division_name=cand["division"],
                        method="narrow_phase_pip",
                        candidates_count=len(candidates),
                        latency_ms=latency
                    )

        # Border-clip fallback: if point was inside AABB but slightly clipped by raster boundary,
        # choose candidate whose centroid/center is closest
        best_cand = None
        min_dist_sq = float("inf")
        for cand in candidates:
            min_lat, max_lat, min_lon, max_lon = cand["bbox"]
            c_lat = (min_lat + max_lat) / 2.0
            c_lon = (min_lon + max_lon) / 2.0
            d2 = (lat - c_lat) ** 2 + (lon - c_lon) ** 2
            if d2 < min_dist_sq:
                min_dist_sq = d2
                best_cand = cand

        latency = (time.perf_counter() - t0) * 1000.0
        return RouteDecision(
            is_bangladesh=True,
            upazila_code=best_cand["code"],
            upazila_name=best_cand["name"],
            district_name=best_cand["district"],
            division_name=best_cand["division"],
            method="border_nearest_aabb_fallback",
            candidates_count=len(candidates),
            latency_ms=latency
        )
