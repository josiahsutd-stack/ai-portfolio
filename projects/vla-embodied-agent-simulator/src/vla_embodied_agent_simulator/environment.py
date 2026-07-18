from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any

Position = tuple[int, int]

ACTIONS = [
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "pick",
    "drop",
    "inspect",
    "charge",
    "wait",
]

MOVE_DELTAS: dict[str, Position] = {
    "move_up": (0, -1),
    "move_down": (0, 1),
    "move_left": (-1, 0),
    "move_right": (1, 0),
}


@dataclass(frozen=True)
class TaskSpec:
    instruction: str
    task_type: str
    target_object: str | None = None
    target_zone: str | None = None
    success_action: str = "wait"


@dataclass(frozen=True)
class SiteScenario:
    scenario_id: str
    name: str
    instruction: str
    width: int
    height: int
    start: Position
    objects: dict[str, Position]
    zones: dict[str, Position]
    obstacles: set[Position] = field(default_factory=set)
    restricted_zones: set[Position] = field(default_factory=set)
    slow_zones: set[Position] = field(default_factory=set)
    worker_zones: set[Position] = field(default_factory=set)
    battery: float = 30.0
    max_steps: int = 60
    notes: str = ""


@dataclass(frozen=True)
class EpisodeStep:
    step: int
    action: str
    reward: float
    done: bool
    info: dict[str, Any]
    state: dict[str, Any]


