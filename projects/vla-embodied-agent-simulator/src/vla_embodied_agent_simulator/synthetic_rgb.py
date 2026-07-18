from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from .environment import GridWorldEnv, Position

RGB_WINDOW_SIZE = 5
RGB_RADIUS = RGB_WINDOW_SIZE // 2
RGB_PIXELS_PER_CELL = 2
RGB_IMAGE_SIZE = RGB_WINDOW_SIZE * RGB_PIXELS_PER_CELL

RGB_PALETTES: dict[str, dict[str, tuple[int, int, int]]] = {
    "day": {
        "floor": (220, 226, 218),
        "out_of_bounds": (48, 55, 58),
        "obstacle": (39, 49, 46),
        "restricted_zone": (218, 88, 65),
        "worker_zone": (235, 179, 67),
        "slow_zone": (154, 178, 169),
        "object": (65, 145, 121),
        "named_zone": (78, 132, 164),
        "subgoal": (238, 241, 238),
        "agent": (250, 250, 248),
    },
    "overcast": {
        "floor": (178, 186, 183),
        "out_of_bounds": (31, 35, 40),
        "obstacle": (58, 61, 68),
        "restricted_zone": (177, 74, 88),
        "worker_zone": (195, 151, 76),
        "slow_zone": (123, 143, 151),
        "object": (53, 124, 117),
        "named_zone": (88, 115, 151),
        "subgoal": (221, 224, 228),
        "agent": (245, 244, 238),
    },
    "worklight": {
        "floor": (95, 83, 61),
        "out_of_bounds": (16, 20, 29),
        "obstacle": (64, 52, 48),
        "restricted_zone": (204, 48, 98),
        "worker_zone": (232, 219, 120),
        "slow_zone": (87, 111, 118),
        "object": (41, 173, 157),
        "named_zone": (123, 93, 176),
        "subgoal": (252, 221, 149),
        "agent": (228, 246, 255),
    },
}


def render_synthetic_rgb_observation(
    env: GridWorldEnv,
    subgoal: Position,
    *,
    palette_name: str = "day",
) -> np.ndarray:
    palette = _palette(palette_name)
    image = np.zeros((RGB_IMAGE_SIZE, RGB_IMAGE_SIZE, 3), dtype=np.uint8)
    offsets = range(-RGB_RADIUS, RGB_RADIUS + 1)
    for local_y, dy in enumerate(offsets):
        for local_x, dx in enumerate(offsets):
            point = env.agent[0] + dx, env.agent[1] + dy
            category = _cell_category(env, point)
            color = palette[category]
            y0 = local_y * RGB_PIXELS_PER_CELL
            x0 = local_x * RGB_PIXELS_PER_CELL
            image[
                y0 : y0 + RGB_PIXELS_PER_CELL,
                x0 : x0 + RGB_PIXELS_PER_CELL,
            ] = color
            if point == subgoal:
                image[y0, x0 : x0 + RGB_PIXELS_PER_CELL] = palette["subgoal"]
            if point == env.agent:
                image[
                    y0 : y0 + RGB_PIXELS_PER_CELL,
                    x0 : x0 + RGB_PIXELS_PER_CELL,
                ] = palette["agent"]
    return image


def _palette(name: str) -> Mapping[str, tuple[int, int, int]]:
    try:
        return RGB_PALETTES[name]
    except KeyError as exc:
        available = ", ".join(sorted(RGB_PALETTES))
        raise ValueError(f"unknown RGB palette `{name}`; choose one of {available}") from exc


def _cell_category(env: GridWorldEnv, point: Position) -> str:
    if not (0 <= point[0] < env.width and 0 <= point[1] < env.height):
        return "out_of_bounds"
    if point in env.obstacles:
        return "obstacle"
    if point in env.restricted_zones:
        return "restricted_zone"
    if point in env.worker_zones:
        return "worker_zone"
    if point in env.slow_zones:
        return "slow_zone"
    if point in env.objects.values():
        return "object"
    if point in env.zones.values():
        return "named_zone"
    return "floor"
