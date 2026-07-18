# Construction Embodied Agent Evaluation

## Evaluation Questions

1. Can each classifier imitate expert actions on states from unseen procedural layouts?
2. Does expert-state action quality translate into closed-loop completion?
3. Does agent-centered local encoding recover performance lost by a flattened world-frame raster?
4. How often does each raw learned policy attempt unsafe or task-invalid actions?
5. What changes when an action filter is applied?
6. Does the deterministic A* reference solve the same holdout scenarios?

## Shared Split

| Split | Delivery | Inspection | Charging | Total | Expert steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 64 | 64 | 64 | 192 | 1,830 |
| Holdout | 32 | 32 | 32 | 96 | 948 |

Train seed: `1701`. Holdout seed: `2903`. Scenario IDs include the split and are tested for zero overlap. All three classifiers use the same generated scenarios and A* action labels.

## Compared Representations

| Representation | Model | Inputs | Holdout accuracy | Macro-F1 |
| --- | --- | ---: | ---: | ---: |
| Engineered state | `RandomForestClassifier` | 24 | `0.855` | `0.916` |
| Flattened semantic state raster | `StandardScaler` + 64-unit `MLPClassifier` | 398 | `0.478` | `0.454` |
| Egocentric 5x5 local state | `StandardScaler` + 64-unit `MLPClassifier` | 210 | `0.834` | `0.904` |

The world raster contains eight 7x7 channels plus six global values. The egocentric representation contains eight 5x5 channels centered on the agent, with off-grid cells marked explicitly, plus ten task and relative-subgoal values. Hazards outside the local window are hidden from that classifier. Both representations are read directly from simulator state; neither contains camera pixels or learned perception features.

## Closed-Loop Results

| Policy | Success | Unsafe-action rate | Task-error rate | Interventions |
| --- | ---: | ---: | ---: | ---: |
| Engineered-state RF, raw | `0.646` | `0.674` | `0.000` | 0 |
| Engineered-state RF, filtered | `0.698` | `0.000` | `0.000` | 692 |
| Semantic-raster MLP, raw | `0.031` | `0.682` | `0.186` | 0 |
| Semantic-raster MLP, filtered | `0.292` | `0.000` | `0.000` | 3529 |
| Egocentric local-state MLP, raw | `0.573` | `0.595` | `0.064` | 0 |
| Egocentric local-state MLP, filtered | `0.760` | `0.000` | `0.000` | 943 |
| A* planning reference | `1.000` | `0.000` | `0.000` | 0 |

The world-frame neural baseline is materially worse. Agent-centered local encoding recovers `0.356` action accuracy and `0.468` filtered success over it. The egocentric classifier still trails the engineered-state action accuracy by `0.021`, has raw success `0.573`, and relies on 943 full-state filter interventions to reach `0.760`. This is a controlled observation-design result, not a visual-policy or safety result.

## Metric Definitions

| Metric | Meaning | Boundary |
| --- | --- | --- |
| Holdout action accuracy | Fraction of expert actions predicted on holdout expert states. | Does not measure recovery after policy-induced state drift. |
| Holdout macro-F1 | Class-balanced expert-action score. | Rare terminal actions remain supported by a small synthetic set. |
| Closed-loop success | Fraction of holdout scenarios ending with the task-specific `task_complete`, `inspection_complete`, or `charged` event. | Timeout and nonterminal battery recovery are failures; the metric applies only to this simulator distribution. |
| Unsafe-action rate | Blocked movement attempts divided by executed actions. | Simulator violations are not physical-safety measurements. |
| Task-error rate | Invalid pick, drop, inspect, or charge commands divided by actions. | Command validity is not task completion. |
| Intervention count | Top-ranked learned actions rejected by the filter. | A safe replacement may still fail the task. |
| Reward and steps | Local efficiency indicators. | Reward design has no external validation. |

## Leakage Controls

- Different deterministic seeds generate train and holdout scenarios.
- Scenario IDs are disjoint and overlap is written to the JSON summary.
- Holdout trajectories are not used for fitting either model.
- All three learned models receive identical scenario splits and expert labels.
- Learned policies do not call the A* expert for task-goal routing during rollout.
- The safety filter does not insert an expert task route. A reserve controller may route only to a charger.
- Tests fail if IDs overlap, observation schemas drift, filtered unsafe-action rates become nonzero, timeout or recovery is counted as task success, or generated artifacts disappear.

## Reproduce

```bash
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python -m pytest tests/test_vla_embodied_agent.py
```

The machine-readable source of record is [`demo_outputs/behavior_cloning_eval_summary.json`](demo_outputs/behavior_cloning_eval_summary.json).
