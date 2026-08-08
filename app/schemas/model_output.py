"""Versioned output contract returned by every contamination model."""

from enum import Enum
from pydantic import Field

from app.schemas.base import SchemaBase


class RiskLevel(str, Enum):
    """Normalized severity shared by prediction and guidance responses."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class ModelInfo(SchemaBase):
    """Metadata identifying the model that generated the prediction."""

    name: str
    version: str
    target: str


class PredictionValue(SchemaBase):
    """Standardized prediction result."""

    value: float | None = None
    unit: str | None = None
    risk_level: RiskLevel


class Confidence(SchemaBase):
    """
    Optional model confidence.

    Only use this field when the model has a meaningful confidence
    or calibrated probability value.
    """

    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class PredictionOutput(SchemaBase):
    """
    Standard output contract returned by every AI model.
    """

    schema_version: str = "1.0"
    request_id: str

    model: ModelInfo
    prediction: PredictionValue

    confidence: Confidence | None = None

    warnings: list[str] = Field(default_factory=list)
