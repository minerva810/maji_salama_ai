"""HTTP endpoints for model-level water quality predictions."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.model_output import PredictionOutput
from app.services.prediction_service import get_prediction_service

router = APIRouter()


@router.get("/predictions/{well_id}")
def get_prediction(well_id: str) -> list[PredictionOutput]:
    """Return fluoride and bacterial predictions for a well."""

    # Placeholder features; replace with the well's persisted model input.
    features = {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5}
    return get_prediction_service(settings.RISK_MODEL_TYPE).predict(well_id, features)
