from __future__ import annotations

import html
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

import mujoco

from .environment import MOVE_DELTAS, GridWorldEnv, Position, SiteScenario
from .evaluation import PolicyFn

CELL_SIZE_METERS = 1.0
ROBOT_RADIUS_METERS = 0.18
OBSTACLE_HALF_EXTENT_METERS = 0.34
COMMAND_STEPS = 260
RECOVERY_STEPS = 260
TARGET_TOLERANCE_METERS = 0.08


@dataclass(frozen=True)
class PhysicsCommandResult:
    step: int
    action: str
    grid_start: Position
    commanded_grid_target: Position
    discrete_grid_result: Position
    physics_start_xy: tuple[float, float]
    physics_command_end_xy: tuple[float, float]
    physics_recovery_end_xy: tuple[float, float]
    command_target_error_m: float
    replay_alignment_error_m: float
    reached_command_target: bool
    contact_geometries: list[str]
    contact_sample_count: int


@dataclass(frozen=True)
class PhysicsReplayResult:
    scenario_id: str
    task_type: str
    policy_name: str
    discrete_success: bool
    action_count: int
    movement_command_count: int
    reached_movement_target_count: int
    contact_command_count: int
    contact_sample_count: int
    unique_contact_geometries: list[str]
    max_command_target_error_m: float
    final_alignment_error_m: float
    commands: list[PhysicsCommandResult]


class MuJoCoPlanarReplay:
    """Headless planar rigid-body replay for discrete grid commands."""

    def __init__(self, scenario: SiteScenario) -> None:
        self.scenario = scenario
        self.model = mujoco.MjModel.from_xml_string(_scenario_xml(scenario))
        self.data = mujoco.MjData(self.model)
        self._start = scenario.start
        self._robot_geom_id = mujoco.mj_name2id(
            self.model,
            mujoco.mjtObj.mjOBJ_GEOM,
            "robot",
        )
        mujoco.mj_forward(self.model, self.data)

    @property
    def position_xy(self) -> tuple[float, float]:
        body_id = mujoco.mj_name2id(
            self.model,
            mujoco.mjtObj.mjOBJ_BODY,
            "robot_body",
        )
        position = self.data.xpos[body_id]
        return round(float(position[0]), 6), round(float(position[1]), 6)

    def command_grid_target(
        self,
        target: Position,
        *,
        steps: int = COMMAND_STEPS,
    ) -> tuple[tuple[float, float], list[str], int]:
        target_xy = grid_to_world(target)
        self.data.ctrl[0] = target_xy[0] - self._start[0] * CELL_SIZE_METERS
        self.data.ctrl[1] = target_xy[1] - self._start[1] * CELL_SIZE_METERS
        contacts: set[str] = set()
        contact_samples = 0
        for _ in range(steps):
            mujoco.mj_step(self.model, self.data)
            step_contacts = self._robot_contacts()
            if step_contacts:
                contact_samples += 1
                contacts.update(step_contacts)
        return self.position_xy, sorted(contacts), contact_samples

    def _robot_contacts(self) -> set[str]:
        names: set[str] = set()
        for index in range(self.data.ncon):
            contact = self.data.contact[index]
            if self._robot_geom_id not in {contact.geom1, contact.geom2}:
                continue
            other_id = contact.geom2 if contact.geom1 == self._robot_geom_id else contact.geom1
            name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, other_id)
            if name and name != "floor":
                names.add(name)
        return names


def grid_to_world(position: Position) -> tuple[float, float]:
    return position[0] * CELL_SIZE_METERS, position[1] * CELL_SIZE_METERS


