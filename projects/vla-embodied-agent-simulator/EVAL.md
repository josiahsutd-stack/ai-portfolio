# Construction Embodied Agent Evaluation

## Evaluation Questions

1. Can each classifier imitate expert actions on states from unseen procedural layouts?
2. Does expert-state action quality translate into closed-loop completion?
3. Does agent-centered local encoding recover performance lost by a flattened world-frame raster?
4. How often does each raw learned policy attempt unsafe or task-invalid actions?
5. What changes when an action filter is applied?
6. Does the deterministic A* reference solve the same holdout scenarios?
7. How much does a rendered-pixel policy degrade under an unseen appearance palette?

## Shared Split

| Split | Delivery | Inspection | Charging | Total | Expert steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 64 | 64 | 64 | 192 | 1,830 |
| Holdout | 32 | 32 | 32 | 96 | 948 |

Train seed: `1701`. Holdout seed: `2903`. Scenario IDs include the split and are tested for zero overlap. All four learned policy families use the same generated scenarios and A* action labels. The RGB policy expands each expert state across the `day` and `overcast` training palettes; the `worklight` palette is held out.

## Compared Representations

| Representation | Model | Inputs | Holdout accuracy | Macro-F1 |
| --- | --- | ---: | ---: | ---: |
| Engineered state | `RandomForestClassifier` | 24 | `0.855` | `0.916` |
| Flattened semantic state raster | `StandardScaler` + 64-unit `MLPClassifier` | 398 | `0.478` | `0.454` |
| Egocentric 5x5 local state | `StandardScaler` + 64-unit `MLPClassifier` | 210 | `0.834` | `0.904` |
| Synthetic 10x10 RGB crop plus task telemetry | `StandardScaler` + 64-unit `MLPClassifier` | 310 | `0.813` | `0.805` |
| Same RGB model, pixels replaced by training means | No refit; ten active telemetry values | 310 | `0.474` | `0.464` |
| Same RGB model, unseen `worklight` palette | No refit | 310 | `0.417` | `0.429` |

The world raster contains eight 7x7 channels plus six global values. The egocentric representation contains eight 5x5 channels centered on the agent, with off-grid cells marked explicitly, plus ten task and relative-subgoal values. The RGB representation replaces those local semantic channels with 300 normalized pixel values while retaining the same ten task/navigation values. Hazards outside each local window are hidden from its classifier. The RGB pixels are rendered from privileged state; they are not captured by a physical or photorealistic simulated camera.

## Closed-Loop Results

| Policy | Success | Unsafe-action rate | Task-error rate | Interventions |
| --- | ---: | ---: | ---: | ---: |
| Engineered-state RF, raw | `0.646` | `0.674` | `0.000` | 0 |
| Engineered-state RF, filtered | `0.698` | `0.000` | `0.000` | 692 |
| Semantic-raster MLP, raw | `0.031` | `0.682` | `0.186` | 0 |
| Semantic-raster MLP, filtered | `0.292` | `0.000` | `0.000` | 3529 |
| Egocentric local-state MLP, raw | `0.573` | `0.595` | `0.064` | 0 |
| Egocentric local-state MLP, filtered | `0.760` | `0.000` | `0.000` | 943 |
| Synthetic RGB MLP, raw | `0.635` | `0.041` | `0.489` | 0 |
| Synthetic RGB MLP, filtered | `0.719` | `0.000` | `0.000` | 965 |
| Synthetic RGB MLP, shifted appearance, raw | `0.000` | `0.472` | `0.335` | 0 |
| Synthetic RGB MLP, shifted appearance, filtered | `0.427` | `0.000` | `0.000` | 3315 |
| A* planning reference | `1.000` | `0.000` | `0.000` | 0 |

The world-frame neural baseline is materially worse. Agent-centered local encoding recovers `0.356` action accuracy and `0.468` filtered success over it. Mean-pixel ablation reduces standard RGB action accuracy by `0.340`, from `0.813` to `0.474`, so the image is not merely decorative beside telemetry. The unseen palette then loses `0.396` action accuracy and `0.292` filtered success. Its raw completion falls from `0.635` to `0.000`, while the filter intervenes 3,315 times to recover `0.427`. This is controlled synthetic-rendering evidence, not physical-camera perception or robot-safety evidence.

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
| Appearance-shift delta | Difference between the standard and held-out RGB palettes for the same states and labels. | Tests only one hand-authored color shift; it is not a broad visual-robustness benchmark. |
| Mean-pixel ablation | Holdout score after every RGB value is replaced with its training-set mean while telemetry remains unchanged. | Shows pixel dependence, but not which visual categories were learned or whether perception transfers. |

## Leakage Controls

- Different deterministic seeds generate train and holdout scenarios.
- Scenario IDs are disjoint and overlap is written to the JSON summary.
- Holdout trajectories are not used for fitting either model.
- All four learned policy families receive identical scenario splits and expert labels.
- The RGB model sees two training palettes. The work-light palette is used only for evaluation, and standard/shifted metrics are reported separately.
- Learned policies do not call the A* expert for task-goal routing during rollout.
- The safety filter does not insert an expert task route. A reserve controller may route only to a charger.
- Tests fail if IDs overlap, observation schemas drift, the RGB holdout palette appears in training, filtered unsafe-action rates become nonzero, timeout or recovery is counted as task success, or generated artifacts disappear.

## Reproduce

```bash
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python -m pytest tests/test_vla_embodied_agent.py
```

The machine-readable source of record is [`demo_outputs/behavior_cloning_eval_summary.json`](demo_outputs/behavior_cloning_eval_summary.json).
