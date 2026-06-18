import pytest
from construction_robot_task_planner import GridMap, RobotTask, plan_robot_task


def test_robot_planner_finds_route_around_obstacle() -> None:
    site_map = GridMap(
        width=5,
        height=5,
        obstacles={(1, 0), (1, 1), (1, 2)},
        restricted_zones=set(),
        slow_zones={(2, 3)},
        charging_stations={(0, 0)},
    )
    task = RobotTask(
        task_id="T-1",
        robot_type="material_runner",
        start=(0, 0),
        goal=(4, 4),
        payload_kg=10,
        battery_pct=80,
        priority="high",
    )

    plan = plan_robot_task(site_map, task)

    assert plan["steps"][0]["action"] == "start"
    assert plan["steps"][-1]["action"] == "arrive"
    assert plan["risk"]["path_length"] > 0


def test_robot_planner_rejects_blocked_start() -> None:
    site_map = GridMap(
        width=3,
        height=3,
        obstacles={(0, 0)},
        restricted_zones=set(),
        slow_zones=set(),
        charging_stations=set(),
    )
    task = RobotTask("T-2", "scanner", (0, 0), (2, 2), 0, 90, "low")

    with pytest.raises(ValueError):
        plan_robot_task(site_map, task)
