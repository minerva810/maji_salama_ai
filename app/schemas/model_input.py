"""Versioned input contract shared by the backend and model adapters."""

from pydantic import Field

from app.schemas.base import SchemaBase
from app.schemas.environment import Environment
from app.schemas.well import Well


class ModelInput(SchemaBase):
    """
    Standard input contract between the backend and AI models.

    Every prediction model should receive data in this structure.
    Model-specific feature extraction belongs in the relevant model adapter.
    """

    schema_version: str = "1.0"
    request_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for this prediction request",
    )

    well: Well
    environment: Environment