@dataclass
class GridWorldEnv:
    width: int = 5
    height: int = 5
    agent: Position = (0, 0)
    carrying: str | None = None
    objects: dict[str, Position] = field(default_factory=lambda: {"red_object": (2, 1)})
    zones: dict[str, Position] = field(
        default_factory=lambda: {"blue_zone": (4, 4), "base": (0, 0)}
    )
    obstacles: set[Position] = field(default_factory=lambda: {(1, 1), (3, 2)})
    restricted_zones: set[Position] = field(default_factory=lambda: {(2, 2)})
    slow_zones: set[Position] = field(default_factory=set)
    worker_zones: set[Position] = field(default_factory=set)
    battery: float = 30.0
    max_steps: int = 60
    task: TaskSpec | None = None
    step_count: int = 0
    trace: list[EpisodeStep] = field(default_factory=list)
    scenario_id: str = "legacy_pick_and_place"
    scenario_name: str = "Legacy Pick And Place"
    _initial_config: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self._initial_config = self._snapshot_config()

    @classmethod
    def from_scenario(cls, scenario: SiteScenario) -> GridWorldEnv:
        env = cls()
        env.load_scenario(scenario)
        return env

    def load_scenario(self, scenario: SiteScenario) -> None:
        self.width = scenario.width
        self.height = scenario.height
        self.agent = scenario.start
        self.carrying = None
        self.objects = dict(scenario.objects)
        self.zones = dict(scenario.zones)
        self.obstacles = set(scenario.obstacles)
        self.restricted_zones = set(scenario.restricted_zones)
        self.slow_zones = set(scenario.slow_zones)
        self.worker_zones = set(scenario.worker_zones)
        self.battery = scenario.battery
        self.max_steps = scenario.max_steps
        self.task = parse_instruction(scenario.instruction, self)
        self.step_count = 0
        self.trace = []
        self.scenario_id = scenario.scenario_id
        self.scenario_name = scenario.name
        self._initial_config = self._snapshot_config()

    def clone(self) -> GridWorldEnv:
        env = GridWorldEnv(
            width=self.width,
            height=self.height,
            agent=self.agent,
            carrying=self.carrying,
            objects=dict(self.objects),
            zones=dict(self.zones),
            obstacles=set(self.obstacles),
            restricted_zones=set(self.restricted_zones),
            slow_zones=set(self.slow_zones),
            worker_zones=set(self.worker_zones),
            battery=self.battery,
            max_steps=self.max_steps,
            task=self.task,
            step_count=self.step_count,
            trace=list(self.trace),
            scenario_id=self.scenario_id,
            scenario_name=self.scenario_name,
        )
        env._initial_config = {
            **self._initial_config,
            "objects": dict(self._initial_config.get("objects", {})),
            "zones": dict(self._initial_config.get("zones", {})),
            "obstacles": set(self._initial_config.get("obstacles", set())),
            "restricted_zones": set(self._initial_config.get("restricted_zones", set())),
            "slow_zones": set(self._initial_config.get("slow_zones", set())),
            "worker_zones": set(self._initial_config.get("worker_zones", set())),
        }
        return env

    def reset(self, scenario: SiteScenario | None = None) -> dict[str, Any]:
        if scenario is not None:
            self.load_scenario(scenario)
            return self.state()
        config = self._initial_config
        self.width = int(config["width"])
        self.height = int(config["height"])
        self.agent = tuple(config["agent"])  # type: ignore[assignment]
        self.carrying = None
        self.objects = dict(config["objects"])
        self.zones = dict(config["zones"])
        self.obstacles = set(config["obstacles"])
        self.restricted_zones = set(config["restricted_zones"])
        self.slow_zones = set(config["slow_zones"])
        self.worker_zones = set(config["worker_zones"])
        self.battery = float(config["battery"])
        self.max_steps = int(config["max_steps"])
        self.task = config["task"]
        self.step_count = 0
        self.trace = []
        self.scenario_id = str(config["scenario_id"])
        self.scenario_name = str(config["scenario_name"])
        return self.state()

    def state(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "carrying": self.carrying,
            "objects": dict(self.objects),
            "zones": dict(self.zones),
            "obstacles": sorted(self.obstacles),
            "restricted_zones": sorted(self.restricted_zones),
            "slow_zones": sorted(self.slow_zones),
            "worker_zones": sorted(self.worker_zones),
            "battery": round(self.battery, 2),
            "step_count": self.step_count,
            "task": self.task.__dict__ if self.task else None,
            "scenario_id": self.scenario_id,
        }

    def action_mask(self) -> dict[str, bool]:
        return {action: self.is_action_safe(action)[0] for action in ACTIONS}

    def is_action_safe(self, action: str) -> tuple[bool, str]:
        if action not in ACTIONS:
            return False, "invalid_action"
        if action in MOVE_DELTAS:
            target = self._move_target(action)
            if not self._in_bounds(target):
                return False, "out_of_bounds"
            if target in self.obstacles:
                return False, "obstacle"
            if target in self.restricted_zones:
                return False, "restricted_zone"
            if target in self.worker_zones:
                return False, "worker_proximity"
        if self.battery <= 0 and action != "charge":
            return False, "battery_depleted"
        return True, "safe"

    def step(self, action: str) -> tuple[dict[str, Any], float, bool, dict[str, Any]]:
        safe, reason = self.is_action_safe(action)
        if not safe:
            info = {"error": "unsafe_or_blocked_move", "reason": reason}
            self._record_step(action, -1.0, False, info)
            return self.state(), -1.0, False, info

        self.step_count += 1
        reward = -0.1
        done = False
        info: dict[str, Any] = {"safety": reason}

        if action in MOVE_DELTAS:
            self.agent = self._move_target(action)
            self.battery -= 1.0
            if self.agent in self.slow_zones:
                reward -= 0.2
                info["slow_zone"] = True
        elif action == "pick":
            reward, info = self._pick()
        elif action == "drop":
            reward, done, info = self._drop()
        elif action == "inspect":
            reward, done, info = self._inspect()
        elif action == "charge":
            reward, done, info = self._charge()
        elif action == "wait":
            self.battery -= 0.2

        if self.step_count >= self.max_steps and not done:
            done = True
            info["timeout"] = True
            reward -= 1.0
        self._record_step(action, reward, done, info)
        return self.state(), reward, done, info

    def render_text(self) -> str:
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                point = (x, y)
                if point == self.agent:
                    row.append("A")
                elif point in self.obstacles:
                    row.append("X")
                elif point in self.restricted_zones:
                    row.append("R")
                elif point in self.worker_zones:
                    row.append("W")
                elif point in self.objects.values():
                    row.append("O")
                elif point in self.slow_zones:
                    row.append("S")
                elif point in self.zones.values():
                    row.append("Z")
                else:
                    row.append(".")
            rows.append(" ".join(row))
        return "\n".join(rows)

    def safe_neighbors(self, position: Position) -> list[tuple[str, Position, float]]:
        neighbors: list[tuple[str, Position, float]] = []
        for action, delta in MOVE_DELTAS.items():
            target = (position[0] + delta[0], position[1] + delta[1])
            if (
                self._in_bounds(target)
                and target not in self.obstacles
                and target not in self.restricted_zones
                and target not in self.worker_zones
            ):
                cost = 1.4 if target in self.slow_zones else 1.0
                neighbors.append((action, target, cost))
        return neighbors

    def _snapshot_config(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "agent": self.agent,
            "objects": dict(self.objects),
            "zones": dict(self.zones),
            "obstacles": set(self.obstacles),
            "restricted_zones": set(self.restricted_zones),
            "slow_zones": set(self.slow_zones),
            "worker_zones": set(self.worker_zones),
            "battery": self.battery,
            "max_steps": self.max_steps,
            "task": self.task,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
        }

    def _move_target(self, action: str) -> Position:
        delta = MOVE_DELTAS[action]
        return self.agent[0] + delta[0], self.agent[1] + delta[1]

    def _in_bounds(self, position: Position) -> bool:
        return 0 <= position[0] < self.width and 0 <= position[1] < self.height

    def _pick(self) -> tuple[float, dict[str, Any]]:
        for name, location in list(self.objects.items()):
            if location == self.agent:
                self.carrying = name
                del self.objects[name]
                return 1.0, {"picked": name, "safety": "safe"}
        return -0.5, {"error": "nothing_to_pick", "safety": "safe"}

    def _drop(self) -> tuple[float, bool, dict[str, Any]]:
        target_zone = self.task.target_zone if self.task else "blue_zone"
        if self.carrying and self.agent == self.zones.get(target_zone):
            dropped = self.carrying
            self.carrying = None
            return 5.0, True, {"success": "task_complete", "dropped": dropped}
        return -0.5, False, {"error": "drop_not_allowed", "safety": "safe"}

    def _inspect(self) -> tuple[float, bool, dict[str, Any]]:
        target_zone = self.task.target_zone if self.task else None
        if target_zone and self.agent == self.zones.get(target_zone):
            return 3.0, True, {"success": "inspection_complete"}
        return 0.2, False, {"inspection": "local_observation"}

    def _charge(self) -> tuple[float, bool, dict[str, Any]]:
        target_zone = self.task.target_zone if self.task else "base"
        charging_points = {
            self.zones.get("base"),
            self.zones.get("charging_dock"),
        }
        if self.task and self.task.task_type == "charge":
            charging_points.add(self.zones.get(target_zone))
        if self.agent in charging_points:
            done = self.task.task_type == "charge" if self.task else False
            if done:
                self.battery = max(self.battery, 30.0)
                return 2.0, True, {"success": "charged"}
            if self.battery < 30.0:
                self.battery = 30.0
                return 0.5, False, {"event": "battery_recovered", "safety": "safe"}
            return -0.2, False, {"error": "charge_not_needed", "safety": "safe"}
        return -0.5, False, {"error": "not_at_charger"}

    def _record_step(self, action: str, reward: float, done: bool, info: dict[str, Any]) -> None:
        self.trace.append(
            EpisodeStep(
                step=len(self.trace) + 1,
                action=action,
                reward=round(reward, 3),
                done=done,
                info=dict(info),
                state=self.state(),
            )
        )


