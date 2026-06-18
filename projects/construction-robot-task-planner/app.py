from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import pandas as pd
import streamlit as st

from construction_robot_task_planner import GridMap, RobotTask, plan_robot_task
from shared.data import read_json

DATA_PATH = PROJECT_ROOT / "sample_data" / "site_tasks.json"

st.set_page_config(page_title="Construction Robot Task Planner", page_icon="AI", layout="wide")
st.title("Construction Robot Task Planner")
st.caption("Synthetic embodied AI demo for construction robot task planning and site navigation.")

payload = read_json(DATA_PATH)
site_map = GridMap.from_dict(payload["site_map"])
task_lookup = {task["task_id"]: task for task in payload["tasks"]}
task_id = st.selectbox("Robot task", list(task_lookup))
task = RobotTask.from_dict(task_lookup[task_id])
plan = plan_robot_task(site_map, task)

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Planned route")
    grid = [["." for _x in range(site_map.width)] for _y in range(site_map.height)]
    for x, y in site_map.obstacles:
        grid[y][x] = "X"
    for x, y in site_map.restricted_zones:
        grid[y][x] = "R"
    for x, y in site_map.slow_zones:
        grid[y][x] = "S"
    for step in plan["steps"]:
        grid[int(step["y"])][int(step["x"])] = "*"
    grid[task.start[1]][task.start[0]] = "A"
    grid[task.goal[1]][task.goal[0]] = "B"
    st.dataframe(pd.DataFrame(grid), use_container_width=True)
    st.caption("A=start, B=goal, X=obstacle, R=restricted, S=slow, *=planned route")

with right:
    st.subheader("Task")
    st.json(task_lookup[task_id])
    st.subheader("Risk estimate")
    st.json(plan["risk"])

st.subheader("Plan steps")
st.dataframe(plan["steps"], use_container_width=True)
