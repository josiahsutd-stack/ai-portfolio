from __future__ import annotations

from html import escape
from typing import Any

from .environment import GridWorldEnv, Position
from .synthetic_rgb import render_synthetic_rgb_observation


def _rgb_thumbnail(
    env: GridWorldEnv,
    subgoal: Position,
    *,
    palette_name: str,
    origin_x: int,
    origin_y: int,
    scale: int = 8,
) -> str:
    image = render_synthetic_rgb_observation(env, subgoal, palette_name=palette_name)
    return "".join(
        f'<rect x="{origin_x + x * scale}" y="{origin_y + y * scale}" '
        f'width="{scale}" height="{scale}" fill="rgb({int(pixel[0])},{int(pixel[1])},{int(pixel[2])})"/>'
        for y, row in enumerate(image)
        for x, pixel in enumerate(row)
    )


def render_semantic_raster_svg(
    env: GridWorldEnv,
    subgoal: Position,
    evaluation: dict[str, Any],
) -> str:
    cell_size = 52
    grid_x = 42
    grid_y = 112
    cells: list[str] = []
    for y in range(7):
        for x in range(7):
            point = (x, y)
            fill = "#f8faf8"
            label = ""
            if x >= env.width or y >= env.height:
                fill = "#e5e9e6"
            elif point in env.obstacles:
                fill, label = "#26322e", "X"
            elif point in env.restricted_zones:
                fill, label = "#e76f51", "R"
            elif point in env.worker_zones:
                fill, label = "#e9b44c", "W"
            elif point in env.slow_zones:
                fill, label = "#d7e0dc", "S"
            elif point in env.objects.values():
                fill, label = "#58a58c", "O"
            elif point in env.zones.values():
                fill, label = "#7fa8bd", "Z"
            px = grid_x + x * cell_size
            py = grid_y + y * cell_size
            stroke = "#e85d3f" if point == subgoal else "#c9d3ce"
            stroke_width = 4 if point == subgoal else 1
            cells.append(
                f'<rect x="{px}" y="{py}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )
            if label:
                cells.append(
                    f'<text x="{px + cell_size / 2}" y="{py + 33}" text-anchor="middle" '
                    f'font-family="Arial, sans-serif" font-size="15" font-weight="700" '
                    f'fill="#13221d">{label}</text>'
                )
            if point == env.agent:
                cells.append(
                    f'<circle cx="{px + cell_size / 2}" cy="{py + cell_size / 2}" r="13" '
                    'fill="#ffffff" stroke="#267d6a" stroke-width="5"/>'
                )
    local_min_x = max(0, env.agent[0] - 2)
    local_max_x = min(6, env.agent[0] + 2)
    local_min_y = max(0, env.agent[1] - 2)
    local_max_y = min(6, env.agent[1] + 2)
    cells.append(
        f'<rect x="{grid_x + local_min_x * cell_size + 4}" '
        f'y="{grid_y + local_min_y * cell_size + 4}" '
        f'width="{(local_max_x - local_min_x + 1) * cell_size - 8}" '
        f'height="{(local_max_y - local_min_y + 1) * cell_size - 8}" '
        'fill="none" stroke="#267d6a" stroke-width="3" stroke-dasharray="8 6"/>'
    )
    structured = evaluation["training"]
    raster = evaluation["semantic_raster_training"]
    egocentric = evaluation["egocentric_training"]
    rgb = evaluation["synthetic_rgb_training"]
    policies = evaluation["policies"]
    structured_policy = policies["behavior_cloning_shielded"]
    raster_policy = policies["semantic_raster_mlp_shielded"]
    egocentric_policy = policies["egocentric_mlp_shielded"]
    rgb_policy = policies["synthetic_rgb_mlp_shielded"]
    rgb_shifted_policy = policies["synthetic_rgb_mlp_shifted_shielded"]
    task_type = env.task.task_type if env.task else "unknown"
    day_thumbnail = _rgb_thumbnail(
        env,
        subgoal,
        palette_name="day",
        origin_x=42,
        origin_y=548,
    )
    shifted_thumbnail = _rgb_thumbnail(
        env,
        subgoal,
        palette_name="worklight",
        origin_x=158,
        origin_y=548,
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="800" viewBox="0 0 1000 800" role="img" aria-labelledby="title desc">
  <title id="title">Construction-agent observation representation comparison</title>
  <desc id="desc">A synthetic construction grid, normal and shifted RGB crops, and measured engineered-state, semantic-raster, egocentric, and rendered-pixel policy results.</desc>
  <rect width="1000" height="800" fill="#f4f3ed"/>
  <rect width="1000" height="12" fill="#13221d"/>
  <text x="42" y="51" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">OBSERVATION REPRESENTATION STUDY / SYNTHETIC SIMULATOR STATE</text>
  <text x="42" y="86" font-family="Arial, sans-serif" font-size="27" font-weight="700" fill="#13221d">Representation choices expose performance and brittleness</text>
  {''.join(cells)}
  <text x="42" y="505" font-family="Arial, sans-serif" font-size="12" fill="#267d6a">Dashed outline: agent-centered 5 x 5 observation window</text>
  <text x="42" y="532" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#13221d">DAY RGB</text>
  <text x="158" y="532" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#13221d">UNSEEN WORK-LIGHT RGB</text>
  {day_thumbnail}
  {shifted_thumbnail}
  <text x="42" y="646" font-family="Arial, sans-serif" font-size="12" fill="#5f6e68">Actual 10 x 10 pixel inputs, enlarged with nearest-neighbor display.</text>
  <text x="430" y="128" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#267d6a">OBSERVATION CONTRACTS</text>
  <text x="430" y="158" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">World raster: 8 x 7 x 7 channels + 6 globals</text>
  <text x="430" y="184" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">Egocentric: 8 x 5 x 5 channels + 10 globals</text>
  <text x="430" y="210" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">RGB crop: 10 x 10 x 3 pixels + 10 globals</text>
  <text x="430" y="234" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Task: {escape(task_type)} / synthetic renderer / no physical camera</text>
  <line x1="430" y1="254" x2="950" y2="254" stroke="#cad4cf"/>
  <text x="430" y="282" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">SHARED 96-SCENARIO HOLDOUT</text>
  <text x="430" y="312" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">Engineered state + random forest</text>
  <text x="430" y="336" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Action accuracy {structured['holdout_action_accuracy']:.3f} / filtered success {structured_policy['success_rate']:.3f}</text>
  <text x="430" y="370" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">World-frame raster + 64-unit MLP</text>
  <text x="430" y="394" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Action accuracy {raster['holdout_action_accuracy']:.3f} / filtered success {raster_policy['success_rate']:.3f}</text>
  <text x="430" y="428" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">Egocentric local state + 64-unit MLP</text>
  <text x="430" y="452" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Action accuracy {egocentric['holdout_action_accuracy']:.3f} / filtered success {egocentric_policy['success_rate']:.3f} / {egocentric_policy['intervention_count']} interventions</text>
  <text x="430" y="486" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#13221d">Rendered RGB crop + 64-unit MLP</text>
  <text x="430" y="510" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Day: accuracy {rgb['standard_holdout_action_accuracy']:.3f} / filtered success {rgb_policy['success_rate']:.3f}</text>
  <text x="430" y="530" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Mean-pixel ablation: accuracy {rgb['pixel_ablated_holdout_action_accuracy']:.3f} / delta {rgb['standard_minus_pixel_ablated_accuracy']:.3f}</text>
  <text x="430" y="550" font-family="Arial, sans-serif" font-size="13" fill="#5f6e68">Unseen work-light: accuracy {rgb['shifted_holdout_action_accuracy']:.3f} / filtered success {rgb_shifted_policy['success_rate']:.3f}</text>
  <rect x="430" y="580" width="520" height="118" rx="5" fill="#13221d"/>
  <text x="451" y="608" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e9b44c">INTERPRETATION</text>
  <text x="451" y="633" font-family="Arial, sans-serif" font-size="13" fill="#ffffff">Pixel ablation confirms that image values contribute beyond task telemetry.</text>
  <text x="451" y="653" font-family="Arial, sans-serif" font-size="13" fill="#ffffff">The unseen palette shift exposes severe visual brittleness and filter dependence.</text>
  <text x="451" y="673" font-family="Arial, sans-serif" font-size="13" fill="#ffffff">Pixels still originate from privileged simulator state, not a physical camera.</text>
  <text x="42" y="766" font-family="Arial, sans-serif" font-size="12" fill="#5f6e68">Legend: A agent / X obstacle / R restricted / W worker / S slow / O object / Z named zone / red border current subgoal</text>
</svg>
"""
