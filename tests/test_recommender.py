import pytest
from spatial_design_recommender import DesignScenario, recommend_design_actions, score_design


def test_recommender_flags_low_daylight_and_high_circulation() -> None:
    scenario = DesignScenario(
        name="Deep plan",
        floor_area_m2=900,
        room_count=25,
        avg_daylight_score=0.3,
        circulation_ratio=0.42,
        adjacency_priority="amenities near core",
        public_private_separation=0.45,
    )

    recommendations = recommend_design_actions(scenario)
    categories = {item.category for item in recommendations}

    assert score_design(scenario) < 70
    assert "daylight" in categories
    assert "circulation" in categories


def test_recommender_rejects_invalid_geometry_inputs() -> None:
    scenario = DesignScenario(
        name="Invalid",
        floor_area_m2=0,
        room_count=0,
        avg_daylight_score=0.5,
        circulation_ratio=0.25,
        adjacency_priority="none",
        public_private_separation=0.5,
    )

    with pytest.raises(ValueError):
        score_design(scenario)
