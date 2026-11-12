"""
Crop Sequence Evaluator & Diagnostic Advisory Decision Support System (DSS)
Designed for the NASA Space Apps Challenge ("Field Shift: Adapting Farms with NASA Data").

Deterministic biophysical audit (Stages 1-5) and explainable AI advisory (Stage 6).
"""

from .models import (
    FarmerProfile,
    LocationInput,
    FieldConditions,
    FarmerPriorities,
    CropEpisode,
    SequenceAuditResult,
    SmartSwapRecommendation,
    DetectedIssue,
    DSSAdvisoryReport,
)
from .evaluator_engine import CropSequenceEvaluatorEngine

__all__ = [
    "FarmerProfile",
    "LocationInput",
    "FieldConditions",
    "FarmerPriorities",
    "CropEpisode",
    "SequenceAuditResult",
    "SmartSwapRecommendation",
    "DetectedIssue",
    "DSSAdvisoryReport",
    "CropSequenceEvaluatorEngine",
]
