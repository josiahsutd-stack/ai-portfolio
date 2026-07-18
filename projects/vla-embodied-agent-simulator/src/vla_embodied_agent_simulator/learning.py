from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import joblib
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

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
from .semantic_raster_rendering import render_semantic_raster_svg
from .synthetic_rgb import (
    RGB_IMAGE_SIZE,
    RGB_WINDOW_SIZE,
    render_synthetic_rgb_observation,
)

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
TRAIN_SCENARIOS_PER_TASK = 64
HOLDOUT_SCENARIOS_PER_TASK = 32
SEMANTIC_RASTER_SIZE = 7
SEMANTIC_RASTER_CHANNELS = (
    "agent",
    "current_subgoal",
    "obstacle",
    "restricted_zone",
    "worker_zone",
    "slow_zone",
    "object",
    "named_zone",
)
SEMANTIC_RASTER_GLOBAL_FEATURES = (
    "task_deliver",
    "task_inspect",
    "task_charge",
    "carrying",
    "battery_ratio",
    "step_ratio",
)
SEMANTIC_RASTER_FEATURE_COUNT = SEMANTIC_RASTER_SIZE * SEMANTIC_RASTER_SIZE * len(
    SEMANTIC_RASTER_CHANNELS
) + len(SEMANTIC_RASTER_GLOBAL_FEATURES)
EGOCENTRIC_WINDOW_SIZE = 5
EGOCENTRIC_RADIUS = EGOCENTRIC_WINDOW_SIZE // 2
EGOCENTRIC_CHANNELS = (
    "obstacle",
    "restricted_zone",
    "worker_zone",
    "slow_zone",
    "object",
    "named_zone",
    "current_subgoal_in_view",
    "out_of_bounds",
)
EGOCENTRIC_GLOBAL_FEATURES = (
    "task_deliver",
    "task_inspect",
    "task_charge",
    "carrying",
    "battery_ratio",
    "step_ratio",
    "relative_subgoal_x",
    "relative_subgoal_y",
    "subgoal_distance_x",
    "subgoal_distance_y",
)
EGOCENTRIC_FEATURE_COUNT = EGOCENTRIC_WINDOW_SIZE * EGOCENTRIC_WINDOW_SIZE * len(
    EGOCENTRIC_CHANNELS
) + len(EGOCENTRIC_GLOBAL_FEATURES)
SYNTHETIC_RGB_GLOBAL_FEATURES = EGOCENTRIC_GLOBAL_FEATURES
SYNTHETIC_RGB_FEATURE_COUNT = RGB_IMAGE_SIZE * RGB_IMAGE_SIZE * 3 + len(
    SYNTHETIC_RGB_GLOBAL_FEATURES
)
SYNTHETIC_RGB_TRAIN_PALETTES = ("day", "overcast")
SYNTHETIC_RGB_STANDARD_PALETTE = "day"
SYNTHETIC_RGB_SHIFTED_PALETTE = "worklight"

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


@dataclass(frozen=True)
class SemanticRasterTrainingResult:
    train_scenario_count: int
    holdout_scenario_count: int
    training_step_count: int
    holdout_expert_step_count: int
    holdout_action_accuracy: float
    holdout_action_macro_f1: float
    classes: list[str]
    feature_count: int
    raster_size: int
    channel_names: list[str]
    global_feature_names: list[str]
    hidden_layer_sizes: list[int]
    model_file: str
    random_seed: int


@dataclass(frozen=True)
class EgocentricTrainingResult:
    train_scenario_count: int
    holdout_scenario_count: int
    training_step_count: int
    holdout_expert_step_count: int
    holdout_action_accuracy: float
    holdout_action_macro_f1: float
    classes: list[str]
    feature_count: int
    window_size: int
    radius: int
    channel_names: list[str]
    global_feature_names: list[str]
    hidden_layer_sizes: list[int]
    model_file: str
    random_seed: int


@dataclass(frozen=True)
class SyntheticRGBTrainingResult:
    train_scenario_count: int
    holdout_scenario_count: int
    training_step_count: int
    augmented_training_example_count: int
    holdout_expert_step_count: int
    standard_holdout_action_accuracy: float
    standard_holdout_action_macro_f1: float
    shifted_holdout_action_accuracy: float
    shifted_holdout_action_macro_f1: float
    pixel_ablated_holdout_action_accuracy: float
    pixel_ablated_holdout_action_macro_f1: float
    standard_minus_pixel_ablated_accuracy: float
    classes: list[str]
    feature_count: int
    image_size: int
    window_size: int
    channel_count: int
    global_feature_names: list[str]
    train_palettes: list[str]
    standard_palette: str
    shifted_palette: str
    hidden_layer_sizes: list[int]
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


