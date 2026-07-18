from __future__ import annotations

from html import escape

from .models import CandidateAssessment, SiteScenario

COLORS = ("#e85d3f", "#e9a23b", "#2f7d6d", "#5b6da8")


def _plan_group(
    scenario: SiteScenario,
    assessment: CandidateAssessment,
    x: float,
    y: float,
    width: float,
    height: float,
    show_labels: bool = True,
) -> str:
    padding = 20
    scale = min(
        (width - 2 * padding) / scenario.site_width_m,
        (height - 2 * padding) / scenario.site_depth_m,
    )
    plan_width = scenario.site_width_m * scale
    plan_height = scenario.site_depth_m * scale
    origin_x = x + (width - plan_width) / 2
    origin_y = y + (height - plan_height) / 2

    def sx(value: float) -> float:
        return origin_x + value * scale

    def sy(value: float) -> float:
        return origin_y + plan_height - value * scale

    parts = [
        f'<rect x="{origin_x:.1f}" y="{origin_y:.1f}" width="{plan_width:.1f}" height="{plan_height:.1f}" fill="#f7f5ef" stroke="#17231f" stroke-width="2"/>',
    ]
    envelope = scenario.buildable_bounds
    parts.append(
        f'<rect x="{sx(envelope.x):.1f}" y="{sy(envelope.y2):.1f}" width="{envelope.width * scale:.1f}" height="{envelope.depth * scale:.1f}" fill="none" stroke="#8d9a91" stroke-dasharray="7 5" stroke-width="1.5"/>'
    )
    for index, mass in enumerate(assessment.candidate.masses):
        rect = mass.footprint
        color = COLORS[index % len(COLORS)]
        parts.append(
            f'<rect x="{sx(rect.x):.1f}" y="{sy(rect.y2):.1f}" width="{rect.width * scale:.1f}" height="{rect.depth * scale:.1f}" fill="{color}" fill-opacity="0.88" stroke="#17231f" stroke-width="1.5"/>'
        )
        if show_labels:
            parts.append(
                f'<text x="{sx(rect.center.x):.1f}" y="{sy(rect.center.y):.1f}" text-anchor="middle" dominant-baseline="middle" font-size="12" font-weight="700" fill="#ffffff">{escape(mass.label)} · {mass.floors}F</text>'
            )
    for point, label, color in (
        (scenario.ingress, "IN", "#2f7d6d"),
        (scenario.egress, "OUT", "#5b6da8"),
    ):
        parts.append(
            f'<circle cx="{sx(point.x):.1f}" cy="{sy(point.y):.1f}" r="7" fill="{color}" stroke="#ffffff" stroke-width="2"/>'
        )
        if show_labels:
            parts.append(
                f'<text x="{sx(point.x) + 10:.1f}" y="{sy(point.y) - 9:.1f}" font-size="10" font-weight="700" fill="#17231f">{label}</text>'
            )
    return "".join(parts)


def _iso_point(
    x: float, y: float, origin_x: float, origin_y: float, scale: float
) -> tuple[float, float]:
    return origin_x + (x - y) * scale, origin_y + (x + y) * scale * 0.48


