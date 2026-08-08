"""Canonical well identity, operational status, and geographic location."""

from enum import Enum
from pydantic import Field

from app.schemas.base import SchemaBase


class WellStatus(str, Enum):
    """Field-verified availability of a registered water source."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"


class Location(SchemaBase):
    """Validated geographic coordinates and their coordinate reference system."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    crs: str = "EPSG:4326"


class AdministrativeArea(SchemaBase):
    """Optional administrative labels associated with a well."""

    district: str | None = None
    ward: str | None = None


class Well(SchemaBase):
    """Canonical well record shared by APIs, model input, and guidance services."""

    well_id: str
    site_name: str | None = None
    status: WellStatus = WellStatus.UNKNOWN
    location: Location
    administrative_area: AdministrativeArea | None = None
