#!/usr/bin/env python3
"""
evaluate_sequence_cli.py - Standalone Command-Line Interface for Crop Sequence Evaluator DSS
Accepts farmer sequence JSON or CLI arguments, runs the deterministic biophysical audit (Stages 1-5),
and generates bilingual Bengali & English diagnostic advice (Stage 6).

Usage Examples:
    python3 src/evaluate_sequence_cli.py --demo bogura
    python3 src/evaluate_sequence_cli.py --json path/to/farmer_profile.json
    python3 src/evaluate_sequence_cli.py --lat 24.785 --lon 89.042 --sequence "Potato,Tomato,T. Aman Rice"
"""

import sys
import os
import re
import json
import argparse

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator.models import FarmerProfile
from src.evaluator.evaluator_engine import CropSequenceEvaluatorEngine


def get_demo_bogura_payload() -> dict:
    """Returns the verified Bogura smallholder prototype input profile."""
    return {
        "location": {
            "lat": 24.7850,
            "lon": 89.0420,
            "upazila": "Adamdighi",
            "district": "Bogura",
            "division": "Rajshahi",
            "aez": 3
        },
        "field_conditions": {
            "land_type": "MHL",
            "soil_texture": "Silt Loam",
            "soil_ph": 6.2,
            "soil_organic_carbon_pct": 1.10,
            "soil_salinity_ec_e": 0.80,
            "drainage_condition": "moderate",
            "bulk_density": 1.50
        },
        "farmer_priorities": {
            "land_size_ha": 0.40,
            "total_budget_bdt": 120000.0,
            "irrigation_source": "shallow_tubewell",
            "water_cost_per_m3_bdt": 3.5,
            "food_security_staple_needed": True,
            "risk_tolerance": "moderate"
        },
        "target_horizon_years": 1,
        "farmer_evaluated_sequence": [
            {
                "year": 1,
                "season": "Rabi",
                "crop_name": "Potato",
                "cultivar": "Diamond (HYV)",
                "stover_management": "removed"
            },
            {
                "year": 1,
                "season": "Kharif-1",
                "crop_name": "Tomato",
                "cultivar": "Summer Hybrid",
                "stover_management": "incorporated"
            },
            {
                "year": 1,
                "season": "Kharif-2",
                "crop_name": "T. Aman Rice",
                "cultivar": "BRRI dhan49",
                "stover_management": "incorporated"
            }
        ],
        "preferences": {
            "language": "bn",
            "tone": "farmer_friendly"
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="NASA-Powered Crop Sequence Evaluator Decision Support System (DSS)"
    )
    parser.add_argument("--demo", choices=["bogura", "satkhira", "barind"], help="Run built-in benchmark demo")
    parser.add_argument("--profile", "--input-json", dest="profile_path", type=str, help="Path to input JSON farmer profile")
    parser.add_argument("--lat", type=float, default=24.7850, help="Latitude (e.g. 24.7850)")
    parser.add_argument("--lon", type=float, default=89.0420, help="Longitude (e.g. 89.0420)")
    parser.add_argument("--upazila", type=str, default="", help="Upazila name (e.g. Adamdighi)")
    parser.add_argument("--district", type=str, default="", help="District name (e.g. Bogura)")
    parser.add_argument("--sequence", type=str, help="Comma or semicolon separated crop names (e.g. 'Potato,Tomato,T. Aman Rice' or 'Rabi:Potato;Kharif-1:Tomato;Kharif-2:T. Aman')")
    parser.add_argument("--salinity", type=float, default=0.8, help="Soil salinity ECe in dS/m (e.g. 7.5)")
    parser.add_argument("--ph", type=float, default=6.5, help="Soil pH (e.g. 5.5)")
    parser.add_argument("--land-type", type=str, default="MHL", help="Land type: HL, MHL, MLL, LL, VLL")
    parser.add_argument("--budget", type=float, default=120000.0, help="Total farmer budget in BDT")
    parser.add_argument("--area", type=float, default=0.40, help="Farm land area in hectares")
    parser.add_argument("--irrigation", type=str, default="shallow_tubewell", choices=["surface_canal", "shallow_tubewell", "deep_tubewell", "rainfed"], help="Irrigation source")
    parser.add_argument("--json", "--output-json", dest="output_json", action="store_true", help="Print machine-readable JSON output")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    payload = None
    if args.demo == "bogura":
        payload = get_demo_bogura_payload()
    elif args.demo == "satkhira":
        payload = get_demo_bogura_payload()
        payload["location"] = {"lat": 22.33, "lon": 89.15, "upazila": "Shyamnagar", "district": "Satkhira", "division": "Khulna"}
        payload["field_conditions"]["soil_salinity_ec_e"] = 7.5
        payload["farmer_evaluated_sequence"] = [
            {"year": 1, "season": "Rabi", "crop_name": "Lentil"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Mungbean"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    elif args.demo == "barind":
        payload = get_demo_bogura_payload()
        payload["location"] = {"lat": 24.45, "lon": 88.32, "upazila": "Godagari", "district": "Rajshahi", "division": "Rajshahi"}
        payload["field_conditions"]["land_type"] = "HL"
        payload["farmer_evaluated_sequence"] = [
            {"year": 1, "season": "Rabi", "crop_name": "Boro Rice"},
            {"year": 1, "season": "Kharif-1", "crop_name": "Fallow"},
            {"year": 1, "season": "Kharif-2", "crop_name": "T. Aman Rice"}
        ]
    elif args.profile_path:
        with open(args.profile_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    elif args.sequence:
        # Build sequence parsing both comma/semicolon and Season:Crop syntax
        raw_tokens = [t.strip() for t in re.split(r"[,;]+", args.sequence) if t.strip()]
        default_seasons = ["Rabi", "Kharif-1", "Kharif-2"]
        seq = []
        for i, token in enumerate(raw_tokens):
            if ":" in token:
                parts = token.split(":", 1)
                s = parts[0].strip()
                name = parts[1].strip()
            else:
                s = default_seasons[i % 3]
                name = token

            yr = (i // 3) + 1
            seq.append({"year": yr, "season": s, "crop_name": name})

        payload = {
            "location": {
                "lat": args.lat,
                "lon": args.lon,
                "upazila": args.upazila or None,
                "district": args.district or None
            },
            "field_conditions": {
                "land_type": args.land_type,
                "soil_salinity_ec_e": args.salinity,
                "soil_ph": args.ph
            },
            "farmer_priorities": {
                "total_budget_bdt": args.budget,
                "land_size_ha": args.area,
                "irrigation_source": args.irrigation
            },
            "farmer_evaluated_sequence": seq
        }
    else:
        # Fallback to bogura demo if no target provided
        payload = get_demo_bogura_payload()

    profile = FarmerProfile.from_dict(payload)
    engine = CropSequenceEvaluatorEngine()

    result = engine.evaluate(profile)

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return

    # Formatted Diagnostic Report
    print("=" * 76)
    print("🌾 KRISHIBONDHU AI - CROP SEQUENCE EVALUATOR & DECISION SUPPORT SYSTEM")
    print("   Powered by NASA Earth Observations & Soil Biogeochemistry")
    print("=" * 76)
    loc = result.farmer_profile.location
    print(f"📍 Location: {loc.upazila or 'N/A'}, {loc.district or 'N/A'} ({loc.lat:.4f}°N, {loc.lon:.4f}°E)")
    print(f"🌱 Land Type: {result.farmer_profile.field_conditions.land_type} | Soil Salinity: {result.farmer_profile.field_conditions.soil_salinity_ec_e:.1f} dS/m | Soil pH: {result.farmer_profile.field_conditions.soil_ph:.1f}")
    print(f"💰 Farmer Budget: {result.farmer_profile.farmer_priorities.total_budget_bdt:,.0f} BDT | Area: {result.farmer_profile.farmer_priorities.land_size_ha} ha")

    print("\n--- EVALUATED CROP SEQUENCE ---")
    for ep in result.episodes:
        print(f"  • Year {ep.year} [{ep.season}]: {ep.crop_name} ({ep.botanical_family}, {ep.duration_days} days, Root: {ep.root_type})")

    print("\n" + "-" * 76)
    print(f"🎯 ROTATION HEALTH SCORE: {result.overall_health_score:.1f} / 100  |  GRADE: {result.grade}  |  STATUS: {result.risk_category}")
    print("-" * 76)

    print("📊 Sub-Score Breakdown:")
    for k, v in result.sub_scores.items():
        bar = "█" * int(v / 5) + "░" * (20 - int(v / 5))
        print(f"  - {k.capitalize():<12}: {v:>5.1f}/100 [{bar}]")

    print("\n🧪 Biogeochemical & Physical Metrics:")
    print(f"  • Annual Net ΔSOC      : {result.soc_trajectory.get('delta_soc_annual_t_c_ha', 0):+.3f} t C/ha/year")
    print(f"  • Annual Net Nitrogen  : {result.nitrogen_balance.get('net_n_balance_annual_kg_ha', 0):+.1f} kg N/ha/year")
    print(f"  • Water Deficit (P-ET0): {result.water_balance.get('net_water_deficit_mm', 0):.1f} mm")

    print("\n⚠️ Detected Agronomic Issues & Risks:")
    if not result.detected_issues:
        print("  ✓ Zero severe biological, chemical, or temporal conflicts detected.")
    else:
        for idx, issue in enumerate(result.detected_issues, 1):
            icon = "🔴" if issue.severity == "CRITICAL_BLOCKER" else ("🟠" if issue.severity == "HIGH_RISK" else "🟡")
            print(f"  {idx}. {icon} [{issue.severity}] {issue.title}")
            print(f"     Details: {issue.description}")
            if issue.suggested_action:
                print(f"     Action : {issue.suggested_action}")

    if result.smart_swaps:
        print("\n💡 DETERMINISTIC SMART CROP SWAP (TARGETED REMEDIATION):")
        for s in result.smart_swaps:
            print(f"  • Replace '{s.problematic_crop}' with ➜ '{s.recommended_replacement}'")
            print(f"    Why: {s.reason}")
            print(f"    Score After Swap: {s.projected_score_after_swap:.0f} / 100 (+{s.projected_score_after_swap - result.overall_health_score:.0f} pts)")

    if result.advisory_report:
        adv = result.advisory_report
        summary = adv.get("advisory_summary", {})
        print("\n" + "=" * 76)
        print("🤖 KRISHIBONDHU AI ADVISORY (কৃষিবন্ধু এআই পরামর্শ)")
        print("=" * 76)
        print(f"📢 {summary.get('verdict_title')}")
        print(f"📝 {summary.get('one_sentence_takeaway')}")

        budget_chk = adv.get("socio_economic_budget_check", {})
        print(f"\n💵 বাজেট মূল্যায়ন: {budget_chk.get('budget_status')}")

        checklist = adv.get("upcoming_season_action_checklist", [])
        if checklist:
            print("\n📋 আসন্ন মৌসুমের করণীয় তালিকা (Action Checklist):")
            for item in checklist:
                print(f"  ✓ {item}")

    print("=" * 76)


if __name__ == "__main__":
    main()
