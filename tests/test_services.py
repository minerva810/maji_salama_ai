"""Regression tests for prediction, classification, and guidance services."""

from math import nan

import pytest
from pydantic import ValidationError

from app.schemas.environment import Environment, SoilFeatures
from app.schemas.model_output import RiskLevel
from app.schemas.well import Location, Well, WellStatus
from app.services.guidance_service import GuidanceService
from app.services.prediction_service import DummyPredictionService
from app.services.risk_service import classify_bacterial, classify_fluoride


def test_dummy_prediction_returns_one_output_per_target() -> None:
    predictions = DummyPredictionService().predict(
        "well-1",
        {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5},
    )

    assert [output.model.target for output in predictions] == [
        "fluoride",
        "bacterial",
    ]
    assert predictions[0].prediction.risk_level is RiskLevel.MEDIUM
    assert predictions[1].prediction.risk_level is RiskLevel.LOW


def test_invalid_measurements_are_unknown() -> None:
    assert classify_fluoride(-1) is RiskLevel.UNKNOWN
    assert classify_bacterial(nan) is RiskLevel.UNKNOWN


def test_schemas_reject_unknown_fields_at_every_level() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        Well(
            well_id="well-1",
            location=Location(latitude=0, longitude=0),
            unexpected="value",
        )

    with pytest.raises(ValidationError, match="extra_forbidden"):
        Environment(soil=SoilFeatures(ph=7, unexpected="value"))


def test_guidance_uses_candidate_specific_features() -> None:
    source = Well(
        well_id="source",
        location=Location(latitude=-4.5, longitude=35.7),
    )
    nearby = Well(
        well_id="nearby",
        site_name="Nearby Well",
        status=WellStatus.ACTIVE,
        location=Location(latitude=-4.51, longitude=35.71),
    )

    guidance = GuidanceService().create_guidance(
        source,
        {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5},
        [nearby],
        candidate_features={
            "nearby": {"fluoride_mg_L": 0.5, "ecoli_cfu_100ml": 0.5}
        },
    )

    assert guidance.alternative_well is not None
    assert guidance.alternative_well.well_id == "nearby"
    assert guidance.alternative_well.status is WellStatus.ACTIVE
    assert guidance.alternative_well.distance_km > 0
    assert guidance.actions[0].action == "use fluoride-removal treatment"


def test_low_risk_guidance_does_not_recommend_treatment() -> None:
    source = Well(
        well_id="source",
        location=Location(latitude=0, longitude=0),
    )

    guidance = GuidanceService().create_guidance(
        source,
        {"fluoride_mg_L": 0.5, "ecoli_cfu_100ml": 0.5},
        [],
    )

    assert guidance.actions == []
    assert guidance.message == "Water risk is low; continue routine quality testing."


def test_inactive_candidates_are_excluded() -> None:
    source = Well(well_id="source", location=Location(latitude=0, longitude=0))
    inactive = Well(
        well_id="inactive",
        status=WellStatus.INACTIVE,
        location=Location(latitude=0.01, longitude=0.01),
    )

    guidance = GuidanceService().create_guidance(
        source,
        {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5},
        [inactive],
        candidate_features={
            "inactive": {"fluoride_mg_L": 0.5, "ecoli_cfu_100ml": 0.5}
        },
    )

    assert guidance.alternative_well is None


def test_active_candidate_is_preferred_over_nearer_unknown_candidate() -> None:
    source = Well(well_id="source", location=Location(latitude=0, longitude=0))
    unknown = Well(
        well_id="unknown",
        location=Location(latitude=0.01, longitude=0.01),
    )
    active = Well(
        well_id="active",
        status=WellStatus.ACTIVE,
        location=Location(latitude=0.02, longitude=0.02),
    )
    low_risk = {"fluoride_mg_L": 0.5, "ecoli_cfu_100ml": 0.5}

    guidance = GuidanceService().create_guidance(
        source,
        {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5},
        [unknown, active],
        candidate_features={"unknown": low_risk, "active": low_risk},
    )

    assert guidance.alternative_well is not None
    assert guidance.alternative_well.well_id == "active"


def test_unknown_candidate_is_returned_with_verification_action() -> None:
    source = Well(well_id="source", location=Location(latitude=0, longitude=0))
    unknown = Well(
        well_id="unknown",
        location=Location(latitude=0.01, longitude=0.01),
    )

    guidance = GuidanceService().create_guidance(
        source,
        {"fluoride_mg_L": 2.5, "ecoli_cfu_100ml": 0.5},
        [unknown],
        candidate_features={
            "unknown": {"fluoride_mg_L": 0.5, "ecoli_cfu_100ml": 0.5}
        },
    )

    assert guidance.alternative_well is not None
    assert guidance.alternative_well.status is WellStatus.UNKNOWN
    assert guidance.actions[-1].action == "verify alternative well availability"
