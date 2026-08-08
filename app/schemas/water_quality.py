"""Laboratory or field measurements collected from a registered well."""

from datetime import date
from pydantic import Field

from app.schemas.base import SchemaBase


class WaterQualityMeasurement(SchemaBase):
    """Validated contaminant and chemistry measurements for one sample."""

    sample_id: str
    well_id: str

    fluoride_mg_L: float | None = Field(default=None, ge=0)
    ph: float | None = Field(default=None, ge=0, le=14)
    ec_uS_cm: float | None = Field(default=None, ge=0)
    tds_mg_L: float | None = Field(default=None, ge=0)
    ecoli_cfu_100ml: float | None = Field(default=None, ge=0)

    sample_collection_date: date | None = None
    notes: str | None = None
