from __future__ import annotations

import math
import random

from .models import Mass, MassingCandidate, Rect, SiteScenario

TYPOLOGIES = ("slab", "twin_bar", "courtyard", "stepped")


def _fit_dimensions(area: float, bounds: Rect, aspect: float) -> tuple[float, float]:
    width = math.sqrt(max(area, 1.0) * max(aspect, 0.2))
    depth = area / width
    scale = min(1.0, bounds.width * 0.96 / width, bounds.depth * 0.96 / depth)
    return max(2.0, width * scale), max(2.0, depth * scale)


def _place_rect(rng: random.Random, bounds: Rect, width: float, depth: float) -> Rect:
    available_x = max(0.0, bounds.width - width)
    available_y = max(0.0, bounds.depth - depth)
    return Rect(
        bounds.x + rng.uniform(0.0, available_x),
        bounds.y + rng.uniform(0.0, available_y),
        min(width, bounds.width),
        min(depth, bounds.depth),
    )


def _slab(
    rng: random.Random, bounds: Rect, area: float, floors: int, generator: str
) -> tuple[Mass, ...]:
    aspect = rng.uniform(1.25, 3.2)
    width, depth = _fit_dimensions(area, bounds, aspect)
    if rng.random() < 0.5:
        width, depth = depth, width
        width = min(width, bounds.width * 0.96)
        depth = min(depth, bounds.depth * 0.96)
    return (Mass("A", _place_rect(rng, bounds, width, depth), floors),)


def _twin_bar(
    rng: random.Random, bounds: Rect, area: float, floors: int, generator: str
) -> tuple[Mass, ...]:
    horizontal = rng.random() < 0.5
    gap = min(rng.uniform(4.0, 9.0), min(bounds.width, bounds.depth) * 0.2)
    if horizontal:
        width = min(bounds.width * rng.uniform(0.64, 0.94), math.sqrt(area * 2.2))
        depth = max(2.5, area / max(2 * width, 1.0))
        if 2 * depth + gap > bounds.depth * 0.96:
            depth = max(2.0, (bounds.depth * 0.96 - gap) / 2)
        x = bounds.x + max(0.0, (bounds.width - width) * rng.random())
        total_depth = 2 * depth + gap
        y = bounds.y + max(0.0, (bounds.depth - total_depth) * rng.random())
        return (
            Mass("A", Rect(x, y, width, depth), floors),
            Mass("B", Rect(x, y + depth + gap, width, depth), floors),
        )
    depth = min(bounds.depth * rng.uniform(0.64, 0.94), math.sqrt(area * 2.2))
    width = max(2.5, area / max(2 * depth, 1.0))
    if 2 * width + gap > bounds.width * 0.96:
        width = max(2.0, (bounds.width * 0.96 - gap) / 2)
    total_width = 2 * width + gap
    x = bounds.x + max(0.0, (bounds.width - total_width) * rng.random())
    y = bounds.y + max(0.0, (bounds.depth - depth) * rng.random())
    return (
        Mass("A", Rect(x, y, width, depth), floors),
        Mass("B", Rect(x + width + gap, y, width, depth), floors),
    )


def _courtyard(
    rng: random.Random, bounds: Rect, area: float, floors: int, generator: str
) -> tuple[Mass, ...]:
    outer_width = bounds.width * rng.uniform(0.62, 0.92)
    outer_depth = bounds.depth * rng.uniform(0.62, 0.92)
    max_ring_area = outer_width * outer_depth * 0.72
    ring_area = min(area, max_ring_area)
    span = outer_width + outer_depth
    discriminant = max(0.01, span * span - 4 * ring_area)
    thickness = (span - math.sqrt(discriminant)) / 4
    thickness = min(max(2.5, thickness), outer_width * 0.28, outer_depth * 0.28)
    x = bounds.x + (bounds.width - outer_width) * rng.random()
    y = bounds.y + (bounds.depth - outer_depth) * rng.random()
    return (
        Mass("South", Rect(x, y, outer_width, thickness), floors),
        Mass(
            "North",
            Rect(x, y + outer_depth - thickness, outer_width, thickness),
            floors,
        ),
        Mass(
            "West",
            Rect(x, y + thickness, thickness, outer_depth - 2 * thickness),
            floors,
        ),
        Mass(
            "East",
            Rect(
                x + outer_width - thickness,
                y + thickness,
                thickness,
                outer_depth - 2 * thickness,
            ),
            floors,
        ),
    )


