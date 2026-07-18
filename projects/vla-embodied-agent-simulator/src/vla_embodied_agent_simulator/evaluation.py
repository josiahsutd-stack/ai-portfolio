from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from .environment import GridWorldEnv, SiteScenario, default_construction_scenarios
from .policies import PolicyPlan, naive_language_policy, random_policy, safety_shielded_policy

PolicyFn = Callable[[GridWorldEnv, str], PolicyPlan]


@dataclass(frozen=True)
class EpisodeResult:
    scenario_id: str
    scenario_name: str
    instruction: str
    policy_name: str
    success: bool
    steps: int
    total_reward: float
    unsafe_action_count: int
    task_error_count: int
    blocked_action_count: int
    intervention_count: int
    final_position: tuple[int, int]
    trace: list[dict[str, object]]


def run_episode(
    scenario: SiteScenario,
    policy: PolicyFn,
    *,
    seed: int = 7,
) -> EpisodeResult:
    env = GridWorldEnv.from_scenario(scenario)
    if policy is random_policy:
        plan = random_policy(env, scenario.instruction, seed=seed)
    else:
        plan = policy(env, scenario.instruction)
    total_reward = 0.0
    done = False
    for action in plan.actions[: scenario.max_steps]:
        _state, reward, done, _info = env.step(action)
        total_reward += reward
        if done:
            break
    trace = [
        {
            "step": step.step,
            "action": step.action,
            "reward": step.reward,
            "done": step.done,
            "info": step.info,
            "state": step.state,
        }
        for step in env.trace
    ]
    blocked_action_count = sum(
        1 for step in env.trace if step.info.get("error") == "unsafe_or_blocked_move"
    )
    unsafe_action_count = blocked_action_count
    task_error_count = sum(
        1
        for step in env.trace
        if "error" in step.info and step.info.get("error") != "unsafe_or_blocked_move"
    )
    return EpisodeResult(
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.name,
        instruction=scenario.instruction,
        policy_name=plan.policy_name,
        success=done and bool(env.trace and env.trace[-1].info.get("success")),
        steps=len(env.trace),
        total_reward=round(total_reward, 3),
        unsafe_action_count=unsafe_action_count,
        task_error_count=task_error_count,
        blocked_action_count=blocked_action_count,
        intervention_count=len(plan.interventions),
        final_position=env.agent,
        trace=trace,
    )


def evaluate_policy_suite(
    scenarios: list[SiteScenario] | None = None,
) -> dict[str, object]:
    scenario_set = scenarios or default_construction_scenarios()
    policies: list[PolicyFn] = [random_policy, naive_language_policy, safety_shielded_policy]
    episodes = [
        run_episode(scenario, policy, seed=index + 3)
        for index, scenario in enumerate(scenario_set)
        for policy in policies
    ]
    by_policy: dict[str, list[EpisodeResult]] = {}
    for episode in episodes:
        by_policy.setdefault(episode.policy_name, []).append(episode)
    policy_metrics = {
        policy_name: {
            "episode_count": len(rows),
            "success_rate": round(mean([1.0 if row.success else 0.0 for row in rows]), 3),
            "average_steps": round(mean([row.steps for row in rows]), 3),
            "average_reward": round(mean([row.total_reward for row in rows]), 3),
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
        for policy_name, rows in sorted(by_policy.items())
    }
    return {
        "scenario_count": len(scenario_set),
        "policies": policy_metrics,
        "episodes": [asdict(episode) for episode in episodes],
    }


def write_evaluation_artifacts(output_dir: str | Path) -> dict[str, object]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    payload = evaluate_policy_suite()
    compact_payload = {
        "scenario_count": payload["scenario_count"],
        "policies": payload["policies"],
        "episodes": [_compact_episode(episode) for episode in payload["episodes"]],
    }
    (target / "vla_eval_summary.json").write_text(
        json.dumps(compact_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "vla_eval_report.md").write_text(_markdown_report(payload), encoding="utf-8")
    sample_episode = next(
        episode for episode in payload["episodes"] if episode["policy_name"] == "safety_shielded"
    )
    (target / "sample_episode_trace.json").write_text(
        json.dumps(sample_episode, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "sample_episode_replay.md").write_text(
        _episode_replay(sample_episode),
        encoding="utf-8",
    )
    return payload


def _compact_episode(episode: dict[str, object]) -> dict[str, object]:
    return {
        "scenario_id": episode["scenario_id"],
        "scenario_name": episode["scenario_name"],
        "policy_name": episode["policy_name"],
        "success": episode["success"],
        "steps": episode["steps"],
        "total_reward": episode["total_reward"],
        "unsafe_action_count": episode["unsafe_action_count"],
        "task_error_count": episode["task_error_count"],
        "blocked_action_count": episode["blocked_action_count"],
        "intervention_count": episode["intervention_count"],
        "final_position": episode["final_position"],
    }


def _markdown_report(payload: dict[str, object]) -> str:
    lines = [
        "# Construction Embodied Agent Evaluation",
        "",
        "Local construction-site simulation metrics. This is not a real robot deployment.",
        "",
        f"- Scenarios: {payload['scenario_count']}",
        "",
        "| Policy | Success rate | Avg steps | Avg reward | Unsafe action rate | Task error rate | Blocked actions | Safety interventions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    policies = payload["policies"]
    assert isinstance(policies, dict)
    for policy_name, metrics in policies.items():
        assert isinstance(metrics, dict)
        lines.append(
            "| {policy} | {success} | {steps} | {reward} | {unsafe} | {task_error} | {blocked} | {interventions} |".format(
                policy=policy_name,
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
            "- `random` is a weak baseline for action-space sanity checks.",
            "- `naive_language` maps instruction text to direct moves without site-aware route planning.",
            "- `safety_shielded` uses parsed task intent plus safe route planning around obstacles, workers, and restricted zones.",
            "- Metrics are simulator regression checks, not evidence of robot-hardware safety.",
        ]
    )
    return "\n".join(lines) + "\n"


def _episode_replay(episode: dict[str, object]) -> str:
    lines = [
        "# Sample Embodied Agent Episode Replay",
        "",
        f"- Scenario: {episode['scenario_name']}",
        f"- Instruction: {episode['instruction']}",
        f"- Policy: {episode['policy_name']}",
        f"- Success: {episode['success']}",
        f"- Steps: {episode['steps']}",
        f"- Total reward: {episode['total_reward']}",
        "",
        "| Step | Action | Reward | Done | Info | Agent | Carrying |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    trace = episode["trace"]
    assert isinstance(trace, list)
    for row in trace:
        assert isinstance(row, dict)
        state = row["state"]
        assert isinstance(state, dict)
        lines.append(
            "| {step} | {action} | {reward} | {done} | `{info}` | {agent} | {carrying} |".format(
                step=row["step"],
                action=row["action"],
                reward=row["reward"],
                done=row["done"],
                info=json.dumps(row["info"], sort_keys=True),
                agent=state["agent"],
                carrying=state["carrying"],
            )
        )
    return "\n".join(lines) + "\n"
