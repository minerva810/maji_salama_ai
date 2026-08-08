"""Environmental features associated with a groundwater prediction request."""

from pydantic import Field

from app.schemas.base import SchemaBase


class ClimateFeatures(SchemaBase):
    """Seasonal climate observations used by contamination models."""

    year: int | None = None
    season: str | None = None
    total_season_rain_mm: float | None = None


class SoilFeatures(SchemaBase):
    """Soil chemistry measurements matched to a well location."""

    ph: float | None = Field(default=None, ge=0, le=14)
    calcium_extractable: float | None = None
    magnesium_extractable: float | None = None
    organic_carbon: float | None = None
    iron_extractable: float | None = None

class GeologyFeatures(SchemaBase):
    """GLiM lithology attributes matched to a well location."""

    glim_id: str | None = None
    lithology_code: str | None = None
    lithology_class: str | None = None
    lithology_detail: str | None = None


class DataQuality(SchemaBase):
    """Provenance and spatial-match quality for environmental features."""

    soil_source_latitude: float | None = None
    soil_source_longitude: float | None = None
    soil_match_distance_km: float | None = None

    lithology_match_method: str | None = None
    lithology_match_distance_km: float | None = None

class Environment(SchemaBase):
    """Grouped environmental context supplied to model feature extraction."""

    climate: ClimateFeatures | None = None
    soil: SoilFeatures | None = None
    geology: GeologyFeatures | None = None
    data_quality: DataQuality | None = None
