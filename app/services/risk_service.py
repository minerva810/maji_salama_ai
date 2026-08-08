"""Domain thresholds that map contaminant measurements to risk levels."""

from math import isfinite

from app.schemas.model_output import RiskLevel


def classify_fluoride(value: float | None) -> RiskLevel:
    """Classify fluoride concentration in mg/L using project thresholds."""

    if value is None or not isfinite(value) or value < 0:
        return RiskLevel.UNKNOWN
    if value <= 1.5:
        return RiskLevel.LOW
    if value <= 3.0:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH


def classify_bacterial(value: float | None) -> RiskLevel:
    """Classify E. coli concentration in CFU/100mL using project thresholds."""

    if value is None or not isfinite(value) or value < 0:
        return RiskLevel.UNKNOWN
    if value < 1:
        return RiskLevel.LOW
    if value <= 10:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH
