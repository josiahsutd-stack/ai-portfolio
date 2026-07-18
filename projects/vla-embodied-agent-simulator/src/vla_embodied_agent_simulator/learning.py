from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

from .environment import (
    MOVE_DELTAS,
    GridWorldEnv,
    Position,
    SiteScenario,
    parse_instruction,
    plan_from_instruction,
    shortest_path_actions,
)
from .policies import PolicyPlan, safety_shielded_policy

FEATURE_NAMES = [
    "task_deliver",
    "task_inspect",
    "task_charge",
    "carrying",
    "battery_ratio",
    "agent_x",
    "agent_y",
    "goal_x",
    "goal_y",
    "relative_goal_x",
    "relative_goal_y",
    "absolute_goal_x",
    "absolute_goal_y",
    "at_subgoal",
    "at_object",
    "at_target_zone",
    *[f"safe_{action}" for action in MOVE_DELTAS],
    *[f"distance_gain_{action}" for action in MOVE_DELTAS],
]

PolicyFn = Callable[[GridWorldEnv, str], PolicyPlan]


@dataclass(frozen=True)
class BehaviorCloningTrainingResult:
    train_scenario_count: int
    holdout_scenario_count: int
    training_step_count: int
    holdout_expert_step_count: int
    holdout_action_accuracy: float
    holdout_action_macro_f1: float
    classes: list[str]
    feature_count: int
    model_file: str
    random_seed: int


def generate_behavior_cloning_scenarios(
    split: str,
    *,
    count_per_task: int = 8,
) -> list[SiteScenario]:
    if split not in {"train", "holdout"}:
        raise ValueError("split must be `train` or `holdout`")
    seed = 1701 if split == "train" else 2903
    rng = random.Random(seed)
    scenarios: list[SiteScenario] = []
    for task_type in ("deliver", "inspect", "charge"):
        for index in range(count_per_task):
            scenarios.append(_valid_random_scenario(rng, split, task_type, index))
    return scenarios


def encode_policy_state(env: GridWorldEnv) -> list[float]:
    task = env.task or parse_instruction("wait", env)
    subgoal = _current_subgoal(env)
    width_scale = max(1, env.width - 1)
    height_scale = max(1, env.height - 1)
    dx = subgoal[0] - env.agent[0]
    dy = subgoal[1] - env.agent[1]
    current_distance = abs(dx) + abs(dy)
    target_zone = env.zones.get(task.target_zone or "")
    at_object = env.agent in env.objects.values()
    at_target_zone = target_zone is not None and env.agent == target_zone
    features = [
        float(task.task_type == "deliver"),
        float(task.task_type == "inspect"),
        float(task.task_type == "charge"),
        float(env.carrying is not None),
        min(1.0, max(0.0, env.battery / 40.0)),
        env.agent[0] / width_scale,
        env.agent[1] / height_scale,
        subgoal[0] / width_scale,
        subgoal[1] / height_scale,
        dx / width_scale,
        dy / height_scale,
        abs(dx) / width_scale,
        abs(dy) / height_scale,
        float(env.agent == subgoal),
        float(at_object),
        float(at_target_zone),
    ]
    for action in MOVE_DELTAS:
        features.append(float(env.is_action_safe(action)[0]))
    for _action, delta in MOVE_DELTAS.items():
        next_position = env.agent[0] + delta[0], env.agent[1] + delta[1]
        next_distance = abs(subgoal[0] - next_position[0]) + abs(subgoal[1] - next_position[1])
        features.append((current_distance - next_distance) / max(width_scale, height_scale))
    return features


