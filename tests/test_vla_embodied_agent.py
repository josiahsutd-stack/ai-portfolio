from dataclasses import replace
from pathlib import Path

import pytest
from vla_embodied_agent_simulator import (
    HOLDOUT_SCENARIOS_PER_TASK,
    SEMANTIC_RASTER_FEATURE_COUNT,
    SEMANTIC_RASTER_SIZE,
    TRAIN_SCENARIOS_PER_TASK,
    GridWorldEnv,
    default_construction_scenarios,
    encode_semantic_raster_state,
    evaluate_policy_suite,
    generate_behavior_cloning_scenarios,
    make_behavior_cloning_policy,
    parse_instruction,
    run_episode,
    safety_shielded_policy,
    train_behavior_cloning_policy,
    train_semantic_raster_policy,
    write_behavior_cloning_artifacts,
    write_evaluation_artifacts,
)


def test_embodied_agent_parses_construction_delivery_task() -> None:
    scenario = default_construction_scenarios()[0]
    env = GridWorldEnv.from_scenario(scenario)

    task = parse_instruction(scenario.instruction, env)

    assert task.task_type == "deliver"
    assert task.target_object == "drywall_stack"
    assert task.target_zone == "level_2_staging"
    assert task.success_action == "drop"


def test_safety_shielded_policy_completes_scenario_without_blocked_moves() -> None:
    scenario = default_construction_scenarios()[0]
    episode = run_episode(scenario, safety_shielded_policy)

    assert episode.success
    assert episode.blocked_action_count == 0
    assert episode.unsafe_action_count == 0
    assert episode.steps > 0
    assert episode.final_position == scenario.zones["level_2_staging"]


def test_embodied_agent_policy_suite_reports_safety_metrics() -> None:
    payload = evaluate_policy_suite(default_construction_scenarios())
    shielded = payload["policies"]["safety_shielded"]
    naive = payload["policies"]["naive_language"]

    assert shielded["success_rate"] == 1.0
    assert shielded["unsafe_action_rate"] == 0.0
    assert naive["blocked_action_count"] >= 1
    assert payload["scenario_count"] == 3


def test_embodied_agent_evaluation_artifacts_are_written(tmp_path: Path) -> None:
    payload = write_evaluation_artifacts(tmp_path)

    assert payload["scenario_count"] == 3
    assert (tmp_path / "vla_eval_summary.json").exists()
    assert (tmp_path / "vla_eval_report.md").exists()
    assert (tmp_path / "sample_episode_trace.json").exists()
    assert (tmp_path / "sample_episode_replay.md").exists()


def test_behavior_cloning_scenario_splits_are_deterministic_and_disjoint() -> None:
    train = generate_behavior_cloning_scenarios("train", count_per_task=TRAIN_SCENARIOS_PER_TASK)
    holdout = generate_behavior_cloning_scenarios(
        "holdout", count_per_task=HOLDOUT_SCENARIOS_PER_TASK
    )

    assert train == generate_behavior_cloning_scenarios(
        "train", count_per_task=TRAIN_SCENARIOS_PER_TASK
    )
    assert len(train) == 192
    assert len(holdout) == 96
    assert {row.scenario_id for row in train}.isdisjoint({row.scenario_id for row in holdout})
    assert {GridWorldEnv.from_scenario(row).task.task_type for row in train} == {
        "deliver",
        "inspect",
        "charge",
    }


def test_behavior_cloning_fits_real_action_classifier(tmp_path: Path) -> None:
    model, result = train_behavior_cloning_policy(model_output_dir=tmp_path)

    assert result.train_scenario_count == 192
    assert result.holdout_scenario_count == 96
    assert result.holdout_action_accuracy >= 0.8
    assert result.holdout_action_macro_f1 >= 0.8
    assert result.feature_count > 10
    assert {"pick", "drop", "inspect", "charge"}.issubset(result.classes)
    assert len(model.classes_) == len(result.classes)
    assert (tmp_path / result.model_file).exists()


