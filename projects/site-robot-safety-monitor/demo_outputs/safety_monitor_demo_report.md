# Robot Safety Rule Execution Report

Deterministic execution over bundled synthetic telemetry. This is not a safety-accuracy evaluation because the fixture has no ground-truth event labels.

## Fixture Result

- Input rows: 36
- Rule events: 26
- High severity: 19
- Medium severity: 7

## Events By Rule

- emergency_stop: 2
- obstacle_clearance: 5
- payload_stability: 2
- restricted_zone_speed: 7
- worker_proximity: 10

## First Emitted Event

- Timestamp: 2026-06-18T09:01:00
- Robot: cart-runner-02
- Rule: worker_proximity
- Severity: high
- Evidence: Worker distance 0.76 m while speed was 1.06 m/s.
- Recommended action: Reduce speed, increase exclusion buffer, or switch to escorted/manual mode.

## Interpretation Boundary

- All telemetry is synthetic and generated locally.
- Thresholds are hand-authored demonstration values, not values derived from a robotics safety standard.
- The fixture has no labeled truth set, so false positives, false negatives, precision, and recall are unknown.
- No sensors, ROS messages, controller integration, latency testing, hardware, field testing, or certified safety logic are included.
