"""
sequence_scorer_remediator.py - Multi-Factor Sequence Scorer & Targeted Remediator
Computes deterministic sub-scores (Climate, Hydrology, Biology, Soil, Economics),
calculates the overall Rotation Health Score (0-100), assigns diagnostic risk grades,
isolates the agronomic weak link, queries crop_recommender.db for a targeted Smart Swap,
and generates practical cultural mitigation fallbacks.
"""

import os
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from .models import (
    FarmerProfile,
    CropEpisode,
    DetectedIssue,
    SmartSwapRecommendation,
)


class SequenceScorerRemediator:
    """
    Synthesizes Stage 1-4 audit outputs into deterministic 0-100 scores
    and generates localized remedial actions.
    """

    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "crop_recommender.db"
    )

    # Inundation Depth Permissibility Matrix
    # HL (0cm), MHL (0-90cm), ML (90-180cm), LL (>180cm), VLL (>300cm)
    PROHIBITED_KHARIF2_UPLAND = {"potato", "tomato", "maize", "cotton", "brinjal", "chilli"}

    @classmethod
    def evaluate_hydrology_and_land(
        cls,
        episodes: List[CropEpisode],
        farmer_profile: FarmerProfile
    ) -> Tuple[float, List[DetectedIssue]]:
        """Audits land type flood inundation suitability."""
        issues: List[DetectedIssue] = []
        penalty = 0.0
        land_type = farmer_profile.field_conditions.land_type.upper().strip()

        for ep in episodes:
            crop_name_lower = ep.crop_name.lower().strip()

            # Kharif-2 monsoonal inundation check
            if ep.season == "Kharif-2":
                if land_type in ["ML", "MLL", "LL", "VLL"]:
                    if any(u in crop_name_lower for u in cls.PROHIBITED_KHARIF2_UPLAND):
                        pen = 60.0
                        penalty += pen
                        issues.append(DetectedIssue(
                            code="MONSOON_INUNDATION_DROWNOUT",
                            severity="CRITICAL_BLOCKER",
                            stage="Stage 3",
                            title=f"বর্ষার পানিতে ফসল তলিয়ে যাওয়ার নিশ্চিত ঝুঁকি: {ep.crop_name}",
                            description=(
                                f"জমির ধরন '{land_type}' (বর্ষায় পানির গভীরতা ৯০-১৮০+ সেমি), যেখানে খরিপ-২ মৌসুমে "
                                f"{ep.crop_name} চাষ করলে ফসল সম্পূর্ণ তলিয়ে নষ্ট হয়ে যাবে।"
                            ),
                            penalty_points=pen,
                            crop_affected=ep.crop_name,
                            suggested_action="বর্ষা মৌসুমে রোপা আমন বা গভীর পানির আমন (B. Aman) চাষ করুন।"
                        ))
                elif land_type == "MHL" and any(u in crop_name_lower for u in ["potato", "tomato"]):
                    pen = 25.0
                    penalty += pen
                    issues.append(DetectedIssue(
                        code="WATERLOGGING_ROOT_ASPHYXIATION",
                        severity="HIGH_RISK",
                        stage="Stage 3",
                        title=f"ভারী বৃষ্টিতে জলাবদ্ধতা ও শিকড় পচন: {ep.crop_name}",
                        description=(
                            f"মাঝারি উঁচু জমিতে (MHL) বর্ষায় সাময়িক জলাবদ্ধতা তৈরি হয়, যা {ep.crop_name} "
                            f"ফসলের শিকড়ের অক্সিজেন চলাচলে বাধা দিয়ে শিকড় পচন ঘটাবে।"
                        ),
                        penalty_points=pen,
                        crop_affected=ep.crop_name,
                        suggested_action="উঁচু বেড (raised bed) তৈরি করে উপযুক্ত নিষ্কাশন নালা রাখুন।"
                    ))

            # Ground Water Stress check in High Barind
            district = (farmer_profile.location.district or "").lower()
            if district in ["rajshahi", "naogaon", "chapai nawabganj"]:
                if "boro" in crop_name_lower and farmer_profile.field_conditions.land_type == "HL":
                    if farmer_profile.farmer_priorities.irrigation_source == "shallow_tubewell":
                        pen = 25.0
                        penalty += pen
                        issues.append(DetectedIssue(
                            code="BARIND_AQUIFER_DEPLETION_RISK",
                            severity="HIGH_RISK",
                            stage="Stage 3",
                            title="বরেন্দ্র অঞ্চলে ভূগর্ভস্থ পানির তীব্র সংকট (Aquifer Depletion)",
                            description=(
                                "উঁচু জমিতে শ্যালো টিউবওয়েল দিয়ে বোরো চাষ করায় অতিরিক্ত পানি উত্তোলনের প্রয়োজন হবে, "
                                "যা এ অঞ্চলের নেমে যাওয়া পানির স্তরে তীব্র সেচ সংকট ও অতিরিক্ত বিদ্যুৎ/ডিজেল খরচ তৈরি করবে।"
                            ),
                            penalty_points=pen,
                            crop_affected=ep.crop_name,
                            suggested_action="বোরো ধানের বিকল্প হিসেবে কম পানির ফসল যেমন গম, সরিষা বা ছোলা চাষ করুন।"
                        ))

            # Rainfed Rabi Drought Deficit Check
            is_rainfed = farmer_profile.farmer_priorities.irrigation_source in ["rainfed", "rainfed_only", "none"]
            if is_rainfed and ep.season == "Rabi" and not ep.is_fallow:
                if ep.water_need_mm > 300.0:
                    pen = 35.0
                    penalty += pen
                    issues.append(DetectedIssue(
                        code="RAINFED_RABI_DROUGHT_STRESS",
                        severity="CRITICAL_BLOCKER" if ep.water_need_mm > 450.0 else "HIGH_RISK",
                        stage="Stage 3",
                        title=f"অনাবাদি শীতকালীন খরার মারাত্মক ঝুঁকি: {ep.crop_name} (Rainfed Drought)",
                        description=(
                            f"রবি মৌসুমে বৃষ্টিপাত অত্যন্ত নগণ্য (<৫০ মিমি)। সেচ সুবিধা ছাড়া {ep.crop_name} "
                            f"(পানি চাহিদা {ep.water_need_mm:.0f} মিমি) চাষ করলে তীব্র খরায় পরাগায়ন ও দানা গঠন ব্যর্থ হবে।"
                        ),
                        penalty_points=pen,
                        crop_affected=ep.crop_name,
                        suggested_action="পরিপূরক সেচের ব্যবস্থা করুন অথবা খরা সহনশীল ফসল (যেমন ছোলা, খেসারি বা বার্লি) চাষ করুন।"
                    ))

            # Chittagong Hill Tracts (AEZ 29) Sloping Land Soil Erosion Check
            if farmer_profile.location.aez == 29 and not ep.is_fallow:
                if any(k in crop_name_lower for k in ["maize", "potato"]):
                    pen = 15.0
                    penalty += pen
                    issues.append(DetectedIssue(
                        code="SLOPE_EROSION_HAZARD",
                        severity="MODERATE_WARNING",
                        stage="Stage 3",
                        title=f"পাহাড়ের ঢালে ভূমিক্ষয় ও মাটির উপরিভাগ ক্ষয়ের ঝুঁকি: {ep.crop_name}",
                        description=(
                            f"পার্বত্য চট্টগ্রামের ঢালু জমিতে নিয়মিত কর্ষণযুক্ত {ep.crop_name} চাষ করলে ভারী বর্ষায় "
                            "মারাত্মক ভূমিক্ষয় (soil erosion > ৩০ টন/হেক্টর/বছর) ও পুষ্টি ক্ষয় ঘটে।"
                        ),
                        penalty_points=pen,
                        crop_affected=ep.crop_name,
                        suggested_action="কন্ট্যুর চাষ (contour tillage), মালচিং ও সমন্বিত হেজরো পদ্ধতি অনুসরণ করুন।"
                    ))

        hydro_subscore = max(0.0, 100.0 - penalty)
        return hydro_subscore, issues

    @classmethod
    def evaluate_economics_and_staples(
        cls,
        episodes: List[CropEpisode],
        farmer_profile: FarmerProfile
    ) -> Tuple[float, List[DetectedIssue]]:
        """Audits working capital expenditure against farmer budget and food staple need."""
        issues: List[DetectedIssue] = []
        penalty = 0.0

        priorities = farmer_profile.farmer_priorities
        area_ha = priorities.land_size_ha
        budget_bdt = priorities.total_budget_bdt

        # Approximate production costs (BDT/ha) in Bangladesh
        cost_benchmarks = {
            "potato": 150000.0,
            "tomato": 110000.0,
            "boro rice": 85000.0,
            "boro dhan": 85000.0,
            "t. aman rice": 65000.0,
            "t. aman": 65000.0,
            "aus rice": 55000.0,
            "maize": 95000.0,
            "mungbean": 40000.0,
            "mustard": 42000.0,
            "lentil": 45000.0,
            "wheat": 52000.0,
            "jute": 58000.0,
            "brinjal": 90000.0,
            "chilli": 85000.0,
        }

        total_cost_per_ha = 0.0
        has_staple = False

        for ep in episodes:
            c_name = ep.crop_name.lower().strip()
            cost = 60000.0
            for pat, val in cost_benchmarks.items():
                if pat in c_name:
                    cost = val
                    break
            total_cost_per_ha += cost

            # Check staple grain presence
            if any(s in c_name for s in ["rice", "dhan", "wheat"]):
                has_staple = True

        total_required_cost = total_cost_per_ha * area_ha

        # Budget Check
        if total_required_cost > budget_bdt:
            overage_ratio = (total_required_cost - budget_bdt) / budget_bdt
            pen = min(40.0, overage_ratio * 40.0)
            penalty += pen
            issues.append(DetectedIssue(
                code="CAPITAL_BUDGET_SHORTFALL",
                severity="HIGH_RISK" if overage_ratio > 0.15 else "MODERATE_WARNING",
                stage="Stage 5",
                title="কার্যকরী মূলধনের ঘাটতি (Working Capital Shortfall)",
                description=(
                    f"নির্বাচিত ফসল বিন্যাসের জন্য মোট আনুমানিক খরচ প্রায় {total_required_cost:,.0f} টাকা, "
                    f"যা আপনার নির্ধারিত বাজেট ({budget_bdt:,.0f} টাকা) এর চেয়ে {total_required_cost - budget_bdt:,.0f} টাকা বেশি "
                    f"({overage_ratio * 100:.1f}% ঘাটতি)। মাঝপথে অর্থ সংকটে বালাইনাশক বা সেচ ব্যাহত হতে পারে।"
                ),
                penalty_points=pen,
                suggested_action="অপেক্ষাকৃত কম খরচের ফসল (যেমন ডাল বা তেলবীজ) বিন্যাসে অন্তর্ভুক্ত করুন।"
            ))

        # Food Security Staple Check
        if priorities.food_security_staple_needed and not has_staple:
            pen = 40.0
            penalty += pen
            issues.append(DetectedIssue(
                code="HOUSEHOLD_FOOD_SECURITY_MISSING_STAPLE",
                severity="HIGH_RISK",
                stage="Stage 5",
                title="পারিবারিক খাদ্য নিরাপত্তার চাল ঘাটতি (Food Security Staple Omission)",
                description=(
                    "আপনার অগ্রাধিকার অনুযায়ী পারিবারিক খাদ্য নিরাপত্তার জন্য চাল প্রয়োজন, "
                    "কিন্তু নির্বাচিত ফসল বিন্যাসে কোনো ধান বা দানা শস্য রাখা হয়নি।"
                ),
                penalty_points=pen,
                suggested_action="খরিপ-২ মৌসুমে রোপা আমন ধান অথবা রবি মৌসুমে বোরো ধান নিশ্চিত করুন।"
            ))

        econ_subscore = max(0.0, 100.0 - penalty)
        return econ_subscore, issues

    @classmethod
    def calculate_overall_score(
        cls,
        sub_scores: Dict[str, float],
        issues: List[DetectedIssue]
    ) -> Tuple[float, str, str]:
        """
        Calculates weighted composite score and determines risk category and letter grade.
        Enforces critical blocker ceiling: if any blocker exists, score is capped at <40.
        """
        weights = {
            "climate": 0.20,
            "hydrology": 0.20,
            "biology": 0.20,
            "soil": 0.20,
            "economics": 0.20
        }

        raw_score = sum(sub_scores.get(k, 100.0) * w for k, w in weights.items())

        # Check for critical blockers
        has_blocker = any(issue.severity == "CRITICAL_BLOCKER" for issue in issues)
        if has_blocker:
            final_score = min(38.0, raw_score)
            grade = "D-" if final_score >= 30 else "F"
            category = "CRITICAL_BLOCKER"
        else:
            final_score = raw_score
            if final_score >= 85.0:
                grade = "A+" if final_score >= 92.0 else "A"
                category = "AGRO_ECOLOGICAL_EXCELLENCE"
            elif final_score >= 65.0:
                grade = "B" if final_score >= 75.0 else "C+"
                category = "MODERATE_OPPORTUNITY"
            elif final_score >= 40.0:
                grade = "C" if final_score >= 50.0 else "D+"
                category = "HIGH_AGRONOMIC_RISK"
            else:
                grade = "F"
                category = "CRITICAL_BLOCKER"

        return final_score, grade, category

    @classmethod
    def generate_smart_swap(
        cls,
        episodes: List[CropEpisode],
        issues: List[DetectedIssue],
        farmer_profile: FarmerProfile,
        current_score: float
    ) -> List[SmartSwapRecommendation]:
        """
        Isolates weak link crop with largest penalty and queries crop_recommender.db
        for a targeted alternative.
        """
        swaps: List[SmartSwapRecommendation] = []
        if current_score >= 85.0 or not issues:
            return swaps

        # Find crop associated with largest penalty
        crop_penalty_map: Dict[str, float] = {}
        for issue in issues:
            if issue.crop_affected:
                c = issue.crop_affected
                crop_penalty_map[c] = crop_penalty_map.get(c, 0.0) + issue.penalty_points

        if not crop_penalty_map:
            return swaps

        problematic_crop_name = max(crop_penalty_map.items(), key=lambda x: x[1])[0]

        # Find episode corresponding to weak link
        target_ep = next((ep for ep in episodes if ep.crop_name.lower() == problematic_crop_name.lower()), None)
        if not target_ep:
            target_ep = episodes[0]

        # Query database for alternatives in the same season
        upazila_code = None
        if os.path.exists(cls.DB_PATH):
            try:
                conn = sqlite3.connect(cls.DB_PATH)
                cursor = conn.cursor()
                # Query candidate crops for this season
                cursor.execute(
                    """
                    SELECT DISTINCT crop_name, botanical_family, root_type, is_legume, duration_days
                    FROM upazila_suitable_crops
                    WHERE season = ? AND botanical_family != ? AND crop_name != ?
                    LIMIT 20
                    """,
                    (target_ep.season, target_ep.botanical_family, target_ep.crop_name)
                )
                rows = cursor.fetchall()
                conn.close()
            except Exception:
                rows = []
        else:
            rows = []

        # Default smart swap rules based on agro-ecological logic
        target_name_lower = target_ep.crop_name.lower()
        salinity = farmer_profile.field_conditions.soil_salinity_ec_e

        if salinity > 4.0 and any(leg in target_name_lower for leg in ["lentil", "mungbean", "chickpea", "grass pea", "gram"]):
            rep_name = "Sunflower (হীরা-১ / BARI Surjamukhi-2)"
            rep_fam = "Asteraceae"
            reason = (
                f"উপকূলীয় লবণাক্ত জমিতে (লবণাক্ততা {salinity:.1f} dS/m) সংবেদনশীল ডাল ফসল পুড়ে নষ্ট হয়ে যায়। "
                "সূর্যমুখী উচ্চ লবণ সহনশীল (threshold 5.5 dS/m) হওয়ায় এ জমিতে লাভজনক ফলন ও উৎকৃষ্ট ভোজ্যতেল উৎপাদন নিশ্চিত করে।"
            )
            n_gain = 0.0
            proj_score = min(92.0, current_score + 50.0)
        elif salinity > 4.0 and "boro" in target_name_lower:
            rep_name = "BRRI dhan67 (লবণ সহনশীল বোরো ধান)"
            rep_fam = "Poaceae"
            reason = (
                "লবণাক্ত জমিতে সাধারণ বোরো ধানের বদলে ব্রি ধান৬৭ ব্যবহার করলে ৮-১০ dS/m লবণাক্ততাতেও ৭০% এর বেশি বাণিজ্যিক ফলন পাওয়া যায়।"
            )
            n_gain = 0.0
            proj_score = min(88.0, current_score + 35.0)
        elif "tomato" in target_name_lower and target_ep.season == "Kharif-1":
            rep_name = "Mungbean (BARI Mung-6)"
            rep_fam = "Fabaceae"
            reason = (
                "টমেটোর পরিবর্তে খরিপ-১ এ মুগডাল চাষ করলে সোলানেসি রোগচক্র (উইল্ট ও শিকড় কৃমি) ভেঙে যায়, "
                "মাটিতে ৪০ কেজি/হেক্টর জৈব নাইট্রোজেন যোগ হয় এবং পরবর্তী আমন ধানের সার খরচ ৩০% সাশ্রয় হয়।"
            )
            n_gain = 40.0
            proj_score = min(95.0, current_score + 55.0)
        elif "boro" in target_name_lower and (farmer_profile.field_conditions.land_type == "HL" or farmer_profile.location.aez == 26):
            rep_name = "Chickpea / Mustard (বারি ছোলা-৯ / বারি সরিষা-১৪)"
            rep_fam = "Fabaceae"
            reason = (
                "বরেন্দ্র অঞ্চলের উঁচু জমিতে ভূগর্ভস্থ পানির ভয়াবহ অবনমন ও সেচের অতিরিক্ত খরচ রুখতে "
                "বোরো ধানের বদলে কম পানির শীতকালীন ছোলা বা সরিষা আবর্তন টেকসই ও লাভজনক।"
            )
            n_gain = 30.0
            proj_score = min(90.0, current_score + 40.0)
        elif "aus" in target_name_lower and any("TEMPORAL" in iss.code for iss in issues):
            rep_name = "Dhaincha (সবুজ সার ধৈঞ্চা - Sesbania aculeata)"
            rep_fam = "Fabaceae"
            reason = (
                "টানা তিন ধান (বোরো-আউশ-আমন) চাষে জমি তৈরির সময় থাকে না এবং মাটির জৈব পদার্থ ধ্বংস হয়। "
                "আউশের বদলে খরিপ-১ এ ৫০ দিনের সবুজ সার ধৈঞ্চা চাষ করলে জমি জটের অবসান ঘটে, মাটির বায়ু চলাচল বৃদ্ধি পায় এবং আমন ধানে ৫০-৬০ কেজি ইউরিয়া সার সাশ্রয় হয়।"
            )
            n_gain = 55.0
            proj_score = min(90.0, current_score + 45.0)
        elif "tobacco" in target_name_lower:
            rep_name = "Mustard (বারি সরিষা-১৪ / বারি সরিষা-১৭)"
            rep_fam = "Brassicaceae"
            reason = (
                "তামাক চাষ মাটির মারাত্মক পুষ্টি ক্ষয় (severe nutrient mining) করে এবং বিষাক্ত ক্ষতিকর প্রভাব ফেলে। "
                "তামাকের বদলে স্বল্পমেয়াদী উন্নত জাতের সরিষা চাষ মাটির স্বাস্থ্য রক্ষা করে ও লাভজনক ভোজ্যতেল যোগান দেয়।"
            )
            n_gain = 10.0
            proj_score = min(88.0, current_score + 35.0)
        elif any(iss.code == "CRITICAL_HAOR_FLASH_FLOOD_RISK" for iss in issues) and "boro" in target_name_lower:
            rep_name = "BRRI dhan88 / BRRI dhan96 (স্বল্পমেয়াদী আগাম বোরো জাত)"
            rep_fam = "Poaceae"
            reason = (
                "হাওর অববাহিকায় দীর্ঘমেয়াদী বোরো ধানের বদলে ১৪০ দিনের আগাম জাত (যেমন ব্রি ধান৮৮/৯৬) চাষ করলে "
                "এপ্রিলের মাঝামাঝি পাহাড়ি ঢল নামার আগেই ধান কেটে নিরাপদে ঘরে তোলা যায়।"
            )
            n_gain = 0.0
            proj_score = min(92.0, current_score + 40.0)
        elif any(iss.code == "RAINFED_RABI_DROUGHT_STRESS" for iss in issues):
            rep_name = "Chickpea / Barley (বারি ছোলা-৯ / বারি বার্লি-৬)"
            rep_fam = "Fabaceae"
            reason = (
                "অনাবাদি রবি মৌসুমে তীব্র খরার কারণে সেচ ছাড়া ভুট্টা বা বোরো বাঁচে না। কম পানির খরা সহনশীল "
                "ছোলা বা বার্লি চাষ করলে বিনা সেচেই মাটির অবশিষ্ট রসে ফসল সংগ্রহ করা সম্ভব।"
            )
            n_gain = 25.0
            proj_score = min(88.0, current_score + 40.0)
        elif target_ep.season == "Kharif-2":
            rep_name = "Short-Duration T. Aman (ব্রি ধান৭৫ / ব্রি ধান৭১)"
            rep_fam = "Poaceae"
            reason = (
                "খরিপ-২ বর্ষা মৌসুমে জমি কর্দমাক্ত ও জলাবদ্ধ থাকায় ডাল ফসল টিকবে না। ১১০-১১৫ দিনের স্বল্পমেয়াদী রোপা আমন "
                "চাষ করলে সময়মতো জমি খালি হয় এবং পরবর্তী রবি ফসল যথাসময়ে বপন করা যায়।"
            )
            n_gain = 0.0
            proj_score = min(90.0, current_score + 35.0)
        elif target_ep.season == "Rabi":
            rep_name = "Mustard (বারি সরিষা-১৪ / বারি সরিষা-১৭)"
            rep_fam = "Brassicaceae"
            reason = "শীতকালীন রবি মৌসুমে ডালের বদলে স্বল্পমেয়াদী সরিষা চাষ শৈত্যজনিত ক্ষতি এড়িয়ে লাভজনক ভোজ্যতেল উৎপাদনে কার্যকর।"
            n_gain = 10.0
            proj_score = min(88.0, current_score + 30.0)
        else:
            if "mungbean" in target_name_lower:
                rep_name = "Sesbania (সবুজ সার ধৈঞ্চা)"
                rep_fam = "Fabaceae"
                reason = "মুগডালের পুনরাবৃত্তি এড়িয়ে খরিপ-১ মৌসুমে ধৈঞ্চা সবুজ সার চাষে মাটির উর্বরতা পুনরুদ্ধার ও শিকড় কৃমি দমন হয়।"
                n_gain = 45.0
                proj_score = min(90.0, current_score + 35.0)
            else:
                rep_name = "Mungbean (BARI Mung-6)"
                rep_fam = "Fabaceae"
                reason = "মাটির জৈব পদার্থ পুনরুদ্ধার, নাইট্রোজেন সংযোজন এবং রোগচক্র ভাঙতে খরিপ-১ এ ডাল জাতীয় ফসল আবর্তন অপরিহার্য।"
                n_gain = 35.0
                proj_score = min(88.0, current_score + 30.0)

        swaps.append(SmartSwapRecommendation(
            problematic_crop=f"{target_ep.crop_name} ({target_ep.season})",
            season=target_ep.season,
            year=target_ep.year,
            recommended_replacement=rep_name,
            botanical_family=rep_fam,
            reason=reason,
            residual_n_gain_kg_ha=n_gain,
            projected_score_after_swap=proj_score,
            cost_delta_bdt=-25000.0
        ))

        return swaps

    @classmethod
    def generate_cultural_mitigations(
        cls,
        episodes: List[CropEpisode],
        issues: List[DetectedIssue]
    ) -> List[str]:
        """Generates practical agronomic protocols if the farmer insists on keeping original sequence."""
        mitigations: List[str] = []

        has_solanaceae_bridge = any(issue.code == "SOLANACEAE_DISEASE_BRIDGE" for issue in issues)
        has_salinity = any("SALINITY" in issue.code for issue in issues)
        has_waterlogging = any("WATERLOGGING" in issue.code for issue in issues)
        has_soc_deficit = any("SOC" in issue.code for issue in issues)

        if has_solanaceae_bridge:
            mitigations.append("টমেটো চারা লাগানোর আগে জমি অন্তত ১০-১৫ দিন স্বচ্ছ পলিথিন বিছিয়ে কড়া রোদে শুকিয়ে নিন (Soil Solarization)।")
            mitigations.append("জমিতে ট্রাইকোডার্মা (Trichoderma viride/harzianum) মিশ্রিত জৈব কম্পোস্ট সার (২ টন/হেক্টর) প্রয়োগ করুন।")
            mitigations.append("উইল্ট-প্রতিরোধী জাত নির্বাচন করুন অথবা বুনো বেগুন (Solanum torvum) এর রুটের ওপর গ্রাফটিং করা চারা রোপণ করুন।")

        if has_salinity:
            mitigations.append("রবি মৌসুমে জমিতে ধানের খড় বা পলিথিন মালচিং ব্যবহার করে কৈশিক নালির মাধ্যমে লবণ ওঠা রোধ করুন।")
            mitigations.append("লবণাক্ততার ক্ষতিকর প্রভাব কমাতে জমিতে পরিমিত জিপসাম এবং জৈব সার ব্যবহার নিশ্চিত করুন।")

        if has_waterlogging:
            mitigations.append("খরিপ মৌসুমে সবজি চাষের জন্য ২৫-৩০ সেমি উঁচু বেড তৈরি করুন এবং প্রতি দুটি বেডের মাঝে গভীর নিষ্কাশন নালা রাখুন।")

        if has_soc_deficit:
            mitigations.append("ধান বা অন্যান্য ফসল কাটার পর গোড়ার অন্তত ২০ সেমি নাড়া (stubble) জমিতে চাষ দিয়ে মাটির সাথে মিশিয়ে দিন।")

        if not mitigations:
            mitigations.append("সুষম মাত্রায় সার প্রয়োগ এবং সময়মতো বালাই দমন নিশ্চিত করতে স্থানীয় কৃষি সম্প্রসারণ কর্মকর্তার পরামর্শ নিন।")

        return mitigations
