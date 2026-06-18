import pandas as pd
from site_robot_safety_monitor import analyze_telemetry


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
