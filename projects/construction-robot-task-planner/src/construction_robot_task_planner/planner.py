from __future__ import annotations

import heapq
from dataclasses import asdict, dataclass
from typing import Any

Point = tuple[int, int]


@dataclass(frozen=True)
class GridMap:
    width: int
    height: int
    obstacles: set[Point]
    restricted_zones: set[Point]
    slow_zones: set[Point]
    charging_stations: set[Point]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> GridMap:
        return cls(
            width=int(payload["width"]),
            height=int(payload["height"]),
            obstacles={tuple(item) for item in payload.get("obstacles", [])},
            restricted_zones={tuple(item) for item in payload.get("restricted_zones", [])},
            slow_zones={tuple(item) for item in payload.get("slow_zones", [])},
            charging_stations={tuple(item) for item in payload.get("charging_stations", [])},
        )


@dataclass(frozen=True)
class RobotTask:
    task_id: str
    robot_type: str
    start: Point
    goal: Point
    payload_kg: float
    battery_pct: float
    priority: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RobotTask:
        return cls(
            task_id=str(payload["task_id"]),
            robot_type=str(payload["robot_type"]),
            start=tuple(payload["start"]),
            goal=tuple(payload["goal"]),
            payload_kg=float(payload.get("payload_kg", 0)),
            battery_pct=float(payload.get("battery_pct", 100)),
            priority=str(payload.get("priority", "medium")),
        )


@dataclass(frozen=True)
class PlanStep:
    index: int
    x: int
    y: int
    action: str
    note: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _neighbors(point: Point, site_map: GridMap) -> list[Point]:
    x, y = point
    candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [
        item
        for item in candidates
        if 0 <= item[0] < site_map.width
        and 0 <= item[1] < site_map.height
        and item not in site_map.obstacles
    ]


def _heuristic(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _move_cost(point: Point, site_map: GridMap) -> float:
    if point in site_map.restricted_zones:
        return 8.0
    if point in site_map.slow_zones:
        return 2.4
    return 1.0


def _reconstruct(came_from: dict[Point, Point], current: Point) -> list[Point]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))


def _a_star(site_map: GridMap, start: Point, goal: Point) -> list[Point]:
    if start in site_map.obstacles or goal in site_map.obstacles:
        raise ValueError("Start or goal is blocked by an obstacle.")
    queue: list[tuple[float, Point]] = [(0, start)]
    came_from: dict[Point, Point] = {}
    cost_so_far = {start: 0.0}
    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            return _reconstruct(came_from, current)
        for next_point in _neighbors(current, site_map):
            new_cost = cost_so_far[current] + _move_cost(next_point, site_map)
            if next_point not in cost_so_far or new_cost < cost_so_far[next_point]:
                cost_so_far[next_point] = new_cost
                priority = new_cost + _heuristic(next_point, goal)
                heapq.heappush(queue, (priority, next_point))
                came_from[next_point] = current
    raise ValueError("No feasible route found for the robot task.")


def estimate_plan_risk(site_map: GridMap, task: RobotTask, path: list[Point]) -> dict[str, object]:
    restricted_steps = sum(1 for point in path if point in site_map.restricted_zones)
    slow_steps = sum(1 for point in path if point in site_map.slow_zones)
    battery_required = len(path) * 1.8 + task.payload_kg * 0.06
    risks: list[str] = []
    if restricted_steps:
        risks.append("route touches restricted/high coordination zones")
    if task.battery_pct < battery_required + 15:
        risks.append("battery margin is low for task distance and payload")
    if task.payload_kg > 60:
        risks.append("payload requires speed limiting and stability checks")
    if not risks:
        risks.append("no major synthetic planning risks detected")
    return {
        "path_length": len(path),
        "restricted_steps": restricted_steps,
        "slow_zone_steps": slow_steps,
        "battery_required_estimate": round(battery_required, 1),
        "battery_margin": round(task.battery_pct - battery_required, 1),
        "risks": risks,
    }


def plan_robot_task(site_map: GridMap, task: RobotTask) -> dict[str, object]:
    path = _a_star(site_map, task.start, task.goal)
    steps = []
    for index, point in enumerate(path):
        if point == task.start:
            action = "start"
        elif point == task.goal:
            action = "arrive"
        elif point in site_map.slow_zones:
            action = "slow_move"
        elif point in site_map.restricted_zones:
            action = "cautious_crossing"
        else:
            action = "move"
        note = (
            "reduce speed and request human awareness"
            if action in {"slow_move", "cautious_crossing"}
            else ""
        )
        steps.append(PlanStep(index=index, x=point[0], y=point[1], action=action, note=note))
    return {
        "task_id": task.task_id,
        "robot_type": task.robot_type,
        "steps": [step.to_dict() for step in steps],
        "risk": estimate_plan_risk(site_map, task, path),
    }
