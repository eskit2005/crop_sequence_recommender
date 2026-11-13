"""
soil_biogeochem_auditor.py - Quantitative Soil Health & Biogeochemistry Auditor
Implements duration-weighted Soil Organic Carbon (SOC) trajectory (Hénin-Dupuis/Lal),
Net Nitrogen budget with legume Nitrogen Harvest Index (NHI=0.70), piecewise pH stress,
and calibrated Maas-Hoffman salinity yield reduction models.
"""

from typing import List, Dict, Any, Tuple
from .models import CropEpisode, FieldConditions, DetectedIssue


class SoilBiogeochemAuditor:
    """
    Audits Soil Organic Carbon (SOC), Nitrogen drawdown vs BNF, pH boundaries,
    and dry-season soil salinity yield penalties.
    """

    # Crop Nitrogen Drawdown Benchmarks (kg N/ha) per BARC FRG-2018
    N_DRAWDOWN_BENCHMARKS = {
        "potato": 125.0,
        "tomato": 110.0,
        "maize": 200.0,
        "boro rice": 130.0,
        "boro dhan": 130.0,
        "t. aman rice": 85.0,
        "t. aman": 85.0,
        "aus rice": 75.0,
        "brinjal": 100.0,
        "chilli": 70.0,
        "mustard": 60.0,
        "wheat": 90.0,
        "jute": 45.0,
        "cauliflower": 80.0,
        "cabbage": 85.0,
        "onion": 70.0,
        "garlic": 65.0,
        "sunflower": 75.0,
    }

    # Maas-Hoffman Salinity Parameters (a: threshold dS/m, b: slope % per dS/m)
    # References: FAO-29, Maas & Hoffman (1977), BRRI Coastal Trials
    MAAS_HOFFMAN_PARAMS = {
        "potato": (1.7, 12.0),
        "lentil": (1.5, 20.0),
        "mungbean": (1.6, 18.0),
        "chickpea": (1.5, 17.0),
        "grass pea": (3.5, 10.0),
        "sunflower": (5.5, 5.0),
        "mustard": (5.0, 7.0),
        "maize": (1.7, 12.0),
        "tomato": (2.5, 9.9),
        "brinjal": (2.5, 10.0),
        "wheat": (6.0, 7.1),
        "barley": (8.0, 5.0),
        "boro rice": (3.0, 12.0),
        "t. aman rice": (3.0, 12.0),
        "brri dhan67": (4.2, 9.0),
        "brri dhan97": (4.5, 8.5),
        "brri dhan73": (4.0, 8.5),
    }

    # Optimal pH ranges by crop species
    PH_OPTIMUM_RANGES = {
        "potato": (5.0, 6.5),
        "tomato": (5.5, 6.8),
        "maize": (5.8, 7.0),
        "boro rice": (5.5, 7.2),
        "t. aman rice": (5.5, 7.2),
        "mungbean": (6.0, 7.2),
        "lentil": (6.0, 7.5),
        "chickpea": (6.0, 7.5),
        "mustard": (6.0, 7.5),
        "wheat": (6.0, 7.5),
        "jute": (5.5, 7.0),
        "brinjal": (5.5, 6.8),
    }

    @classmethod
    def audit_soc_trajectory(
        cls,
        episodes: List[CropEpisode],
        field_cond: FieldConditions,
        horizon_years: int = 1
    ) -> Tuple[Dict[str, float], List[DetectedIssue]]:
        """
        Calculates duration-weighted Soil Organic Carbon annual trajectory.
        Derived from Hénin & Dupuis (1945), ICBM, and Lal (2004).
        """
        issues: List[DetectedIssue] = []
        depth_m = 0.20
        # Baseline carbon in top 20cm (t C/ha)
        soc_baseline = 10000.0 * depth_m * field_cond.bulk_density * (field_cond.soil_organic_carbon_pct / 100.0)
        k_decomp = 0.030  # Subtropical base microbial oxidation rate (yr^-1)

        total_c_humified = 0.0
        weighted_decay_fraction = 0.0
        total_crop_days = 0

        for ep in episodes:
            if ep.is_fallow or ep.crop_name.lower().strip() == "fallow":
                continue
            crop_key = ep.crop_name.lower().strip()
            total_crop_days += ep.duration_days

            # Determine biomass carbon input and humification coefficient
            if ep.is_legume:
                if ep.stover_management == "incorporated":
                    c_input = 0.85
                    alpha_hum = 0.20
                    f_till = 0.75  # reduced tillage
                else:
                    c_input = 0.10
                    alpha_hum = 0.15
                    f_till = 1.0
            elif "potato" in crop_key:
                c_input = -0.15  # tuber extraction net export
                alpha_hum = 0.20
                f_till = 1.40  # intensive digging tillage
            elif "rice" in crop_key or "dhan" in crop_key:
                c_input = 0.40  # stubble retention
                alpha_hum = 0.20
                f_till = 1.0
            elif "tomato" in crop_key or "brinjal" in crop_key:
                c_input = 0.20
                alpha_hum = 0.15
                f_till = 1.0
            elif "maize" in crop_key:
                c_input = 0.60
                alpha_hum = 0.22
                f_till = 1.0
            elif "sesbania" in crop_key or "dhaincha" in crop_key:
                c_input = 2.00  # dedicated green manure
                alpha_hum = 0.12
                f_till = 1.0
            else:
                c_input = 0.30
                alpha_hum = 0.18
                f_till = 1.0

            # Soil redox modifier
            if ("rice" in crop_key or "dhan" in crop_key) and field_cond.land_type in ["MHL", "ML", "LL", "VLL"]:
                f_redox = 0.55  # anaerobic waterlogging suppresses aerobic decay
            else:
                f_redox = 1.0

            humified_input = c_input * alpha_hum
            total_c_humified += humified_input

            crop_decay = (ep.duration_days / 365.0) * f_redox * f_till
            weighted_decay_fraction += crop_decay

        # Account for uncultivated bare fallow days
        total_calendar_days = horizon_years * 365.0
        fallow_days = max(0.0, total_calendar_days - total_crop_days)
        fallow_decay = (fallow_days / 365.0) * 1.0 * 1.0
        weighted_decay_fraction += fallow_decay

        total_c_decomposed = soc_baseline * k_decomp * weighted_decay_fraction
        delta_soc_annual = (total_c_humified - total_c_decomposed) / float(horizon_years)

        soc_result = {
            "soc_baseline_t_c_ha": soc_baseline,
            "total_c_humified_t_c": total_c_humified,
            "total_c_decomposed_t_c": total_c_decomposed,
            "delta_soc_annual_t_c_ha": delta_soc_annual,
            "annual_soc_loss_pct": (delta_soc_annual / soc_baseline) * 100.0 if soc_baseline > 0 else 0.0
        }

        if delta_soc_annual < -0.30:
            issues.append(DetectedIssue(
                code="SEVERE_SOC_DEPLETION",
                severity="HIGH_RISK",
                stage="Stage 4",
                title="তীব্র জৈব কার্বন ক্ষয় (Severe Soil Organic Carbon Mining)",
                description=(
                    f"বার্ষিক মাটির জৈব কার্বন ক্ষয় {abs(delta_soc_annual):.3f} টন C/হেক্টর। "
                    f"পরপর কন্দ বা ভারী পুষ্টিগ্রাহী ফসলে অবশেষ সংরক্ষণ না করায় মাটির গঠন দুর্বল হচ্ছে।"
                ),
                penalty_points=20.0,
                suggested_action="খরিপ-১ এ মুগডাল বা ধৈঞ্চা সবুজ সার চাষ করে অবশেষ মাটিতে মিশিয়ে দিন।"
            ))
        elif delta_soc_annual < 0.0:
            issues.append(DetectedIssue(
                code="NEGATIVE_SOC_BALANCE",
                severity="MODERATE_WARNING",
                stage="Stage 4",
                title="মাটির জৈব পদার্থ ঘাটতি (Negative SOC Balance)",
                description=f"বার্ষিক জৈব কার্বন ব্যালেন্স সামান্য ঋণাত্মক ({delta_soc_annual:.3f} t C/ha)।",
                penalty_points=10.0,
                suggested_action="ফসল কাটার পর কমপক্ষে ২০ সেমি নাড়া (stubble) মাটিতে চাষ দিয়ে মিশিয়ে দিন।"
            ))

        return soc_result, issues

    @classmethod
    def audit_nutrient_balance(
        cls,
        episodes: List[CropEpisode],
        horizon_years: int = 1
    ) -> Tuple[Dict[str, float], List[DetectedIssue]]:
        """
        Calculates Net Nitrogen Balance (kg N/ha/year) across sequence.
        Factors in Legume Nitrogen Harvest Index (NHI = 0.70; Herridge et al., 2008).
        """
        issues: List[DetectedIssue] = []
        total_n_drawdown = 0.0
        total_bnf_residual_n = 0.0
        legume_count = 0

        for ep in episodes:
            if ep.is_fallow or ep.crop_name.lower().strip() == "fallow":
                continue
            crop_key = ep.crop_name.lower().strip()

            if ep.is_legume:
                legume_count += 1
                if "sesbania" in crop_key or "dhaincha" in crop_key:
                    # 100% biomass incorporated
                    residual_n = 60.0
                elif ep.stover_management == "incorporated":
                    # Grain exported (NHI=0.70), stover + nodules ploughed in
                    residual_n = 20.0
                else:
                    # Stover removed for cattle feed/fuel (net deficit)
                    residual_n = -10.0
                total_bnf_residual_n += residual_n
            else:
                # Find drawdown benchmark
                drawdown = 80.0
                for pattern, value in cls.N_DRAWDOWN_BENCHMARKS.items():
                    if pattern in crop_key:
                        drawdown = value
                        break
                total_n_drawdown += drawdown

        net_n_balance_annual = (total_bnf_residual_n - total_n_drawdown) / float(horizon_years)

        n_result = {
            "total_n_drawdown_kg_ha": total_n_drawdown,
            "total_bnf_residual_n_kg_ha": total_bnf_residual_n,
            "net_n_balance_annual_kg_ha": net_n_balance_annual,
            "legume_frequency_per_year": legume_count / float(horizon_years)
        }

        if net_n_balance_annual < -150.0:
            issues.append(DetectedIssue(
                code="EXHAUSTIVE_NUTRIENT_MINING",
                severity="HIGH_RISK",
                stage="Stage 4",
                title="তীব্র নাইট্রোজেন ক্ষয় ও পুষ্টি ঘাটতি (Exhaustive Soil Mining)",
                description=(
                    f"বার্ষিক নাইট্রোজেন ঘাটতি {abs(net_n_balance_annual):.1f} কেজি N/হেক্টর। "
                    f"কোনো ডাল বা সবুজ সার ছাড়াই পরপর ভারী পুষ্টিগ্রাহী ফসল চাষ করা হচ্ছে।"
                ),
                penalty_points=25.0,
                suggested_action="অন্তত একটি মৌসুমে মুগডাল বা ধৈঞ্চা অন্তর্ভুক্ত করে জৈব নাইট্রোজেন যোগ করুন।"
            ))
        elif net_n_balance_annual < -100.0:
            issues.append(DetectedIssue(
                code="MODERATE_NUTRIENT_DEFICIT",
                severity="MODERATE_WARNING",
                stage="Stage 4",
                title="মাঝারি পুষ্টি ঘাটতি (Moderate Nutrient Deficit)",
                description=f"বার্ষিক নাইট্রোজেন ঘাটতি {abs(net_n_balance_annual):.1f} kg N/ha।",
                penalty_points=12.0,
                suggested_action="পরিমিত সুষম সার (ইউরিয়া, টিএসপি, এমওপি, জিপসাম) প্রয়োগ নিশ্চিত করুন।"
            ))

        return n_result, issues

    @classmethod
    def audit_salinity(
        cls,
        episodes: List[CropEpisode],
        field_cond: FieldConditions
    ) -> Tuple[Dict[str, Any], List[DetectedIssue]]:
        """
        Calculates Maas-Hoffman piecewise linear crop yield reduction under soil salinity.
        Yrel = max(0, 100 - b * (ECe - a))
        """
        issues: List[DetectedIssue] = []
        ec_e = field_cond.soil_salinity_ec_e
        crop_responses: Dict[str, Dict[str, float]] = {}

        for ep in episodes:
            if ep.is_fallow or ep.crop_name.lower().strip() == "fallow":
                continue
            crop_key = ep.crop_name.lower().strip()
            cultivar_key = (ep.cultivar or "").lower().strip()

            # Check cultivar-specific override first (e.g. BRRI dhan67)
            params = None
            if "dhan67" in cultivar_key or "dhan67" in crop_key:
                params = cls.MAAS_HOFFMAN_PARAMS["brri dhan67"]
            elif "dhan97" in cultivar_key or "dhan97" in crop_key:
                params = cls.MAAS_HOFFMAN_PARAMS["brri dhan97"]
            else:
                for pat, p in cls.MAAS_HOFFMAN_PARAMS.items():
                    if pat in crop_key:
                        params = p
                        break

            if params is None:
                params = (ep.salinity_threshold_a or 3.0, ep.salinity_slope_b or 10.0)

            threshold_a, slope_b = params

            # In monsoon (Kharif-2), salinity is heavily diluted by floodwaters (dilution factor 0.35)
            effective_ec = ec_e * 0.35 if ep.season == "Kharif-2" else ec_e

            if effective_ec <= threshold_a:
                y_rel = 100.0
            else:
                y_rel = max(0.0, 100.0 - slope_b * (effective_ec - threshold_a))

            crop_responses[ep.crop_name] = {
                "threshold_a": threshold_a,
                "slope_b": slope_b,
                "effective_ec_e": effective_ec,
                "relative_yield_pct": y_rel
            }

            if y_rel < 40.0:
                issues.append(DetectedIssue(
                    code="CRITICAL_SALINITY_TOXICITY",
                    severity="CRITICAL_BLOCKER",
                    stage="Stage 3",
                    title=f"মারাত্মক লবণাক্ততার বিষাক্ততা: {ep.crop_name} (Fatal Salinity Failure)",
                    description=(
                        f"মাটির লবণাক্ততা {ec_e:.1f} dS/m এ {ep.crop_name} ফসলের প্রত্যাশিত ফলন মাত্র "
                        f"{y_rel:.1f}% (লবণ সহনশীলতার সীমা {threshold_a} dS/m)। ফসলটি সম্পূর্ণ নষ্ট হওয়ার ঝুঁকি রয়েছে।"
                    ),
                    penalty_points=50.0,
                    crop_affected=ep.crop_name,
                    suggested_action="লবণ সহনশীল ফসল (সূর্যমুখী, বার্লি, ব্রি ধান৬৭) নির্বাচন করুন।"
                ))
            elif y_rel < 75.0:
                issues.append(DetectedIssue(
                    code="HIGH_SALINITY_YIELD_LOSS",
                    severity="HIGH_RISK",
                    stage="Stage 3",
                    title=f"লবণাক্ততার কারণে ফলন হ্রাস: {ep.crop_name}",
                    description=f"লবণাক্ততার কারণে ফলন প্রায় {100.0 - y_rel:.1f}% কমে যাবে (ফলন {y_rel:.1f}%)।",
                    penalty_points=20.0,
                    crop_affected=ep.crop_name,
                    suggested_action="লবণ সহনশীল জাত ব্যবহার করুন এবং মালচিং প্রয়োগ করে বাষ্পীভবন কমান।"
                ))

        return {"crop_responses": crop_responses}, issues

    @classmethod
    def audit_soil_ph(
        cls,
        episodes: List[CropEpisode],
        field_cond: FieldConditions
    ) -> Tuple[float, List[DetectedIssue]]:
        """
        Evaluates crop suitability against local soil pH.
        SpH = 100 - 40 * |pH - Boundary|
        """
        issues: List[DetectedIssue] = []
        soil_ph = field_cond.soil_ph
        total_penalty = 0.0

        for ep in episodes:
            if ep.is_fallow or ep.crop_name.lower().strip() == "fallow":
                continue
            crop_key = ep.crop_name.lower().strip()
            opt_range = (5.5, 7.2)
            for pat, r in cls.PH_OPTIMUM_RANGES.items():
                if pat in crop_key:
                    opt_range = r
                    break

            ph_min, ph_max = opt_range
            if soil_ph < ph_min:
                diff = ph_min - soil_ph
                penalty = min(50.0, 40.0 * diff)
                total_penalty += penalty
                if penalty > 15.0:
                    issues.append(DetectedIssue(
                        code="SOIL_ACIDITY_STRESS",
                        severity="MODERATE_WARNING",
                        stage="Stage 4",
                        title=f"মাটির অম্লত্বজনিত চাপ: {ep.crop_name} (Soil Acidity Stress)",
                        description=(
                            f"মাটির pH {soil_ph:.1f} ফসলের কাঙ্ক্ষিত মাত্রা ({ph_min:.1f}) এর চেয়ে কম। "
                            f"ফসফরাস আবদ্ধ হওয়া ও অ্যালুমিনিয়াম বিষাক্ততার ঝুঁকি রয়েছে।"
                        ),
                        penalty_points=penalty,
                        crop_affected=ep.crop_name,
                        suggested_action="জমিতে ১.০-১.৫ টন/হেক্টর ডলোচুন (dololime) প্রয়োগ করুন।"
                    ))
            elif soil_ph > ph_max:
                diff = soil_ph - ph_max
                penalty = min(50.0, 40.0 * diff)
                total_penalty += penalty
                if penalty > 15.0:
                    issues.append(DetectedIssue(
                        code="SOIL_ALKALINITY_STRESS",
                        severity="MODERATE_WARNING",
                        stage="Stage 4",
                        title=f"মাটির ক্ষারত্বজনিত চাপ: {ep.crop_name}",
                        description=f"মাটির pH {soil_ph:.1f} ফসলের সর্বোচ্চ মাত্রা ({ph_max:.1f}) এর বেশি।",
                        penalty_points=penalty,
                        crop_affected=ep.crop_name,
                        suggested_action="জিপসাম সার ও জৈব কম্পোস্টের ব্যবহার বাড়ান।"
                    ))

        ph_subscore = max(0.0, 100.0 - total_penalty / max(1, len(episodes)))
        return ph_subscore, issues
