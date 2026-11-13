"""
models.py - Data Contracts & Schemas for Crop Sequence Evaluator DSS
Pure standard library dataclasses for input ingestion, biophysical auditing,
and explainable generative AI diagnostics.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class LocationInput:
    lat: float
    lon: float
    upazila: Optional[str] = None
    district: Optional[str] = None
    division: Optional[str] = None
    aez: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FieldConditions:
    land_type: str = "MHL"                       # HL, MHL, ML, LL, VLL
    soil_texture: str = "Silt Loam"
    soil_ph: float = 6.2
    soil_organic_carbon_pct: float = 1.10
    soil_salinity_ec_e: float = 0.80             # dS/m
    drainage_condition: str = "moderate"         # poor, moderate, good
    bulk_density: float = 1.50                   # g/cm3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FarmerPriorities:
    land_size_ha: float = 0.40
    total_budget_bdt: float = 120000.0
    irrigation_source: str = "shallow_tubewell"  # rainfed_only, shallow_tubewell, deep_tubewell, surface_canal
    water_cost_per_m3_bdt: float = 3.5
    food_security_staple_needed: bool = True
    risk_tolerance: str = "moderate"             # conservative, moderate, aggressive

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CropInput:
    year: int
    season: str                                  # Rabi, Kharif-1, Kharif-2, Fallow
    crop_name: str
    sowing_date_approx: Optional[str] = None     # YYYY-MM-DD
    cultivar: Optional[str] = None
    stover_management: str = "incorporated"      # removed, incorporated, grazed

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FarmerProfile:
    location: LocationInput
    field_conditions: FieldConditions
    farmer_priorities: FarmerPriorities
    farmer_evaluated_sequence: List[CropInput]
    target_horizon_years: int = 1
    preferences: Dict[str, Any] = field(default_factory=lambda: {"language": "bn", "tone": "farmer_friendly"})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location.to_dict(),
            "field_conditions": self.field_conditions.to_dict(),
            "farmer_priorities": self.farmer_priorities.to_dict(),
            "farmer_evaluated_sequence": [c.to_dict() for c in self.farmer_evaluated_sequence],
            "target_horizon_years": self.target_horizon_years,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FarmerProfile":
        loc_data = data.get("location", {})
        loc = LocationInput(
            lat=float(loc_data.get("lat", 24.7850)),
            lon=float(loc_data.get("lon", 89.0420)),
            upazila=loc_data.get("upazila"),
            district=loc_data.get("district"),
            division=loc_data.get("division"),
            aez=loc_data.get("aez")
        )

        fc_data = data.get("field_conditions", {})
        fc = FieldConditions(
            land_type=fc_data.get("land_type", "MHL"),
            soil_texture=fc_data.get("soil_texture", "Silt Loam"),
            soil_ph=float(fc_data.get("soil_ph", 6.2)),
            soil_organic_carbon_pct=float(fc_data.get("soil_organic_carbon_pct", 1.10)),
            soil_salinity_ec_e=float(fc_data.get("soil_salinity_ec_e", 0.80)),
            drainage_condition=fc_data.get("drainage_condition", "moderate"),
            bulk_density=float(fc_data.get("bulk_density", 1.50))
        )

        fp_data = data.get("farmer_priorities", {})
        fp = FarmerPriorities(
            land_size_ha=float(fp_data.get("land_size_ha", 0.40)),
            total_budget_bdt=float(fp_data.get("total_budget_bdt", 120000.0)),
            irrigation_source=fp_data.get("irrigation_source", "shallow_tubewell"),
            water_cost_per_m3_bdt=float(fp_data.get("water_cost_per_m3_bdt", 3.5)),
            food_security_staple_needed=bool(fp_data.get("food_security_staple_needed", True)),
            risk_tolerance=fp_data.get("risk_tolerance", "moderate")
        )

        seq_raw = data.get("farmer_evaluated_sequence", [])
        seq = [
            CropInput(
                year=int(item.get("year", 1)),
                season=str(item.get("season", "Rabi")),
                crop_name=str(item.get("crop_name", "")),
                sowing_date_approx=item.get("sowing_date_approx"),
                cultivar=item.get("cultivar"),
                stover_management=item.get("stover_management", "incorporated")
            )
            for item in seq_raw
        ]

        return cls(
            location=loc,
            field_conditions=fc,
            farmer_priorities=fp,
            farmer_evaluated_sequence=seq,
            target_horizon_years=int(data.get("target_horizon_years", 1)),
            preferences=data.get("preferences", {"language": "bn", "tone": "farmer_friendly"})
        )


@dataclass
class CropEpisode:
    year: int
    season: str
    crop_name: str
    duration_days: int
    start_day_offset: int
    botanical_family: str
    root_type: str
    is_legume: bool
    water_need_mm: float
    salinity_threshold_a: float
    salinity_slope_b: float
    flood_depth_tolerance_cm: float
    stover_management: str = "incorporated"
    cultivar: Optional[str] = None
    is_fallow: bool = False

    @property
    def end_day_offset(self) -> int:
        return self.start_day_offset + self.duration_days


@dataclass
class DetectedIssue:
    code: str
    severity: str                                # CRITICAL_BLOCKER, HIGH_RISK, MODERATE_WARNING, OPPORTUNITY
    stage: str                                   # Stage 2, Stage 3, Stage 4, Stage 5
    title: str
    description: str
    penalty_points: float
    crop_affected: Optional[str] = None
    suggested_action: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SmartSwapRecommendation:
    problematic_crop: str
    season: str
    year: int
    recommended_replacement: str
    botanical_family: str
    reason: str
    residual_n_gain_kg_ha: float
    projected_score_after_swap: float
    cost_delta_bdt: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DSSAdvisoryReport:
    advisory_summary: Dict[str, Any]
    nasa_climate_and_soil_insights: Dict[str, Any]
    socio_economic_budget_check: Dict[str, Any]
    critical_risks_explained: List[Dict[str, Any]]
    targeted_smart_swap: Optional[Dict[str, Any]]
    if_you_insist_on_original_sequence: List[str]
    upcoming_season_action_checklist: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SequenceAuditResult:
    farmer_profile: FarmerProfile
    overall_health_score: float
    grade: str                                   # A+, A, B, C, D, F
    risk_category: str                           # AGRO_ECOLOGICAL_EXCELLENCE, MODERATE_OPPORTUNITY, HIGH_AGRONOMIC_RISK, CRITICAL_BLOCKER
    sub_scores: Dict[str, float]                 # climate, hydrology, biology, soil, economics
    detected_issues: List[DetectedIssue]
    soc_trajectory: Dict[str, float]
    nitrogen_balance: Dict[str, float]
    water_balance: Dict[str, float]
    turnaround_gaps: List[Dict[str, Any]]
    episodes: List[CropEpisode]
    smart_swaps: List[SmartSwapRecommendation]
    cultural_mitigations: List[str]
    advisory_report: Optional[Dict[str, Any]] = None

    @property
    def composite_score(self) -> float:
        """Ergonomic alias for overall_health_score."""
        return self.overall_health_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "farmer_profile": self.farmer_profile.to_dict(),
            "overall_health_score": round(self.overall_health_score, 1),
            "grade": self.grade,
            "risk_category": self.risk_category,
            "sub_scores": {k: round(v, 1) for k, v in self.sub_scores.items()},
            "detected_issues": [issue.to_dict() for issue in self.detected_issues],
            "soc_trajectory": {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in self.soc_trajectory.items()},
            "nitrogen_balance": {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in self.nitrogen_balance.items()},
            "water_balance": {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in self.water_balance.items()},
            "turnaround_gaps": self.turnaround_gaps,
            "smart_swaps": [swap.to_dict() for swap in self.smart_swaps],
            "cultural_mitigations": self.cultural_mitigations,
            "advisory_report": self.advisory_report
        }