def test_semantic_raster_encoder_has_stable_channel_contract() -> None:
    env = GridWorldEnv.from_scenario(default_construction_scenarios()[0])

    features = encode_semantic_raster_state(env)

    channel_size = SEMANTIC_RASTER_SIZE**2
    assert len(features) == SEMANTIC_RASTER_FEATURE_COUNT
    assert sum(features[:channel_size]) == 1.0
    assert sum(features[channel_size : 2 * channel_size]) == 1.0
    assert features == encode_semantic_raster_state(env)


def test_semantic_raster_encoder_rejects_unsupported_grid_size() -> None:
    scenario = replace(default_construction_scenarios()[0], width=8)
    env = GridWorldEnv.from_scenario(scenario)

    with pytest.raises(ValueError, match="supports grids up to 7x7"):
        encode_semantic_raster_state(env)


def test_semantic_raster_policy_fits_neural_action_classifier(tmp_path: Path) -> None:
    model, result = train_semantic_raster_policy(model_output_dir=tmp_path)

    assert result.train_scenario_count == 192
    assert result.holdout_scenario_count == 96
    assert result.feature_count == SEMANTIC_RASTER_FEATURE_COUNT
    assert result.holdout_action_accuracy >= 0.4
    assert result.holdout_action_macro_f1 >= 0.4
    assert {"pick", "drop", "inspect", "charge"}.issubset(result.classes)
    assert len(model.classes_) == len(result.classes)
    assert (tmp_path / result.model_file).exists()


def test_behavior_cloning_holdout_reports_failures_and_safety_effect(tmp_path: Path) -> None:
    payload = write_behavior_cloning_artifacts(
        tmp_path,
        model_output_dir=tmp_path / "model",
        site_asset_path=tmp_path / "site" / "semantic-raster-comparison.svg",
    )
    raw = payload["policies"]["behavior_cloning_raw"]
    shielded = payload["policies"]["behavior_cloning_shielded"]
    raster_raw = payload["policies"]["semantic_raster_mlp_raw"]
    raster_shielded = payload["policies"]["semantic_raster_mlp_shielded"]
    comparison = payload["representation_comparison"]

    assert payload["split"]["scenario_id_overlap"] == []
    assert raw["unsafe_action_rate"] > 0
    assert shielded["unsafe_action_rate"] == 0.0
    assert shielded["success_rate"] >= raw["success_rate"]
    assert shielded["intervention_count"] > 0
    assert raster_raw["unsafe_action_rate"] > 0
    assert raster_shielded["unsafe_action_rate"] == 0.0
    assert raster_shielded["success_rate"] >= raster_raw["success_rate"]
    assert shielded["success_rate"] > raster_shielded["success_rate"]
    assert comparison["expert_action_accuracy_delta_structured_minus_raster"] > 0
    assert comparison["shielded_success_delta_structured_minus_raster"] > 0
    assert (tmp_path / "behavior_cloning_eval_summary.json").exists()
    assert (tmp_path / "behavior_cloning_eval_report.md").exists()
    assert (tmp_path / "behavior_cloning_model_card.md").exists()
    assert (tmp_path / "semantic_raster_model_card.md").exists()
    assert (tmp_path / "semantic_raster_comparison.svg").exists()
    assert (tmp_path / "behavior_cloning_failure_analysis.md").exists()
    assert (tmp_path / "site" / "semantic-raster-comparison.svg").exists()


def test_behavior_cloning_filter_preserves_safe_demo_completion() -> None:
    model, _result = train_behavior_cloning_policy()
    policy = make_behavior_cloning_policy(model, safety_filter=True)

    episode = run_episode(default_construction_scenarios()[0], policy)

    assert episode.success
    assert episode.unsafe_action_count == 0
    assert episode.blocked_action_count == 0
