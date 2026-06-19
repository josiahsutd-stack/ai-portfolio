from pathlib import Path

from vla_embodied_agent_simulator import (
    GridWorldEnv,
    default_construction_scenarios,
    evaluate_policy_suite,
    parse_instruction,
    run_episode,
    safety_shielded_policy,
    write_evaluation_artifacts,
)


def test_vla_parses_construction_delivery_task() -> None:
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


def test_vla_policy_suite_reports_safety_metrics() -> None:
    payload = evaluate_policy_suite(default_construction_scenarios())
    shielded = payload["policies"]["safety_shielded"]
    naive = payload["policies"]["naive_language"]

    assert shielded["success_rate"] == 1.0
    assert shielded["unsafe_action_rate"] == 0.0
    assert naive["blocked_action_count"] >= 1
    assert payload["scenario_count"] == 3


def test_vla_evaluation_artifacts_are_written(tmp_path: Path) -> None:
    payload = write_evaluation_artifacts(tmp_path)

    assert payload["scenario_count"] == 3
    assert (tmp_path / "vla_eval_summary.json").exists()
    assert (tmp_path / "vla_eval_report.md").exists()
    assert (tmp_path / "sample_episode_trace.json").exists()
    assert (tmp_path / "sample_episode_replay.md").exists()