def encode_semantic_raster_state(env: GridWorldEnv) -> list[float]:
    if env.width > SEMANTIC_RASTER_SIZE or env.height > SEMANTIC_RASTER_SIZE:
        raise ValueError(
            f"semantic raster supports grids up to {SEMANTIC_RASTER_SIZE}x{SEMANTIC_RASTER_SIZE}"
        )
    task = env.task or parse_instruction("wait", env)
    subgoal = _current_subgoal(env)
    channel_points = (
        {env.agent},
        {subgoal},
        set(env.obstacles),
        set(env.restricted_zones),
        set(env.worker_zones),
        set(env.slow_zones),
        set(env.objects.values()),
        set(env.zones.values()),
    )
    features = [
        float((x, y) in points)
        for points in channel_points
        for y in range(SEMANTIC_RASTER_SIZE)
        for x in range(SEMANTIC_RASTER_SIZE)
    ]
    features.extend(
        [
            float(task.task_type == "deliver"),
            float(task.task_type == "inspect"),
            float(task.task_type == "charge"),
            float(env.carrying is not None),
            min(1.0, max(0.0, env.battery / 70.0)),
            min(1.0, env.step_count / max(1, env.max_steps)),
        ]
    )
    if len(features) != SEMANTIC_RASTER_FEATURE_COUNT:
        raise RuntimeError("semantic raster feature schema changed unexpectedly")
    return features


def encode_egocentric_local_state(env: GridWorldEnv) -> list[float]:
    subgoal = _current_subgoal(env)
    channel_points = (
        set(env.obstacles),
        set(env.restricted_zones),
        set(env.worker_zones),
        set(env.slow_zones),
        set(env.objects.values()),
        set(env.zones.values()),
        {subgoal},
    )
    offsets = range(-EGOCENTRIC_RADIUS, EGOCENTRIC_RADIUS + 1)
    features = [
        float((env.agent[0] + dx, env.agent[1] + dy) in points)
        for points in channel_points
        for dy in offsets
        for dx in offsets
    ]
    features.extend(
        float(not (0 <= env.agent[0] + dx < env.width and 0 <= env.agent[1] + dy < env.height))
        for dy in offsets
        for dx in offsets
    )
    features.extend(_task_navigation_features(env, subgoal))
    if len(features) != EGOCENTRIC_FEATURE_COUNT:
        raise RuntimeError("egocentric feature schema changed unexpectedly")
    return features


def encode_synthetic_rgb_observation(
    env: GridWorldEnv,
    *,
    palette_name: str = SYNTHETIC_RGB_STANDARD_PALETTE,
) -> list[float]:
    subgoal = _current_subgoal(env)
    image = render_synthetic_rgb_observation(env, subgoal, palette_name=palette_name)
    features = (image.astype(float) / 255.0).reshape(-1).tolist()
    features.extend(_task_navigation_features(env, subgoal))
    if len(features) != SYNTHETIC_RGB_FEATURE_COUNT:
        raise RuntimeError("synthetic RGB feature schema changed unexpectedly")
    return features


def _task_navigation_features(env: GridWorldEnv, subgoal: Position) -> list[float]:
    task = env.task or parse_instruction("wait", env)
    width_scale = max(1, env.width - 1)
    height_scale = max(1, env.height - 1)
    dx = subgoal[0] - env.agent[0]
    dy = subgoal[1] - env.agent[1]
    return [
        float(task.task_type == "deliver"),
        float(task.task_type == "inspect"),
        float(task.task_type == "charge"),
        float(env.carrying is not None),
        min(1.0, max(0.0, env.battery / 70.0)),
        min(1.0, env.step_count / max(1, env.max_steps)),
        dx / width_scale,
        dy / height_scale,
        abs(dx) / width_scale,
        abs(dy) / height_scale,
    ]


def train_behavior_cloning_policy(
    *,
    model_output_dir: str | Path | None = None,
    train_scenarios: list[SiteScenario] | None = None,
    holdout_scenarios: list[SiteScenario] | None = None,
) -> tuple[RandomForestClassifier, BehaviorCloningTrainingResult]:
    train_set = train_scenarios or generate_behavior_cloning_scenarios(
        "train", count_per_task=TRAIN_SCENARIOS_PER_TASK
    )
    holdout_set = holdout_scenarios or generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )
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


def train_semantic_raster_policy(
    *,
    model_output_dir: str | Path | None = None,
    train_scenarios: list[SiteScenario] | None = None,
    holdout_scenarios: list[SiteScenario] | None = None,
) -> tuple[Pipeline, SemanticRasterTrainingResult]:
    train_set = train_scenarios or generate_behavior_cloning_scenarios(
        "train", count_per_task=TRAIN_SCENARIOS_PER_TASK
    )
    holdout_set = holdout_scenarios or generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )
    train_features, train_actions = _expert_examples(
        train_set, encoder=encode_semantic_raster_state
    )
    holdout_features, holdout_actions = _expert_examples(
        holdout_set, encoder=encode_semantic_raster_state
    )
    model = make_pipeline(
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(64,),
            activation="relu",
            solver="lbfgs",
            alpha=0.001,
            max_iter=1500,
            random_state=73,
        ),
    )
    model.fit(train_features, train_actions)
    holdout_predictions = model.predict(holdout_features)
    model_file = "semantic_raster_mlp_policy.joblib"
    if model_output_dir is not None:
        model_path = Path(model_output_dir) / model_file
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    result = SemanticRasterTrainingResult(
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
        feature_count=SEMANTIC_RASTER_FEATURE_COUNT,
        raster_size=SEMANTIC_RASTER_SIZE,
        channel_names=list(SEMANTIC_RASTER_CHANNELS),
        global_feature_names=list(SEMANTIC_RASTER_GLOBAL_FEATURES),
        hidden_layer_sizes=[64],
        model_file=model_file,
        random_seed=73,
    )
    return model, result