def _stepped(
    rng: random.Random, bounds: Rect, area: float, floors: int, generator: str
) -> tuple[Mass, ...]:
    width, depth = _fit_dimensions(area, bounds, rng.uniform(1.1, 2.2))
    left_width = width * rng.uniform(0.42, 0.58)
    right_width = width - left_width
    x = bounds.x + max(0.0, (bounds.width - width) * rng.random())
    y = bounds.y + max(0.0, (bounds.depth - depth) * rng.random())
    return (
        Mass("Tower", Rect(x, y, left_width, depth), floors),
        Mass("Terrace", Rect(x + left_width, y, right_width, depth), max(1, floors - 2)),
    )


def _make_pattern(
    typology: str,
    rng: random.Random,
    bounds: Rect,
    area: float,
    floors: int,
    generator: str,
) -> tuple[Mass, ...]:
    builders = {
        "slab": _slab,
        "twin_bar": _twin_bar,
        "courtyard": _courtyard,
        "stepped": _stepped,
    }
    return builders[typology](rng, bounds, area, floors, generator)


def _shift_baseline(
    rng: random.Random, masses: tuple[Mass, ...], scenario: SiteScenario
) -> tuple[Mass, ...]:
    dx = rng.uniform(-scenario.site_width_m * 0.16, scenario.site_width_m * 0.16)
    dy = rng.uniform(-scenario.site_depth_m * 0.16, scenario.site_depth_m * 0.16)
    return tuple(
        Mass(
            mass.label,
            Rect(
                mass.footprint.x + dx,
                mass.footprint.y + dy,
                mass.footprint.width,
                mass.footprint.depth,
            ),
            mass.floors,
        )
        for mass in masses
    )


def generate_candidates(
    scenario: SiteScenario,
    count: int = 120,
    seed: int = 7,
    mode: str = "constraint_aware",
) -> list[MassingCandidate]:
    if count < 1:
        raise ValueError("Candidate count must be positive.")
    if mode not in {"constraint_aware", "unconstrained_baseline"}:
        raise ValueError(f"Unsupported generation mode: {mode}")
    rng = random.Random(seed)
    candidates: list[MassingCandidate] = []
    for index in range(count):
        typology = TYPOLOGIES[index % len(TYPOLOGIES)]
        if mode == "constraint_aware":
            bounds = scenario.buildable_bounds
            minimum_floors = max(
                1,
                math.ceil(
                    scenario.target_gfa_m2
                    / max(bounds.area * scenario.max_site_coverage * 0.90, 1.0)
                ),
            )
            floors = rng.randint(min(minimum_floors, scenario.max_floors), scenario.max_floors)
            target_area = scenario.target_gfa_m2 / floors
            target_area *= rng.uniform(0.84, 1.12)
            target_area = min(
                target_area,
                scenario.site_bounds.area * scenario.max_site_coverage * 0.97,
                bounds.area * 0.92,
            )
            target_area = max(target_area, bounds.area * 0.10)
            masses = _make_pattern(typology, rng, bounds, target_area, floors, mode)
        else:
            bounds = scenario.site_bounds
            floors = rng.randint(1, scenario.max_floors + 3)
            target_area = bounds.area * rng.uniform(0.12, 0.78)
            masses = _make_pattern(typology, rng, bounds, target_area, floors, mode)
            masses = _shift_baseline(rng, masses, scenario)
        candidates.append(
            MassingCandidate(
                candidate_id=f"{mode[:2]}-{seed:03d}-{index:03d}",
                typology=typology,
                generator=mode,
                masses=masses,
            )
        )
    return candidates
