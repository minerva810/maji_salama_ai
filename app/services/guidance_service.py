"""Business rules that turn model predictions into actionable water guidance."""

from math import asin, cos, radians, sin, sqrt

from app.schemas.guidance import (
    AlternativeWell,
    GuidanceAction,
    GuidanceResponse,
    RiskResult,
)
from app.schemas.model_output import PredictionOutput, RiskLevel
from app.schemas.well import Well, WellStatus
from app.services.prediction_service import get_prediction_service


class GuidanceService:
    """Coordinate risk prediction, treatment advice, and alternative selection."""

    def __init__(self, model_type: str = "dummy"):
        self.prediction_service = get_prediction_service(model_type)

    def create_guidance(
        self,
        well: Well,
        features: dict,
        candidates: list[Well],
        candidate_features: dict[str, dict] | None = None,
    ) -> GuidanceResponse:
        """Create final guidance for a well and its candidate alternatives."""

        risk = self._to_risk_result(
            self.prediction_service.predict(well.well_id, features)
        )
        alternative = self._pick_lower_risk_candidate(
            well,
            risk,
            candidates,
            candidate_features or {},
        )

        return GuidanceResponse(
            well_id=well.well_id,
            risk=risk,
            actions=self._build_actions(risk, alternative),
            alternative_well=alternative,
            message=self._build_message(risk, alternative),
        )

    @staticmethod
    def _to_risk_result(predictions: list[PredictionOutput]) -> RiskResult:
        """Combine target-specific model outputs into the guidance risk summary."""

        levels = {
            output.model.target: output.prediction.risk_level
            for output in predictions
        }
        return RiskResult(
            fluoride=levels.get("fluoride", RiskLevel.UNKNOWN),
            bacterial=levels.get("bacterial", RiskLevel.UNKNOWN),
        )

    def _pick_lower_risk_candidate(
        self,
        well: Well,
        risk: RiskResult,
        candidates: list[Well],
        candidate_features: dict[str, dict],
    ) -> AlternativeWell | None:
        """Prefer active lower-risk wells and use unknown status only as fallback."""

        current_score = self._risk_score(risk)
        best: Well | None = None
        best_key: tuple[int, float] | None = None

        for candidate in candidates:
            # Inactive wells must never enter prediction or recommendation flows.
            if candidate.status is WellStatus.INACTIVE:
                continue

            candidate_predictions = self.prediction_service.predict(
                candidate.well_id,
                candidate_features.get(candidate.well_id, {}),
            )
            candidate_risk = self._to_risk_result(candidate_predictions)
            if self._risk_score(candidate_risk) >= current_score:
                continue

            distance = self._distance_km(well, candidate)
            status_priority = 0 if candidate.status is WellStatus.ACTIVE else 1
            candidate_key = (status_priority, distance)
            if best_key is None or candidate_key < best_key:
                best = candidate
                best_key = candidate_key

        if best is None or best_key is None:
            return None
        return AlternativeWell(
            well_id=best.well_id,
            status=best.status,
            distance_km=round(best_key[1], 2),
            site_name=best.site_name,
        )

    @staticmethod
    def _build_actions(
        risk: RiskResult,
        alternative: AlternativeWell | None,
    ) -> list[GuidanceAction]:
        """Translate contaminant risk levels into treatment or testing actions."""

        actions: list[GuidanceAction] = []
        if risk.fluoride in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            actions.append(
                GuidanceAction(
                    action="use fluoride-removal treatment",
                    reason=f"Fluoride risk is {risk.fluoride.value}",
                )
            )
        if risk.bacterial in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            actions.append(
                GuidanceAction(
                    action="boil or chlorinate water",
                    reason=f"Bacterial risk is {risk.bacterial.value}",
                )
            )
        if RiskLevel.UNKNOWN in {risk.fluoride, risk.bacterial}:
            actions.append(
                GuidanceAction(
                    action="test water quality",
                    reason="One or more risk measurements are unavailable",
                )
            )
        if alternative is not None and alternative.status is WellStatus.UNKNOWN:
            actions.append(
                GuidanceAction(
                    action="verify alternative well availability",
                    reason="The candidate well has not been field-verified",
                )
            )
        return actions

    @staticmethod
    def _build_message(
        risk: RiskResult,
        alternative: AlternativeWell | None,
    ) -> str:
        """Create the short summary displayed alongside structured actions."""

        if RiskLevel.HIGH in {risk.fluoride, risk.bacterial}:
            message = "Do not drink untreated water from this well."
        elif RiskLevel.UNKNOWN in {risk.fluoride, risk.bacterial}:
            message = "Test the water before use."
        elif risk.fluoride is RiskLevel.LOW and risk.bacterial is RiskLevel.LOW:
            message = "Water risk is low; continue routine quality testing."
        else:
            message = "Follow the recommended treatment actions before drinking."

        if alternative is not None and alternative.status is WellStatus.ACTIVE:
            return f"{message} A nearby active lower-risk well is available."
        if alternative is not None:
            return f"{message} Verify the conditional alternative before use."
        return message

    @staticmethod
    def _risk_score(risk: RiskResult) -> int:
        """Convert a combined risk result into an ordering score."""

        levels = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.UNKNOWN: 3,
        }
        return levels[risk.fluoride] + levels[risk.bacterial]

    @staticmethod
    def _distance_km(first: Well, second: Well) -> float:
        """Calculate great-circle distance between two WGS84 well locations."""

        lat1 = radians(first.location.latitude)
        lon1 = radians(first.location.longitude)
        lat2 = radians(second.location.latitude)
        lon2 = radians(second.location.longitude)
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        haversine = (
            sin(delta_lat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        )
        return 2 * 6371.0088 * asin(sqrt(haversine))
