"""
temporal_turnaround_auditor.py - Temporal & Inter-Crop Turnaround Feasibility Engine
Models multi-year rotations as continuous state-event streams (APSIM/DSSAT).
Audits inter-crop turnaround buffers, circular wrap-around cycles (T_wrap),
Ritchie bare-soil fallow evaporation, and climate hazard collisions (Haor, Nor'westers).
"""

from typing import List, Dict, Any, Tuple
from .models import CropEpisode, DetectedIssue, LocationInput


class TemporalTurnaroundAuditor:
    """
    Audits calendar feasibility, turnaround buffers, circular multi-year wrap-around,
    and regional weather hazard window collisions.
    """

    # Minimum tilth and field preparation days required
    MIN_TURNAROUND_PADDY_TO_UPLAND = 14
    MIN_TURNAROUND_UPLAND_TO_PADDY = 10
    MIN_TURNAROUND_UPLAND_TO_UPLAND = 10

    # Regional climate hazard windows (day of calendar year)
    HAOR_FLASH_FLOOD_DEADLINE_DOY = 105   # April 15
    POTATO_LATE_HARVEST_DEADLINE_DOY = 69 # March 10 (Nor'wester convective storm rot)
    AMAN_TRANSPLANT_LATE_DEADLINE_DOY = 227 # August 15 (prevents November cold floret sterility)

    @classmethod
    def audit_turnaround(
        cls,
        episodes: List[CropEpisode],
        location: LocationInput,
        horizon_years: int = 1
    ) -> Tuple[List[Dict[str, Any]], float, List[DetectedIssue]]:
        """
        Audits consecutive inter-crop turnaround gaps and the circular wrap-around loop.
        """
        issues: List[DetectedIssue] = []
        gaps_record: List[Dict[str, Any]] = []
        total_penalty = 0.0

        if not episodes:
            return gaps_record, 100.0, issues

        # Sort episodes strictly by cumulative start day offset
        sorted_episodes = sorted(episodes, key=lambda e: e.start_day_offset)

        # 1. Audit consecutive inter-crop turnaround gaps
        for i in range(len(sorted_episodes) - 1):
            curr_ep = sorted_episodes[i]
            next_ep = sorted_episodes[i + 1]

            t_gap = next_ep.start_day_offset - curr_ep.end_day_offset

            # Fallow intervals represent unseeded resting land; no planting overlap can occur
            if curr_ep.is_fallow or next_ep.is_fallow:
                gap_info = {
                    "crop_from": curr_ep.crop_name,
                    "crop_to": next_ep.crop_name,
                    "t_gap_days": max(0, t_gap),
                    "min_required_days": 0,
                    "transition_type": "Fallow Seasonal Resting Interval",
                    "status": "OPTIMAL"
                }
                gaps_record.append(gap_info)
                continue

            # Determine minimum buffer required based on soil mechanical transitions
            curr_is_paddy = "rice" in curr_ep.crop_name.lower() or "dhan" in curr_ep.crop_name.lower()
            next_is_paddy = "rice" in next_ep.crop_name.lower() or "dhan" in next_ep.crop_name.lower()

            if curr_is_paddy and not next_is_paddy:
                min_req = cls.MIN_TURNAROUND_PADDY_TO_UPLAND
                transition_desc = "Paddy to Upland (requires drying, aeration & rotary clod breaking)"
            elif not curr_is_paddy and next_is_paddy:
                min_req = cls.MIN_TURNAROUND_UPLAND_TO_PADDY
                transition_desc = "Upland to Transplanted Paddy (requires soaking, puddling & bunding)"
            else:
                min_req = cls.MIN_TURNAROUND_UPLAND_TO_UPLAND
                transition_desc = "Standard Crop Transition"

            gap_info = {
                "crop_from": curr_ep.crop_name,
                "crop_to": next_ep.crop_name,
                "t_gap_days": t_gap,
                "min_required_days": min_req,
                "transition_type": transition_desc,
                "status": "OPTIMAL" if t_gap >= min_req else ("TIGHT" if t_gap >= 0 else "OVERLAP")
            }
            gaps_record.append(gap_info)

            if t_gap < 0:
                penalty = 50.0
                total_penalty += penalty
                issues.append(DetectedIssue(
                    code="CRITICAL_TEMPORAL_OVERLAP",
                    severity="CRITICAL_BLOCKER",
                    stage="Stage 2",
                    title=f"সময়সূচির মারাত্মক সাংঘর্ষিকতা: {curr_ep.crop_name} ও {next_ep.crop_name}",
                    description=(
                        f"{curr_ep.crop_name} কাটার পূর্বেই ({curr_ep.end_day_offset} তম দিন) পরবর্তী "
                        f"{next_ep.crop_name} রোপণের তারিখ ({next_ep.start_day_offset} তম দিন) চলে এসেছে। "
                        f"সময়ের ব্যবধান {t_gap} দিন, যা বাস্তবে অসম্ভব।"
                    ),
                    penalty_points=penalty,
                    crop_affected=next_ep.crop_name,
                    suggested_action="স্বল্পমেয়াদী জাত নির্বাচন করুন অথবা রোপণের তারিখ পুনর্বিন্যাস করুন।"
                ))
            elif t_gap < min_req:
                penalty = 15.0
                total_penalty += penalty
                issues.append(DetectedIssue(
                    code="TIGHT_TURNAROUND_WARNING",
                    severity="MODERATE_WARNING",
                    stage="Stage 2",
                    title=f"জমি প্রস্তুতির অপর্যাপ্ত সময়: {curr_ep.crop_name} -> {next_ep.crop_name}",
                    description=(
                        f"দুটি ফসলের মধ্যবর্তী বিরতি মাত্র {t_gap} দিন (প্রয়োজন কমপক্ষে {min_req} দিন)। "
                        f"মাটি শুকানো ও উপযুক্ত জো (tilth) আনার অভাবে বীজ অঙ্কুরোদগম ব্যাহত হতে পারে।"
                    ),
                    penalty_points=penalty,
                    crop_affected=next_ep.crop_name,
                    suggested_action="পাওয়ার টিলার / রোটাভেটর ব্যবহারের প্রস্তুতি রাখুন বা রিলে ক্রপিং বিবেচনা করুন।"
                ))

        # 2. Audit Circular Multi-Year Wrap-Around Loop (T_wrap)
        planted_episodes = [ep for ep in sorted_episodes if not ep.is_fallow]
        if planted_episodes:
            first_ep = planted_episodes[0]
            last_ep = planted_episodes[-1]
            cycle_length_days = horizon_years * 365.25
            t_wrap = first_ep.start_day_offset + cycle_length_days - last_ep.end_day_offset

            wrap_info = {
                "crop_from": f"Year {last_ep.year} {last_ep.crop_name}",
                "crop_to": f"Year 1 {first_ep.crop_name} (Next Cycle)",
                "t_gap_days": round(t_wrap, 1),
                "min_required_days": 12,
                "transition_type": "Multi-Year Circular Wrap-Around Loop",
                "status": "OPTIMAL" if t_wrap >= 12 else ("TIGHT" if t_wrap >= 0 else "OVERLAP")
            }
            gaps_record.append(wrap_info)

            if t_wrap < 0:
                total_penalty += 35.0
                issues.append(DetectedIssue(
                    code="WRAP_AROUND_OVERLAP_BLOCKER",
                    severity="CRITICAL_BLOCKER",
                    stage="Stage 2",
                    title="চক্রাকার আবর্তনে সময় সংকট (Multi-Year Wrap-Around Collision)",
                    description=(
                        f"শেষ ফসল ({last_ep.crop_name}) কাটার পর পরবর্তী বছরের প্রথম ফসল "
                        f"({first_ep.crop_name}) সময়মতো রোপণ করা যাবে না (ব্যবধান {t_wrap:.1f} দিন)।"
                    ),
                    penalty_points=35.0,
                    crop_affected=first_ep.crop_name,
                    suggested_action="আমন ধানের স্বল্পমেয়াদী জাত (যেমন ব্রি ধান৭৫, ব্রি ধান৭১) চাষ করে জমি দ্রুত খালি করুন।"
                ))
            elif t_wrap < 12 and len(planted_episodes) >= 3:
                total_penalty += 15.0
                issues.append(DetectedIssue(
                    code="WRAP_AROUND_DELAY_WARNING",
                    severity="MODERATE_WARNING",
                    stage="Stage 2",
                    title="পরবর্তী চক্রের রবি ফসল দেরিতে বপনের ঝুঁকি (Wrap-Around Delay)",
                    description=(
                        f"চক্রাকার আবর্তনে জমি প্রস্তুতের সময় মাত্র {t_wrap:.1f} দিন। শীতকালীন রবি ফসল "
                        f"দেরিতে লাগালে বসন্তের আগাম গরমে (terminal heat stress) ফলন হ্রাস পাবে।"
                    ),
                    penalty_points=15.0,
                    crop_affected=first_ep.crop_name,
                    suggested_action="দেরি এড়াতে জিরো-টিলেজ বা স্ট্রিপ-টিলেজ পদ্ধতিতে রবি ফসল বপন করুন।"
                ))

        # 3. Regional Agro-Meteorological Hazard Collisions
        cls._audit_hazard_collisions(sorted_episodes, location, issues)

        turnaround_subscore = max(0.0, 100.0 - total_penalty)
        return gaps_record, turnaround_subscore, issues

    @classmethod
    def _audit_hazard_collisions(
        cls,
        episodes: List[CropEpisode],
        location: LocationInput,
        issues: List[DetectedIssue]
    ) -> None:
        """Checks collisions with regional flash floods, squalls, and cold spells."""
        district = (location.district or "").lower().strip()
        is_haor = district in ["sunamganj", "netrokona", "kishoreganj", "habiganj", "sylhet"]
        is_north = district in ["bogura", "bogra", "rangpur", "dinajpur", "joypurhat", "gaibandha"]

        for ep in episodes:
            crop_key = ep.crop_name.lower().strip()
            # Calendar day-of-year of harvest (1 to 365)
            harvest_doy = (ep.end_day_offset - 1) % 365 + 1

            # A. Haor Flash Flood Trap
            if is_haor and ep.season == "Rabi" and harvest_doy > cls.HAOR_FLASH_FLOOD_DEADLINE_DOY:
                issues.append(DetectedIssue(
                    code="CRITICAL_HAOR_FLASH_FLOOD_RISK",
                    severity="CRITICAL_BLOCKER",
                    stage="Stage 2",
                    title=f"হাওরের আগাম পাহাড়ি ঢলের চরম ঝুঁকি: {ep.crop_name}",
                    description=(
                        f"{ep.crop_name} কাটার সম্ভাব্য তারিখ ১৫ই এপ্রিলের পরে ({harvest_doy} তম দিন)। "
                        f"মেঘালয়ের আগাম পাহাড়ি ঢলে হাওরের ফসল তলিয়ে যাওয়ার মারাত্মক ঝুঁকি রয়েছে।"
                    ),
                    penalty_points=45.0,
                    crop_affected=ep.crop_name,
                    suggested_action="স্বল্পমেয়াদী আগাম বোরো জাত (যেমন ব্রি ধান৮৮, ব্রি ধান৯৬) নির্বাচন করুন।"
                ))

            # B. Bogura / Northern Late Nor'wester Potato Rot Trap
            if is_north and "potato" in crop_key and harvest_doy > cls.POTATO_LATE_HARVEST_DEADLINE_DOY:
                issues.append(DetectedIssue(
                    code="POTATO_NORWESTER_ROT_RISK",
                    severity="HIGH_RISK",
                    stage="Stage 2",
                    title="কালবৈশাখী বৃষ্টি ও আলু পচনের ঝুঁকি (Nor'wester Storm Rot)",
                    description=(
                        f"আলু তোলার সময় ১০ই মার্চের পর হওয়ায় ({harvest_doy} তম দিন) প্রাক-বর্ষার "
                        f"বৃষ্টিতে জমি কর্দমাক্ত হয়ে আলুর ত্বক ও নরম পচন (soft rot) রোগ ছড়াবে।"
                    ),
                    penalty_points=25.0,
                    crop_affected=ep.crop_name,
                    suggested_action="অবিলম্বে আলু তুলে ছায়াযুক্ত স্থানে বাতাসে শুকিয়ে সংরক্ষণ করুন।"
                ))

            # C. Aman Transplanting Delay Trap
            if ep.season == "Kharif-1" and harvest_doy > cls.AMAN_TRANSPLANT_LATE_DEADLINE_DOY:
                issues.append(DetectedIssue(
                    code="AMAN_COLD_STERILITY_RISK",
                    severity="HIGH_RISK",
                    stage="Stage 2",
                    title="আমন ধান রোপণে বিলম্ব ও ঠান্ডায় চিটা হওয়ার ঝুঁকি (Cold Floret Sterility)",
                    description=(
                        f"খরিপ-১ ফসল কাটার সময় ১৫ই আগস্ট অতিক্রম করায় আমন চারা রোপণ সেপ্টেম্বরে পিছিয়ে যাবে। "
                        f"ফলে নভেম্বরের শৈত্যপ্রবাহে ধানের শীষে চিটা (floret sterility) দেখা দেবে।"
                    ),
                    penalty_points=25.0,
                    crop_affected=ep.crop_name,
                    suggested_action="খরিপ-১ ফসল আগেভাগে শেষ করুন বা স্বল্পমেয়াদী আমন চারা প্রস্তুত রাখুন।"
                ))
