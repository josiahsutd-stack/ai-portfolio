from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from html import escape


@dataclass(frozen=True)
class Stage:
    tag: str
    title: tuple[str, ...]
    details: tuple[str, ...]
    output: str


@dataclass(frozen=True)
class EvidencePanel:
    tag: str
    headline: str
    details: tuple[str, ...]
    accent: str


@dataclass(frozen=True)
class SystemMap:
    title: str
    subtitle: str
    badges: tuple[str, ...]
    stages: tuple[Stage, ...]
    connectors: tuple[str, ...]
    evidence: tuple[EvidencePanel, ...]
    boundary: str
    sources: tuple[str, ...]


STAGE_ACCENTS = ("#1E88E5", "#00A896", "#F2B134", "#E66A47", "#6B5DD3")


def _text(x: float, y: float, value: str, css_class: str, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" class="{css_class}" text-anchor="{anchor}">'
        f"{escape(value)}</text>"
    )


def _lines(
    x: float,
    start_y: float,
    values: tuple[str, ...],
    css_class: str,
    gap: float,
) -> list[str]:
    return [_text(x, start_y + index * gap, value, css_class) for index, value in enumerate(values)]


def render_system_map(spec: SystemMap) -> str:
    if len(spec.stages) != 5:
        raise ValueError("A system map requires exactly five journey stages.")
    if len(spec.connectors) != 4:
        raise ValueError("A system map requires exactly four connector labels.")
    if len(spec.evidence) != 3:
        raise ValueError("A system map requires exactly three evidence panels.")

    width = 1400
    height = 840
    card_width = 240
    card_height = 300
    card_y = 195
    card_xs = [40 + index * 264 for index in range(5)]
    panel_xs = [40, 488, 936]
    panel_width = 424
    metadata = escape(json.dumps(asdict(spec), sort_keys=True, separators=(",", ":")))

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="map-title map-desc">'
        ),
        f"<metadata>{metadata}</metadata>",
        f'<title id="map-title">{escape(spec.title)} system map</title>',
        (
            f'<desc id="map-desc">{escape(spec.subtitle)} Five implementation stages lead to '
            "measured evidence, explicit controls, and a bounded professional-review output.</desc>"
        ),
        """<defs>
  <filter id="card-shadow" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="7" stdDeviation="8" flood-color="#0D1B2A" flood-opacity="0.11"/>
  </filter>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#5D6A78"/>
  </marker>
  <style>
    text { font-family: Inter, "Segoe UI", Arial, sans-serif; letter-spacing: 0; }
    .title { font-size: 34px; font-weight: 700; fill: #FFFFFF; }
    .subtitle { font-size: 17px; font-weight: 400; fill: #C9D4DE; }
    .badge { font-size: 12px; font-weight: 700; fill: #FFFFFF; }
    .section { font-size: 13px; font-weight: 700; fill: #526170; }
    .tag { font-size: 11px; font-weight: 700; fill: #526170; }
    .stage-title { font-size: 20px; font-weight: 700; fill: #142333; }
    .detail { font-size: 14px; font-weight: 400; fill: #425466; }
    .output-label { font-size: 10px; font-weight: 700; fill: #6A7785; }
    .output { font-size: 13px; font-weight: 600; fill: #203447; }
    .connector { font-size: 11px; font-weight: 700; fill: #526170; }
    .panel-tag { font-size: 11px; font-weight: 700; fill: #526170; }
    .panel-headline { font-size: 22px; font-weight: 700; fill: #142333; }
    .panel-detail { font-size: 14px; font-weight: 400; fill: #425466; }
    .footer { font-size: 14px; font-weight: 600; fill: #26394C; }
    .source { font-size: 11px; font-weight: 600; fill: #6A7785; }
  </style>
</defs>""",
        '<rect width="1400" height="840" fill="#F4F7FA"/>',
        '<rect width="1400" height="140" fill="#0D1B2A"/>',
        '<path d="M0 140 H1400" stroke="#1E88E5" stroke-width="4"/>',
        _text(40, 58, spec.title, "title"),
        _text(40, 94, spec.subtitle, "subtitle"),
    ]

    badge_widths = [max(88, 18 + len(badge) * 7.4) for badge in spec.badges]
    total_badge_width = sum(badge_widths) + max(0, len(badge_widths) - 1) * 10
    badge_x = width - 40 - total_badge_width
    for badge, badge_width in zip(spec.badges, badge_widths, strict=True):
        parts.extend(
            [
                f'<rect x="{badge_x}" y="48" width="{badge_width}" height="30" rx="4" fill="#20364A" stroke="#4C6478"/>',
                _text(badge_x + badge_width / 2, 68, badge, "badge", "middle"),
            ]
        )
        badge_x += badge_width + 10

    parts.append(_text(40, 172, "EXECUTED SYSTEM JOURNEY", "section"))

    for index, (stage, x, accent) in enumerate(
        zip(spec.stages, card_xs, STAGE_ACCENTS, strict=True), start=1
    ):
        parts.extend(
            [
                f'<rect x="{x}" y="{card_y}" width="{card_width}" height="{card_height}" rx="7" fill="#FFFFFF" filter="url(#card-shadow)"/>',
                f'<rect x="{x}" y="{card_y}" width="{card_width}" height="7" rx="7" fill="{accent}"/>',
                f'<circle cx="{x + 30}" cy="{card_y + 38}" r="17" fill="{accent}"/>',
                _text(x + 30, card_y + 43, str(index), "badge", "middle"),
                _text(x + 56, card_y + 42, stage.tag.upper(), "tag"),
            ]
        )
        parts.extend(_lines(x + 20, card_y + 92, stage.title, "stage-title", 24))
        divider_y = card_y + 151
        parts.append(f'<path d="M{x + 20} {divider_y} H{x + card_width - 20}" stroke="#DCE3EA"/>')
        for detail_index, detail in enumerate(stage.details):
            detail_y = card_y + 181 + detail_index * 24
            parts.extend(
                [
                    f'<circle cx="{x + 25}" cy="{detail_y - 5}" r="3" fill="{accent}"/>',
                    _text(x + 38, detail_y, detail, "detail"),
                ]
            )
        parts.extend(
            [
                _text(x + 20, card_y + 269, "OUTPUT", "output-label"),
                _text(x + 20, card_y + 289, stage.output, "output"),
            ]
        )

    for index, label in enumerate(spec.connectors):
        start_x = card_xs[index] + card_width + 7
        end_x = card_xs[index + 1] - 9
        mid_x = (start_x + end_x) / 2
        parts.extend(
            [
                f'<path d="M{start_x} 348 H{end_x}" stroke="#5D6A78" stroke-width="2" marker-end="url(#arrow)"/>',
                f'<rect x="{mid_x - 40}" y="321" width="80" height="20" rx="3" fill="#F4F7FA"/>',
                _text(mid_x, 335, label.upper(), "connector", "middle"),
            ]
        )

    parts.append(_text(40, 542, "PROOF, CONTROLS, AND FAILURE BOUNDARIES", "section"))
    for panel, x in zip(spec.evidence, panel_xs, strict=True):
        parts.extend(
            [
                f'<rect x="{x}" y="565" width="{panel_width}" height="168" rx="7" fill="#FFFFFF" stroke="#D8E0E8"/>',
                f'<rect x="{x}" y="565" width="8" height="168" rx="4" fill="{panel.accent}"/>',
                _text(x + 28, 595, panel.tag.upper(), "panel-tag"),
                _text(x + 28, 630, panel.headline, "panel-headline"),
            ]
        )
        parts.extend(_lines(x + 28, 663, panel.details, "panel-detail", 23))

    source_label = "GENERATED FROM " + " + ".join(spec.sources)
    parts.extend(
        [
            '<rect x="40" y="770" width="1320" height="45" rx="6" fill="#E7EDF3"/>',
            '<rect x="40" y="770" width="8" height="45" rx="4" fill="#E66A47"/>',
            _text(64, 798, "HUMAN REVIEW BOUNDARY: " + spec.boundary, "footer"),
            _text(1360, 829, source_label, "source", "end"),
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"
