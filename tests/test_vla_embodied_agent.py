from pathlib import Path

from vla_embodied_agent_simulator import (
    GridWorldEnv,
    default_construction_scenarios,
    evaluate_policy_suite,
    generate_behavior_cloning_scenarios,
    make_behavior_cloning_policy,
    parse_instruction,
    run_episode,
    safety_shielded_policy,
    train_behavior_cloning_policy,
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
    train = generate_behavior_cloning_scenarios("train")
    holdout = generate_behavior_cloning_scenarios("holdout")

    assert train == generate_behavior_cloning_scenarios("train")
    assert len(train) == 24
    assert len(holdout) == 24
    assert {row.scenario_id for row in train}.isdisjoint({row.scenario_id for row in holdout})
    assert {GridWorldEnv.from_scenario(row).task.task_type for row in train} == {
        "deliver",
        "inspect",
        "charge",
    }


def test_behavior_cloning_fits_real_action_classifier(tmp_path: Path) -> None:
    model, result = train_behavior_cloning_policy(model_output_dir=tmp_path)

    assert result.train_scenario_count == 24
    assert result.holdout_scenario_count == 24
    assert result.holdout_action_accuracy >= 0.8
    assert result.holdout_action_macro_f1 >= 0.8
    assert result.feature_count > 10
    assert {"pick", "drop", "inspect", "charge"}.issubset(result.classes)
    assert len(model.classes_) == len(result.classes)
    assert (tmp_path / result.model_file).exists()


def test_behavior_cloning_holdout_reports_failures_and_safety_effect(tmp_path: Path) -> None:
    payload = write_behavior_cloning_artifacts(
        tmp_path,
        model_output_dir=tmp_path / "model",
    )
    raw = payload["policies"]["behavior_cloning_raw"]
    shielded = payload["policies"]["behavior_cloning_shielded"]

    assert payload["split"]["scenario_id_overlap"] == []
    assert raw["unsafe_action_rate"] > 0
    assert shielded["unsafe_action_rate"] == 0.0
    assert shielded["success_rate"] >= raw["success_rate"]
    assert shielded["intervention_count"] > 0
    assert (tmp_path / "behavior_cloning_eval_summary.json").exists()
    assert (tmp_path / "behavior_cloning_eval_report.md").exists()
    assert (tmp_path / "behavior_cloning_model_card.md").exists()
    assert (tmp_path / "behavior_cloning_failure_analysis.md").exists()


def test_behavior_cloning_filter_preserves_safety_on_low_battery_demo() -> None:
    model, _result = train_behavior_cloning_policy()
    policy = make_behavior_cloning_policy(model, safety_filter=True)

    episode = run_episode(default_construction_scenarios()[0], policy)

    assert episode.unsafe_action_count == 0
    assert episode.blocked_action_count == 0
    assert episode.intervention_count > 0