def replay_policy_in_physics(
    scenario: SiteScenario,
    policy: PolicyFn,
) -> PhysicsReplayResult:
    env = GridWorldEnv.from_scenario(scenario)
    plan = policy(env, scenario.instruction)
    env = GridWorldEnv.from_scenario(scenario)
    replay = MuJoCoPlanarReplay(scenario)
    commands: list[PhysicsCommandResult] = []
    terminal_info: dict[str, object] = {}
    done = False

    for step_index, action in enumerate(plan.actions[: scenario.max_steps], start=1):
        grid_start = env.agent
        _state, _reward, done, terminal_info = env.step(action)
        if action in MOVE_DELTAS:
            delta = MOVE_DELTAS[action]
            commanded_target = grid_start[0] + delta[0], grid_start[1] + delta[1]
            physics_start = replay.position_xy
            command_end, contacts, contact_samples = replay.command_grid_target(commanded_target)
            command_error = _distance(command_end, grid_to_world(commanded_target))
            recovery_end = command_end
            if env.agent != commanded_target:
                recovery_end, _recovery_contacts, _samples = replay.command_grid_target(
                    env.agent,
                    steps=RECOVERY_STEPS,
                )
            commands.append(
                PhysicsCommandResult(
                    step=step_index,
                    action=action,
                    grid_start=grid_start,
                    commanded_grid_target=commanded_target,
                    discrete_grid_result=env.agent,
                    physics_start_xy=physics_start,
                    physics_command_end_xy=command_end,
                    physics_recovery_end_xy=recovery_end,
                    command_target_error_m=round(command_error, 4),
                    replay_alignment_error_m=round(
                        _distance(recovery_end, grid_to_world(env.agent)),
                        4,
                    ),
                    reached_command_target=command_error <= TARGET_TOLERANCE_METERS,
                    contact_geometries=contacts,
                    contact_sample_count=contact_samples,
                )
            )
        if done:
            break

    task_success = terminal_info.get("success") in {
        "task_complete",
        "inspection_complete",
        "charged",
    }
    unique_contacts = sorted({name for command in commands for name in command.contact_geometries})
    return PhysicsReplayResult(
        scenario_id=scenario.scenario_id,
        task_type=env.task.task_type if env.task else "unknown",
        policy_name=plan.policy_name,
        discrete_success=done and task_success and not terminal_info.get("timeout", False),
        action_count=len(env.trace),
        movement_command_count=len(commands),
        reached_movement_target_count=sum(command.reached_command_target for command in commands),
        contact_command_count=sum(bool(command.contact_geometries) for command in commands),
        contact_sample_count=sum(command.contact_sample_count for command in commands),
        unique_contact_geometries=unique_contacts,
        max_command_target_error_m=round(
            max((command.command_target_error_m for command in commands), default=0.0),
            4,
        ),
        final_alignment_error_m=round(
            _distance(replay.position_xy, grid_to_world(env.agent)),
            4,
        ),
        commands=commands,
    )


def evaluate_physics_replay(
    scenarios: Sequence[SiteScenario],
    policies: Sequence[PolicyFn],
) -> dict[str, object]:
    episodes = [
        replay_policy_in_physics(scenario, policy) for scenario in scenarios for policy in policies
    ]
    by_policy: dict[str, list[PhysicsReplayResult]] = {}
    for episode in episodes:
        by_policy.setdefault(episode.policy_name, []).append(episode)
    metrics = {}
    for policy_name, rows in sorted(by_policy.items()):
        movement_commands = sum(row.movement_command_count for row in rows)
        contact_commands = sum(row.contact_command_count for row in rows)
        reached_commands = sum(row.reached_movement_target_count for row in rows)
        metrics[policy_name] = {
            "episode_count": len(rows),
            "discrete_success_rate": round(mean(float(row.discrete_success) for row in rows), 3),
            "movement_command_count": movement_commands,
            "reached_movement_target_rate": round(
                reached_commands / max(1, movement_commands),
                3,
            ),
            "contact_command_count": contact_commands,
            "contact_command_rate": round(contact_commands / max(1, movement_commands), 3),
            "contact_sample_count": sum(row.contact_sample_count for row in rows),
            "max_command_target_error_m": round(
                max(row.max_command_target_error_m for row in rows),
                4,
            ),
            "max_final_alignment_error_m": round(
                max(row.final_alignment_error_m for row in rows),
                4,
            ),
        }
    return {
        "evaluation_type": "headless MuJoCo planar rigid-body command replay",
        "engine": f"MuJoCo {mujoco.__version__}",
        "scenario_count": len(scenarios),
        "policy_count": len(policies),
        "cell_size_m": CELL_SIZE_METERS,
        "robot_radius_m": ROBOT_RADIUS_METERS,
        "command_steps": COMMAND_STEPS,
        "target_tolerance_m": TARGET_TOLERANCE_METERS,
        "policies": metrics,
        "episodes": [asdict(episode) for episode in episodes],
        "claim_boundary": (
            "Continuous planar command replay with rigid contacts; not a mobile-robot model, "
            "controller validation, ROS integration, perception stack, or physical-safety result."
        ),
    }


