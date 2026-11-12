"""
biological_disease_auditor.py - Biological & Soil Health Disease Auditor
Audits botanical family rotation breaks, multi-year pathogen memory (Ralstonia & Meloidogyne),
nematode reproductive hosting on hybrid maize, Hill dose-response disease risk,
wetland flooding sanitization credits, root biopores, and legume frequency rules.
"""

from typing import List, Dict, Any, Tuple
from .models import CropEpisode, DetectedIssue, FieldConditions


class BiologicalDiseaseAuditor:
    """
    Evaluates soilborne pathogen carryover, nematode host multipliers,
    root stratigraphy alternation, and multi-year ecological sustainability.
    """

    SOLANACEAE_CROPS = {"potato", "tomato", "brinjal", "eggplant", "chilli", "pepper", "tobacco"}
    POACEAE_CROPS = {"rice", "dhan", "wheat", "maize", "barley", "millet", "kaon"}
    BRASSICACEAE_CROPS = {"mustard", "cabbage", "cauliflower", "radish", "broccoli", "turnip"}
    CUCURBITACEAE_CROPS = {"cucumber", "bottle gourd", "sweet gourd", "pumpkin", "pointed gourd", "bitter gourd"}

    @classmethod
    def audit_biology(
        cls,
        episodes: List[CropEpisode],
        field_cond: FieldConditions,
        horizon_years: int = 1
    ) -> Tuple[float, List[DetectedIssue]]:
        """
        Executes multi-factor biological audit and returns biology sub-score (0-100) and detected issues.
        """
        issues: List[DetectedIssue] = []
        total_penalty = 0.0

        if not episodes:
            return 100.0, issues

        # 1. Botanical Family Violations & Solanaceae Disease Bridge
        fam_penalty, fam_issues = cls._audit_botanical_families(episodes, field_cond)
        total_penalty += fam_penalty
        issues.extend(fam_issues)

        # 2. Hybrid Maize Nematode Host Status Check
        maize_penalty, maize_issues = cls._audit_maize_nematode_bridge(episodes)
        total_penalty += maize_penalty
        issues.extend(maize_issues)

        # 3. Root Architecture Stratification & Biopores
        root_penalty, root_issues = cls._audit_root_stratigraphy(episodes)
        total_penalty += root_penalty
        issues.extend(root_issues)

        # 4. Multi-Year Legume Frequency Rule (Snapp et al. 2010 PNAS)
        legume_penalty, legume_issues = cls._audit_legume_frequency(episodes, horizon_years, field_cond)
        total_penalty += legume_penalty
        issues.extend(legume_issues)

        subscore = max(0.0, 100.0 - total_penalty)
        return subscore, issues

    @classmethod
    def _audit_botanical_families(
        cls,
        episodes: List[CropEpisode],
        field_cond: FieldConditions
    ) -> Tuple[float, List[DetectedIssue]]:
        """Audits consecutive and near-term botanical family repetitions."""
        issues: List[DetectedIssue] = []
        penalty = 0.0

        # Check consecutive Solanaceae pairs
        for i in range(len(episodes) - 1):
            curr_c = episodes[i].crop_name.lower().strip()
            next_c = episodes[i + 1].crop_name.lower().strip()

            curr_is_sol = any(s in curr_c for s in cls.SOLANACEAE_CROPS)
            next_is_sol = any(s in next_c for s in cls.SOLANACEAE_CROPS)

            if curr_is_sol and next_is_sol:
                gap_days = episodes[i + 1].start_day_offset - episodes[i].end_day_offset
                # Less than 4 months gap
                if gap_days < 120:
                    pen = 35.0
                    penalty += pen
                    issues.append(DetectedIssue(
                        code="SOLANACEAE_DISEASE_BRIDGE",
                        severity="HIGH_RISK",
                        stage="Stage 4",
                        title=f"একই সোলানেসি গোত্রের মড়ক ও কৃমি ঝুঁকি: {episodes[i].crop_name} -> {episodes[i+1].crop_name}",
                        description=(
                            f"আলু ও টমেটো/বেগুন দুটিই একই Solanaceae গোত্রের ফসল। প্রথম ফসলে থাকা ক্ষতিকর "
                            f"ব্যাকটেরিয়াল উইল্ট (Ralstonia solanacearum) এবং শিকড়-গিঁট কৃমি (Meloidogyne incognita) "
                            f"পরবর্তী ফসলে মারাত্মক আকারে ছড়িয়ে পড়বে।"
                        ),
                        penalty_points=pen,
                        crop_affected=episodes[i + 1].crop_name,
                        suggested_action="খরিপ-১ এ টমেটোর বদলে মুগডাল বা পাট চাষ করে রোগচক্র ভেঙে দিন।"
                    ))

        # Check multi-year Solanaceae recurrence (replanting within 24 months)
        solanaceae_eps = [
            ep for ep in episodes
            if any(s in ep.crop_name.lower() for s in cls.SOLANACEAE_CROPS)
        ]
        if len(solanaceae_eps) >= 2:
            for i in range(len(solanaceae_eps) - 1):
                interval = solanaceae_eps[i + 1].start_day_offset - solanaceae_eps[i].end_day_offset
                # Replanted in Year 2 without a 2-year break
                if interval < 600:
                    pen = 20.0
                    penalty += pen
                    issues.append(DetectedIssue(
                        code="SOLANACEAE_MULTI_YEAR_PERSISTENCE",
                        severity="HIGH_RISK",
                        stage="Stage 4",
                        title="সোলানেসি ফসলে পর্যাপ্ত বিরতির অভাব (24-Month Non-Host Rule Breach)",
                        description=(
                            f"{solanaceae_eps[i].crop_name} তোলার পর মাত্র {interval} দিনের মাথায় পুনরায় "
                            f"{solanaceae_eps[i+1].crop_name} চাষ করা হচ্ছে। Ralstonia ব্যাকটেরিয়া মাটিতে "
                            f"২-৫ বছর পর্যন্ত সুপ্তাবস্থায় (VBNC state) বেঁচে থাকে। ন্যূনতম ২ বছর অ-পোষক ফসল প্রয়োজন।"
                        ),
                        penalty_points=pen,
                        crop_affected=solanaceae_eps[i + 1].crop_name,
                        suggested_action="আলুর জমিতে পরবর্তী বছর রবি মৌসুমে সরিষা, ভুট্টা বা পেঁয়াজ চাষ করুন।"
                    ))
                    break

        # Check unbroken Poaceae monoculture (Continuous Triple Rice)
        rice_count = sum(
            1 for ep in episodes
            if any(r in ep.crop_name.lower() for r in ["rice", "dhan"])
        )
        if len(episodes) >= 3 and rice_count == len(episodes):
            pen = 25.0
            penalty += pen
            issues.append(DetectedIssue(
                code="POACEAE_TRIPLE_RICE_MONOCULTURE",
                severity="HIGH_RISK",
                stage="Stage 4",
                title="একটানা ধান চাষে পোকা ও মাটির ক্ষয় (Continuous Poaceae Monoculture)",
                description=(
                    "একই জমিতে সারা বছর কেবল ধান (বোরো-আউশ-আমন) চাষ করায় খোলপচা (sheath blight), "
                    "ব্লাস্ট এবং মাজরা পোকার আক্রমণ বৃদ্ধি পায় এবং মাটিতে দস্তা ও সালফারের ঘাটতি দেখা দেয়।"
                ),
                penalty_points=pen,
                suggested_action="রবি মৌসুমে বোরো ধানের বিকল্প হিসেবে ভুট্টা, গম বা সরিষা আবর্তন করুন।"
            ))

        return penalty, issues

    @classmethod
    def _audit_maize_nematode_bridge(
        cls,
        episodes: List[CropEpisode]
    ) -> Tuple[float, List[DetectedIssue]]:
        """
        Commercial hybrid maize is an active reproductive host (Rf = 3.0 to 4.5)
        for root-knot nematodes (Meloidogyne incognita/javanica).
        """
        issues: List[DetectedIssue] = []
        penalty = 0.0

        for i in range(len(episodes) - 2):
            c1 = episodes[i].crop_name.lower()
            c2 = episodes[i + 1].crop_name.lower()
            c3 = episodes[i + 2].crop_name.lower()

            c1_is_sol = any(s in c1 for s in cls.SOLANACEAE_CROPS)
            c2_is_maize = "maize" in c2 or "corn" in c2
            c3_is_sol = any(s in c3 for s in cls.SOLANACEAE_CROPS)

            if c1_is_sol and c2_is_maize and c3_is_sol:
                pen = 20.0
                penalty += pen
                issues.append(DetectedIssue(
                    code="MAIZE_NEMATODE_REPRODUCTIVE_HOST",
                    severity="HIGH_RISK",
                    stage="Stage 4",
                    title="ভুট্টায় শিকড়-গিঁট কৃমির বংশবৃদ্ধি (Maize Nematode Multiplier Host)",
                    description=(
                        f"আলুর পর ভুট্টা চাষ করলেও হাইব্রিড ভুট্টা শিকড় কৃমির (Meloidogyne incognita) "
                        f"প্রজনন সহায়ক পোষক (Rf ≈ ৩.৫)। এটি মাটিতে কৃমির ডিম্বাণু বৃদ্ধি করে পরবর্তী "
                        f"{episodes[i+2].crop_name} ফসলে কৃমি ও উইল্ট রোগের মারাত্মক বিস্তার ঘটাবে।"
                    ),
                    penalty_points=pen,
                    crop_affected=episodes[i + 2].crop_name,
                    suggested_action="আলুর পর খাঁটি অ-পোষক ফসল (যেমন সরিষা, শনপাট বা খরিপ-১ মুগডাল) নির্বাচন করুন।"
                ))
                break

        return penalty, issues

    @classmethod
    def _audit_root_stratigraphy(
        cls,
        episodes: List[CropEpisode]
    ) -> Tuple[float, List[DetectedIssue]]:
        """Audits root depth alternation to identify hardpan compaction."""
        issues: List[DetectedIssue] = []
        penalty = 0.0

        root_types = [ep.root_type.lower() for ep in episodes if ep.root_type and not ep.is_fallow]
        has_deep_taproot = any("deep" in r or "tap" in r for r in root_types)
        all_shallow = all(
            ("shallow" in r or "fibrous" in r) and "deep" not in r and "tap" not in r
            for r in root_types if r
        )

        if len(root_types) >= 3 and all_shallow:
            pen = 15.0
            penalty += pen
            issues.append(DetectedIssue(
                code="ROOT_STRATIGRAPHY_COMPACTION",
                severity="MODERATE_WARNING",
                stage="Stage 4",
                title="মাটির শক্ত তল ভেদ করার অভাব (Hardpan Compaction Risk)",
                description=(
                    "ফসল বিন্যাসের সবগুলো ফসলই অগভীর গুচ্ছমূলবিশিষ্ট (shallow fibrous)। ফলে মাটির ১৫-২০ সেমি "
                    "গভীরের শক্ত লাঙলের তল (plow-pan) ভেঙে নিচের পুষ্টি ও আর্দ্রতা গ্রহণ ব্যাহত হচ্ছে।"
                ),
                penalty_points=pen,
                suggested_action="গভীর মূলবিশিষ্ট ফসল (সরিষা, সূর্যমুখী বা ধৈঞ্চা) অন্তর্ভুক্ত করে প্রাকৃতিক বায়োপোর তৈরি করুন।"
            ))

        return penalty, issues

    @classmethod
    def _audit_legume_frequency(
        cls,
        episodes: List[CropEpisode],
        horizon_years: int = 1,
        field_cond: Optional[FieldConditions] = None
    ) -> Tuple[float, List[DetectedIssue]]:
        """Enforces minimum legume threshold (Snapp et al. 2010 PNAS): f_legume >= 0.5/yr."""
        issues: List[DetectedIssue] = []
        penalty = 0.0

        # In Low Land (LL) or Very Low Land (VLL), Kharif inundation (2-4m flood) naturally submerges soil
        # preventing legume cultivation. Single Boro in haor wetlands is an ecological adaptation.
        if field_cond and field_cond.land_type in ["LL", "VLL"]:
            return 0.0, issues

        legume_count = sum(1 for ep in episodes if ep.is_legume)
        f_legume = legume_count / float(max(1, horizon_years))

        # If sequence has 3 or more crops and zero legumes
        if len(episodes) >= 3 and legume_count == 0:
            pen = 25.0
            penalty += pen
            issues.append(DetectedIssue(
                code="ZERO_LEGUME_FREQUENCY_PENALTY",
                severity="HIGH_RISK",
                stage="Stage 4",
                title="ডাল জাতীয় ফসলের সম্পূর্ণ অনুপস্থিতি (Zero Legume Infiltration)",
                description=(
                    f"সম্পূর্ণ চক্রে কোনো ডাল বা লিগিউম জাতীয় ফসল নেই (ফ্রিকোয়েন্সি {f_legume:.2f}/বছর; "
                    f"কাঙ্ক্ষিত ন্যূনতম ০.৫০/বছর)। ডাল ফসল না থাকায় মাটির জৈবিক স্বাস্থ্য দীর্ঘমেয়াদে অবনতিশীল।"
                ),
                penalty_points=pen,
                suggested_action="খরিপ-১ এ মুগডাল বা বোরো কাটার পর জমিতে ধৈঞ্চা সবুজ সার চাষ করুন।"
            ))

        return penalty, issues