def default_construction_scenarios() -> list[SiteScenario]:
    return [
        SiteScenario(
            scenario_id="drywall_delivery",
            name="Drywall Delivery To Level 2 Staging",
            instruction="Deliver the drywall stack to the level 2 staging area.",
            width=7,
            height=6,
            start=(0, 0),
            objects={"drywall_stack": (1, 4)},
            zones={"level_2_staging": (6, 4), "charging_dock": (0, 0), "base": (0, 0)},
            obstacles={(2, 1), (2, 2), (3, 4), (4, 3)},
            restricted_zones={(3, 3)},
            slow_zones={(1, 3), (5, 4)},
            worker_zones={(3, 1)},
            battery=28.0,
            notes="Material movement with worker and restricted-zone avoidance.",
        ),
        SiteScenario(
            scenario_id="corridor_inspection",
            name="Blocked Corridor Inspection",
            instruction="Inspect the blocked corridor near the north lift lobby.",
            width=7,
            height=5,
            start=(0, 4),
            objects={},
            zones={"north_lift_lobby": (5, 1), "charging_dock": (0, 4), "base": (0, 4)},
            obstacles={(2, 3), (3, 3), (4, 3)},
            restricted_zones={(3, 2)},
            slow_zones={(1, 4), (5, 2)},
            worker_zones={(4, 1)},
            battery=20.0,
            notes="Inspection task with a worker zone near the goal.",
        ),
        SiteScenario(
            scenario_id="low_battery_return",
            name="Low Battery Return To Charger",
            instruction="Return to the charging dock before continuing work.",
            width=6,
            height=5,
            start=(5, 4),
            objects={},
            zones={"charging_dock": (0, 0), "base": (0, 0)},
            obstacles={(3, 2), (2, 2)},
            restricted_zones={(1, 3)},
            slow_zones={(4, 3), (1, 1)},
            worker_zones={(4, 1)},
            battery=9.0,
            notes="Recovery behavior under battery constraints.",
        ),
    ]


