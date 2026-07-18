from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from math import ceil

from .models import (
    CandidateAssessment,
    ConstraintViolation,
    MassingCandidate,
    Point,
    SiteScenario,
)

OBJECTIVES = ("gfa_fit", "solar", "daylight", "wind", "access")


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _union_length(intervals: Iterable[tuple[float, float]]) -> float:
    ordered = sorted((start, end) for start, end in intervals if end > start)
    if not ordered:
        return 0.0
    total = 0.0
    current_start, current_end = ordered[0]
    for start, end in ordered[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    return total + current_end - current_start


def _facade_solar_score(candidate: MassingCandidate, scenario: SiteScenario) -> float:
    base_weights = {"north": 0.20, "east": 0.62, "south": 1.00, "west": 0.56}
    rotations = round(scenario.north_rotation_deg / 90) % 4
    cardinal = ["north", "east", "south", "west"]

    def rotated(direction: str) -> str:
        return cardinal[(cardinal.index(direction) + rotations) % 4]

    weighted = 0.0
    perimeter = 0.0
    for mass in candidate.masses:
        rect = mass.footprint
        lengths = {
            "north": rect.width,
            "east": rect.depth,
            "south": rect.width,
            "west": rect.depth,
        }
        weighted += sum(length * base_weights[rotated(side)] for side, length in lengths.items())
        perimeter += rect.perimeter
    raw = weighted / max(perimeter, 1e-9)
    return _clamp((raw - 0.20) / 0.80)


def _daylight_proxy(candidate: MassingCandidate) -> float:
    footprint_area = sum(mass.footprint.area for mass in candidate.masses)
    exposed_perimeter = sum(mass.footprint.perimeter for mass in candidate.masses)
    perimeter_area_ratio = exposed_perimeter / max(footprint_area, 1e-9)
    return _clamp((perimeter_area_ratio - 0.07) / 0.18)


def _wind_proxy(candidate: MassingCandidate, scenario: SiteScenario, coverage: float) -> float:
    north_south = scenario.prevailing_wind_from in {"north", "south"}
    if north_south:
        intervals = ((mass.footprint.x, mass.footprint.x2) for mass in candidate.masses)
        span = scenario.buildable_bounds.width
    else:
        intervals = ((mass.footprint.y, mass.footprint.y2) for mass in candidate.masses)
        span = scenario.buildable_bounds.depth
    projected_blockage = _clamp(_union_length(intervals) / max(span, 1e-9))
    open_ground = _clamp(1 - coverage / scenario.max_site_coverage)
    return _clamp(0.68 * (1 - projected_blockage) + 0.32 * open_ground)


def _cell_for_point(point: Point, resolution: float, columns: int, rows: int) -> tuple[int, int]:
    return (
        min(columns - 1, max(0, int(point.x / resolution))),
        min(rows - 1, max(0, int(point.y / resolution))),
    )


def _site_access_distance(start: Point, masses: tuple, scenario: SiteScenario) -> float | None:
    resolution = scenario.grid_resolution_m
    columns = max(1, ceil(scenario.site_width_m / resolution))
    rows = max(1, ceil(scenario.site_depth_m / resolution))
    blocked: set[tuple[int, int]] = set()
    for column in range(columns):
        for row in range(rows):
            point = Point((column + 0.5) * resolution, (row + 0.5) * resolution)
            if any(mass.footprint.contains_point(point) for mass in masses):
                blocked.add((column, row))
    start_cell = _cell_for_point(start, resolution, columns, rows)
    if start_cell in blocked:
        return None
    targets: set[tuple[int, int]] = set()
    for column, row in blocked:
        for delta_x, delta_y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = column + delta_x, row + delta_y
            if (
                0 <= neighbour[0] < columns
                and 0 <= neighbour[1] < rows
                and neighbour not in blocked
            ):
                targets.add(neighbour)
    if not targets:
        return None
    queue = deque([(start_cell, 0)])
    visited = {start_cell}
    while queue:
        cell, distance = queue.popleft()
        if cell in targets:
            return distance * resolution
        for delta_x, delta_y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = cell[0] + delta_x, cell[1] + delta_y
            if (
                0 <= neighbour[0] < columns
                and 0 <= neighbour[1] < rows
                and neighbour not in blocked
                and neighbour not in visited
            ):
                visited.add(neighbour)
                queue.append((neighbour, distance + 1))
    return None


def assess_candidate(candidate: MassingCandidate, scenario: SiteScenario) -> CandidateAssessment:
    violations: list[ConstraintViolation] = []
    site = scenario.site_bounds
    envelope = scenario.buildable_bounds
    for mass in candidate.masses:
        if not site.contains_rect(mass.footprint):
            violations.append(
                ConstraintViolation("outside_site", f"Mass {mass.label} extends beyond the site.")
            )
        if not envelope.contains_rect(mass.footprint):
            violations.append(
                ConstraintViolation(
                    "setback_envelope",
                    f"Mass {mass.label} extends beyond the supplied setback envelope.",
                )
            )
        height = mass.floors * scenario.floor_to_floor_m
        if height > scenario.max_height_m + 1e-6:
            violations.append(
                ConstraintViolation(
                    "height_limit",
                    f"Mass {mass.label} reaches {height:.1f} m above the {scenario.max_height_m:.1f} m limit.",
                )
            )
    for index, first in enumerate(candidate.masses):
        for second in candidate.masses[index + 1 :]:
            if first.footprint.intersection_area(second.footprint) > 1e-6:
                violations.append(
                    ConstraintViolation(
                        "mass_overlap", f"Masses {first.label} and {second.label} overlap."
                    )
                )

    footprint_area = sum(mass.footprint.area for mass in candidate.masses)
    gfa = sum(mass.footprint.area * mass.floors for mass in candidate.masses)
    coverage = footprint_area / site.area
    if coverage > scenario.max_site_coverage + 1e-6:
        violations.append(
            ConstraintViolation(
                "site_coverage",
                f"Coverage {coverage:.3f} exceeds the supplied {scenario.max_site_coverage:.3f} limit.",
            )
        )
    if gfa > scenario.max_gfa_m2 + 1e-6:
        violations.append(
            ConstraintViolation(
                "max_gfa",
                f"GFA {gfa:.1f} m2 exceeds the supplied {scenario.max_gfa_m2:.1f} m2 maximum.",
            )
        )

    ingress_distance = _site_access_distance(scenario.ingress, candidate.masses, scenario)
    egress_distance = _site_access_distance(scenario.egress, candidate.masses, scenario)
    if ingress_distance is None:
        violations.append(
            ConstraintViolation(
                "ingress_path", "No open-site grid path reaches a mass from the ingress point."
            )
        )
    if egress_distance is None:
        violations.append(
            ConstraintViolation(
                "egress_path", "No open-site grid path reaches a mass from the egress point."
            )
        )

    gfa_error = abs(gfa - scenario.target_gfa_m2) / scenario.target_gfa_m2
    gfa_fit = _clamp(1 - gfa_error)
    route_sum = (ingress_distance or 0.0) + (egress_distance or 0.0)
    route_reference = max(1.0, 2 * (scenario.site_width_m + scenario.site_depth_m))
    access = (
        0.0
        if ingress_distance is None or egress_distance is None
        else _clamp(1 - route_sum / route_reference)
    )
    solar = _facade_solar_score(candidate, scenario)
    daylight = _daylight_proxy(candidate)
    wind = _wind_proxy(candidate, scenario, coverage)
    metrics = {
        "gfa_m2": round(gfa, 3),
        "gfa_error_fraction": round(gfa_error, 6),
        "coverage": round(coverage, 6),
        "height_m": round(
            max(mass.floors for mass in candidate.masses) * scenario.floor_to_floor_m, 3
        ),
        "ingress_path_m": round(ingress_distance, 3) if ingress_distance is not None else -1.0,
        "egress_path_m": round(egress_distance, 3) if egress_distance is not None else -1.0,
        "gfa_fit": round(gfa_fit, 6),
        "solar": round(solar, 6),
        "daylight": round(daylight, 6),
        "wind": round(wind, 6),
        "access": round(access, 6),
    }
    weights = scenario.weights.normalized()
    utility = sum(metrics[objective] * weights[objective] for objective in OBJECTIVES)
    return CandidateAssessment(
        candidate=candidate,
        feasible=not violations,
        violations=tuple(violations),
        metrics=metrics,
        utility_score=round(utility, 6),
    )


def _dominates(first: CandidateAssessment, second: CandidateAssessment) -> bool:
    first_values = [first.metrics[name] for name in OBJECTIVES]
    second_values = [second.metrics[name] for name in OBJECTIVES]
    return all(a >= b for a, b in zip(first_values, second_values, strict=True)) and any(
        a > b for a, b in zip(first_values, second_values, strict=True)
    )


def rank_candidates(
    candidates: Iterable[MassingCandidate], scenario: SiteScenario
) -> list[CandidateAssessment]:
    assessments = [assess_candidate(candidate, scenario) for candidate in candidates]
    feasible = [assessment for assessment in assessments if assessment.feasible]
    front_ids = {
        assessment.candidate.candidate_id
        for assessment in feasible
        if not any(
            _dominates(other, assessment)
            for other in feasible
            if other.candidate.candidate_id != assessment.candidate.candidate_id
        )
    }
    ranked = [
        CandidateAssessment(
            candidate=assessment.candidate,
            feasible=assessment.feasible,
            violations=assessment.violations,
            metrics=assessment.metrics,
            utility_score=assessment.utility_score,
            pareto_optimal=assessment.candidate.candidate_id in front_ids,
        )
        for assessment in assessments
    ]
    return sorted(
        ranked,
        key=lambda item: (
            not item.feasible,
            not item.pareto_optimal,
            -item.utility_score,
            item.candidate.candidate_id,
        ),
    )