def train_behavior_cloning_policy(
    *,
    model_output_dir: str | Path | None = None,
    train_scenarios: list[SiteScenario] | None = None,
    holdout_scenarios: list[SiteScenario] | None = None,
) -> tuple[RandomForestClassifier, BehaviorCloningTrainingResult]:
    train_set = train_scenarios or generate_behavior_cloning_scenarios("train")
    holdout_set = holdout_scenarios or generate_behavior_cloning_scenarios("holdout")
    train_features, train_actions = _expert_examples(train_set)
    holdout_features, holdout_actions = _expert_examples(holdout_set)
    model = RandomForestClassifier(
        n_estimators=160,
        max_depth=16,
        min_samples_leaf=1,
        class_weight="balanced_subsample",
        random_state=37,
        n_jobs=1,
    )
    model.fit(train_features, train_actions)
    holdout_predictions = model.predict(holdout_features)
    model_file = "behavior_cloning_policy.joblib"
    if model_output_dir is not None:
        model_path = Path(model_output_dir) / model_file
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    result = BehaviorCloningTrainingResult(
        train_scenario_count=len(train_set),
        holdout_scenario_count=len(holdout_set),
        training_step_count=len(train_actions),
        holdout_expert_step_count=len(holdout_actions),
        holdout_action_accuracy=round(
            float(accuracy_score(holdout_actions, holdout_predictions)), 3
        ),
        holdout_action_macro_f1=round(
            float(f1_score(holdout_actions, holdout_predictions, average="macro")),
            3,
        ),
        classes=sorted(str(value) for value in model.classes_),
        feature_count=len(FEATURE_NAMES),
        model_file=model_file,
        random_seed=37,
    )
    return model, result


def make_behavior_cloning_policy(
    model: RandomForestClassifier,
    *,
    safety_filter: bool,
) -> PolicyFn:
    policy_name = "behavior_cloning_shielded" if safety_filter else "behavior_cloning_raw"

    def policy(env: GridWorldEnv, instruction: str) -> PolicyPlan:
        probe = env.clone()
        task = parse_instruction(instruction, probe)
        probe.task = task
        actions: list[str] = []
        interventions: list[dict[str, object]] = []
        for _ in range(env.max_steps):
            probabilities = model.predict_proba([encode_policy_state(probe)])[0]
            ranked = sorted(
                zip(model.classes_, probabilities, strict=True),
                key=lambda item: (-float(item[1]), str(item[0])),
            )
            raw_action = str(ranked[0][0])
            action = raw_action
            if safety_filter:
                recovery_action = _battery_recovery_action(probe)
                if recovery_action is not None:
                    action = recovery_action
                    reason = "battery_reserve"
                else:
                    action = next(
                        (
                            str(candidate)
                            for candidate, _probability in ranked
                            if _action_is_context_valid(probe, str(candidate))
                        ),
                        "wait",
                    )
                    reason = _invalid_action_reason(probe, raw_action)
                if action != raw_action:
                    interventions.append(
                        {
                            "step": len(actions) + 1,
                            "blocked_action": raw_action,
                            "reason": reason,
                            "replacement": action,
                        }
                    )
            actions.append(action)
            _state, _reward, done, _info = probe.step(action)
            if done:
                break
        return PolicyPlan(
            policy_name=policy_name,
            actions=actions,
            interventions=interventions,
            task=task,
        )

    return policy


