# VLA Embodied Agent Evaluation

Local construction-site simulation metrics. This is not a real robot deployment.

- Scenarios: 3

| Policy | Success rate | Avg steps | Avg reward | Unsafe action rate | Blocked actions | Safety interventions |
| --- | --- | --- | --- | --- | --- | --- |
| naive_language | 0.667 | 10.333 | -0.467 | 0.161 | 4 | 0 |
| random | 0.0 | 18 | -3.8 | 0.37 | 6 | 0 |
| safety_shielded | 1.0 | 11 | 2.567 | 0.0 | 0 | 0 |

## Interpretation

- `random` is a weak baseline for action-space sanity checks.
- `naive_language` maps instruction text to direct moves without site-aware route planning.
- `safety_shielded` uses parsed task intent plus safe route planning around obstacles, workers, and restricted zones.
- Metrics are simulator regression checks, not evidence of robot-hardware safety.
