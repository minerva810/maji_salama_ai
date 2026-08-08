"""HTTP endpoints that convert model risks into user-facing safety guidance."""

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.guidance import GuidanceResponse
from app.schemas.well import AdministrativeArea, Location, Well, WellStatus
from app.services.guidance_service import GuidanceService

router = APIRouter()


@router.get("/guidance/{well_id}")
def get_guidance(well_id: str) -> GuidanceResponse:
    """Build safety guidance for a known well and nearby alternatives."""

    # Demo records stand in for the future database and feature repository.
    if well_id != "102":
        raise HTTPException(status_code=404, detail="Well not found")

    well = Well(
        well_id="102",
        site_name="Sample Well 102",
        location=Location(latitude=-4.5, longitude=35.7),
        administrative_area=AdministrativeArea(
            district="Dodoma",
            ward="DODOMA-NORTH-SOUTH",
        ),
    )
    features = {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5}
    candidates = [
        Well(
            well_id="108",
            site_name="Sample Well 108",
            status=WellStatus.ACTIVE,
            location=Location(latitude=-4.51, longitude=35.71),
        )
    ]
    candidate_features = {
        "108": {"fluoride_mg_L": 0.5, "ecoli_cfu_100ml": 0.5}
    }

    service = GuidanceService(model_type=settings.RISK_MODEL_TYPE)
    return service.create_guidance(
        well,
        features,
        candidates,
        candidate_features=candidate_features,
    )