def evaluate_behavior_cloning(
    *,
    model_output_dir: str | Path | None = None,
) -> dict[str, object]:
    from .evaluation import run_episode

    train_scenarios = generate_behavior_cloning_scenarios("train")
    holdout_scenarios = generate_behavior_cloning_scenarios("holdout")
    model, training = train_behavior_cloning_policy(
        model_output_dir=model_output_dir,
        train_scenarios=train_scenarios,
        holdout_scenarios=holdout_scenarios,
    )
    policies: list[PolicyFn] = [
        make_behavior_cloning_policy(model, safety_filter=False),
        make_behavior_cloning_policy(model, safety_filter=True),
        safety_shielded_policy,
    ]
    episodes = [
        run_episode(scenario, policy) for scenario in holdout_scenarios for policy in policies
    ]
    by_policy: dict[str, list[Any]] = {}
    for episode in episodes:
        by_policy.setdefault(episode.policy_name, []).append(episode)
    metrics = {
        name: {
            "episode_count": len(rows),
            "success_rate": round(mean(float(row.success) for row in rows), 3),
            "average_steps": round(mean(row.steps for row in rows), 3),
            "average_reward": round(mean(row.total_reward for row in rows), 3),
            "unsafe_action_rate": round(
                sum(row.unsafe_action_count for row in rows)
                / max(1, sum(row.steps for row in rows)),
                3,
            ),
            "task_error_rate": round(
                sum(row.task_error_count for row in rows) / max(1, sum(row.steps for row in rows)),
                3,
            ),
            "blocked_action_count": sum(row.blocked_action_count for row in rows),
            "intervention_count": sum(row.intervention_count for row in rows),
        }
        for name, rows in sorted(by_policy.items())
    }
    train_ids = {scenario.scenario_id for scenario in train_scenarios}
    holdout_ids = {scenario.scenario_id for scenario in holdout_scenarios}
    task_types: dict[str, str] = {}
    for scenario in holdout_scenarios:
        task = GridWorldEnv.from_scenario(scenario).task
        if task is not None:
            task_types[scenario.scenario_id] = task.task_type
    return {
        "evaluation_type": "fixed-seed procedural construction-site holdout",
        "training": asdict(training),
        "split": {
            "train_scenario_ids": sorted(train_ids),
            "holdout_scenario_ids": sorted(holdout_ids),
            "scenario_id_overlap": sorted(train_ids & holdout_ids),
        },
        "policies": metrics,
        "episodes": [
            {
                "scenario_id": episode.scenario_id,
                "task_type": task_types.get(episode.scenario_id),
                "policy_name": episode.policy_name,
                "success": episode.success,
                "steps": episode.steps,
                "total_reward": episode.total_reward,
                "unsafe_action_count": episode.unsafe_action_count,
                "task_error_count": episode.task_error_count,
                "blocked_action_count": episode.blocked_action_count,
                "intervention_count": episode.intervention_count,
            }
            for episode in episodes
        ],
    }


def write_behavior_cloning_artifacts(
    output_dir: str | Path,
    *,
    model_output_dir: str | Path | None = None,
) -> dict[str, object]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    payload = evaluate_behavior_cloning(model_output_dir=model_output_dir)
    (target / "behavior_cloning_eval_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "behavior_cloning_eval_report.md").write_text(
        _behavior_cloning_report(payload),
        encoding="utf-8",
    )
    (target / "behavior_cloning_model_card.md").write_text(
        _behavior_cloning_model_card(payload),
        encoding="utf-8",
    )
    (target / "behavior_cloning_failure_analysis.md").write_text(
        _behavior_cloning_failure_analysis(payload),
        encoding="utf-8",
    )
    return payload


def _valid_random_scenario(
    rng: random.Random,
    split: str,
    task_type: str,
    index: int,
) -> SiteScenario:
    width = 7
    height = 7
    positions = [(x, y) for y in range(height) for x in range(width)]
    for _attempt in range(200):
        start = rng.choice(positions)
        goal = rng.choice([point for point in positions if _distance(start, point) >= 5])
        object_position = None
        if task_type == "deliver":
            candidates = [
                point
                for point in positions
                if point not in {start, goal}
                and _distance(start, point) >= 2
                and _distance(point, goal) >= 3
            ]
            object_position = rng.choice(candidates)
        protected = {start, goal}
        if object_position is not None:
            protected.add(object_position)
        available = [point for point in positions if point not in protected]
        rng.shuffle(available)
        obstacles = set(available[:5])
        restricted = set(available[5:7])
        workers = set(available[7:9])
        slow = set(available[9:12])
        scenario_id = f"bc_{split}_{task_type}_{index:02d}"
        if task_type == "deliver":
            instruction = "Deliver the material stack to the staging area."
            objects = {"material_stack": object_position} if object_position else {}
            zones = {"staging_area": goal, "charging_dock": start, "base": start}
        elif task_type == "inspect":
            instruction = "Inspect the inspection point before the next work shift."
            objects = {}
            zones = {"inspection_point": goal, "charging_dock": start, "base": start}
        else:
            instruction = "Return to the charging dock before continuing work."
            objects = {}
            zones = {"charging_dock": goal, "base": goal}
        scenario = SiteScenario(
            scenario_id=scenario_id,
            name=f"Behavior Cloning {split.title()} {task_type.title()} {index + 1}",
            instruction=instruction,
            width=width,
            height=height,
            start=start,
            objects=objects,
            zones=zones,
            obstacles=obstacles,
            restricted_zones=restricted,
            slow_zones=slow,
            worker_zones=workers,
            battery=70.0,
            max_steps=55,
            notes=f"Fixed-seed procedural {split} scenario for behavior-cloning evaluation.",
        )
        env = GridWorldEnv.from_scenario(scenario)
        if task_type == "deliver" and object_position is not None:
            valid = bool(shortest_path_actions(env, start, object_position)) and bool(
                shortest_path_actions(env, object_position, goal)
            )
        else:
            valid = bool(shortest_path_actions(env, start, goal))
        if valid:
            return scenario
    raise RuntimeError(
        f"could not generate valid {split} {task_type} scenario after {_attempt + 1} attempts"
    )


