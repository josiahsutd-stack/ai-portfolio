from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DesignScenario:
    name: str
    floor_area_m2: float
    room_count: int
    avg_daylight_score: float
    circulation_ratio: float
    adjacency_priority: str
    public_private_separation: float

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> DesignScenario:
        required = {
            "name",
            "floor_area_m2",
            "room_count",
            "avg_daylight_score",
            "circulation_ratio",
            "adjacency_priority",
            "public_private_separation",
        }
        missing = required - set(payload)
        if missing:
            raise ValueError(f"Missing scenario fields: {sorted(missing)}")
        return cls(
            name=str(payload["name"]),
            floor_area_m2=float(payload["floor_area_m2"]),
            room_count=int(payload["room_count"]),
            avg_daylight_score=float(payload["avg_daylight_score"]),
            circulation_ratio=float(payload["circulation_ratio"]),
            adjacency_priority=str(payload["adjacency_priority"]),
            public_private_separation=float(payload["public_private_separation"]),
        )


@dataclass(frozen=True)
class Recommendation:
    category: str
    priority: str
    score_impact: int
    rationale: str
    action: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def score_design(scenario: DesignScenario) -> int:
    if scenario.floor_area_m2 <= 0 or scenario.room_count <= 0:
        raise ValueError("Floor area and room count must be positive.")
    daylight = scenario.avg_daylight_score * 35
    circulation = max(0, 1 - abs(scenario.circulation_ratio - 0.24) / 0.24) * 25
    density = max(0, 1 - abs((scenario.floor_area_m2 / scenario.room_count) - 42) / 42) * 20
    separation = scenario.public_private_separation * 20
    return round(max(0, min(100, daylight + circulation + density + separation)))


def recommend_design_actions(scenario: DesignScenario) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    if scenario.avg_daylight_score < 0.55:
        recommendations.append(
            Recommendation(
                "daylight",
                "high",
                18,
                "Average daylight score is below the target band for frequently occupied rooms.",
                "Move high-occupancy rooms closer to facade zones and consider borrowed light or atrium strategies.",
            )
        )
    if scenario.circulation_ratio > 0.32:
        recommendations.append(
            Recommendation(
                "circulation",
                "high",
                15,
                "Circulation ratio suggests too much area is being consumed by corridors or residual space.",
                "Consolidate corridor runs and cluster rooms around clearer primary routes.",
            )
        )
    elif scenario.circulation_ratio < 0.18:
        recommendations.append(
            Recommendation(
                "circulation",
                "medium",
                8,
                "Circulation ratio may be too tight for accessible movement and wayfinding.",
                "Check turning spaces, queuing, and public route widths before reducing circulation further.",
            )
        )
    average_room_area = scenario.floor_area_m2 / scenario.room_count
    if average_room_area < 22:
        recommendations.append(
            Recommendation(
                "room sizing",
                "medium",
                9,
                "Average room area is small relative to the program count.",
                "Merge low-value small rooms or re-balance program areas around critical spaces.",
            )
        )
    if scenario.public_private_separation < 0.6:
        recommendations.append(
            Recommendation(
                "zoning",
                "medium",
                11,
                "Public/private separation score suggests blurred access control or acoustic boundaries.",
                "Group public functions near entries and push private rooms deeper into controlled zones.",
            )
        )
    if not recommendations:
        recommendations.append(
            Recommendation(
                "overall",
                "low",
                4,
                "The scenario is within the target demo bands for daylight, circulation, sizing, and zoning.",
                "Run adjacency-specific review and stakeholder testing before finalizing.",
            )
        )
    return recommendations
