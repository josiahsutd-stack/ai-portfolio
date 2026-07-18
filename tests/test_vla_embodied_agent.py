from dataclasses import replace
from pathlib import Path

import pytest
from vla_embodied_agent_simulator import (
    EGOCENTRIC_FEATURE_COUNT,
    EGOCENTRIC_WINDOW_SIZE,
    HOLDOUT_SCENARIOS_PER_TASK,
    RGB_IMAGE_SIZE,
    SEMANTIC_RASTER_FEATURE_COUNT,
    SEMANTIC_RASTER_SIZE,
    SYNTHETIC_RGB_FEATURE_COUNT,
    SYNTHETIC_RGB_SHIFTED_PALETTE,
    TRAIN_SCENARIOS_PER_TASK,
    GridWorldEnv,
    MuJoCoPlanarReplay,
    PolicyPlan,
    default_construction_scenarios,
    encode_egocentric_local_state,
    encode_semantic_raster_state,
    encode_synthetic_rgb_observation,
    evaluate_physics_replay,
    evaluate_policy_suite,
    generate_behavior_cloning_scenarios,
    make_behavior_cloning_policy,
    make_synthetic_rgb_policy,
    naive_language_policy,
    parse_instruction,
    render_synthetic_rgb_observation,
    replay_policy_in_physics,
    run_episode,
    safety_shielded_policy,
    train_behavior_cloning_policy,
    train_egocentric_policy,
    train_semantic_raster_policy,
    train_synthetic_rgb_policy,
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


def test_non_charge_task_cannot_claim_success_by_charging() -> None:
    scenario = replace(default_construction_scenarios()[0], battery=30.0)
    env = GridWorldEnv.from_scenario(scenario)

    _state, reward, done, info = env.step("charge")

    assert not done
    assert reward < 0
    assert info["error"] == "charge_not_needed"
    assert "success" not in info


def test_low_battery_recovery_is_nonterminal_for_delivery_task() -> None:
    scenario = replace(default_construction_scenarios()[0], battery=5.0)
    env = GridWorldEnv.from_scenario(scenario)

    _state, reward, done, info = env.step("charge")

    assert not done
    assert reward == 0.5
    assert env.battery == 30.0
    assert info["event"] == "battery_recovered"
    assert "success" not in info


def test_delivery_destination_is_not_an_implicit_charging_point() -> None:
    scenario = replace(default_construction_scenarios()[0], battery=5.0)
    env = GridWorldEnv.from_scenario(scenario)
    env.agent = scenario.zones["level_2_staging"]

    _state, reward, done, info = env.step("charge")

    assert not done
    assert reward < 0
    assert env.battery == 5.0
    assert info["error"] == "not_at_charger"


def test_charge_loop_timeout_is_not_counted_as_task_success() -> None:
    scenario = replace(default_construction_scenarios()[0], max_steps=4)

    def charge_loop(env: GridWorldEnv, instruction: str) -> PolicyPlan:
        return PolicyPlan(
            policy_name="charge_loop",
            actions=["charge"] * env.max_steps,
            task=parse_instruction(instruction, env),
        )

    episode = run_episode(scenario, charge_loop)

    assert not episode.success
    assert episode.steps == scenario.max_steps
    assert episode.trace[-1]["info"]["timeout"] is True
    assert "success" not in episode.trace[-1]["info"]


def test_embodied_agent_evaluation_artifacts_are_written(tmp_path: Path) -> None:
    payload = write_evaluation_artifacts(tmp_path)

    assert payload["scenario_count"] == 3
    assert (tmp_path / "vla_eval_summary.json").exists()
    assert (tmp_path / "vla_eval_report.md").exists()
    assert (tmp_path / "sample_episode_trace.json").exists()
    assert (tmp_path / "sample_episode_replay.md").exists()


def test_mujoco_replay_maps_grid_start_to_continuous_geometry() -> None:
    scenario = default_construction_scenarios()[0]
    replay = MuJoCoPlanarReplay(scenario)

    assert replay.position_xy == (0.0, 0.0)
    assert replay.model.nu == 2
    assert replay.model.ngeom >= len(scenario.obstacles) + 6


def test_mujoco_replay_detects_contacts_for_unfiltered_commands() -> None:
    result = replay_policy_in_physics(
        default_construction_scenarios()[0],
        naive_language_policy,
    )

    assert result.contact_command_count >= 1
    assert "obstacle_3_4" in result.unique_contact_geometries
    assert result.reached_movement_target_count < result.movement_command_count
    assert result.final_alignment_error_m <= 0.08


def test_mujoco_replay_shielded_route_reaches_targets_without_contact() -> None:
    result = replay_policy_in_physics(
        default_construction_scenarios()[0],
        safety_shielded_policy,
    )

    assert result.discrete_success
    assert result.contact_command_count == 0
    assert result.reached_movement_target_count == result.movement_command_count
    assert result.max_command_target_error_m <= 0.08
    assert result.final_alignment_error_m <= 0.08


def test_mujoco_replay_aggregate_is_deterministic() -> None:
    scenarios = default_construction_scenarios()
    policies = [naive_language_policy, safety_shielded_policy]

    first = evaluate_physics_replay(scenarios, policies)
    second = evaluate_physics_replay(scenarios, policies)

    assert first == second
    assert first["policies"]["naive_language"]["contact_command_count"] == 4
    assert first["policies"]["safety_shielded"]["contact_command_count"] == 0


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


def test_egocentric_encoder_has_local_observation_contract() -> None:
    scenario = default_construction_scenarios()[0]
    env = GridWorldEnv.from_scenario(scenario)

    features = encode_egocentric_local_state(env)
    channel_size = EGOCENTRIC_WINDOW_SIZE**2
    out_of_bounds = features[7 * channel_size : 8 * channel_size]

    assert len(features) == EGOCENTRIC_FEATURE_COUNT
    assert sum(out_of_bounds) == 16.0
    assert features[-10] == 1.0
    assert features == encode_egocentric_local_state(env)


def test_egocentric_encoder_hides_hazards_outside_local_window() -> None:
    scenario = default_construction_scenarios()[0]
    distant_hazard = replace(scenario, obstacles=scenario.obstacles | {(6, 5)})

    base = encode_egocentric_local_state(GridWorldEnv.from_scenario(scenario))
    changed = encode_egocentric_local_state(GridWorldEnv.from_scenario(distant_hazard))

    assert base == changed


def test_egocentric_policy_fits_local_state_classifier(tmp_path: Path) -> None:
    model, result = train_egocentric_policy(model_output_dir=tmp_path)

    assert result.train_scenario_count == 192
    assert result.holdout_scenario_count == 96
    assert result.feature_count == EGOCENTRIC_FEATURE_COUNT
    assert result.window_size == 5
    assert result.holdout_action_accuracy >= 0.8
    assert result.holdout_action_macro_f1 >= 0.85
    assert {"pick", "drop", "inspect", "charge"}.issubset(result.classes)
    assert len(model.classes_) == len(result.classes)
    assert (tmp_path / result.model_file).exists()


def test_synthetic_rgb_encoder_is_pixel_derived_and_deterministic() -> None:
    env = GridWorldEnv.from_scenario(default_construction_scenarios()[0])

    standard = encode_synthetic_rgb_observation(env)
    shifted = encode_synthetic_rgb_observation(
        env,
        palette_name=SYNTHETIC_RGB_SHIFTED_PALETTE,
    )

    assert len(standard) == SYNTHETIC_RGB_FEATURE_COUNT
    assert standard == encode_synthetic_rgb_observation(env)
    assert standard[:-10] != shifted[:-10]
    assert standard[-10:] == shifted[-10:]
    assert all(0.0 <= value <= 1.0 for value in standard[:-10])

    image = render_synthetic_rgb_observation(env, env.objects["drywall_stack"])
    assert image.shape == (RGB_IMAGE_SIZE, RGB_IMAGE_SIZE, 3)
    assert image.dtype.name == "uint8"
    assert len({tuple(pixel) for row in image for pixel in row}) >= 3

    with pytest.raises(ValueError, match="unknown RGB palette"):
        encode_synthetic_rgb_observation(env, palette_name="missing")


def test_synthetic_rgb_encoder_hides_distant_hazards() -> None:
    scenario = default_construction_scenarios()[0]
    distant_hazard = replace(scenario, obstacles=scenario.obstacles | {(6, 5)})

    base = encode_synthetic_rgb_observation(GridWorldEnv.from_scenario(scenario))
    changed = encode_synthetic_rgb_observation(GridWorldEnv.from_scenario(distant_hazard))

    assert base == changed


def test_synthetic_rgb_policy_fits_and_reports_appearance_shift(tmp_path: Path) -> None:
    model, result = train_synthetic_rgb_policy(model_output_dir=tmp_path)

    assert result.train_scenario_count == 192
    assert result.holdout_scenario_count == 96
    assert result.training_step_count == 1830
    assert result.augmented_training_example_count == 3660
    assert result.feature_count == SYNTHETIC_RGB_FEATURE_COUNT
    assert result.standard_holdout_action_accuracy >= 0.5
    assert result.shifted_holdout_action_accuracy >= 0.2
    assert result.pixel_ablated_holdout_action_accuracy < result.standard_holdout_action_accuracy
    assert result.standard_minus_pixel_ablated_accuracy >= 0.2
    assert result.standard_palette not in {result.shifted_palette}
    assert result.shifted_palette not in result.train_palettes
    assert {"pick", "drop", "inspect", "charge"}.issubset(result.classes)
    assert len(model.classes_) == len(result.classes)
    assert (tmp_path / result.model_file).exists()


def test_synthetic_rgb_filtered_policy_executes_demo_scenario() -> None:
    model, _result = train_synthetic_rgb_policy()
    policy = make_synthetic_rgb_policy(model, safety_filter=True)

    episode = run_episode(default_construction_scenarios()[0], policy)

    assert episode.unsafe_action_count == 0
    assert episode.blocked_action_count == 0


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
    egocentric_raw = payload["policies"]["egocentric_mlp_raw"]
    egocentric_shielded = payload["policies"]["egocentric_mlp_shielded"]
    rgb_raw = payload["policies"]["synthetic_rgb_mlp_raw"]
    rgb_shielded = payload["policies"]["synthetic_rgb_mlp_shielded"]
    rgb_shifted_raw = payload["policies"]["synthetic_rgb_mlp_shifted_raw"]
    rgb_shifted_shielded = payload["policies"]["synthetic_rgb_mlp_shifted_shielded"]
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
    assert egocentric_raw["unsafe_action_rate"] > 0
    assert egocentric_shielded["unsafe_action_rate"] == 0.0
    assert egocentric_shielded["success_rate"] > shielded["success_rate"]
    assert egocentric_shielded["success_rate"] > raster_shielded["success_rate"]
    assert egocentric_shielded["intervention_count"] > 0
    assert rgb_raw["unsafe_action_rate"] > 0
    assert rgb_shielded["unsafe_action_rate"] == 0.0
    assert rgb_shifted_raw["unsafe_action_rate"] > 0
    assert rgb_shifted_shielded["unsafe_action_rate"] == 0.0
    assert rgb_shielded["intervention_count"] > 0
    assert rgb_shifted_shielded["intervention_count"] > 0
    assert comparison["expert_action_accuracy_delta_structured_minus_raster"] > 0
    assert comparison["shielded_success_delta_structured_minus_raster"] > 0
    assert comparison["expert_action_accuracy_delta_egocentric_minus_raster"] > 0
    assert comparison["shielded_success_delta_egocentric_minus_structured"] > 0
    assert (tmp_path / "behavior_cloning_eval_summary.json").exists()
    assert (tmp_path / "behavior_cloning_eval_report.md").exists()
    assert (tmp_path / "behavior_cloning_model_card.md").exists()
    assert (tmp_path / "semantic_raster_model_card.md").exists()
    assert (tmp_path / "egocentric_mlp_model_card.md").exists()
    assert (tmp_path / "synthetic_rgb_mlp_model_card.md").exists()
    assert (tmp_path / "synthetic_rgb_observation_day.png").exists()
    assert (tmp_path / "synthetic_rgb_observation_worklight.png").exists()
    assert (tmp_path / "semantic_raster_comparison.svg").exists()
    assert (tmp_path / "behavior_cloning_failure_analysis.md").exists()
    assert (tmp_path / "physics_replay_summary.json").exists()
    assert (tmp_path / "physics_replay_report.md").exists()
    assert (tmp_path / "physics_replay_comparison.svg").exists()
    assert (tmp_path / "site" / "semantic-raster-comparison.svg").exists()
    physics = payload["physics_replay"]["policies"]
    assert physics["egocentric_mlp_raw"]["contact_command_count"] > 0
    assert physics["egocentric_mlp_shielded"]["contact_command_count"] == 0
    assert physics["egocentric_mlp_shielded"]["reached_movement_target_rate"] == 1.0


def test_behavior_cloning_filter_preserves_safe_demo_completion() -> None:
    model, _result = train_behavior_cloning_policy()
    policy = make_behavior_cloning_policy(model, safety_filter=True)

    episode = run_episode(default_construction_scenarios()[0], policy)

    assert episode.success
    assert episode.unsafe_action_count == 0
    assert episode.blocked_action_count == 0
