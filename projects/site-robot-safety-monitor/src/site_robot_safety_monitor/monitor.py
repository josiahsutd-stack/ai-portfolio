from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

RULE_THRESHOLDS = {
    "worker_proximity": {"distance_m_lt": 1.2, "speed_mps_gt": 0.8},
    "obstacle_clearance": {"distance_m_lt": 0.7, "speed_mps_gt": 0.5},
    "restricted_zone_speed": {"speed_mps_gt": 1.0},
    "payload_stability": {"payload_kg_gt": 60.0, "tilt_deg_gt": 8.0},
}


@dataclass(frozen=True)
class RiskEvent:
    timestamp: str
    robot_id: str
    severity: str
    risk_type: str
    evidence: str
    recommended_action: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_telemetry(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    if data.empty:
        raise ValueError("Robot telemetry is empty.")
    return data


def classify_risk_event(row: pd.Series) -> list[RiskEvent]:
    events: list[RiskEvent] = []
    timestamp = str(row["timestamp"])
    robot_id = str(row["robot_id"])
    speed = float(row["speed_mps"])
    worker_distance = float(row["nearest_worker_m"])
    obstacle_distance = float(row["nearest_obstacle_m"])
    zone = str(row["zone_type"])
    payload = float(row["payload_kg"])
    tilt = float(row["tilt_deg"])
    emergency_stop = bool(row["emergency_stop"])

    if emergency_stop:
        events.append(
            RiskEvent(
                timestamp,
                robot_id,
                "high",
                "emergency_stop",
                "Emergency stop was triggered.",
                "Pause autonomy, inspect the robot, and log the incident before resuming.",
            )
        )
    worker_rule = RULE_THRESHOLDS["worker_proximity"]
    if worker_distance < worker_rule["distance_m_lt"] and speed > worker_rule["speed_mps_gt"]:
        events.append(
            RiskEvent(
                timestamp,
                robot_id,
                "high",
                "worker_proximity",
                f"Worker distance {worker_distance:.2f} m while speed was {speed:.2f} m/s.",
                "Reduce speed, increase exclusion buffer, or switch to escorted/manual mode.",
            )
        )
    obstacle_rule = RULE_THRESHOLDS["obstacle_clearance"]
    if obstacle_distance < obstacle_rule["distance_m_lt"] and speed > obstacle_rule["speed_mps_gt"]:
        events.append(
            RiskEvent(
                timestamp,
                robot_id,
                "medium",
                "obstacle_clearance",
                f"Obstacle distance {obstacle_distance:.2f} m while moving.",
                "Slow down and re-plan around temporary site obstruction.",
            )
        )
    restricted_rule = RULE_THRESHOLDS["restricted_zone_speed"]
    if "restricted" in zone.lower() and speed > restricted_rule["speed_mps_gt"]:
        events.append(
            RiskEvent(
                timestamp,
                robot_id,
                "high",
                "restricted_zone_speed",
                f"Robot moved at {speed:.2f} m/s in `{zone}`.",
                "Require explicit human authorization and speed cap for restricted zones.",
            )
        )
    payload_rule = RULE_THRESHOLDS["payload_stability"]
    if payload > payload_rule["payload_kg_gt"] and tilt > payload_rule["tilt_deg_gt"]:
        events.append(
            RiskEvent(
                timestamp,
                robot_id,
                "medium",
                "payload_stability",
                f"Payload {payload:.0f} kg with tilt {tilt:.1f} degrees.",
                "Lower speed, verify load securing, and avoid uneven temporary surfaces.",
            )
        )
    return events


def analyze_telemetry(data: pd.DataFrame) -> dict[str, object]:
    if data.empty:
        return {"event_count": 0, "events": [], "summary": "No telemetry records supplied."}
    events: list[RiskEvent] = []
    for _, row in data.iterrows():
        events.extend(classify_risk_event(row))
    high_count = sum(1 for event in events if event.severity == "high")
    medium_count = sum(1 for event in events if event.severity == "medium")
    summary = (
        f"Detected {len(events)} safety event(s): {high_count} high and {medium_count} medium. "
        "Review high-severity events before allowing autonomous operation."
        if events
        else "No synthetic robot safety events detected."
    )
    return {
        "event_count": len(events),
        "high_count": high_count,
        "medium_count": medium_count,
        "events": [event.to_dict() for event in events],
        "summary": summary,
    }
