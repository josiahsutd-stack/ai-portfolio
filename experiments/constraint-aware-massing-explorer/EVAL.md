# Evaluation

## Question

Does constraint-aware sampling produce more feasible and useful candidates than geometry sampled without awareness of the same constraints?

## Protocol

- Three bundled synthetic site scenarios.
- Three fixed seeds: `11`, `23`, and `37`.
- Equal candidate counts for each generation mode in each run.
- A shared hard validator and shared objective functions.
- Pareto filtering only after feasibility checks.

The unconstrained baseline samples typology dimensions, floors, and positions without using setback, height, coverage, or GFA targets. The constraint-aware mode samples inside the buildable envelope and conditions footprint/floor ranges on supplied limits. Neither mode repairs candidates after validation.

## Metrics

| Metric | Definition |
| --- | --- |
| Feasible-candidate rate | Candidates with zero hard-constraint violations divided by generated candidates. |
| Best utility | Highest weighted objective score among feasible candidates in a run. |
| Best GFA error | Lowest absolute target-GFA error among feasible candidates in a run. |
| Pareto count | Feasible candidates not dominated across GFA fit, solar, daylight, wind, and access proxies. |
| Violation counts | Validator events; one candidate may produce multiple events. |

## Checked-In Result

| Metric | Constraint-aware | Unconstrained baseline |
| --- | ---: | ---: |
| Mean feasible-candidate rate | `0.977` | `0.052` |
| Mean best utility per run | `0.767` | `0.628` |
| Mean best target-GFA error | `0.19%` | `34.47%` |

Constraint-aware generation produced `20` maximum-GFA violation events and no other hard-failure type across the nine runs. The unconstrained baseline produced failures across setbacks, site bounds, height, coverage, maximum GFA, and both access points. These are implementation-level regression results over synthetic scenarios.

## Proxy Definitions

- **GFA fit:** `1 - absolute percentage error`, clipped to `[0, 1]`.
- **Solar:** orientation-weighted exposed facade length with a stated north rotation.
- **Daylight:** normalized exposed-perimeter-to-footprint-area ratio.
- **Wind:** open-ground ratio plus projected blockage perpendicular to the prevailing cardinal wind.
- **Access:** normalized grid-route length from supplied ingress and egress points to a mass edge.

These proxies are useful for option ranking inside this demo. They are not substitutes for climate files, ray tracing, daylight autonomy, CFD, pedestrian simulation, fire engineering, or accessibility review.

## Leakage And Fairness Controls

- Both modes use the same scenarios, seeds, candidate counts, validator, and utility calculation.
- The constraint-aware generator is expected to improve feasibility because it receives the hard constraints; this is an engineering baseline comparison, not a claim of learned intelligence.
- No external test set or expert labels are available. Results should not be read as design-quality generalization.

## Artifacts

- [`demo_outputs/evaluation_summary.json`](demo_outputs/evaluation_summary.json): run-level and aggregate metrics.
- [`demo_outputs/evaluation_report.md`](demo_outputs/evaluation_report.md): compact result table.
- [`demo_outputs/failure_analysis.md`](demo_outputs/failure_analysis.md): violation counts by mode.
- [`demo_outputs/top_options.json`](demo_outputs/top_options.json): geometry and metrics for selected Pareto options.
- [`demo_outputs/top_option.svg`](demo_outputs/top_option.svg): actual evaluated option diagram.
- [`demo_outputs/option_comparison.svg`](demo_outputs/option_comparison.svg): three-option comparison.
