import json
from pathlib import Path

import pandas as pd
from site_robot_safety_monitor import RULE_THRESHOLDS, analyze_telemetry, load_telemetry

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "projects" / "site-robot-safety-monitor"


def test_robot_safety_monitor_flags_high_risk_events() -> None:
    data = pd.DataFrame(
        [
            {
                "timestamp": "2026-06-18T09:00:00",
                "robot_id": "cart-01",
                "speed_mps": 1.3,
                "nearest_worker_m": 0.8,
                "nearest_obstacle_m": 0.5,
                "zone_type": "restricted lift zone",
                "payload_kg": 72,
                "tilt_deg": 10,
                "emergency_stop": True,
            }
        ]
    )

    result = analyze_telemetry(data)
    risk_types = {event["risk_type"] for event in result["events"]}

    assert result["high_count"] >= 3
    assert "worker_proximity" in risk_types
    assert "restricted_zone_speed" in risk_types
    assert "emergency_stop" in risk_types


def test_robot_safety_monitor_handles_empty_inputs() -> None:
    result = analyze_telemetry(pd.DataFrame())

    assert result["event_count"] == 0
    assert result["events"] == []


def test_worker_proximity_rule_is_exclusive_at_threshold() -> None:
    threshold = RULE_THRESHOLDS["worker_proximity"]
    row = pd.Series(
        {
            "timestamp": "2026-06-18T09:00:00",
            "robot_id": "cart-01",
            "speed_mps": threshold["speed_mps_gt"],
            "nearest_worker_m": threshold["distance_m_lt"],
            "nearest_obstacle_m": 5.0,
            "zone_type": "open deck",
            "payload_kg": 0,
            "tilt_deg": 0,
            "emergency_stop": False,
        }
    )

    result = analyze_telemetry(pd.DataFrame([row]))

    assert result["event_count"] == 0


def test_versioned_safety_artifact_matches_current_fixture() -> None:
    data = load_telemetry(PROJECT_ROOT / "sample_data" / "synthetic_robot_telemetry.csv")
    result = analyze_telemetry(data)
    artifact = json.loads(
        (PROJECT_ROOT / "demo_outputs" / "safety_monitor_demo_summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["data_status"] == "synthetic"
    assert artifact["report_type"] == "deterministic_rule_execution"
    assert artifact["dataset"]["row_count"] == len(data)
    assert artifact["thresholds"] == RULE_THRESHOLDS
    assert artifact["result"]["event_count"] == result["event_count"]
    assert artifact["result"]["high_count"] == result["high_count"]
    assert artifact["result"]["medium_count"] == result["medium_count"]
    assert artifact["first_event"] == result["events"][0]
    assert artifact["first_event"]["evidence"] == (
        "Worker distance 0.76 m while speed was 1.06 m/s."
    )