def train_egocentric_policy(
    *,
    model_output_dir: str | Path | None = None,
    train_scenarios: list[SiteScenario] | None = None,
    holdout_scenarios: list[SiteScenario] | None = None,
) -> tuple[Pipeline, EgocentricTrainingResult]:
    train_set = train_scenarios or generate_behavior_cloning_scenarios(
        "train", count_per_task=TRAIN_SCENARIOS_PER_TASK
    )
    holdout_set = holdout_scenarios or generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )
    train_features, train_actions = _expert_examples(
        train_set, encoder=encode_egocentric_local_state
    )
    holdout_features, holdout_actions = _expert_examples(
        holdout_set, encoder=encode_egocentric_local_state
    )
    model = make_pipeline(
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(64,),
            activation="relu",
            solver="lbfgs",
            alpha=0.001,
            max_iter=1500,
            random_state=91,
        ),
    )
    model.fit(train_features, train_actions)
    holdout_predictions = model.predict(holdout_features)
    model_file = "egocentric_mlp_policy.joblib"
    if model_output_dir is not None:
        model_path = Path(model_output_dir) / model_file
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    result = EgocentricTrainingResult(
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
        feature_count=EGOCENTRIC_FEATURE_COUNT,
        window_size=EGOCENTRIC_WINDOW_SIZE,
        radius=EGOCENTRIC_RADIUS,
        channel_names=list(EGOCENTRIC_CHANNELS),
        global_feature_names=list(EGOCENTRIC_GLOBAL_FEATURES),
        hidden_layer_sizes=[64],
        model_file=model_file,
        random_seed=91,
    )
    return model, result


def train_synthetic_rgb_policy(
    *,
    model_output_dir: str | Path | None = None,
    train_scenarios: list[SiteScenario] | None = None,
    holdout_scenarios: list[SiteScenario] | None = None,
) -> tuple[Pipeline, SyntheticRGBTrainingResult]:
    train_set = train_scenarios or generate_behavior_cloning_scenarios(
        "train", count_per_task=TRAIN_SCENARIOS_PER_TASK
    )
    holdout_set = holdout_scenarios or generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )
    train_features, train_actions = _expert_examples_with_rgb_palettes(
        train_set,
        palettes=SYNTHETIC_RGB_TRAIN_PALETTES,
    )
    standard_features, holdout_actions = _expert_examples(
        holdout_set,
        encoder=lambda env: encode_synthetic_rgb_observation(
            env,
            palette_name=SYNTHETIC_RGB_STANDARD_PALETTE,
        ),
    )
    shifted_features, shifted_actions = _expert_examples(
        holdout_set,
        encoder=lambda env: encode_synthetic_rgb_observation(
            env,
            palette_name=SYNTHETIC_RGB_SHIFTED_PALETTE,
        ),
    )
    if holdout_actions != shifted_actions:
        raise RuntimeError("RGB holdout action labels changed across appearance conditions")
    model = make_pipeline(
        StandardScaler(),
        MLPClassifier(
            hidden_layer_sizes=(64,),
            activation="relu",
            solver="lbfgs",
            alpha=0.001,
            max_iter=1500,
            random_state=113,
        ),
    )
    model.fit(train_features, train_actions)
    standard_predictions = model.predict(standard_features)
    shifted_predictions = model.predict(shifted_features)
    scaler = model.named_steps["standardscaler"]
    pixel_count = RGB_IMAGE_SIZE * RGB_IMAGE_SIZE * 3
    mean_pixels = scaler.mean_[:pixel_count].tolist()
    pixel_ablated_features = [mean_pixels + row[pixel_count:] for row in standard_features]
    pixel_ablated_predictions = model.predict(pixel_ablated_features)
    standard_accuracy = float(accuracy_score(holdout_actions, standard_predictions))
    pixel_ablated_accuracy = float(accuracy_score(holdout_actions, pixel_ablated_predictions))
    model_file = "synthetic_rgb_mlp_policy.joblib"
    if model_output_dir is not None:
        model_path = Path(model_output_dir) / model_file
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    result = SyntheticRGBTrainingResult(
        train_scenario_count=len(train_set),
        holdout_scenario_count=len(holdout_set),
        training_step_count=len(train_actions) // len(SYNTHETIC_RGB_TRAIN_PALETTES),
        augmented_training_example_count=len(train_actions),
        holdout_expert_step_count=len(holdout_actions),
        standard_holdout_action_accuracy=round(standard_accuracy, 3),
        standard_holdout_action_macro_f1=round(
            float(f1_score(holdout_actions, standard_predictions, average="macro")),
            3,
        ),
        shifted_holdout_action_accuracy=round(
            float(accuracy_score(holdout_actions, shifted_predictions)), 3
        ),
        shifted_holdout_action_macro_f1=round(
            float(f1_score(holdout_actions, shifted_predictions, average="macro")),
            3,
        ),
        pixel_ablated_holdout_action_accuracy=round(pixel_ablated_accuracy, 3),
        pixel_ablated_holdout_action_macro_f1=round(
            float(f1_score(holdout_actions, pixel_ablated_predictions, average="macro")),
            3,
        ),
        standard_minus_pixel_ablated_accuracy=round(
            standard_accuracy - pixel_ablated_accuracy,
            3,
        ),
        classes=sorted(str(value) for value in model.classes_),
        feature_count=SYNTHETIC_RGB_FEATURE_COUNT,
        image_size=RGB_IMAGE_SIZE,
        window_size=RGB_WINDOW_SIZE,
        channel_count=3,
        global_feature_names=list(SYNTHETIC_RGB_GLOBAL_FEATURES),
        train_palettes=list(SYNTHETIC_RGB_TRAIN_PALETTES),
        standard_palette=SYNTHETIC_RGB_STANDARD_PALETTE,
        shifted_palette=SYNTHETIC_RGB_SHIFTED_PALETTE,
        hidden_layer_sizes=[64],
        model_file=model_file,
        random_seed=113,
    )
    return model, result


