import pandas as pd
from bim_issue_detection_agent import detect_issues


def test_detects_core_bim_issues() -> None:
    data = pd.DataFrame(
        [
            {
                "room_id": "A-1",
                "room_name": "",
                "area_scheduled": 20,
                "area_model": 28,
                "door_clearance_mm": 760,
                "material_spec": "",
                "fire_rating_note": "",
                "accessibility_note": "",
                "coordination_comment": "MEP clash unresolved",
            },
            {
                "room_id": "A-1",
                "room_name": "Accessible WC",
                "area_scheduled": 10,
                "area_model": 10,
                "door_clearance_mm": 780,
                "material_spec": "tile",
                "fire_rating_note": "",
                "accessibility_note": "",
                "coordination_comment": "",
            },
        ]
    )

    issue_types = {issue.issue_type for issue in detect_issues(data)}

    assert "duplicate_room_id" in issue_types
    assert "missing_room_name" in issue_types
    assert "area_mismatch" in issue_types
    assert "door_clearance_conflict" in issue_types


def test_bim_empty_dataframe_returns_no_issues() -> None:
    assert detect_issues(pd.DataFrame()) == []