def _expert_examples(scenarios: list[SiteScenario]) -> tuple[list[list[float]], list[str]]:
    features: list[list[float]] = []
    actions: list[str] = []
    for scenario in scenarios:
        env = GridWorldEnv.from_scenario(scenario)
        plan = plan_from_instruction(scenario.instruction, env)
        for action in plan:
            features.append(encode_policy_state(env))
            actions.append(action)
            _state, _reward, done, _info = env.step(action)
            if done:
                break
        if not env.trace or not env.trace[-1].info.get("success"):
            raise RuntimeError(f"expert failed generated scenario {scenario.scenario_id}")
    return features, actions


def _current_subgoal(env: GridWorldEnv) -> Position:
    task = env.task
    if task is None:
        return env.agent
    if task.task_type == "deliver":
        if env.carrying:
            return env.zones.get(task.target_zone or "", env.agent)
        return env.objects.get(task.target_object or "", env.agent)
    return env.zones.get(task.target_zone or "", env.agent)


def _action_is_context_valid(env: GridWorldEnv, action: str) -> bool:
    safe, _reason = env.is_action_safe(action)
    if not safe:
        return False
    task = env.task
    if action == "pick":
        return env.carrying is None and env.agent in env.objects.values()
    if action == "drop":
        return bool(env.carrying and task and env.agent == env.zones.get(task.target_zone or ""))
    if action == "inspect":
        return bool(task and env.agent == env.zones.get(task.target_zone or ""))
    if action == "charge":
        return bool(
            env.agent
            in {
                env.zones.get("base"),
                env.zones.get("charging_dock"),
                env.zones.get(task.target_zone or "") if task else None,
            }
        )
    return True


def _battery_recovery_action(env: GridWorldEnv) -> str | None:
    charger_positions = {
        position
        for position in (env.zones.get("charging_dock"), env.zones.get("base"))
        if position is not None
    }
    routes = [
        (shortest_path_actions(env, env.agent, charger), charger) for charger in charger_positions
    ]
    routes = [(route, charger) for route, charger in routes if route or charger == env.agent]
    if not routes:
        return None
    route, charger = min(routes, key=lambda item: (len(item[0]), item[1]))
    if env.battery > len(route) + 2:
        return None
    if env.agent == charger:
        return "charge"
    return route[0]


def _invalid_action_reason(env: GridWorldEnv, action: str) -> str:
    safe, reason = env.is_action_safe(action)
    return "invalid_task_context" if safe else reason


def _distance(start: Position, goal: Position) -> int:
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])


