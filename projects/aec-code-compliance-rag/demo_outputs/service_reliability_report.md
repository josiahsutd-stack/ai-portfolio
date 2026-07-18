# Local Service Reliability Evaluation

Fixed concurrent in-process ASGI evaluation over the bundled synthetic corpus. It exercises local persistence and objective logic; it is not external load testing, availability evidence, or a production SLO.

## Workload

- Requests: 48
- Maximum concurrency: 8
- Distinct questions: 4
- The hybrid index is warmed through readiness before timing the query workload.

## Objective Result

- Status: `pass`
- P95 latency budget: at or below `500.0` ms - pass
- Server-error-rate budget: at or below `0.01` - pass
- Successful responses: `48/48`
- Server errors: `0`
- Durable query rows after app reconstruction: `48`
- Process request count after app reconstruction: `0`

Exact wall-clock latency is printed at runtime but is not committed because it is machine-dependent. The versioned artifact records only whether the fixed local budget was met.

## Contract Checks

| Check | Result |
| --- | --- |
| readiness warms index | pass |
| all workload requests return 200 | pass |
| request ids remain unique and propagated | pass |
| query logs are complete and redacted | pass |
| no server errors in workload | pass |
| p95 latency budget is met | pass |
| server error rate budget is met | pass |
| query objective has sufficient data | pass |
| durable query count matches workload | pass |
| durable telemetry survives app reconstruction | pass |
| process metrics reset on app reconstruction | pass |
| objective status survives app reconstruction | pass |
| telemetry schema excludes request payloads | pass |
| telemetry writes succeed | pass |

## Boundary

Telemetry stores timestamp, service-instance id, bounded request id, method, route template, status, and latency. It does not store arbitrary headers, query strings, questions, or response bodies. The SQLite file is a local durability mechanism, not a distributed metrics backend. This evaluation does not demonstrate TLS, identity-aware authorization, multi-process aggregation, autoscaling, sustained capacity, incident response, or external availability.
