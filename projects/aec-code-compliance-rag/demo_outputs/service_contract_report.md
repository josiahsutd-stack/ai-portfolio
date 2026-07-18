# Local Service Contract Evaluation

In-process ASGI evaluation over the bundled synthetic corpus. This proves local interface behavior, not cloud deployment, operational reliability, or user adoption.

| Contract check | Result |
| --- | --- |
| liveness is public | pass |
| readiness checks configuration and index | pass |
| missing key is rejected | pass |
| wrong key is rejected | pass |
| grounded query is answered | pass |
| request id is propagated | pass |
| no evidence status is preserved | pass |
| invalid retrieval mode is rejected | pass |
| retrieval endpoint returns ranked results | pass |
| query payloads are redacted by default | pass |
| query logs preserve request ids | pass |
| service metrics record routes and errors | pass |

## Observed Evidence

- Contract checks passed: 12/12
- Indexed documents at readiness: 7
- Grounded answer citations: 4
- Raw retrieval results: 3
- Redacted query-log rows: 2
- Requests observed before metrics response: 9
- Client errors observed before metrics response: 3

## Boundary

The API key, request tracing, readiness, metrics, and local SQLite audit log are implementation evidence only. They do not establish internet exposure, secret management, distributed tracing, load capacity, availability, incident response, privacy compliance, or production security.