def _behavior_cloning_report(payload: dict[str, object]) -> str:
    training = payload["training"]
    policies = payload["policies"]
    assert isinstance(training, dict)
    assert isinstance(policies, dict)
    lines = [
        "# Behavior-Cloning Holdout Evaluation",
        "",
        "Fixed-seed procedural construction-site simulation. Train and holdout scenario IDs are disjoint. This is not a learned foundation VLA or robot deployment.",
        "",
        "## Dataset And Action Metrics",
        "",
        f"- Training scenarios: {training['train_scenario_count']}",
        f"- Holdout scenarios: {training['holdout_scenario_count']}",
        f"- Expert training steps: {training['training_step_count']}",
        f"- Holdout expert steps: {training['holdout_expert_step_count']}",
        f"- Holdout expert-action accuracy: {training['holdout_action_accuracy']}",
        f"- Holdout expert-action macro-F1: {training['holdout_action_macro_f1']}",
        "",
        "## Closed-Loop Holdout Results",
        "",
        "| Policy | Success rate | Avg steps | Avg reward | Unsafe action rate | Task error rate | Blocked actions | Interventions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, metrics in policies.items():
        assert isinstance(metrics, dict)
        lines.append(
            "| {name} | {success} | {steps} | {reward} | {unsafe} | {task_error} | {blocked} | {interventions} |".format(
                name=name,
                success=metrics["success_rate"],
                steps=metrics["average_steps"],
                reward=metrics["average_reward"],
                unsafe=metrics["unsafe_action_rate"],
                task_error=metrics["task_error_rate"],
                blocked=metrics["blocked_action_count"],
                interventions=metrics["intervention_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Action accuracy is measured on expert states; closed-loop success is the stronger test because policy errors change later states.",
            "- The raw behavior-cloning policy exposes model errors without repair.",
            "- The shielded variant rejects unsafe or task-invalid actions but does not receive an expert route toward the task goal; charger-only recovery is separate.",
            "- The deterministic A* policy is an oracle-style planning reference, not a learned baseline.",
            "- Results apply only to this small 2D procedural simulator.",
        ]
    )
    return "\n".join(lines) + "\n"


def _behavior_cloning_model_card(payload: dict[str, object]) -> str:
    training = payload["training"]
    assert isinstance(training, dict)
    return (
        "# Behavior-Cloning Policy Model Card\n\n"
        "Random-forest action classifier trained on fixed-seed expert A* demonstrations from procedural 7x7 construction-site grids.\n\n"
        "## Inputs\n\n"
        f"- {training['feature_count']} numeric state features covering task phase, carrying state, battery, agent/subgoal geometry, local movement safety, and distance change.\n"
        "- No image, depth, point-cloud, language embedding, or robot telemetry input.\n\n"
        "## Output\n\n"
        f"- Action classes: {', '.join(training['classes'])}.\n"
        "- The safety-filtered policy ranks model probabilities, rejects unsafe or task-invalid actions, and invokes a charger-only reserve controller before battery depletion.\n\n"
        "## Training Boundary\n\n"
        "- Expert labels come from the simulator's A* planner.\n"
        "- Train and holdout scenario seeds and IDs are disjoint.\n"
        "- The joblib binary is generated locally and ignored by Git; deterministic metrics and reports are versioned.\n\n"
        "## Not Demonstrated\n\n"
        "This model is not a foundation VLA, does not consume pixels or free-form language embeddings, and has no physics, ROS, sim-to-real, hardware, or physical-safety validation.\n"
    )


def _behavior_cloning_failure_analysis(payload: dict[str, object]) -> str:
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    failures = [
        row
        for row in episodes
        if isinstance(row, dict) and not row["success"] and row["policy_name"] != "safety_shielded"
    ]
    lines = [
        "# Behavior-Cloning Failure Analysis",
        "",
        "Failed learned-policy episodes from the disjoint procedural holdout set.",
        "",
        f"- Learned-policy episodes: {sum(1 for row in episodes if isinstance(row, dict) and str(row['policy_name']).startswith('behavior_cloning'))}",
        f"- Failed learned-policy episodes: {len(failures)}",
        "",
        "| Scenario | Task | Policy | Steps | Reward | Unsafe actions | Task errors | Blocked actions | Interventions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in failures:
        lines.append(
            "| {scenario} | {task} | {policy} | {steps} | {reward} | {unsafe} | {task_error} | {blocked} | {interventions} |".format(
                scenario=row["scenario_id"],
                task=row["task_type"],
                policy=row["policy_name"],
                steps=row["steps"],
                reward=row["total_reward"],
                unsafe=row["unsafe_action_count"],
                task_error=row["task_error_count"],
                blocked=row["blocked_action_count"],
                interventions=row["intervention_count"],
            )
        )
    lines.extend(
        [
            "",
            "The learned policy has no expert fallback toward the task goal. Failures therefore remain visible as evidence of compounding imitation error, limited state features, and a small training distribution.",
        ]
    )
    return "\n".join(lines) + "\n"