def write_physics_replay_artifacts(
    payload: dict[str, object],
    output_dir: str | Path,
    *,
    site_asset_path: str | Path | None = None,
) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    compact_payload = {
        **payload,
        "episodes": [_compact_physics_episode(row) for row in payload["episodes"]],
    }
    (target / "physics_replay_summary.json").write_text(
        json.dumps(compact_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "physics_replay_report.md").write_text(
        _physics_report(payload),
        encoding="utf-8",
    )
    svg = _physics_comparison_svg(payload)
    (target / "physics_replay_comparison.svg").write_text(svg, encoding="utf-8")
    if site_asset_path is not None:
        site_target = Path(site_asset_path)
        site_target.parent.mkdir(parents=True, exist_ok=True)
        site_target.write_text(svg, encoding="utf-8")


def _compact_physics_episode(row: object) -> dict[str, object]:
    assert isinstance(row, dict)
    return {key: value for key, value in row.items() if key != "commands"}


def _scenario_xml(scenario: SiteScenario) -> str:
    start_x, start_y = grid_to_world(scenario.start)
    geoms = [
        _box_geom(f"obstacle_{x}_{y}", x, y, "0.20 0.24 0.29 1")
        for x, y in sorted(scenario.obstacles)
    ]
    geoms.extend(
        _box_geom(f"restricted_proxy_{x}_{y}", x, y, "0.73 0.16 0.21 1")
        for x, y in sorted(scenario.restricted_zones)
    )
    geoms.extend(
        _cylinder_geom(f"worker_proxy_{x}_{y}", x, y) for x, y in sorted(scenario.worker_zones)
    )
    geoms.extend(_boundary_geoms(scenario.width, scenario.height))
    x_range = max(scenario.width + 1, 2)
    y_range = max(scenario.height + 1, 2)
    return f"""
<mujoco model="{html.escape(scenario.scenario_id)}_planar_replay">
  <compiler angle="radian"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="implicitfast" solver="Newton"/>
  <default>
    <geom friction="0.9 0.05 0.01" solref="0.01 1" solimp="0.95 0.99 0.001"/>
  </default>
  <worldbody>
    <geom name="floor" type="plane" size="{scenario.width} {scenario.height} 0.1" rgba="0.88 0.90 0.92 1"/>
    {''.join(geoms)}
    <body name="robot_body" pos="{start_x:.4f} {start_y:.4f} 0.20">
      <joint name="robot_x" type="slide" axis="1 0 0" range="-{x_range} {x_range}" damping="8"/>
      <joint name="robot_y" type="slide" axis="0 1 0" range="-{y_range} {y_range}" damping="8"/>
      <geom name="robot" type="cylinder" size="{ROBOT_RADIUS_METERS} 0.18" mass="10" rgba="0.02 0.55 0.64 1"/>
    </body>
  </worldbody>
  <actuator>
    <position name="drive_x" joint="robot_x" kp="180" kv="78" ctrllimited="true" ctrlrange="-{x_range} {x_range}" forcelimited="true" forcerange="-140 140"/>
    <position name="drive_y" joint="robot_y" kp="180" kv="78" ctrllimited="true" ctrlrange="-{y_range} {y_range}" forcelimited="true" forcerange="-140 140"/>
  </actuator>
</mujoco>
""".strip()


def _box_geom(name: str, x: int, y: int, rgba: str) -> str:
    return (
        f'<geom name="{name}" type="box" pos="{x} {y} 0.20" '
        f'size="{OBSTACLE_HALF_EXTENT_METERS} {OBSTACLE_HALF_EXTENT_METERS} 0.20" '
        f'rgba="{rgba}"/>'
    )


def _cylinder_geom(name: str, x: int, y: int) -> str:
    return (
        f'<geom name="{name}" type="cylinder" pos="{x} {y} 0.20" '
        'size="0.28 0.20" rgba="0.95 0.62 0.10 1"/>'
    )


def _boundary_geoms(width: int, height: int) -> list[str]:
    center_x = (width - 1) / 2
    center_y = (height - 1) / 2
    half_width = width / 2
    half_height = height / 2
    return [
        f'<geom name="boundary_left" type="box" pos="-0.55 {center_y} 0.20" size="0.05 {half_height} 0.20" rgba="0.35 0.38 0.42 1"/>',
        f'<geom name="boundary_right" type="box" pos="{width - 0.45} {center_y} 0.20" size="0.05 {half_height} 0.20" rgba="0.35 0.38 0.42 1"/>',
        f'<geom name="boundary_top" type="box" pos="{center_x} -0.55 0.20" size="{half_width} 0.05 0.20" rgba="0.35 0.38 0.42 1"/>',
        f'<geom name="boundary_bottom" type="box" pos="{center_x} {height - 0.45} 0.20" size="{half_width} 0.05 0.20" rgba="0.35 0.38 0.42 1"/>',
    ]


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _physics_report(payload: dict[str, object]) -> str:
    policies = payload["policies"]
    assert isinstance(policies, dict)
    lines = [
        "# MuJoCo Planar Physics Replay",
        "",
        "This fixed-set evaluation replays discrete policy commands as continuous planar position-control targets in headless MuJoCo. Static obstacles, restricted-area proxies, worker proxies, and site boundaries participate in rigid contact. It is a command-interface and collision-regression test, not a mobile-robot dynamics or safety validation.",
        "",
        f"- Engine: `{payload['engine']}`",
        f"- Scenarios: {payload['scenario_count']}",
        f"- Policies: {payload['policy_count']}",
        f"- Cell scale: {payload['cell_size_m']} m",
        f"- Target tolerance: {payload['target_tolerance_m']} m",
        "",
        "| Policy | Episodes | Discrete success | Move commands | Reached target | Contact commands | Contact rate | Max final alignment error (m) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy_name, metrics in policies.items():
        assert isinstance(metrics, dict)
        lines.append(
            f"| `{policy_name}` | {metrics['episode_count']} | {metrics['discrete_success_rate']:.3f} | {metrics['movement_command_count']} | {metrics['reached_movement_target_rate']:.3f} | {metrics['contact_command_count']} | {metrics['contact_command_rate']:.3f} | {metrics['max_final_alignment_error_m']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A contact command means the robot body touched a named rigid obstacle or exclusion proxy while pursuing that command; floor contact is excluded.",
            "- Reached-target rate tests whether the continuous body arrived within the declared tolerance before any recovery command.",
            "- A blocked discrete move is returned to the discrete result cell before the next command. This preserves trace alignment and is not presented as a recovery controller.",
            "- Restricted and worker cells are represented as rigid proxies solely to regression-test the command boundary; their geometry is not a physical human or site model.",
            "",
            "## Boundary",
            "",
            str(payload["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def _physics_comparison_svg(payload: dict[str, object]) -> str:
    policies = payload["policies"]
    assert isinstance(policies, dict)
    rows = []
    for policy_name, metrics in policies.items():
        assert isinstance(metrics, dict)
        rows.append((policy_name, metrics))
    width = 980
    height = 180 + 86 * len(rows)
    bar_width = 420
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">MuJoCo planar command replay comparison</title>',
        '<desc id="desc">Reached movement targets and contact command rates for each evaluated policy.</desc>',
        '<rect width="100%" height="100%" fill="#f7f8fa"/>',
        '<text x="48" y="52" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#17212b">MuJoCo planar command replay</text>',
        f'<text x="48" y="82" font-family="Arial, sans-serif" font-size="16" fill="#4c5967">{payload["scenario_count"]} fixed holdout scenarios | rigid contacts | headless continuous replay</text>',
        '<text x="410" y="118" font-family="Arial, sans-serif" font-size="13" fill="#4c5967">0%</text>',
        '<text x="820" y="118" font-family="Arial, sans-serif" font-size="13" text-anchor="end" fill="#4c5967">100%</text>',
    ]
    for index, (policy_name, metrics) in enumerate(rows):
        y = 150 + index * 86
        reached = float(metrics["reached_movement_target_rate"])
        contact = float(metrics["contact_command_rate"])
        svg.extend(
            [
                f'<text x="48" y="{y + 18}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#17212b">{html.escape(policy_name)}</text>',
                f'<text x="48" y="{y + 44}" font-family="Arial, sans-serif" font-size="13" fill="#4c5967">{metrics["movement_command_count"]} commands | {metrics["contact_command_count"]} contact commands</text>',
                f'<rect x="410" y="{y}" width="{bar_width}" height="20" rx="3" fill="#d9dee5"/>',
                f'<rect x="410" y="{y}" width="{bar_width * reached:.1f}" height="20" rx="3" fill="#087f8c"/>',
                f'<text x="842" y="{y + 15}" font-family="Arial, sans-serif" font-size="13" fill="#17212b">target {reached:.3f}</text>',
                f'<rect x="410" y="{y + 30}" width="{bar_width}" height="14" rx="3" fill="#e8ebef"/>',
                f'<rect x="410" y="{y + 30}" width="{bar_width * contact:.1f}" height="14" rx="3" fill="#d1495b"/>',
                f'<text x="842" y="{y + 42}" font-family="Arial, sans-serif" font-size="13" fill="#17212b">contact {contact:.3f}</text>',
            ]
        )
    svg.extend(
        [
            f'<line x1="48" y1="{height - 48}" x2="932" y2="{height - 48}" stroke="#c8ced6"/>',
            f'<text x="48" y="{height - 22}" font-family="Arial, sans-serif" font-size="12" fill="#596673">Synthetic rigid-body replay; not hardware, ROS, or physical-safety evidence.</text>',
            "</svg>",
        ]
    )
    return "\n".join(svg) + "\n"