def _polygon(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def _isometric_group(
    scenario: SiteScenario,
    assessment: CandidateAssessment,
    origin_x: float,
    origin_y: float,
    scale: float,
) -> str:
    parts: list[str] = []
    site_points = [
        _iso_point(0, 0, origin_x, origin_y, scale),
        _iso_point(scenario.site_width_m, 0, origin_x, origin_y, scale),
        _iso_point(scenario.site_width_m, scenario.site_depth_m, origin_x, origin_y, scale),
        _iso_point(0, scenario.site_depth_m, origin_x, origin_y, scale),
    ]
    parts.append(
        f'<polygon points="{_polygon(site_points)}" fill="#eef2ed" stroke="#86938b" stroke-width="1.5"/>'
    )
    ordered = sorted(
        assessment.candidate.masses,
        key=lambda mass: mass.footprint.x + mass.footprint.y,
    )
    for index, mass in enumerate(ordered):
        rect = mass.footprint
        base = [
            _iso_point(rect.x, rect.y, origin_x, origin_y, scale),
            _iso_point(rect.x2, rect.y, origin_x, origin_y, scale),
            _iso_point(rect.x2, rect.y2, origin_x, origin_y, scale),
            _iso_point(rect.x, rect.y2, origin_x, origin_y, scale),
        ]
        rise = mass.floors * scenario.floor_to_floor_m * 1.45
        top = [(px, py - rise) for px, py in base]
        color = COLORS[index % len(COLORS)]
        parts.extend(
            [
                f'<polygon points="{_polygon([base[1], base[2], top[2], top[1]])}" fill="#263d35" fill-opacity="0.78"/>',
                f'<polygon points="{_polygon([base[2], base[3], top[3], top[2]])}" fill="#17231f" fill-opacity="0.70"/>',
                f'<polygon points="{_polygon(top)}" fill="{color}" stroke="#17231f" stroke-width="1.1"/>',
            ]
        )
    return "".join(parts)


def render_candidate_svg(scenario: SiteScenario, assessment: CandidateAssessment) -> str:
    metrics = assessment.metrics
    status = "FEASIBLE" if assessment.feasible else "INFEASIBLE"
    status_color = "#2f7d6d" if assessment.feasible else "#b83a2f"
    plan = _plan_group(scenario, assessment, 30, 125, 510, 470)
    iso_scale = min(5.0, 300 / max(scenario.site_width_m, scenario.site_depth_m))
    iso = _isometric_group(scenario, assessment, 860, 215, iso_scale)
    metric_items = [
        ("GFA", f"{metrics['gfa_m2']:.0f} m2"),
        ("Target error", f"{metrics['gfa_error_fraction'] * 100:.1f}%"),
        ("Coverage", f"{metrics['coverage'] * 100:.1f}%"),
        ("Solar proxy", f"{metrics['solar']:.3f}"),
        ("Daylight proxy", f"{metrics['daylight']:.3f}"),
        ("Wind proxy", f"{metrics['wind']:.3f}"),
    ]
    cards = []
    for index, (label, value) in enumerate(metric_items):
        column = index % 3
        row = index // 3
        x = 620 + column * 180
        y = 445 + row * 78
        cards.append(
            f'<rect x="{x}" y="{y}" width="162" height="62" rx="4" fill="#ffffff" stroke="#d9ded9"/>'
            f'<text x="{x + 12}" y="{y + 22}" font-size="11" fill="#66736c">{escape(label)}</text>'
            f'<text x="{x + 12}" y="{y + 46}" font-size="18" font-weight="700" fill="#17231f">{escape(value)}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img" aria-labelledby="title desc">
  <title id="title">{escape(scenario.name)} massing option {escape(assessment.candidate.candidate_id)}</title>
  <desc id="desc">Generated plan and isometric diagram from synthetic project constraints.</desc>
  <rect width="1200" height="650" fill="#f4f1e9"/>
  <text x="34" y="44" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#e85d3f">CONSTRAINT-AWARE MASSING · SYNTHETIC SCENARIO</text>
  <text x="34" y="80" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#17231f">{escape(scenario.name)}</text>
  <text x="34" y="106" font-family="Arial, sans-serif" font-size="14" fill="#56645d">{escape(assessment.candidate.typology.replace('_', ' ').title())} · {escape(assessment.candidate.candidate_id)}</text>
  <rect x="1020" y="34" width="145" height="34" rx="3" fill="{status_color}"/>
  <text x="1092" y="56" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#ffffff">{status}</text>
  <g font-family="Arial, sans-serif">{plan}</g>
  <text x="620" y="148" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#66736c">MASSING STUDY</text>
  <g>{iso}</g>
  <g font-family="Arial, sans-serif">{''.join(cards)}</g>
  <text x="34" y="628" font-family="Arial, sans-serif" font-size="11" fill="#66736c">Proxy analysis only. Not code certification, detailed egress analysis, daylight simulation, CFD, structure, or constructability validation.</text>
</svg>"""


def render_comparison_svg(scenario: SiteScenario, assessments: list[CandidateAssessment]) -> str:
    cards: list[str] = []
    for index, assessment in enumerate(assessments[:3]):
        x = 25 + index * 390
        cards.append(
            f'<rect x="{x}" y="80" width="365" height="420" rx="5" fill="#ffffff" stroke="#d7ddd8"/>'
            f'<text x="{x + 18}" y="112" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">OPTION {index + 1:02d}</text>'
            f'<text x="{x + 18}" y="140" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#17231f">{escape(assessment.candidate.typology.replace("_", " ").title())}</text>'
            f'<text x="{x + 18}" y="164" font-family="Arial, sans-serif" font-size="12" fill="#647169">Utility {assessment.utility_score:.3f} · GFA error {assessment.metrics["gfa_error_fraction"] * 100:.1f}%</text>'
            + _plan_group(scenario, assessment, x + 12, 178, 341, 270, show_labels=False)
            + f'<text x="{x + 18}" y="476" font-family="Arial, sans-serif" font-size="11" fill="#647169">Solar {assessment.metrics["solar"]:.3f} · Daylight {assessment.metrics["daylight"]:.3f} · Wind {assessment.metrics["wind"]:.3f}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="535" viewBox="0 0 1200 535" role="img" aria-labelledby="title">
  <title id="title">Pareto option comparison for {escape(scenario.name)}</title>
  <rect width="1200" height="535" fill="#eef2ed"/>
  <text x="25" y="34" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#2f7d6d">PARETO OPTION COMPARISON · SYNTHETIC SCENARIO</text>
  <text x="25" y="61" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#17231f">{escape(scenario.name)}</text>
  {''.join(cards)}
</svg>"""
