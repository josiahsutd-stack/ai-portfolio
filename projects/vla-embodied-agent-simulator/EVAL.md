# Construction Embodied Agent Evaluation

## Evaluation Questions

1. Can each classifier imitate expert actions on states from unseen procedural layouts?
2. Does expert-state action quality translate into closed-loop completion?
3. Does a flattened semantic raster help or hurt relative to engineered state features?
4. How often does each raw learned policy attempt unsafe or task-invalid actions?
5. What changes when an action filter is applied?
6. Does the deterministic A* reference solve the same holdout scenarios?

## Shared Split

| Split | Delivery | Inspection | Charging | Total | Expert steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 64 | 64 | 64 | 192 | 1,830 |
| Holdout | 32 | 32 | 32 | 96 | 948 |

Train seed: `1701`. Holdout seed: `2903`. Scenario IDs include the split and are tested for zero overlap. Both classifiers use the same generated scenarios and A* action labels.

## Compared Representations

| Representation | Model | Inputs | Holdout accuracy | Macro-F1 |
| --- | --- | ---: | ---: | ---: |
| Engineered state | `RandomForestClassifier` | 24 | `0.855` | `0.916` |
| Flattened semantic state raster | `StandardScaler` + 64-unit `MLPClassifier` | 398 | `0.478` | `0.454` |

The raster contains eight 7x7 channels for agent, current subgoal, obstacles, restricted zones, worker zones, slow zones, objects, and named zones, plus six global task/state values. These channels are read directly from simulator state; they are not camera pixels or learned perception features.

## Closed-Loop Results

| Policy | Success | Unsafe-action rate | Task-error rate | Interventions |
| --- | ---: | ---: | ---: | ---: |
| Engineered-state RF, raw | `0.646` | `0.674` | `0.000` | 0 |
| Engineered-state RF, filtered | `0.698` | `0.000` | `0.000` | 692 |
| Semantic-raster MLP, raw | `0.031` | `0.682` | `0.186` | 0 |
| Semantic-raster MLP, filtered | `0.469` | `0.000` | `0.000` | 3,617 |
| A* planning reference | `1.000` | `0.000` | `0.000` | 0 |

The neural baseline is materially worse. Its flat input discards explicit spatial inductive bias, and the demonstration set is small for a 398-input network. The result is reported as evidence against an easy "neural is better" assumption, not as a visual-policy success.

## Metric Definitions

| Metric | Meaning | Boundary |
| --- | --- | --- |
| Holdout action accuracy | Fraction of expert actions predicted on holdout expert states. | Does not measure recovery after policy-induced state drift. |
| Holdout macro-F1 | Class-balanced expert-action score. | Rare terminal actions remain supported by a small synthetic set. |
| Closed-loop success | Fraction of holdout scenarios completed from start to terminal action. | Applies only to this simulator distribution. |
| Unsafe-action rate | Blocked movement attempts divided by executed actions. | Simulator violations are not physical-safety measurements. |
| Task-error rate | Invalid pick, drop, inspect, or charge commands divided by actions. | Command validity is not task completion. |
| Intervention count | Top-ranked learned actions rejected by the filter. | A safe replacement may still fail the task. |
| Reward and steps | Local efficiency indicators. | Reward design has no external validation. |

## Leakage Controls

- Different deterministic seeds generate train and holdout scenarios.
- Scenario IDs are disjoint and overlap is written to the JSON summary.
- Holdout trajectories are not used for fitting either model.
- Both models receive identical scenario splits and expert labels.
- Learned policies do not call the A* expert for task-goal routing during rollout.
- The safety filter does not insert an expert task route. A reserve controller may route only to a charger.
- Tests fail if IDs overlap, observation schemas drift, filtered unsafe-action rates become nonzero, or generated artifacts disappear.

## Reproduce

```bash
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python -m pytest tests/test_vla_embodied_agent.py
```

The machine-readable source of record is [`demo_outputs/behavior_cloning_eval_summary.json`](demo_outputs/behavior_cloning_eval_summary.json).
