from __future__ import annotations

import random
from dataclasses import dataclass, field

from .environment import (
    ACTIONS,
    MOVE_DELTAS,
    GridWorldEnv,
    TaskSpec,
    parse_instruction,
    plan_from_instruction,
)


@dataclass(frozen=True)
class PolicyPlan:
    policy_name: str
    actions: list[str]
    interventions: list[dict[str, object]] = field(default_factory=list)
    task: TaskSpec | None = None


def random_policy(env: GridWorldEnv, instruction: str, *, seed: int = 7) -> PolicyPlan:
    rng = random.Random(seed)
    task = parse_instruction(instruction, env)
    actions = [rng.choice(ACTIONS) for _ in range(min(env.max_steps, 18))]
    return PolicyPlan(policy_name="random", actions=actions, task=task)


def naive_language_policy(env: GridWorldEnv, instruction: str) -> PolicyPlan:
    task = parse_instruction(instruction, env)
    env.task = task
    if task.task_type == "deliver" and task.target_object and task.target_zone:
        object_position = env.objects.get(task.target_object)
        zone_position = env.zones.get(task.target_zone)
        if object_position and zone_position:
            return PolicyPlan(
                policy_name="naive_language",
                actions=[
                    *_straight_line_actions(env.agent, object_position),
                    "pick",
                    *_straight_line_actions(object_position, zone_position),
                    "drop",
                ],
                task=task,
            )
    if task.task_type in {"inspect", "charge"} and task.target_zone:
        target = env.zones.get(task.target_zone)
        if target:
            return PolicyPlan(
                policy_name="naive_language",
                actions=[
                    *_straight_line_actions(env.agent, target),
                    task.success_action,
                ],
                task=task,
            )
    return PolicyPlan(policy_name="naive_language", actions=["wait"], task=task)


def safety_shielded_policy(env: GridWorldEnv, instruction: str) -> PolicyPlan:
    task = parse_instruction(instruction, env)
    planned_actions = plan_from_instruction(instruction, env)
    interventions: list[dict[str, object]] = []
    probe = env.clone()
    repaired_actions: list[str] = []
    for action in planned_actions:
        safe, reason = probe.is_action_safe(action)
        if not safe:
            replacement = _first_safe_wait_or_move(probe)
            interventions.append(
                {
                    "blocked_action": action,
                    "reason": reason,
                    "replacement": replacement,
                    "step": len(repaired_actions) + 1,
                }
            )
            action = replacement
        repaired_actions.append(action)
        _state, _reward, done, _info = probe.step(action)
        if done:
            break
    return PolicyPlan(
        policy_name="safety_shielded",
        actions=repaired_actions,
        interventions=interventions,
        task=task,
    )


def _straight_line_actions(start: tuple[int, int], goal: tuple[int, int]) -> list[str]:
    actions: list[str] = []
    dx = goal[0] - start[0]
    dy = goal[1] - start[1]
    actions.extend(["move_right" if dx > 0 else "move_left"] * abs(dx))
    actions.extend(["move_down" if dy > 0 else "move_up"] * abs(dy))
    return actions


def _first_safe_wait_or_move(env: GridWorldEnv) -> str:
    for action in [*MOVE_DELTAS, "wait"]:
        if env.is_action_safe(action)[0]:
            return action
    return "wait"