def make_behavior_cloning_policy(
    model: RandomForestClassifier,
    *,
    safety_filter: bool,
) -> PolicyFn:
    return _make_classifier_policy(
        model,
        encoder=encode_policy_state,
        raw_policy_name="behavior_cloning_raw",
        shielded_policy_name="behavior_cloning_shielded",
        safety_filter=safety_filter,
    )


def make_semantic_raster_policy(
    model: Pipeline,
    *,
    safety_filter: bool,
) -> PolicyFn:
    return _make_classifier_policy(
        model,
        encoder=encode_semantic_raster_state,
        raw_policy_name="semantic_raster_mlp_raw",
        shielded_policy_name="semantic_raster_mlp_shielded",
        safety_filter=safety_filter,
    )


def make_egocentric_policy(
    model: Pipeline,
    *,
    safety_filter: bool,
) -> PolicyFn:
    return _make_classifier_policy(
        model,
        encoder=encode_egocentric_local_state,
        raw_policy_name="egocentric_mlp_raw",
        shielded_policy_name="egocentric_mlp_shielded",
        safety_filter=safety_filter,
    )


def make_synthetic_rgb_policy(
    model: Pipeline,
    *,
    safety_filter: bool,
    palette_name: str = SYNTHETIC_RGB_STANDARD_PALETTE,
) -> PolicyFn:
    shifted = palette_name == SYNTHETIC_RGB_SHIFTED_PALETTE
    prefix = "synthetic_rgb_mlp_shifted" if shifted else "synthetic_rgb_mlp"
    return _make_classifier_policy(
        model,
        encoder=lambda env: encode_synthetic_rgb_observation(
            env,
            palette_name=palette_name,
        ),
        raw_policy_name=f"{prefix}_raw",
        shielded_policy_name=f"{prefix}_shielded",
        safety_filter=safety_filter,
    )


