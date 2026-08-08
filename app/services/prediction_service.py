from app.schemas.model_output import (
    ModelInfo,
    PredictionOutput,
    PredictionValue,
    RiskLevel,
)
from app.services.risk_service import classify_bacterial, classify_fluoride


class DummyPredictionService:
    """Deterministic predictor used until trained model adapters are available."""

    def predict(self, request_id: str, features: dict) -> list[PredictionOutput]:
        """Create one standardized prediction per supported contamination target."""

        return [
            self._build_output(
                request_id=request_id,
                target="fluoride",
                value=features.get("fluoride_mg_L"),
                unit="mg/L",
                risk_level=classify_fluoride(features.get("fluoride_mg_L")),
            ),
            self._build_output(
                request_id=request_id,
                target="bacterial",
                value=features.get("ecoli_cfu_100ml"),
                unit="CFU/100mL",
                risk_level=classify_bacterial(features.get("ecoli_cfu_100ml")),
            ),
        ]

    @staticmethod
    def _build_output(
        request_id: str,
        target: str,
        value: float | None,
        unit: str,
        risk_level: RiskLevel,
    ) -> PredictionOutput:
        """Wrap a classified measurement in the common model response schema."""

        return PredictionOutput(
            request_id=request_id,
            model=ModelInfo(name="dummy", version="1.0", target=target),
            prediction=PredictionValue(
                value=value,
                unit=unit,
                risk_level=risk_level,
            ),
            warnings=["Measurement is unavailable"] if value is None else [],
        )


def get_prediction_service(model_type: str) -> DummyPredictionService:
    """Resolve a configured prediction backend by its stable adapter name."""

    if model_type == "dummy":
        return DummyPredictionService()
    raise ValueError(f"Unsupported model type: {model_type}")
"""Prediction service adapters that produce the shared model output contract."""
