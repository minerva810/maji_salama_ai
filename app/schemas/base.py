"""Shared validation policy for all API and domain schemas."""

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """Reject undeclared fields so malformed payloads fail immediately."""

    model_config = ConfigDict(extra="forbid")
