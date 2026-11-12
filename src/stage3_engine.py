"""
stage3_engine.py - Master Engine and Public API for Stage 3 Crop Candidate Pool Generation
Unified entry point supporting both Bangladesh (BARC CZIS) and Global (FAO EcoCrop).
"""

import sys
import os
import argparse
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

# Ensure project root is in sys.path so the module can run from any directory
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

try:
    from src.router import SpatialRouter, RouteDecision
    from src.stage3_barc_selector import BARCCandidateSelector
    from src.global_env_fetcher import GlobalEnvFetcher, EnvironmentalProfile
    from src.stage3_fao_selector import FAOCandidateSelector
except ModuleNotFoundError:
    from router import SpatialRouter, RouteDecision
    from stage3_barc_selector import BARCCandidateSelector
    from global_env_fetcher import GlobalEnvFetcher, EnvironmentalProfile
    from stage3_fao_selector import FAOCandidateSelector


@dataclass
class Stage3Result:
    latitude: float
    longitude: float
    land_type: str
    pipeline: str  # "BANGLADESH_BARC" or "GLOBAL_FAO_ECOCROP"
    route_details: Dict[str, Any]
    cropping_intensity_k: int
    seasons: Dict[str, List[Dict[str, Any]]]
    candidate_counts: Dict[str, int]
    environmental_metadata: Dict[str, Any]
    total_execution_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Stage3Engine:
    """
    Master Stage 3 Execution Engine.
    Routes coordinates to Bangladesh BARC CZIS or Global FAO EcoCrop pipeline.
    """
    _instance = None

    def __init__(self):
        self.router = SpatialRouter.get_instance()
        self.barc_selector = BARCCandidateSelector()
        self.env_fetcher = GlobalEnvFetcher()
        self.fao_selector = FAOCandidateSelector()

    @classmethod
    def get_instance(cls) -> "Stage3Engine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_candidate_pools(
        self,
        latitude: float,
        longitude: float,
        land_type: str = "MHL"
    ) -> Stage3Result:
        """
        Public contract for Stage 3:
        Inputs: latitude (float), longitude (float), land_type (str, default 'MHL')
        Returns: Stage3Result with seasonal candidate pools (S1=7, S2=5, S3=3) and K in {1, 2, 3}.
        """
        t0 = time.perf_counter()
        
        # Step 1: Spatial Geofencing & Router
        route: RouteDecision = self.router.route(latitude, longitude)
        
        if route.is_bangladesh and route.upazila_code:
            # Bangladesh Pipeline
            barc_res = self.barc_selector.select_candidate_pools(
                upazila_code=route.upazila_code,
                land_type=land_type
            )
            total_time = (time.perf_counter() - t0) * 1000.0

            return Stage3Result(
                latitude=latitude,
                longitude=longitude,
                land_type=land_type.upper(),
                pipeline="BANGLADESH_BARC",
                route_details=route.to_dict(),
                cropping_intensity_k=barc_res["cropping_intensity_k"],
                seasons=barc_res["seasons"],
                candidate_counts=barc_res["candidate_counts"],
                environmental_metadata={
                    "is_haor_wetland": barc_res["is_haor_wetland"],
                    "data_source": "BARC_CZIS_OFFICIAL_MATRICES"
                },
                total_execution_ms=round(total_time, 2)
            )

        else:
            # Global FAO EcoCrop Pipeline
            profile: EnvironmentalProfile = self.env_fetcher.get_profile(latitude, longitude)
            fao_res = self.fao_selector.select_candidate_pools(profile)
            total_time = (time.perf_counter() - t0) * 1000.0

            return Stage3Result(
                latitude=latitude,
                longitude=longitude,
                land_type=land_type.upper(),
                pipeline="GLOBAL_FAO_ECOCROP",
                route_details=route.to_dict(),
                cropping_intensity_k=fao_res["cropping_intensity_k"],
                seasons=fao_res["seasons"],
                candidate_counts=fao_res["candidate_counts"],
                environmental_metadata={
                    "annual_rainfall_mm": profile.annual_rainfall_mm,
                    "soil_ph": profile.soil_ph,
                    "soil_texture": profile.soil_texture,
                    "lgp_days": profile.lgp_days,
                    "source_climate": profile.source_climate,
                    "source_soil": profile.source_soil
                },
                total_execution_ms=round(total_time, 2)
            )


def format_result_cli(res: Stage3Result) -> str:
    lines = [
        "=" * 75,
        f"  STAGE 3 CROP CANDIDATE POOL GENERATOR - EXECUTION RESULT",
        "=" * 75,
        f"  Coordinates   : Lat {res.latitude:.4f}, Lon {res.longitude:.4f}",
        f"  Land Type     : {res.land_type}",
        f"  Pipeline      : {res.pipeline}",
        f"  Execution Time: {res.total_execution_ms:.2f} ms",
        f"  Cropping K    : {res.cropping_intensity_k} Season(s)",
    ]

    if res.pipeline == "BANGLADESH_BARC":
        r = res.route_details
        lines.append(f"  Location      : Upazila {r.get('upazila_name')} ({r.get('upazila_code')}), {r.get('district_name')}, {r.get('division_name')}")
        lines.append(f"  Routing Method: {r.get('method')} ({r.get('latency_ms')} ms)")
    else:
        env = res.environmental_metadata
        lines.append(f"  Climate Source: {env.get('source_climate')}")
        lines.append(f"  Soil Source   : {env.get('source_soil')} ({env.get('soil_texture')}, pH {env.get('soil_ph')})")
        lines.append(f"  Annual Rain   : {env.get('annual_rainfall_mm')} mm | LGP: {env.get('lgp_days')} days")

    lines.append("-" * 75)
    lines.append("  SEASONAL CANDIDATE POOLS:")
    lines.append("-" * 75)

    for s_name, pool in res.seasons.items():
        lines.append(f"  ▶ {s_name.upper()} ({len(pool)} crops):")
        for i, c in enumerate(pool, 1):
            score_str = f"Score: {c.get('suitability_score'):.2f} [{c.get('suitability_tier')}]"
            details = f"Family: {c.get('botanical_family'):14} | Duration: {c.get('duration_days', 0):3d}d | Yield: {c.get('yield_ton_ha', 0):4.1f} t/ha"
            lines.append(f"    {i}. {c.get('crop_name'):22} | {score_str:24} | {details}")

    lines.append("=" * 75)
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 3 Crop Candidate Pool Generator")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--land-type", type=str, default="MHL", help="Land type: HL, MHL, MLL, LL, VLL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    engine = Stage3Engine.get_instance()
    result = engine.get_candidate_pools(args.lat, args.lon, args.land_type)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_result_cli(result))
