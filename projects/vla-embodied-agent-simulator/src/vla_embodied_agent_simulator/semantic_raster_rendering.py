from __future__ import annotations

from html import escape
from typing import Any

from .environment import GridWorldEnv, Position


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
    structured = evaluation["training"]
    raster = evaluation["semantic_raster_training"]
    policies = evaluation["policies"]
    structured_policy = policies["behavior_cloning_shielded"]
    raster_policy = policies["semantic_raster_mlp_shielded"]
    task_type = env.task.task_type if env.task else "unknown"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="540" viewBox="0 0 1000 540" role="img" aria-labelledby="title desc">
  <title id="title">Semantic-raster policy comparison</title>
  <desc id="desc">A fully observable synthetic construction grid rendered into semantic channels, with measured structured and raster policy results.</desc>
  <rect width="1000" height="540" fill="#f4f3ed"/>
  <rect width="1000" height="12" fill="#13221d"/>
  <text x="42" y="51" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">SEMANTIC RASTER / SYNTHETIC SIMULATOR STATE</text>
  <text x="42" y="86" font-family="Arial, sans-serif" font-size="27" font-weight="700" fill="#13221d">A neural baseline, retained because it underperforms</text>
  {''.join(cells)}
  <text x="430" y="135" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#267d6a">OBSERVATION CONTRACT</text>
  <text x="430" y="166" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#13221d">8 x 7 x 7 semantic channels + 6 globals</text>
  <text x="430" y="193" font-family="Arial, sans-serif" font-size="14" fill="#5f6e68">Task: {escape(task_type)} / fully observable / no camera pixels</text>
  <line x1="430" y1="220" x2="950" y2="220" stroke="#cad4cf"/>
  <text x="430" y="256" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">DISJOINT HOLDOUT</text>
  <text x="430" y="288" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#13221d">Engineered state + random forest</text>
  <text x="430" y="316" font-family="Arial, sans-serif" font-size="14" fill="#5f6e68">Action accuracy {structured['holdout_action_accuracy']:.3f} / shielded success {structured_policy['success_rate']:.3f}</text>
  <text x="430" y="354" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#13221d">Flattened raster + 64-unit MLP</text>
  <text x="430" y="382" font-family="Arial, sans-serif" font-size="14" fill="#5f6e68">Action accuracy {raster['holdout_action_accuracy']:.3f} / shielded success {raster_policy['success_rate']:.3f}</text>
  <rect x="430" y="412" width="520" height="78" rx="5" fill="#13221d"/>
  <text x="451" y="441" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e9b44c">INTERPRETATION</text>
  <text x="451" y="466" font-family="Arial, sans-serif" font-size="13" fill="#ffffff">The MLP sees semantic state, not images, and lacks a convolutional spatial bias.</text>
  <text x="451" y="484" font-family="Arial, sans-serif" font-size="13" fill="#ffffff">Its lower result is negative evidence, not a visual-policy capability claim.</text>
  <text x="42" y="512" font-family="Arial, sans-serif" font-size="12" fill="#5f6e68">Legend: A agent / X obstacle / R restricted / W worker / S slow / O object / Z named zone / red border current subgoal</text>
</svg>
"""