def parse_instruction(instruction: str, env: GridWorldEnv) -> TaskSpec:
    text = instruction.lower()
    if "inspect" in text:
        return TaskSpec(
            instruction=instruction,
            task_type="inspect",
            target_zone=_match_zone(text, env, fallback="north_lift_lobby") or "inspection_point",
            success_action="inspect",
        )
    if any(term in text for term in ["charge", "charging", "dock", "return"]):
        return TaskSpec(
            instruction=instruction,
            task_type="charge",
            target_zone=_match_zone(text, env, fallback="charging_dock") or "base",
            success_action="charge",
        )
    if any(term in text for term in ["deliver", "move", "bring", "pick up"]):
        return TaskSpec(
            instruction=instruction,
            task_type="deliver",
            target_object=_match_object(text, env) or next(iter(env.objects), None),
            target_zone=_match_zone(text, env, fallback="blue_zone") or next(iter(env.zones), None),
            success_action="drop",
        )
    if "red" in text and "blue" in text:
        return TaskSpec(
            instruction=instruction,
            task_type="deliver",
            target_object="red_object",
            target_zone="blue_zone",
            success_action="drop",
        )
    return TaskSpec(instruction=instruction, task_type="wait", success_action="wait")


def plan_from_instruction(instruction: str, env: GridWorldEnv) -> list[str]:
    task = parse_instruction(instruction, env)
    env.task = task
    if task.task_type == "deliver" and task.target_object and task.target_zone:
        object_position = env.objects.get(task.target_object)
        zone_position = env.zones.get(task.target_zone)
        if object_position is None or zone_position is None:
            return ["wait"]
        return [
            *shortest_path_actions(env, env.agent, object_position),
            "pick",
            *shortest_path_actions(env, object_position, zone_position),
            "drop",
        ]
    if task.task_type == "inspect" and task.target_zone:
        target = env.zones.get(task.target_zone)
        return [*shortest_path_actions(env, env.agent, target), "inspect"] if target else ["wait"]
    if task.task_type == "charge" and task.target_zone:
        target = env.zones.get(task.target_zone)
        return [*shortest_path_actions(env, env.agent, target), "charge"] if target else ["wait"]
    return ["wait"]


def shortest_path_actions(env: GridWorldEnv, start: Position, goal: Position | None) -> list[str]:
    if goal is None or start == goal:
        return []
    frontier: list[tuple[float, int, Position, list[str], float]] = [(0.0, 0, start, [], 0.0)]
    best_costs: dict[Position, float] = {start: 0.0}
    counter = 0
    while frontier:
        _priority, _counter, position, actions, cost = heapq.heappop(frontier)
        if position == goal:
            return actions
        if cost > best_costs.get(position, float("inf")):
            continue
        for action, neighbor, step_cost in env.safe_neighbors(position):
            next_cost = cost + step_cost
            if next_cost < best_costs.get(neighbor, float("inf")):
                best_costs[neighbor] = next_cost
                counter += 1
                priority = next_cost + _manhattan(neighbor, goal) * 0.01
                heapq.heappush(
                    frontier,
                    (priority, counter, neighbor, [*actions, action], next_cost),
                )
    return []


def _match_object(text: str, env: GridWorldEnv) -> str | None:
    for name in env.objects:
        normalized = name.replace("_", " ")
        if normalized in text or any(part in text for part in normalized.split()):
            return name
    return None


def _match_zone(text: str, env: GridWorldEnv, *, fallback: str) -> str | None:
    for name in env.zones:
        normalized = name.replace("_", " ")
        if normalized in text or all(part in text for part in normalized.split() if part != "zone"):
            return name
    return fallback if fallback in env.zones else None


def _manhattan(start: Position, goal: Position) -> int:
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])
