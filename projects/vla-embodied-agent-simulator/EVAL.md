# Construction Embodied Agent Evaluation

## Evaluation Questions

1. Can the classifier imitate expert actions on states from unseen procedural layouts?
2. Does expert-state action quality translate into closed-loop task completion?
3. How many unsafe or task-invalid actions does the raw policy attempt?
4. What safety and task-completion tradeoff appears after action filtering?
5. Does the deterministic A* reference still solve the same holdout scenarios?

## Splits

| Split | Delivery | Inspection | Charging | Total |
| --- | --- | --- | --- | --- |
| Train | 8 | 8 | 8 | 24 |
| Holdout | 8 | 8 | 8 | 24 |

Train seed: `1701`. Holdout seed: `2903`. Scenario IDs include the split and are tested for zero overlap.

## Supervision

The A* planner generates expert trajectories with full access to the structured map. Each expert state is encoded into 24 numeric features and paired with the next discrete action. The model is a `RandomForestClassifier` with a fixed seed.

This setup evaluates behavior cloning from a simulator expert. It does not evaluate learning from human demonstrations, images, language embeddings, or real robot data.

## Metrics

| Metric | Meaning | Important limitation |
| --- | --- | --- |
| Holdout action accuracy | Fraction of expert actions predicted on holdout expert states. | Does not measure recovery after the policy visits a different state. |
| Holdout action macro-F1 | Class-balanced expert-action score. | Rare terminal actions still come from a small dataset. |
| Closed-loop success rate | Fraction of unseen scenarios completed from start to terminal action. | Applies only to this simulator distribution. |
| Unsafe action rate | Blocked movement attempts caused by bounds, obstacles, restricted/worker zones, or battery state, divided by executed actions. | Simulator rule violations are not physical safety measurements. |
| Task error rate | Invalid non-movement commands such as picking or dropping in the wrong context, divided by executed actions. | Measures command validity, not task success. |
| Intervention count | Raw top-ranked actions replaced by the filter. | A replacement can be safe but still fail the task. |
| Average reward and steps | Simulator efficiency indicators. | Reward design is local and not externally validated. |

## Current Measured Results

| Policy / metric | Result |
| --- | --- |
| Holdout expert-action accuracy | `0.863` |
| Holdout expert-action macro-F1 | `0.922` |
| Raw behavior-cloning success | `0.500` |
| Raw behavior-cloning unsafe-action rate | `0.740` |
| Filtered behavior-cloning success | `0.625` |
| Filtered behavior-cloning unsafe-action rate | `0.000` |
| Filter interventions | `207` |
| A* holdout success | `1.000` |
| A* holdout unsafe-action rate | `0.000` |

The gap between `0.863` action accuracy and `0.500` raw closed-loop success is treated as a failure-analysis result, not hidden variance. The filtered policy removes observed simulator safety violations but does not complete every holdout task.

## Leakage Controls

- Different deterministic seeds generate train and holdout scenarios.
- Scenario IDs are disjoint and overlap is written to the evaluation summary.
- Holdout trajectories are used only for action metrics and final policy evaluation.
- Learned policies do not call the A* expert for task-goal routing during rollout.
- The safety filter does not insert an expert task route. A battery-reserve controller may route only to a charger; the current high-battery holdout does not activate that path.
- Tests fail if scenario IDs overlap or the filtered unsafe-action rate becomes nonzero.

## Reproduce

```bash
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python -m pytest tests/test_vla_embodied_agent.py
```

Inspect:

- `demo_outputs/behavior_cloning_eval_summary.json`
- `demo_outputs/behavior_cloning_eval_report.md`
- `demo_outputs/behavior_cloning_failure_analysis.md`
- `demo_outputs/behavior_cloning_model_card.md`
