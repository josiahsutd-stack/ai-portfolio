from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class Issue:
    room_id: str
    issue_type: str
    severity: str
    message: str
    suggested_fix: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_room_schedule(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path).fillna("")
    if data.empty:
        raise ValueError("BIM room schedule is empty.")
    return data


def _severity(score: int) -> str:
    if score >= 3:
        return "high"
    if score == 2:
        return "medium"
    return "low"


def detect_issues(data: pd.DataFrame) -> list[Issue]:
    if data.empty:
        return []
    issues: list[Issue] = []
    duplicate_ids = set(data.loc[data["room_id"].duplicated(keep=False), "room_id"].astype(str))
    for _, row in data.iterrows():
        room_id = str(row.get("room_id", "")).strip() or "unknown"
        room_name = str(row.get("room_name", "")).strip()
        material = str(row.get("material_spec", "")).strip()
        fire_note = str(row.get("fire_rating_note", "")).strip()
        accessibility_note = str(row.get("accessibility_note", "")).strip()
        comment = str(row.get("coordination_comment", "")).strip()
        scheduled = float(row.get("area_scheduled", 0) or 0)
        modeled = float(row.get("area_model", 0) or 0)
        door_clearance = float(row.get("door_clearance_mm", 0) or 0)
        accessible_context = (
            "accessible" in room_name.lower() or "public" in accessibility_note.lower()
        )

        if room_id in duplicate_ids:
            issues.append(
                Issue(
                    room_id,
                    "duplicate_room_id",
                    "high",
                    f"Room ID `{room_id}` appears more than once.",
                    "Assign unique room IDs before downstream BIM exports or schedules are issued.",
                )
            )
        if not room_name:
            issues.append(
                Issue(
                    room_id,
                    "missing_room_name",
                    "medium",
                    "Room has no name in the exported schedule.",
                    "Add a descriptive room name so drawings, schedules, and QA checks align.",
                )
            )
        if scheduled and abs(scheduled - modeled) / scheduled > 0.1:
            issues.append(
                Issue(
                    room_id,
                    "area_mismatch",
                    _severity(2 if abs(scheduled - modeled) < 10 else 3),
                    f"Scheduled area {scheduled:.1f} m2 differs from modeled area {modeled:.1f} m2.",
                    "Review room boundary, schedule formula, and linked model data.",
                )
            )
        if accessible_context and door_clearance < 850:
            issues.append(
                Issue(
                    room_id,
                    "door_clearance_conflict",
                    "high",
                    f"Door clearance is {door_clearance:.0f} mm in an accessible context.",
                    "Review door size, swing, and adjacent fixture clearances.",
                )
            )
        if not material:
            issues.append(
                Issue(
                    room_id,
                    "missing_material_spec",
                    "low",
                    "Material specification is missing.",
                    "Add finish material or mark it as intentionally unassigned.",
                )
            )
        fire_context = "fire" in comment.lower() or "plant" in room_name.lower()
        if fire_context and not fire_note:
            issues.append(
                Issue(
                    room_id,
                    "missing_fire_rating_note",
                    "high",
                    "Potential fire-rated condition has no fire rating note.",
                    "Coordinate fire strategy and add rating tags to the schedule or drawing note.",
                )
            )
        if "accessible" in room_name.lower() and not accessibility_note:
            issues.append(
                Issue(
                    room_id,
                    "missing_accessibility_note",
                    "medium",
                    "Accessible room has no accessibility note.",
                    "Add the required accessibility assumption or checklist reference.",
                )
            )
        if comment:
            issues.append(
                Issue(
                    room_id,
                    "unresolved_coordination_comment",
                    "medium",
                    f"Unresolved coordination comment: {comment}",
                    "Assign ownership and close or carry the comment into the issue register.",
                )
            )
    return issues
