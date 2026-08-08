"""User-facing safety guidance derived from contamination predictions."""

from pydantic import Field

from app.schemas.base import SchemaBase
from app.schemas.model_output import RiskLevel
from app.schemas.well import WellStatus


class RiskResult(SchemaBase):
    """Combined contamination risk information for a well."""

    fluoride: RiskLevel = RiskLevel.UNKNOWN
    bacterial: RiskLevel = RiskLevel.UNKNOWN


class AlternativeWell(SchemaBase):
    """Alternative source with availability status for safe recommendation use."""

    well_id: str
    status: WellStatus

    distance_km: float = Field(
        ...,
        ge=0,
    )

    site_name: str | None = None


class GuidanceAction(SchemaBase):
    """
    A recommended action based on predicted contamination risk.

    Actions may instruct users to avoid drinking, disinfect water, or apply
    contaminant-specific treatment.
    """

    action: str
    reason: str | None = None


class GuidanceResponse(SchemaBase):
    """
    Final service response generated from model predictions.
    """

    well_id: str

    risk: RiskResult

    actions: list[GuidanceAction] = Field(default_factory=list)

    alternative_well: AlternativeWell | None = None

    message: str | None = None
