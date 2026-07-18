from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import hypot
from typing import Any


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    depth: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.depth <= 0:
            raise ValueError("Rectangle dimensions must be positive.")

    @property
    def x2(self) -> float:
        return self.x + self.width

    @property
    def y2(self) -> float:
        return self.y + self.depth

    @property
    def area(self) -> float:
        return self.width * self.depth

    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.depth)

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.depth / 2)

    def contains_rect(self, other: Rect, tolerance: float = 1e-6) -> bool:
        return (
            other.x >= self.x - tolerance
            and other.y >= self.y - tolerance
            and other.x2 <= self.x2 + tolerance
            and other.y2 <= self.y2 + tolerance
        )

    def contains_point(self, point: Point) -> bool:
        return self.x <= point.x <= self.x2 and self.y <= point.y <= self.y2

    def intersection_area(self, other: Rect) -> float:
        width = max(0.0, min(self.x2, other.x2) - max(self.x, other.x))
        depth = max(0.0, min(self.y2, other.y2) - max(self.y, other.y))
        return width * depth


@dataclass(frozen=True)
class ObjectiveWeights:
    gfa_fit: float = 0.30
    solar: float = 0.18
    daylight: float = 0.20
    wind: float = 0.17
    access: float = 0.15

    def normalized(self) -> dict[str, float]:
        values = asdict(self)
        if any(float(value) < 0 for value in values.values()):
            raise ValueError("Objective weights cannot be negative.")
        total = sum(float(value) for value in values.values())
        if total <= 0:
            raise ValueError("At least one objective weight must be positive.")
        return {key: float(value) / total for key, value in values.items()}


@dataclass(frozen=True)
class SiteScenario:
    scenario_id: str
    name: str
    data_status: str
    source_note: str
    site_width_m: float
    site_depth_m: float
    setback_north_m: float
    setback_east_m: float
    setback_south_m: float
    setback_west_m: float
    max_height_m: float
    floor_to_floor_m: float
    max_site_coverage: float
    target_gfa_m2: float
    max_gfa_m2: float
    prevailing_wind_from: str
    north_rotation_deg: float
    ingress: Point
    egress: Point
    grid_resolution_m: float = 1.0
    weights: ObjectiveWeights = field(default_factory=ObjectiveWeights)

    def __post_init__(self) -> None:
        if not self.scenario_id.strip() or not self.name.strip():
            raise ValueError("Scenario id and name are required.")
        if self.data_status != "synthetic":
            raise ValueError("Bundled scenarios must be explicitly labeled synthetic.")
        if self.site_width_m <= 0 or self.site_depth_m <= 0:
            raise ValueError("Site dimensions must be positive.")
        if (
            min(
                self.setback_north_m,
                self.setback_east_m,
                self.setback_south_m,
                self.setback_west_m,
            )
            < 0
        ):
            raise ValueError("Setbacks cannot be negative.")
        if self.buildable_bounds.width <= 0 or self.buildable_bounds.depth <= 0:
            raise ValueError("Setbacks leave no buildable envelope.")
        if self.max_height_m < self.floor_to_floor_m or self.floor_to_floor_m <= 0:
            raise ValueError("Height limits must allow at least one floor.")
        if not 0 < self.max_site_coverage <= 1:
            raise ValueError("Maximum site coverage must be in (0, 1].")
        if not 0 < self.target_gfa_m2 <= self.max_gfa_m2:
            raise ValueError("Target GFA must be positive and cannot exceed maximum GFA.")
        if self.prevailing_wind_from not in {"north", "east", "south", "west"}:
            raise ValueError("Prevailing wind direction must be cardinal.")
        if self.grid_resolution_m <= 0:
            raise ValueError("Grid resolution must be positive.")
        site = self.site_bounds
        if not site.contains_point(self.ingress) or not site.contains_point(self.egress):
            raise ValueError("Ingress and egress points must lie on or inside the site boundary.")
        if hypot(self.ingress.x - self.egress.x, self.ingress.y - self.egress.y) < 1.0:
            raise ValueError("Ingress and egress points must be distinct.")
        self.weights.normalized()

    @property
    def site_bounds(self) -> Rect:
        return Rect(0.0, 0.0, self.site_width_m, self.site_depth_m)

    @property
    def buildable_bounds(self) -> Rect:
        return Rect(
            self.setback_west_m,
            self.setback_south_m,
            self.site_width_m - self.setback_west_m - self.setback_east_m,
            self.site_depth_m - self.setback_south_m - self.setback_north_m,
        )

    @property
    def max_floors(self) -> int:
        return max(1, int(self.max_height_m // self.floor_to_floor_m))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SiteScenario:
        required = {
            "scenario_id",
            "name",
            "data_status",
            "source_note",
            "site_width_m",
            "site_depth_m",
            "setbacks_m",
            "max_height_m",
            "floor_to_floor_m",
            "max_site_coverage",
            "target_gfa_m2",
            "max_gfa_m2",
            "prevailing_wind_from",
            "north_rotation_deg",
            "ingress",
            "egress",
        }
        missing = sorted(required - payload.keys())
        if missing:
            raise ValueError(f"Missing scenario fields: {missing}")
        setbacks = dict(payload["setbacks_m"])
        weights_payload = dict(payload.get("objective_weights", {}))
        return cls(
            scenario_id=str(payload["scenario_id"]),
            name=str(payload["name"]),
            data_status=str(payload["data_status"]),
            source_note=str(payload["source_note"]),
            site_width_m=float(payload["site_width_m"]),
            site_depth_m=float(payload["site_depth_m"]),
            setback_north_m=float(setbacks["north"]),
            setback_east_m=float(setbacks["east"]),
            setback_south_m=float(setbacks["south"]),
            setback_west_m=float(setbacks["west"]),
            max_height_m=float(payload["max_height_m"]),
            floor_to_floor_m=float(payload["floor_to_floor_m"]),
            max_site_coverage=float(payload["max_site_coverage"]),
            target_gfa_m2=float(payload["target_gfa_m2"]),
            max_gfa_m2=float(payload["max_gfa_m2"]),
            prevailing_wind_from=str(payload["prevailing_wind_from"]).lower(),
            north_rotation_deg=float(payload["north_rotation_deg"]),
            ingress=Point(**{key: float(value) for key, value in dict(payload["ingress"]).items()}),
            egress=Point(**{key: float(value) for key, value in dict(payload["egress"]).items()}),
            grid_resolution_m=float(payload.get("grid_resolution_m", 1.0)),
            weights=ObjectiveWeights(
                **{key: float(value) for key, value in weights_payload.items()}
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["setbacks_m"] = {
            "north": payload.pop("setback_north_m"),
            "east": payload.pop("setback_east_m"),
            "south": payload.pop("setback_south_m"),
            "west": payload.pop("setback_west_m"),
        }
        payload["objective_weights"] = payload.pop("weights")
        return payload


@dataclass(frozen=True)
class Mass:
    label: str
    footprint: Rect
    floors: int

    def __post_init__(self) -> None:
        if self.floors < 1:
            raise ValueError("A mass must have at least one floor.")


@dataclass(frozen=True)
class MassingCandidate:
    candidate_id: str
    typology: str
    generator: str
    masses: tuple[Mass, ...]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("A candidate must contain at least one mass.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstraintViolation:
    code: str
    message: str


@dataclass(frozen=True)
class CandidateAssessment:
    candidate: MassingCandidate
    feasible: bool
    violations: tuple[ConstraintViolation, ...]
    metrics: dict[str, float]
    utility_score: float
    pareto_optimal: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
