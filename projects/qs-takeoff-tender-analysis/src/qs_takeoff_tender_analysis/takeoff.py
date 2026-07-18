from __future__ import annotations

from collections import defaultdict

from .models import FloorPlan, Opening, QuantityLine, TakeoffResult, WallSegment

TOLERANCE = 1e-8


def _key(value: float) -> float:
    return round(float(value), 8)


def classify_wall_segments(plan: FloorPlan) -> tuple[WallSegment, ...]:
    grouped: dict[tuple[str, float], list[tuple[float, float, str]]] = defaultdict(list)
    for room in plan.rooms:
        grouped[("horizontal", _key(room.y))].append((room.x, room.x2, room.room_id))
        grouped[("horizontal", _key(room.y2))].append((room.x, room.x2, room.room_id))
        grouped[("vertical", _key(room.x))].append((room.y, room.y2, room.room_id))
        grouped[("vertical", _key(room.x2))].append((room.y, room.y2, room.room_id))

    segments: list[WallSegment] = []
    for (orientation, coordinate), intervals in sorted(grouped.items()):
        breakpoints = sorted(
            {_key(value) for start, end, _room in intervals for value in (start, end)}
        )
        for start, end in zip(breakpoints, breakpoints[1:], strict=False):
            if end - start <= TOLERANCE:
                continue
            midpoint = (start + end) / 2
            room_ids = tuple(
                sorted(
                    room_id
                    for interval_start, interval_end, room_id in intervals
                    if interval_start - TOLERANCE <= midpoint <= interval_end + TOLERANCE
                )
            )
            if not room_ids:
                continue
            segments.append(
                WallSegment(
                    orientation=orientation,
                    coordinate=coordinate,
                    start=start,
                    end=end,
                    wall_type="external" if len(room_ids) == 1 else "partition",
                    room_ids=room_ids,
                )
            )
    return tuple(segments)


def _opening_wall_type(opening: Opening, segments: tuple[WallSegment, ...]) -> str:
    matching = [
        segment
        for segment in segments
        if segment.orientation == opening.orientation
        and abs(segment.coordinate - opening.coordinate) <= TOLERANCE
        and min(segment.end, opening.end) - max(segment.start, opening.start) > TOLERANCE
    ]
    covered = 0.0
    wall_types: set[str] = set()
    for segment in matching:
        overlap = max(0.0, min(segment.end, opening.end) - max(segment.start, opening.start))
        covered += overlap
        if overlap > TOLERANCE:
            wall_types.add(segment.wall_type)
    if abs(covered - opening.length_units) > TOLERANCE or len(wall_types) != 1:
        raise ValueError(
            f"Opening {opening.opening_id} must lie entirely on one classified wall segment."
        )
    return wall_types.pop()


def _validate_opening_overlaps(plan: FloorPlan) -> None:
    for index, opening in enumerate(plan.openings):
        for other in plan.openings[index + 1 :]:
            if opening.orientation != other.orientation:
                continue
            if abs(opening.coordinate - other.coordinate) > TOLERANCE:
                continue
            if min(opening.end, other.end) - max(opening.start, other.start) > TOLERANCE:
                raise ValueError(f"Openings {opening.opening_id} and {other.opening_id} overlap.")


def calculate_takeoff(plan: FloorPlan) -> TakeoffResult:
    _validate_opening_overlaps(plan)
    segments = classify_wall_segments(plan)
    scale = plan.scale_m_per_unit
    room_refs = tuple(room.room_id for room in plan.rooms)
    opening_refs = tuple(opening.opening_id for opening in plan.openings)

    external_length_m = sum(
        segment.length_units * scale for segment in segments if segment.wall_type == "external"
    )
    partition_length_m = sum(
        segment.length_units * scale for segment in segments if segment.wall_type == "partition"
    )
    floor_area_m2 = sum(room.area_units2 for room in plan.rooms) * scale**2

    external_opening_area = 0.0
    partition_opening_area = 0.0
    window_area = 0.0
    door_count = 0
    for opening in plan.openings:
        wall_type = _opening_wall_type(opening, segments)
        area = opening.length_units * scale * opening.height_m
        if wall_type == "external":
            external_opening_area += area
        else:
            partition_opening_area += area
        if opening.kind == "window":
            window_area += area
        else:
            door_count += 1

    external_wall_area = external_length_m * plan.storey_height_m - external_opening_area
    partition_area = partition_length_m * plan.storey_height_m - partition_opening_area
    if external_wall_area < -TOLERANCE or partition_area < -TOLERANCE:
        raise ValueError("Opening deductions exceed measured wall area.")

    quantities = (
        QuantityLine(
            "QTO-FLR",
            "Floor finish",
            "m2",
            round(floor_area_m2, 4),
            "sum(room width x depth) x scale^2",
            room_refs,
        ),
        QuantityLine(
            "QTO-CEI",
            "Ceiling finish",
            "m2",
            round(floor_area_m2, 4),
            "floor area proxy for one storey",
            room_refs,
        ),
        QuantityLine(
            "QTO-SLB",
            "Concrete floor slab",
            "m3",
            round(floor_area_m2 * plan.slab_thickness_m, 4),
            "floor area x slab thickness",
            room_refs,
        ),
        QuantityLine(
            "QTO-EXT",
            "External walling",
            "m2",
            round(max(0.0, external_wall_area), 4),
            "deduplicated external length x storey height - external openings",
            room_refs + opening_refs,
        ),
        QuantityLine(
            "QTO-INT",
            "Internal partitions",
            "m2",
            round(max(0.0, partition_area), 4),
            "shared-wall length x storey height - partition openings; one-face equivalent",
            room_refs + opening_refs,
        ),
        QuantityLine(
            "QTO-DOR",
            "Door sets",
            "ea",
            float(door_count),
            "count(door openings)",
            tuple(opening.opening_id for opening in plan.openings if opening.kind == "door"),
        ),
        QuantityLine(
            "QTO-WIN",
            "Window units by glazed area",
            "m2",
            round(window_area, 4),
            "sum(window width x height)",
            tuple(opening.opening_id for opening in plan.openings if opening.kind == "window"),
        ),
    )
    return TakeoffResult(
        plan_id=plan.plan_id,
        data_status=plan.data_status,
        status="measured_from_vector_fixture",
        scale_m_per_unit=scale,
        external_wall_length_m=round(external_length_m, 4),
        partition_length_m=round(partition_length_m, 4),
        opening_deductions_m2={
            "external": round(external_opening_area, 4),
            "partition": round(partition_opening_area, 4),
        },
        quantities=quantities,
    )


def naive_room_perimeter_length_m(plan: FloorPlan) -> float:
    return round(
        sum(2 * (room.width + room.depth) for room in plan.rooms) * plan.scale_m_per_unit,
        4,
    )
