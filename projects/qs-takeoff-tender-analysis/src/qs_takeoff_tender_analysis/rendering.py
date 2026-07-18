from __future__ import annotations

from html import escape

from .models import CostEstimate, FloorPlan, TakeoffResult, TenderAnalysis
from .takeoff import classify_wall_segments

INK = "#17231f"
MUTED = "#66736c"
PAPER = "#f4f1e9"
ACCENT = "#e85d3f"
GREEN = "#2f7d6d"
BLUE = "#426b8f"
GOLD = "#d49336"


def render_floor_plan_svg(plan: FloorPlan, takeoff: TakeoffResult) -> str:
    min_x = min(room.x for room in plan.rooms)
    min_y = min(room.y for room in plan.rooms)
    max_x = max(room.x2 for room in plan.rooms)
    max_y = max(room.y2 for room in plan.rooms)
    width_units = max_x - min_x
    depth_units = max_y - min_y
    drawing_x, drawing_y, drawing_w, drawing_h = 50.0, 125.0, 650.0, 445.0
    scale = min(drawing_w / width_units, drawing_h / depth_units) * 0.88
    origin_x = drawing_x + (drawing_w - width_units * scale) / 2 - min_x * scale
    origin_y = drawing_y + (drawing_h - depth_units * scale) / 2 + max_y * scale

    def sx(value: float) -> float:
        return origin_x + value * scale

    def sy(value: float) -> float:
        return origin_y - value * scale

    room_parts: list[str] = []
    fills = ("#e7eee9", "#e8edf2", "#f1e9dc", "#eee8ed")
    for index, room in enumerate(plan.rooms):
        room_parts.append(
            f'<rect x="{sx(room.x):.1f}" y="{sy(room.y2):.1f}" width="{room.width * scale:.1f}" height="{room.depth * scale:.1f}" fill="{fills[index % len(fills)]}" stroke="none"/>'
            f'<text x="{sx((room.x + room.x2) / 2):.1f}" y="{sy((room.y + room.y2) / 2):.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">{escape(room.name)}</text>'
            f'<text x="{sx((room.x + room.x2) / 2):.1f}" y="{sy((room.y + room.y2) / 2) + 19:.1f}" text-anchor="middle" font-size="11" fill="{MUTED}">{room.area_units2 * plan.scale_m_per_unit**2:.1f} m2</text>'
        )
    wall_parts: list[str] = []
    for segment in classify_wall_segments(plan):
        stroke = INK if segment.wall_type == "external" else BLUE
        stroke_width = 5 if segment.wall_type == "external" else 3
        if segment.orientation == "horizontal":
            x1, y1, x2, y2 = (
                sx(segment.start),
                sy(segment.coordinate),
                sx(segment.end),
                sy(segment.coordinate),
            )
        else:
            x1, y1, x2, y2 = (
                sx(segment.coordinate),
                sy(segment.start),
                sx(segment.coordinate),
                sy(segment.end),
            )
        wall_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-linecap="square"/>'
        )
    opening_parts: list[str] = []
    for opening in plan.openings:
        color = ACCENT if opening.kind == "door" else GREEN
        if opening.orientation == "horizontal":
            x1, y1, x2, y2 = sx(opening.x1), sy(opening.y1), sx(opening.x2), sy(opening.y2)
        else:
            x1, y1, x2, y2 = sx(opening.x1), sy(opening.y1), sx(opening.x2), sy(opening.y2)
        opening_parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ffffff" stroke-width="8"/>'
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="4"/>'
        )
    quantity_map = takeoff.quantity_map()
    metrics = [
        ("Floor area", f"{quantity_map['QTO-FLR']:.1f} m2"),
        ("External wall", f"{quantity_map['QTO-EXT']:.1f} m2"),
        ("Partitions", f"{quantity_map['QTO-INT']:.1f} m2"),
        ("Slab", f"{quantity_map['QTO-SLB']:.1f} m3"),
        ("Doors", f"{quantity_map['QTO-DOR']:.0f} ea"),
        ("Windows", f"{quantity_map['QTO-WIN']:.1f} m2"),
    ]
    metric_parts: list[str] = []
    for index, (label, value) in enumerate(metrics):
        y = 154 + index * 66
        metric_parts.append(
            f'<rect x="780" y="{y}" width="360" height="52" rx="4" fill="#ffffff" stroke="#d5ddd7"/>'
            f'<text x="798" y="{y + 20}" font-size="11" fill="{MUTED}">{escape(label)}</text>'
            f'<text x="798" y="{y + 42}" font-size="18" font-weight="700" fill="{INK}">{escape(value)}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img" aria-labelledby="title desc">
  <title id="title">Synthetic vector takeoff for {escape(plan.name)}</title>
  <desc id="desc">Rectangular floor-plan geometry with classified walls, openings, and measured quantities.</desc>
  <rect width="1200" height="650" fill="{PAPER}"/>
  <text x="38" y="42" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="{ACCENT}">VECTOR TAKEOFF / SYNTHETIC FIXTURE</text>
  <text x="38" y="78" font-family="Arial, sans-serif" font-size="29" font-weight="700" fill="{INK}">{escape(plan.name)}</text>
  <text x="38" y="103" font-family="Arial, sans-serif" font-size="13" fill="{MUTED}">Scale {plan.scale_m_per_unit:g} m/unit | Storey height {plan.storey_height_m:g} m | Plan {escape(plan.plan_id)}</text>
  <g font-family="Arial, sans-serif">{''.join(room_parts)}{''.join(wall_parts)}{''.join(opening_parts)}</g>
  <text x="780" y="122" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="{MUTED}">MEASURED QUANTITIES</text>
  <g font-family="Arial, sans-serif">{''.join(metric_parts)}</g>
  <line x1="790" y1="575" x2="830" y2="575" stroke="{INK}" stroke-width="5"/><text x="840" y="579" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">External wall</text>
  <line x1="940" y1="575" x2="980" y2="575" stroke="{BLUE}" stroke-width="3"/><text x="990" y="579" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">Partition</text>
  <text x="38" y="625" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">Measurement fixture only. No PDF/CAD/BIM parsing, professional quantity survey, live rate book, or tender recommendation.</text>
</svg>"""


def render_cost_breakdown_svg(estimate: CostEstimate) -> str:
    lines = sorted(estimate.priced_lines, key=lambda line: line.amount, reverse=True)
    max_amount = max((line.high_amount for line in lines), default=1.0)
    rows: list[str] = []
    for index, line in enumerate(lines):
        y = 138 + index * 59
        bar_width = 620 * line.amount / max_amount
        low_x = 330 + 620 * line.low_amount / max_amount
        high_x = 330 + 620 * line.high_amount / max_amount
        rows.append(
            f'<text x="38" y="{y + 17}" font-size="12" font-weight="700" fill="{INK}">{escape(line.item_code)}</text>'
            f'<text x="105" y="{y + 17}" font-size="12" fill="{MUTED}">{escape(line.description)}</text>'
            f'<rect x="330" y="{y}" width="620" height="22" rx="3" fill="#e4e9e5"/>'
            f'<rect x="330" y="{y}" width="{bar_width:.1f}" height="22" rx="3" fill="{GREEN}"/>'
            f'<line x1="{low_x:.1f}" y1="{y - 4}" x2="{low_x:.1f}" y2="{y + 26}" stroke="{GOLD}" stroke-width="2"/>'
            f'<line x1="{high_x:.1f}" y1="{y - 4}" x2="{high_x:.1f}" y2="{y + 26}" stroke="{GOLD}" stroke-width="2"/>'
            f'<text x="975" y="{y + 17}" font-size="12" font-weight="700" fill="{INK}">{estimate.currency} {line.amount:,.0f}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img" aria-labelledby="title">
  <title id="title">Synthetic cost build-up for {escape(estimate.plan_id)}</title>
  <rect width="1200" height="650" fill="#eef2ed"/>
  <text x="38" y="42" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="{GREEN}">COST BUILD-UP / SYNTHETIC UNIT RATES</text>
  <text x="38" y="78" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="{INK}">{escape(estimate.plan_id)}</text>
  <text x="38" y="103" font-family="Arial, sans-serif" font-size="13" fill="{MUTED}">Base {estimate.currency} {estimate.base_total:,.0f} | Illustrative range {estimate.currency} {estimate.low_total:,.0f}-{estimate.high_total:,.0f} | Rate set {escape(estimate.rate_library_version)}</text>
  <g font-family="Arial, sans-serif">{''.join(rows)}</g>
  <rect x="38" y="570" width="1124" height="44" rx="4" fill="#ffffff" stroke="#d5ddd7"/>
  <text x="56" y="597" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">Gold markers show item-level rate uncertainty only. They exclude scope, market, design-development, and commercial risk.</text>
</svg>"""


def render_tender_comparison_svg(analyses: list[TenderAnalysis]) -> str:
    max_total = max([analysis.submitted_total for analysis in analyses] + [1.0])
    cards: list[str] = []
    for index, analysis in enumerate(analyses):
        x = 35 + index * 382
        review_count = sum(flag.flag != "within_demo_band" for flag in analysis.flags)
        bar_height = 240 * analysis.submitted_total / max_total
        status_color = ACCENT if review_count else GREEN
        cards.append(
            f'<rect x="{x}" y="105" width="350" height="465" rx="5" fill="#ffffff" stroke="#d7ddd8"/>'
            f'<text x="{x + 22}" y="140" font-size="12" font-weight="700" fill="{status_color}">{escape(analysis.tender_id)}</text>'
            f'<text x="{x + 22}" y="170" font-size="20" font-weight="700" fill="{INK}">{escape(analysis.bidder_alias)}</text>'
            f'<rect x="{x + 35}" y="{500 - bar_height:.1f}" width="90" height="{bar_height:.1f}" rx="3" fill="{BLUE}"/>'
            f'<line x1="{x + 20}" y1="{500 - 240 * analysis.benchmark_total / max_total:.1f}" x2="{x + 145}" y2="{500 - 240 * analysis.benchmark_total / max_total:.1f}" stroke="{GOLD}" stroke-width="3" stroke-dasharray="6 4"/>'
            f'<text x="{x + 165}" y="235" font-size="11" fill="{MUTED}">Submitted total</text>'
            f'<text x="{x + 165}" y="260" font-size="18" font-weight="700" fill="{INK}">{analysis.currency} {analysis.submitted_total:,.0f}</text>'
            f'<text x="{x + 165}" y="310" font-size="11" fill="{MUTED}">Benchmark deviation</text>'
            f'<text x="{x + 165}" y="335" font-size="18" font-weight="700" fill="{INK}">{analysis.deviation_fraction * 100:+.1f}%</text>'
            f'<text x="{x + 165}" y="385" font-size="11" fill="{MUTED}">Completeness</text>'
            f'<text x="{x + 165}" y="410" font-size="18" font-weight="700" fill="{INK}">{analysis.completeness_fraction * 100:.0f}%</text>'
            f'<text x="{x + 165}" y="460" font-size="11" fill="{MUTED}">Review flags</text>'
            f'<text x="{x + 165}" y="485" font-size="18" font-weight="700" fill="{status_color}">{review_count}</text>'
            f'<text x="{x + 22}" y="545" font-size="11" fill="{MUTED}">Gold line: synthetic benchmark</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620" role="img" aria-labelledby="title">
  <title id="title">Synthetic tender comparison</title>
  <rect width="1200" height="620" fill="{PAPER}"/>
  <text x="35" y="42" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="{ACCENT}">NORMALIZED TENDER REVIEW / SYNTHETIC BIDS</text>
  <text x="35" y="78" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="{INK}">Transparent exceptions, no award recommendation</text>
  <g font-family="Arial, sans-serif">{''.join(cards)}</g>
  <text x="35" y="600" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">Illustrative comparison bands only. Commercial review, scope normalization, bidder clarification, and professional QS judgment remain required.</text>
</svg>"""
