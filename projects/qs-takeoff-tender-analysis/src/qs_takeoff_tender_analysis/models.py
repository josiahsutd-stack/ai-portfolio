from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Room:
    room_id: str
    name: str
    x: float
    y: float
    width: float
    depth: float

    def __post_init__(self) -> None:
        if not self.room_id.strip() or not self.name.strip():
            raise ValueError("Room id and name are required.")
        if self.width <= 0 or self.depth <= 0:
            raise ValueError("Room dimensions must be positive.")

    @property
    def x2(self) -> float:
        return self.x + self.width

    @property
    def y2(self) -> float:
        return self.y + self.depth

    @property
    def area_units2(self) -> float:
        return self.width * self.depth


@dataclass(frozen=True)
class Opening:
    opening_id: str
    kind: str
    x1: float
    y1: float
    x2: float
    y2: float
    height_m: float

    def __post_init__(self) -> None:
        if not self.opening_id.strip():
            raise ValueError("Opening id is required.")
        if self.kind not in {"door", "window"}:
            raise ValueError("Opening kind must be 'door' or 'window'.")
        if self.height_m <= 0:
            raise ValueError("Opening height must be positive.")
        horizontal = abs(self.y1 - self.y2) <= 1e-9 and abs(self.x1 - self.x2) > 1e-9
        vertical = abs(self.x1 - self.x2) <= 1e-9 and abs(self.y1 - self.y2) > 1e-9
        if not (horizontal or vertical):
            raise ValueError("Openings must be positive-length axis-aligned segments.")

    @property
    def orientation(self) -> str:
        return "horizontal" if abs(self.y1 - self.y2) <= 1e-9 else "vertical"

    @property
    def coordinate(self) -> float:
        return self.y1 if self.orientation == "horizontal" else self.x1

    @property
    def start(self) -> float:
        return min(self.x1, self.x2) if self.orientation == "horizontal" else min(self.y1, self.y2)

    @property
    def end(self) -> float:
        return max(self.x1, self.x2) if self.orientation == "horizontal" else max(self.y1, self.y2)

    @property
    def length_units(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class FloorPlan:
    plan_id: str
    name: str
    data_status: str
    source_note: str
    drawing_unit: str
    scale_m_per_unit: float
    storey_height_m: float
    slab_thickness_m: float
    rooms: tuple[Room, ...]
    openings: tuple[Opening, ...]

    def __post_init__(self) -> None:
        if not self.plan_id.strip() or not self.name.strip():
            raise ValueError("Plan id and name are required.")
        if self.data_status != "synthetic":
            raise ValueError("Bundled floor plans must be explicitly labeled synthetic.")
        if not self.source_note.strip():
            raise ValueError("A floor-plan provenance note is required.")
        if self.drawing_unit not in {"unit", "mm", "cm", "m"}:
            raise ValueError("Unsupported drawing unit.")
        if self.scale_m_per_unit <= 0:
            raise ValueError("A positive drawing scale is required for takeoff.")
        if self.storey_height_m <= 0 or self.slab_thickness_m <= 0:
            raise ValueError("Storey height and slab thickness must be positive.")
        if not self.rooms:
            raise ValueError("At least one room is required.")
        room_ids = [room.room_id for room in self.rooms]
        opening_ids = [opening.opening_id for opening in self.openings]
        if len(room_ids) != len(set(room_ids)):
            raise ValueError("Room ids must be unique.")
        if len(opening_ids) != len(set(opening_ids)):
            raise ValueError("Opening ids must be unique.")
        for index, room in enumerate(self.rooms):
            for other in self.rooms[index + 1 :]:
                overlap_width = min(room.x2, other.x2) - max(room.x, other.x)
                overlap_depth = min(room.y2, other.y2) - max(room.y, other.y)
                if overlap_width > 1e-9 and overlap_depth > 1e-9:
                    raise ValueError(
                        f"Rooms {room.room_id} and {other.room_id} overlap; takeoff requires non-overlapping rectangles."
                    )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> FloorPlan:
        required = {
            "plan_id",
            "name",
            "data_status",
            "source_note",
            "drawing_unit",
            "scale_m_per_unit",
            "storey_height_m",
            "slab_thickness_m",
            "rooms",
            "openings",
        }
        missing = sorted(required - payload.keys())
        if missing:
            raise ValueError(f"Missing floor-plan fields: {missing}")
        return cls(
            plan_id=str(payload["plan_id"]),
            name=str(payload["name"]),
            data_status=str(payload["data_status"]),
            source_note=str(payload["source_note"]),
            drawing_unit=str(payload["drawing_unit"]),
            scale_m_per_unit=float(payload["scale_m_per_unit"]),
            storey_height_m=float(payload["storey_height_m"]),
            slab_thickness_m=float(payload["slab_thickness_m"]),
            rooms=tuple(Room(**room) for room in payload["rooms"]),
            openings=tuple(Opening(**opening) for opening in payload["openings"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WallSegment:
    orientation: str
    coordinate: float
    start: float
    end: float
    wall_type: str
    room_ids: tuple[str, ...]

    @property
    def length_units(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class QuantityLine:
    item_code: str
    description: str
    unit: str
    quantity: float
    formula: str
    source_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TakeoffResult:
    plan_id: str
    data_status: str
    status: str
    scale_m_per_unit: float
    external_wall_length_m: float
    partition_length_m: float
    opening_deductions_m2: dict[str, float]
    quantities: tuple[QuantityLine, ...]

    def quantity_map(self) -> dict[str, float]:
        return {line.item_code: line.quantity for line in self.quantities}

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RateItem:
    item_code: str
    description: str
    unit: str
    unit_rate: float
    uncertainty_fraction: float
    provenance: str

    def __post_init__(self) -> None:
        if self.unit_rate < 0:
            raise ValueError("Unit rates cannot be negative.")
        if not 0 <= self.uncertainty_fraction < 1:
            raise ValueError("Rate uncertainty must be in [0, 1).")
        if not self.provenance.strip():
            raise ValueError("Every rate requires provenance.")


@dataclass(frozen=True)
class RateLibrary:
    version: str
    currency: str
    data_status: str
    source_note: str
    items: tuple[RateItem, ...]

    def __post_init__(self) -> None:
        if self.data_status != "synthetic":
            raise ValueError("Bundled rates must be explicitly labeled synthetic.")
        if not self.version.strip() or not self.currency.strip() or not self.source_note.strip():
            raise ValueError("Rate-library version, currency, and source note are required.")
        codes = [item.item_code for item in self.items]
        if len(codes) != len(set(codes)):
            raise ValueError("Rate item codes must be unique.")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RateLibrary:
        return cls(
            version=str(payload["version"]),
            currency=str(payload["currency"]),
            data_status=str(payload["data_status"]),
            source_note=str(payload["source_note"]),
            items=tuple(RateItem(**item) for item in payload["items"]),
        )


@dataclass(frozen=True)
class CostLine:
    item_code: str
    description: str
    unit: str
    quantity: float
    unit_rate: float
    amount: float
    low_amount: float
    high_amount: float
    rate_provenance: str
    quantity_source_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CostEstimate:
    plan_id: str
    status: str
    currency: str
    rate_library_version: str
    base_total: float
    low_total: float
    high_total: float
    priced_lines: tuple[CostLine, ...]
    unpriced_item_codes: tuple[str, ...]
    exclusions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TenderSubmission:
    tender_id: str
    bidder_alias: str
    data_status: str
    currency: str
    line_items: dict[str, float]

    def __post_init__(self) -> None:
        if self.data_status != "synthetic":
            raise ValueError("Bundled tenders must be explicitly labeled synthetic.")
        if not self.tender_id.strip() or not self.bidder_alias.strip():
            raise ValueError("Tender id and bidder alias are required.")
        if any(float(amount) < 0 for amount in self.line_items.values()):
            raise ValueError("Tender line amounts cannot be negative.")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> TenderSubmission:
        return cls(
            tender_id=str(payload["tender_id"]),
            bidder_alias=str(payload["bidder_alias"]),
            data_status=str(payload["data_status"]),
            currency=str(payload["currency"]),
            line_items={key: float(value) for key, value in payload["line_items"].items()},
        )


@dataclass(frozen=True)
class TenderFlag:
    item_code: str
    flag: str
    benchmark_amount: float | None
    submitted_amount: float | None
    ratio_to_benchmark: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TenderAnalysis:
    tender_id: str
    bidder_alias: str
    status: str
    currency: str
    submitted_total: float
    benchmark_total: float
    deviation_fraction: float
    completeness_fraction: float
    flags: tuple[TenderFlag, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