def _make_classifier_policy(
    model: Any,
    *,
    encoder: Callable[[GridWorldEnv], list[float]],
    raw_policy_name: str,
    shielded_policy_name: str,
    safety_filter: bool,
) -> PolicyFn:
    policy_name = shielded_policy_name if safety_filter else raw_policy_name

    def policy(env: GridWorldEnv, instruction: str) -> PolicyPlan:
        probe = env.clone()
        task = parse_instruction(instruction, probe)
        probe.task = task
        actions: list[str] = []
        interventions: list[dict[str, object]] = []
        for _ in range(env.max_steps):
            probabilities = model.predict_proba([encoder(probe)])[0]
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

    train_scenarios = generate_behavior_cloning_scenarios(
        "train", count_per_task=TRAIN_SCENARIOS_PER_TASK
    )
    holdout_scenarios = generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )
    model, training = train_behavior_cloning_policy(
        model_output_dir=model_output_dir,
        train_scenarios=train_scenarios,
        holdout_scenarios=holdout_scenarios,
    )
    raster_model, raster_training = train_semantic_raster_policy(
        model_output_dir=model_output_dir,
        train_scenarios=train_scenarios,
        holdout_scenarios=holdout_scenarios,
    )
    egocentric_model, egocentric_training = train_egocentric_policy(
        model_output_dir=model_output_dir,
        train_scenarios=train_scenarios,
        holdout_scenarios=holdout_scenarios,
    )
    rgb_model, rgb_training = train_synthetic_rgb_policy(
        model_output_dir=model_output_dir,
        train_scenarios=train_scenarios,
        holdout_scenarios=holdout_scenarios,
    )
    policies: list[PolicyFn] = [
        make_behavior_cloning_policy(model, safety_filter=False),
        make_behavior_cloning_policy(model, safety_filter=True),
        make_semantic_raster_policy(raster_model, safety_filter=False),
        make_semantic_raster_policy(raster_model, safety_filter=True),
        make_egocentric_policy(egocentric_model, safety_filter=False),
        make_egocentric_policy(egocentric_model, safety_filter=True),
        make_synthetic_rgb_policy(rgb_model, safety_filter=False),
        make_synthetic_rgb_policy(rgb_model, safety_filter=True),
        make_synthetic_rgb_policy(
            rgb_model,
            safety_filter=False,
            palette_name=SYNTHETIC_RGB_SHIFTED_PALETTE,
        ),
        make_synthetic_rgb_policy(
            rgb_model,
            safety_filter=True,
            palette_name=SYNTHETIC_RGB_SHIFTED_PALETTE,
        ),
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
    structured_shielded = metrics["behavior_cloning_shielded"]
    raster_shielded = metrics["semantic_raster_mlp_shielded"]
    egocentric_shielded = metrics["egocentric_mlp_shielded"]
    rgb_shielded = metrics["synthetic_rgb_mlp_shielded"]
    rgb_shifted_shielded = metrics["synthetic_rgb_mlp_shifted_shielded"]
    return {
        "evaluation_type": "fixed-seed procedural construction-site holdout",
        "training": asdict(training),
        "semantic_raster_training": asdict(raster_training),
        "egocentric_training": asdict(egocentric_training),
        "synthetic_rgb_training": asdict(rgb_training),
        "representation_comparison": {
            "structured_feature_count": training.feature_count,
            "semantic_raster_feature_count": raster_training.feature_count,
            "egocentric_feature_count": egocentric_training.feature_count,
            "synthetic_rgb_feature_count": rgb_training.feature_count,
            "expert_action_accuracy_delta_structured_minus_raster": round(
                training.holdout_action_accuracy - raster_training.holdout_action_accuracy,
                3,
            ),
            "expert_action_accuracy_delta_egocentric_minus_raster": round(
                egocentric_training.holdout_action_accuracy
                - raster_training.holdout_action_accuracy,
                3,
            ),
            "expert_action_accuracy_delta_structured_minus_egocentric": round(
                training.holdout_action_accuracy - egocentric_training.holdout_action_accuracy,
                3,
            ),
            "shielded_success_delta_structured_minus_raster": round(
                float(structured_shielded["success_rate"]) - float(raster_shielded["success_rate"]),
                3,
            ),
            "shielded_success_delta_egocentric_minus_raster": round(
                float(egocentric_shielded["success_rate"]) - float(raster_shielded["success_rate"]),
                3,
            ),
            "shielded_success_delta_egocentric_minus_structured": round(
                float(egocentric_shielded["success_rate"])
                - float(structured_shielded["success_rate"]),
                3,
            ),
            "expert_action_accuracy_delta_rgb_standard_minus_shifted": round(
                rgb_training.standard_holdout_action_accuracy
                - rgb_training.shifted_holdout_action_accuracy,
                3,
            ),
            "shielded_success_delta_rgb_standard_minus_shifted": round(
                float(rgb_shielded["success_rate"]) - float(rgb_shifted_shielded["success_rate"]),
                3,
            ),
            "interpretation": (
                "The agent-centered local-state MLP recovers most expert-action accuracy lost "
                "by the world-frame flattened raster and has the highest filtered learned-policy "
                "success. The synthetic RGB policy consumes rendered pixels and reports an unseen "
                "appearance shift separately. Its renderer still originates from privileged "
                "simulator state, so this is not real-camera or physical-safety evidence."
            ),
        },
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
    site_asset_path: str | Path | None = None,
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
    (target / "semantic_raster_model_card.md").write_text(
        _semantic_raster_model_card(payload),
        encoding="utf-8",
    )
    (target / "egocentric_mlp_model_card.md").write_text(
        _egocentric_model_card(payload),
        encoding="utf-8",
    )
    (target / "synthetic_rgb_mlp_model_card.md").write_text(
        _synthetic_rgb_model_card(payload),
        encoding="utf-8",
    )
    (target / "behavior_cloning_failure_analysis.md").write_text(
        _behavior_cloning_failure_analysis(payload),
        encoding="utf-8",
    )
    example_scenario = generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )[0]
    example_env = GridWorldEnv.from_scenario(example_scenario)
    example_subgoal = _current_subgoal(example_env)
    for palette_name in (
        SYNTHETIC_RGB_STANDARD_PALETTE,
        SYNTHETIC_RGB_SHIFTED_PALETTE,
    ):
        rgb_image = render_synthetic_rgb_observation(
            example_env,
            example_subgoal,
            palette_name=palette_name,
        )
        Image.fromarray(rgb_image).resize(
            (240, 240),
            Image.Resampling.NEAREST,
        ).save(target / f"synthetic_rgb_observation_{palette_name}.png")
    raster_svg = render_semantic_raster_svg(
        example_env,
        example_subgoal,
        payload,
    )
    (target / "semantic_raster_comparison.svg").write_text(raster_svg, encoding="utf-8")
    if site_asset_path is not None:
        asset = Path(site_asset_path)
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_text(raster_svg, encoding="utf-8")
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


def _expert_examples(
    scenarios: list[SiteScenario],
    *,
    encoder: Callable[[GridWorldEnv], list[float]] = encode_policy_state,
) -> tuple[list[list[float]], list[str]]:
    features: list[list[float]] = []
    actions: list[str] = []
    for scenario in scenarios:
        env = GridWorldEnv.from_scenario(scenario)
        plan = plan_from_instruction(scenario.instruction, env)
        for action in plan:
            features.append(encoder(env))
            actions.append(action)
            _state, _reward, done, _info = env.step(action)
            if done:
                break
        if not env.trace or not env.trace[-1].info.get("success"):
            raise RuntimeError(f"expert failed generated scenario {scenario.scenario_id}")
    return features, actions


def _expert_examples_with_rgb_palettes(
    scenarios: list[SiteScenario],
    *,
    palettes: tuple[str, ...],
) -> tuple[list[list[float]], list[str]]:
    features: list[list[float]] = []
    actions: list[str] = []
    for scenario in scenarios:
        env = GridWorldEnv.from_scenario(scenario)
        plan = plan_from_instruction(scenario.instruction, env)
        for action in plan:
            for palette_name in palettes:
                features.append(encode_synthetic_rgb_observation(env, palette_name=palette_name))
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
            task
            and task.task_type == "charge"
            and env.agent == env.zones.get(task.target_zone or "")
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
    raster_training = payload["semantic_raster_training"]
    egocentric_training = payload["egocentric_training"]
    rgb_training = payload["synthetic_rgb_training"]
    comparison = payload["representation_comparison"]
    policies = payload["policies"]
    assert isinstance(training, dict)
    assert isinstance(raster_training, dict)
    assert isinstance(egocentric_training, dict)
    assert isinstance(rgb_training, dict)
    assert isinstance(comparison, dict)
    assert isinstance(policies, dict)
    policy_labels = {
        "behavior_cloning_raw": "Engineered-state RF, raw",
        "behavior_cloning_shielded": "Engineered-state RF, filtered",
        "semantic_raster_mlp_raw": "Semantic-raster MLP, raw",
        "semantic_raster_mlp_shielded": "Semantic-raster MLP, filtered",
        "egocentric_mlp_raw": "Egocentric local-state MLP, raw",
        "egocentric_mlp_shielded": "Egocentric local-state MLP, filtered",
        "synthetic_rgb_mlp_raw": "Synthetic RGB MLP, raw",
        "synthetic_rgb_mlp_shielded": "Synthetic RGB MLP, filtered",
        "synthetic_rgb_mlp_shifted_raw": "Synthetic RGB MLP, shifted appearance, raw",
        "synthetic_rgb_mlp_shifted_shielded": "Synthetic RGB MLP, shifted appearance, filtered",
        "safety_shielded": "Deterministic A* reference",
    }
    lines = [
        "# Imitation-Policy Holdout Evaluation",
        "",
        "Fixed-seed procedural construction-site simulation. Four learned policy families use the same expert demonstrations and disjoint holdout scenarios. The RGB model receives two training appearances; its unseen work-light appearance is reported separately. This is not a learned foundation VLA or robot deployment.",
        "",
        "## Shared Evaluation Protocol",
        "",
        f"- Training scenarios: {training['train_scenario_count']}",
        f"- Holdout scenarios: {training['holdout_scenario_count']}",
        f"- Expert training steps: {training['training_step_count']}",
        f"- Holdout expert steps: {training['holdout_expert_step_count']}",
        "- Holdout action metrics are measured on expert-visited states.",
        "- Closed-loop metrics measure compounding errors after each policy takes control.",
        "",
        "## Representation Comparison",
        "",
        "| Policy input and model | Features | Holdout action accuracy | Holdout macro-F1 |",
        "| --- | ---: | ---: | ---: |",
        f"| Engineered state + random forest | {training['feature_count']} | {training['holdout_action_accuracy']} | {training['holdout_action_macro_f1']} |",
        f"| Flattened semantic raster + 64-unit MLP | {raster_training['feature_count']} | {raster_training['holdout_action_accuracy']} | {raster_training['holdout_action_macro_f1']} |",
        f"| Egocentric 5x5 local state + 64-unit MLP | {egocentric_training['feature_count']} | {egocentric_training['holdout_action_accuracy']} | {egocentric_training['holdout_action_macro_f1']} |",
        f"| Synthetic 10x10 RGB crop + 10 telemetry values + 64-unit MLP | {rgb_training['feature_count']} | {rgb_training['standard_holdout_action_accuracy']} | {rgb_training['standard_holdout_action_macro_f1']} |",
        f"| Same RGB model, unseen {rgb_training['shifted_palette']} palette | {rgb_training['feature_count']} | {rgb_training['shifted_holdout_action_accuracy']} | {rgb_training['shifted_holdout_action_macro_f1']} |",
        f"| Same RGB model, pixels replaced by training means | 10 active telemetry values | {rgb_training['pixel_ablated_holdout_action_accuracy']} | {rgb_training['pixel_ablated_holdout_action_macro_f1']} |",
        "",
        f"Agent-centered local encoding recovers {comparison['expert_action_accuracy_delta_egocentric_minus_raster']} action accuracy over the world-frame raster and trails the engineered-state model by {comparison['expert_action_accuracy_delta_structured_minus_egocentric']}. The RGB policy consumes rendered pixels, but those pixels are generated deterministically from privileged simulator state rather than captured by a camera.",
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
                name=policy_labels.get(name, name),
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
            "- Each raw learned policy exposes model errors without repair.",
            "- Each shielded variant rejects unsafe or task-invalid actions but does not receive an expert route toward the task goal; charger-only recovery is separate.",
            "- The flattened-raster MLP underperforms the engineered-state random forest. This negative result is retained because it shows that adding a neural network does not automatically improve a small-data spatial-control problem.",
            "- Centering a local semantic window on the agent recovers most of the raster MLP's action accuracy and produces the strongest filtered learned-policy success, despite hiding hazards outside the 5x5 window.",
            "- The egocentric policy still has weaker raw completion than the engineered-state policy and depends on many filter interventions. Filtered success is not model-only safety or control evidence.",
            "- The RGB policy reports both its standard appearance and an unseen palette shift. Any degradation remains visible rather than being averaged into the standard result.",
            f"- Replacing every holdout pixel with its training-set mean reduces action accuracy by {rgb_training['standard_minus_pixel_ablated_accuracy']}. This ablation shows that the image contributes predictive information beyond the ten telemetry values.",
            "- The RGB renderer removes direct semantic channels at the classifier boundary, but it still maps privileged grid state into clean synthetic pixels. It does not model detection, segmentation, depth, calibration, occlusion, or sensor noise.",
            "- No MLP has convolution, temporal memory, a physical camera, or learned language conditioning; none establishes multimodal reasoning or foundation-VLA capability.",
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


def _semantic_raster_model_card(payload: dict[str, object]) -> str:
    training = payload["semantic_raster_training"]
    policies = payload["policies"]
    assert isinstance(training, dict)
    assert isinstance(policies, dict)
    shielded = policies["semantic_raster_mlp_shielded"]
    assert isinstance(shielded, dict)
    return (
        "# Semantic-Raster MLP Model Card\n\n"
        "One-hidden-layer neural action classifier trained on the same fixed-seed A* demonstrations and evaluated on the same disjoint holdout as the engineered-state random forest. It is preserved as a measured negative baseline.\n\n"
        "## Inputs\n\n"
        f"- {training['raster_size']}x{training['raster_size']} fully observable semantic grids with channels for {', '.join(training['channel_names'])}.\n"
        f"- Global features: {', '.join(training['global_feature_names'])}.\n"
        f"- {training['feature_count']} flattened numeric values in total.\n"
        "- The raster is rendered from privileged simulator state, not captured by a camera or inferred by a perception model.\n\n"
        "## Model And Output\n\n"
        f"- StandardScaler followed by an MLPClassifier with hidden layers {training['hidden_layer_sizes']}.\n"
        f"- Action classes: {', '.join(training['classes'])}.\n"
        "- The optional safety filter ranks model probabilities and rejects unsafe or task-invalid actions.\n\n"
        "## Measured Result\n\n"
        f"- Holdout expert-action accuracy: {training['holdout_action_accuracy']}.\n"
        f"- Holdout expert-action macro-F1: {training['holdout_action_macro_f1']}.\n"
        f"- Shielded closed-loop success rate: {shielded['success_rate']}.\n"
        "- This is weaker than the engineered-state random forest on the shared holdout. The likely contributors are limited demonstrations, flattening of the grid, and the absence of convolutional spatial bias.\n\n"
        "## Not Demonstrated\n\n"
        "This model does not establish camera perception, visual grounding, language embeddings, a convolutional policy, a multimodal transformer, reinforcement learning, a foundation VLA, physics, ROS, sim-to-real transfer, hardware control, or physical-safety validation.\n"
    )


def _egocentric_model_card(payload: dict[str, object]) -> str:
    training = payload["egocentric_training"]
    policies = payload["policies"]
    assert isinstance(training, dict)
    assert isinstance(policies, dict)
    raw = policies["egocentric_mlp_raw"]
    shielded = policies["egocentric_mlp_shielded"]
    assert isinstance(raw, dict)
    assert isinstance(shielded, dict)
    return (
        "# Egocentric Local-State MLP Model Card\n\n"
        "One-hidden-layer neural action classifier trained on the same fixed-seed A* demonstrations and evaluated on the same disjoint holdout as the other learned policies.\n\n"
        "## Observation Contract\n\n"
        f"- Agent-centered {training['window_size']}x{training['window_size']} local window with channels for {', '.join(training['channel_names'])}.\n"
        f"- Global task and navigation values: {', '.join(training['global_feature_names'])}.\n"
        f"- {training['feature_count']} numeric inputs in total.\n"
        "- Obstacles and zones outside the local window are hidden from the classifier, while relative subgoal geometry remains available.\n"
        "- Inputs come directly from simulator state, not cameras or a learned perception model.\n\n"
        "## Model And Output\n\n"
        f"- StandardScaler followed by an MLPClassifier with hidden layers {training['hidden_layer_sizes']}.\n"
        f"- Action classes: {', '.join(training['classes'])}.\n"
        "- The optional safety filter applies full simulator rules after classification; it can therefore reject hazards that the local observation did not expose.\n\n"
        "## Measured Result\n\n"
        f"- Holdout expert-action accuracy: {training['holdout_action_accuracy']}.\n"
        f"- Holdout expert-action macro-F1: {training['holdout_action_macro_f1']}.\n"
        f"- Raw closed-loop success rate: {raw['success_rate']}.\n"
        f"- Filtered closed-loop success rate: {shielded['success_rate']}.\n"
        f"- Filter interventions: {shielded['intervention_count']}.\n"
        "- Agent-centered encoding improves substantially over the world-frame flattened raster. The filtered result also depends heavily on hand-authored simulator constraints and is not attributable to the classifier alone.\n\n"
        "## Not Demonstrated\n\n"
        "This model has no camera input, learned perception, convolution, recurrence, memory, uncertainty model, language embedding, reinforcement learning, physics, ROS, sim-to-real transfer, hardware control, or physical-safety validation.\n"
    )


def _synthetic_rgb_model_card(payload: dict[str, object]) -> str:
    training = payload["synthetic_rgb_training"]
    policies = payload["policies"]
    assert isinstance(training, dict)
    assert isinstance(policies, dict)
    standard_raw = policies["synthetic_rgb_mlp_raw"]
    standard_filtered = policies["synthetic_rgb_mlp_shielded"]
    shifted_raw = policies["synthetic_rgb_mlp_shifted_raw"]
    shifted_filtered = policies["synthetic_rgb_mlp_shifted_shielded"]
    assert isinstance(standard_raw, dict)
    assert isinstance(standard_filtered, dict)
    assert isinstance(shifted_raw, dict)
    assert isinstance(shifted_filtered, dict)
    return (
        "# Synthetic RGB Observation MLP Model Card\n\n"
        "One-hidden-layer action classifier fitted to rendered egocentric RGB crops and the same bounded task/navigation telemetry used by the semantic local-state baseline.\n\n"
        "## Observation Contract\n\n"
        f"- {training['image_size']}x{training['image_size']} RGB image representing an agent-centered {training['window_size']}x{training['window_size']} crop.\n"
        f"- Additional values: {', '.join(training['global_feature_names'])}.\n"
        f"- {training['feature_count']} flattened inputs in total.\n"
        f"- Training appearances: {', '.join(training['train_palettes'])}; standard holdout: {training['standard_palette']}; unseen shifted holdout: {training['shifted_palette']}.\n"
        "- The classifier receives pixels rather than semantic channels, but the renderer creates clean pixels directly from privileged simulator state.\n\n"
        "## Model And Output\n\n"
        f"- StandardScaler followed by an MLPClassifier with hidden layers {training['hidden_layer_sizes']}.\n"
        f"- Action classes: {', '.join(training['classes'])}.\n"
        f"- {training['training_step_count']} expert states become {training['augmented_training_example_count']} appearance-variant training examples.\n"
        "- The optional filter applies full simulator rules after classification and can see hazards outside the RGB crop.\n\n"
        "## Measured Result\n\n"
        f"- Standard holdout action accuracy / macro-F1: {training['standard_holdout_action_accuracy']} / {training['standard_holdout_action_macro_f1']}.\n"
        f"- Shifted holdout action accuracy / macro-F1: {training['shifted_holdout_action_accuracy']} / {training['shifted_holdout_action_macro_f1']}.\n"
        f"- Mean-pixel ablation action accuracy / macro-F1: {training['pixel_ablated_holdout_action_accuracy']} / {training['pixel_ablated_holdout_action_macro_f1']}.\n"
        f"- Standard-minus-ablation accuracy: {training['standard_minus_pixel_ablated_accuracy']}.\n"
        f"- Standard raw / filtered success: {standard_raw['success_rate']} / {standard_filtered['success_rate']}.\n"
        f"- Shifted raw / filtered success: {shifted_raw['success_rate']} / {shifted_filtered['success_rate']}.\n"
        f"- Standard / shifted filter interventions: {standard_filtered['intervention_count']} / {shifted_filtered['intervention_count']}.\n\n"
        "## Not Demonstrated\n\n"
        "This model does not establish physical-camera perception, object detection, segmentation, depth estimation, calibration, occlusion handling, realistic sensor noise, convolutional visual learning, language grounding, a foundation VLA, physics, ROS, sim-to-real transfer, hardware control, or physical-safety validation.\n"
    )


def _behavior_cloning_failure_analysis(payload: dict[str, object]) -> str:
    episodes = payload["episodes"]
    assert isinstance(episodes, list)
    learned_policy_names = {
        "behavior_cloning_raw",
        "behavior_cloning_shielded",
        "semantic_raster_mlp_raw",
        "semantic_raster_mlp_shielded",
        "egocentric_mlp_raw",
        "egocentric_mlp_shielded",
        "synthetic_rgb_mlp_raw",
        "synthetic_rgb_mlp_shielded",
        "synthetic_rgb_mlp_shifted_raw",
        "synthetic_rgb_mlp_shifted_shielded",
    }
    failures = [
        row
        for row in episodes
        if isinstance(row, dict)
        and not row["success"]
        and row["policy_name"] in learned_policy_names
    ]
    failure_counts = {
        policy_name: sum(
            1 for row in failures if isinstance(row, dict) and row["policy_name"] == policy_name
        )
        for policy_name in sorted(learned_policy_names)
    }
    lines = [
        "# Imitation-Policy Failure Analysis",
        "",
        "Failed learned-policy episodes from the disjoint procedural holdout set.",
        "",
        f"- Learned-policy episodes: {sum(1 for row in episodes if isinstance(row, dict) and row['policy_name'] in learned_policy_names)}",
        f"- Failed learned-policy episodes: {len(failures)}",
        "- Failures by policy: "
        + ", ".join(f"{name}={count}" for name, count in failure_counts.items()),
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
            "No learned policy has an expert fallback toward the task goal. Failures therefore remain visible as evidence of compounding imitation error, representation limits, and a small training distribution.",
        ]
    )
    return "\n".join(lines) + "\n"
