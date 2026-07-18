from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Any, BinaryIO

import yaml
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "portfolio-site" / "assets" / "Josiah_Lau_Applied_AI_Portfolio_Brief.pdf"
PROFILE_PATH = ROOT / "docs" / "portfolio_profile.yml"

INK = HexColor("#16201D")
MUTED = HexColor("#5D6C66")
LINE = HexColor("#D9E1DD")
PAPER = HexColor("#F7F8F5")
WHITE = HexColor("#FFFFFF")
MOSS = HexColor("#2F6F56")
STEEL = HexColor("#345B70")
CLAY = HexColor("#A75538")
GOLD = HexColor("#D7A441")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 42


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def build_context() -> dict[str, Any]:
    profile = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
    retrieval = load_json(
        "projects/aec-code-compliance-rag/demo_outputs/public_sources/"
        "retrieval_eval_summary.json"
    )
    retrieval_uncertainty = load_json(
        "projects/aec-code-compliance-rag/demo_outputs/public_sources/"
        "retrieval_uncertainty_summary.json"
    )
    embodied = load_json(
        "projects/vla-embodied-agent-simulator/demo_outputs/" "behavior_cloning_eval_summary.json"
    )
    physics = load_json(
        "projects/vla-embodied-agent-simulator/demo_outputs/physics_replay_summary.json"
    )
    massing = load_json(
        "projects/constraint-aware-massing-explorer/demo_outputs/evaluation_summary.json"
    )

    return {
        "profile": profile,
        "aec": {
            "document_hit_at_1": retrieval["summary"]["retrieval_hit_at_1"],
            "document_mrr": retrieval["summary"]["mean_reciprocal_rank"],
            "exact_hit_at_1": retrieval["summary"]["evidence_target_hit_at_1"],
            "page_hit_at_1": retrieval["summary"]["page_target_hit_at_1"],
            "case_count": retrieval["summary"]["case_count"],
            "answerable_cases": retrieval_uncertainty["support"]["answerable_cases"],
            "hit_interval": retrieval_uncertainty["metrics"]["retrieval_hit_at_1"],
        },
        "embodied": {
            "holdout_scenarios": embodied["training"]["holdout_scenario_count"],
            "filtered_success": embodied["policies"]["egocentric_mlp_shielded"]["success_rate"],
            "rgb_standard_success": embodied["policies"]["synthetic_rgb_mlp_raw"]["success_rate"],
            "rgb_shifted_success": embodied["policies"]["synthetic_rgb_mlp_shifted_raw"][
                "success_rate"
            ],
            "physics_scenarios": physics["scenario_count"],
            "raw_contacts": physics["policies"]["egocentric_mlp_raw"]["contact_command_count"],
            "raw_moves": physics["policies"]["egocentric_mlp_raw"]["movement_command_count"],
            "filtered_contacts": physics["policies"]["egocentric_mlp_shielded"][
                "contact_command_count"
            ],
        },
        "massing": {
            "candidate_count": massing["evaluated_candidates_per_mode"],
            "feasible_rate": massing["aggregate"]["constraint_aware_feasible_rate"],
            "baseline_feasible_rate": massing["aggregate"]["baseline_feasible_rate"],
            "gfa_error_percent": massing["aggregate"][
                "constraint_aware_mean_best_gfa_error_percent"
            ],
            "baseline_gfa_error_percent": massing["aggregate"][
                "baseline_mean_best_gfa_error_percent"
            ],
        },
    }


def wrap_lines(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if stringWidth(candidate, font, size) <= width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    font: str = "Helvetica",
    size: float = 9,
    leading: float = 12,
    color=MUTED,
    max_lines: int | None = None,
) -> float:
    lines = wrap_lines(text, font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    pdf.setFont(font, size)
    pdf.setFillColor(color)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_eyebrow(pdf: canvas.Canvas, text: str, x: float, y: float, color=CLAY) -> None:
    pdf.setFillColor(color)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(x, y, text.upper())


def draw_footer(pdf: canvas.Canvas, page_number: int, profile: dict[str, Any]) -> None:
    pdf.setStrokeColor(LINE)
    pdf.line(MARGIN, 30, PAGE_WIDTH - MARGIN, 30)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(MARGIN, 17, "Generated from repository evidence / prototype boundaries retained")
    pdf.drawRightString(PAGE_WIDTH - MARGIN, 17, f"{profile['name']} / {page_number} of 2")


def draw_link(
    pdf: canvas.Canvas,
    label: str,
    url: str,
    x: float,
    y: float,
    *,
    size: float = 8.5,
    color=MOSS,
) -> float:
    pdf.setFont("Helvetica-Bold", size)
    pdf.setFillColor(color)
    pdf.drawString(x, y, label)
    width = stringWidth(label, "Helvetica-Bold", size)
    pdf.linkURL(url, (x, y - 2, x + width, y + size + 2), relative=0)
    return x + width


def draw_project_column(
    pdf: canvas.Canvas,
    *,
    x: float,
    y: float,
    width: float,
    number: str,
    category: str,
    title: str,
    summary: str,
    metric: str,
    metric_note: str,
    boundary: str,
    url: str,
    accent,
) -> None:
    pdf.setFillColor(accent)
    pdf.rect(x, y, width, 3, stroke=0, fill=1)
    draw_eyebrow(pdf, f"{number} / {category}", x, y - 18, accent)
    title_y = draw_wrapped(
        pdf,
        title,
        x,
        y - 40,
        width,
        font="Helvetica-Bold",
        size=13,
        leading=15,
        color=INK,
        max_lines=3,
    )
    summary_y = draw_wrapped(
        pdf,
        summary,
        x,
        title_y - 7,
        width,
        size=8.5,
        leading=11,
        color=MUTED,
        max_lines=6,
    )
    pdf.setFont("Helvetica-Bold", 19)
    pdf.setFillColor(STEEL)
    pdf.drawString(x, summary_y - 13, metric)
    metric_y = draw_wrapped(
        pdf,
        metric_note,
        x,
        summary_y - 29,
        width,
        size=7.8,
        leading=10,
        color=MUTED,
        max_lines=4,
    )
    pdf.setStrokeColor(LINE)
    pdf.line(x, metric_y - 4, x + width, metric_y - 4)
    boundary_y = draw_wrapped(
        pdf,
        boundary,
        x,
        metric_y - 17,
        width,
        size=7.8,
        leading=10,
        color=CLAY,
        max_lines=5,
    )
    draw_link(pdf, "Open visual case study", url, x, boundary_y - 8, size=8)


def draw_page_one(pdf: canvas.Canvas, context: dict[str, Any]) -> None:
    profile = context["profile"]
    aec = context["aec"]
    embodied = context["embodied"]
    massing = context["massing"]

    pdf.setFillColor(INK)
    pdf.rect(0, PAGE_HEIGHT - 184, PAGE_WIDTH, 184, stroke=0, fill=1)
    pdf.setFillColor(GOLD)
    pdf.rect(0, PAGE_HEIGHT - 187, PAGE_WIDTH, 3, stroke=0, fill=1)
    draw_eyebrow(pdf, "Applied AI Portfolio Brief / 2026", MARGIN, PAGE_HEIGHT - 38, GOLD)
    pdf.setFont("Helvetica-Bold", 25)
    pdf.setFillColor(WHITE)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 70, profile["name"])
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 98, profile["positioning"])
    draw_wrapped(
        pdf,
        profile["summary"],
        MARGIN,
        PAGE_HEIGHT - 119,
        PAGE_WIDTH - 2 * MARGIN,
        size=9,
        leading=12,
        color=HexColor("#D9E1DD"),
        max_lines=3,
    )
    link_y = PAGE_HEIGHT - 165
    x = MARGIN
    x = draw_link(pdf, "Visual portfolio", profile["website"], x, link_y, color=GOLD)
    x += 18
    x = draw_link(pdf, "GitHub evidence", profile["github"], x, link_y, color=GOLD)
    x += 18
    x = draw_link(pdf, "LinkedIn", profile["linkedin"], x, link_y, color=GOLD)
    pdf.setFont("Helvetica", 8.5)
    pdf.setFillColor(HexColor("#D9E1DD"))
    pdf.drawRightString(PAGE_WIDTH - MARGIN, link_y, f"{profile['email']} / {profile['location']}")

    y = PAGE_HEIGHT - 221
    draw_eyebrow(pdf, "Selected evidence", MARGIN, y)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(INK)
    pdf.drawString(MARGIN, y - 28, "Three projects, three kinds of engineering evidence")

    column_gap = 18
    column_width = (PAGE_WIDTH - 2 * MARGIN - 2 * column_gap) / 3
    column_y = y - 54
    project_urls = {
        "aec": f"{profile['website']}pages/aec-rag.html",
        "embodied": f"{profile['website']}pages/embodied-ai.html",
        "massing": f"{profile['website']}pages/massing-explorer.html",
    }
    interval = aec["hit_interval"]
    draw_project_column(
        pdf,
        x=MARGIN,
        y=column_y,
        width=column_width,
        number="01",
        category="Flagship / RAG",
        title="AEC Code Compliance RAG",
        summary=(
            "Page-aware public-document ingestion, local retrieval baselines, structured "
            "citations, abstention, service contracts, and bounded telemetry."
        ),
        metric=f"Hit@1 {aec['document_hit_at_1']:.3f}",
        metric_note=(
            f"Document MRR {aec['document_mrr']:.3f}; exact-target Hit@1 "
            f"{aec['exact_hit_at_1']:.3f}; 95% interval "
            f"[{interval['lower']:.3f}, {interval['upper']:.3f}], "
            f"n={aec['answerable_cases']}."
        ),
        boundary=(
            "Candidate-authored fixed snapshot. Document assistance only; no compliance "
            "certification or professional sign-off."
        ),
        url=project_urls["aec"],
        accent=CLAY,
    )
    draw_project_column(
        pdf,
        x=MARGIN + column_width + column_gap,
        y=column_y,
        width=column_width,
        number="02",
        category="Embodied AI",
        title="Construction Embodied Agent Simulator",
        summary=(
            "Shared demonstrations compare state, semantic-raster, egocentric, and rendered-"
            "RGB policies with filtering and planar MuJoCo replay."
        ),
        metric=f"Success {embodied['filtered_success']:.3f}",
        metric_note=(
            f"{embodied['holdout_scenarios']} unseen grids; {embodied['raw_contacts']}/"
            f"{embodied['raw_moves']} raw physics contacts; "
            f"{embodied['filtered_contacts']} filtered contacts."
        ),
        boundary=(
            "Pixels are rendered from simulator state. No physical camera, ROS, robot hardware, "
            "or safety validation."
        ),
        url=project_urls["embodied"],
        accent=MOSS,
    )
    draw_project_column(
        pdf,
        x=MARGIN + 2 * (column_width + column_gap),
        y=column_y,
        width=column_width,
        number="03",
        category="Computational design",
        title="Constraint-Aware Massing Explorer",
        summary=(
            "Seeded rectangular geometry, hard feasibility checks, transparent proxy "
            "objectives, Pareto ranking, and baseline comparison."
        ),
        metric=f"Feasible {massing['feasible_rate']:.3f}",
        metric_note=(
            f"Baseline {massing['baseline_feasible_rate']:.3f}; mean best GFA error "
            f"{massing['gfa_error_percent']:.2f}% vs {massing['baseline_gfa_error_percent']:.2f}%; "
            f"{massing['candidate_count']} candidates per method."
        ),
        boundary=(
            "Synthetic sites and rectangular envelopes. No code inference, calibrated "
            "environmental simulation, or approvable design."
        ),
        url=project_urls["massing"],
        accent=GOLD,
    )

    capability_y = 324
    draw_eyebrow(pdf, "Capabilities", MARGIN, capability_y)
    capability_text = "  /  ".join(
        [
            "Source-grounded AI",
            "Embodied-agent evaluation",
            "Computational geometry",
            "AEC workflow contracts",
            "Testing + reproducibility",
        ]
    )
    draw_wrapped(
        pdf,
        capability_text,
        MARGIN,
        capability_y - 20,
        PAGE_WIDTH - 2 * MARGIN,
        font="Helvetica-Bold",
        size=8.2,
        leading=10,
        color=INK,
        max_lines=2,
    )

    proof_y = 265
    pdf.setFillColor(PAPER)
    pdf.roundRect(MARGIN, proof_y - 85, PAGE_WIDTH - 2 * MARGIN, 85, 6, stroke=0, fill=1)
    draw_eyebrow(pdf, "Reproduce the evidence", MARGIN + 18, proof_y - 20, MOSS)
    pdf.setFont("Courier-Bold", 10)
    pdf.setFillColor(INK)
    pdf.drawString(MARGIN + 18, proof_y - 43, "python scripts/reviewer_check.py")
    draw_wrapped(
        pdf,
        "Checks public claims, commands, links, visual contracts, artifact-backed metrics, and focused tests without regenerating tracked evidence.",
        MARGIN + 18,
        proof_y - 61,
        PAGE_WIDTH - 2 * MARGIN - 36,
        size=8,
        leading=10,
        color=MUTED,
        max_lines=2,
    )

    draw_eyebrow(pdf, "Claim boundary", MARGIN, 136)
    draw_wrapped(
        pdf,
        "Projects are local prototypes unless explicitly stated otherwise. Synthetic data, public-source snapshots, mock providers, and simulation-only robotics are labeled at project level. No customer adoption, deployed reliability, professional compliance outcome, QS sign-off, approvable design, or robot-hardware deployment is claimed.",
        MARGIN,
        118,
        PAGE_WIDTH - 2 * MARGIN,
        size=8.5,
        leading=11,
        color=MUTED,
        max_lines=5,
    )
    draw_footer(pdf, 1, profile)


def draw_journey_row(
    pdf: canvas.Canvas,
    *,
    y: float,
    number: str,
    stage: str,
    project: str,
    output: str,
    status: str,
) -> None:
    pdf.setStrokeColor(LINE)
    pdf.line(MARGIN, y + 7, PAGE_WIDTH - MARGIN, y + 7)
    pdf.setFillColor(CLAY)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(MARGIN, y - 10, number)
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(MARGIN + 28, y - 10, stage)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(MARGIN + 116, y - 10, project)
    draw_wrapped(
        pdf,
        output,
        MARGIN + 116,
        y - 25,
        270,
        size=7.6,
        leading=9,
        color=MUTED,
        max_lines=2,
    )
    pdf.setFillColor(MOSS)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, y - 10, status.upper())


def draw_experience_row(
    pdf: canvas.Canvas, item: dict[str, str], x: float, y: float, width: float
) -> None:
    pdf.setFillColor(GOLD)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(x, y, str(item["period"]).upper())
    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 9.2)
    pdf.drawString(x + 78, y, f"{item['role']} / {item['organization']}")
    draw_wrapped(
        pdf,
        item["scope"],
        x + 78,
        y - 13,
        width - 78,
        size=7.6,
        leading=9,
        color=HexColor("#C7D1CC"),
        max_lines=2,
    )


def draw_page_two(pdf: canvas.Canvas, context: dict[str, Any]) -> None:
    profile = context["profile"]
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(INK)
    pdf.rect(0, PAGE_HEIGHT - 92, PAGE_WIDTH, 92, stroke=0, fill=1)
    draw_eyebrow(pdf, "AEC decision journey", MARGIN, PAGE_HEIGHT - 34, GOLD)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(WHITE)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 64, "Five implemented systems, one bounded handoff")

    journey = [
        (
            "01",
            "Knowledge",
            "AEC Code Compliance RAG",
            "Validated sources -> page-aware chunks -> ranked evidence -> cited answer or abstention",
            "implemented",
        ),
        (
            "02",
            "Intent",
            "Communication + Specification Assistant",
            "Role-tagged messages -> requirements -> conflicts -> scoped approvals -> draft clauses",
            "implemented",
        ),
        (
            "03",
            "Options",
            "Constraint-Aware Massing Explorer",
            "Typed site parameters -> seeded geometry -> hard checks -> proxy ranking",
            "implemented",
        ),
        (
            "04",
            "Quantity",
            "QS Takeoff + Tender Workbench",
            "Vector geometry -> quantities -> rate provenance -> uncertainty -> exceptions",
            "implemented",
        ),
        (
            "05",
            "Action",
            "Construction Embodied Agent Simulator",
            "Task + state -> learned action -> rule filter -> rollout -> planar command replay",
            "implemented",
        ),
    ]
    row_y = PAGE_HEIGHT - 122
    for number, stage, project, output, status in journey:
        draw_journey_row(
            pdf,
            y=row_y,
            number=number,
            stage=stage,
            project=project,
            output=output,
            status=status,
        )
        row_y -= 52
    pdf.setStrokeColor(LINE)
    pdf.line(MARGIN, row_y + 7, PAGE_WIDTH - MARGIN, row_y + 7)
    draw_wrapped(
        pdf,
        "Executed integration: 5 approved requirements -> 16/16 sourced fields -> 96 candidates / 92 feasible -> 7/7 priced schematic takeoff lines. Budget, accessibility, developed design, and tender analysis remain outside automation.",
        MARGIN,
        row_y - 10,
        PAGE_WIDTH - 2 * MARGIN,
        size=8,
        leading=10,
        color=CLAY,
        max_lines=3,
    )

    history_top = row_y - 58
    pdf.setFillColor(INK)
    pdf.roundRect(MARGIN, history_top - 230, PAGE_WIDTH - 2 * MARGIN, 230, 6, stroke=0, fill=1)
    draw_eyebrow(pdf, "Professional delivery", MARGIN + 18, history_top - 22, GOLD)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.setFillColor(WHITE)
    pdf.drawString(MARGIN + 18, history_top - 47, "Design discipline carried into AI engineering")
    experience_y = history_top - 78
    for item in profile["experience"]:
        draw_experience_row(
            pdf,
            item,
            MARGIN + 18,
            experience_y,
            PAGE_WIDTH - 2 * MARGIN - 36,
        )
        experience_y -= 32

    contact_y = 138
    pdf.setStrokeColor(LINE)
    pdf.line(MARGIN, contact_y + 20, PAGE_WIDTH - MARGIN, contact_y + 20)
    draw_eyebrow(pdf, "Continue the review", MARGIN, contact_y)
    x = MARGIN
    x = draw_link(pdf, "Visual portfolio", profile["website"], x, contact_y - 23, size=9)
    x += 22
    x = draw_link(pdf, "Source + evidence", profile["github"], x, contact_y - 23, size=9)
    x += 22
    x = draw_link(pdf, "LinkedIn", profile["linkedin"], x, contact_y - 23, size=9)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, contact_y - 23, profile["email"])
    draw_wrapped(
        pdf,
        "Profile and employment chronology are portfolio-owner supplied. Project metrics are generated from checked-in local artifacts. Neither source is third-party validation.",
        MARGIN,
        contact_y - 45,
        PAGE_WIDTH - 2 * MARGIN,
        size=7.6,
        leading=9,
        color=MUTED,
        max_lines=2,
    )
    draw_footer(pdf, 2, profile)


def render_portfolio_brief(target: str | Path | BinaryIO) -> None:
    context = build_context()
    canvas_target = str(target) if isinstance(target, Path) else target
    pdf = canvas.Canvas(
        canvas_target,
        pagesize=A4,
        pageCompression=1,
        invariant=1,
    )
    pdf.setTitle("Josiah Lau - Applied AI Portfolio Brief")
    pdf.setAuthor("Josiah Lau")
    pdf.setSubject("Applied AI, embodied AI, computational design, and AEC systems")
    draw_page_one(pdf, context)
    pdf.showPage()
    draw_page_two(pdf, context)
    pdf.showPage()
    pdf.save()


def generated_bytes() -> bytes:
    buffer = io.BytesIO()
    render_portfolio_brief(buffer)
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the recruiter-facing portfolio brief.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in PDF is stale.")
    args = parser.parse_args()

    generated = generated_bytes()
    output = args.output.resolve()
    if args.check:
        if not output.exists() or output.read_bytes() != generated:
            raise SystemExit(f"Portfolio brief is missing or stale: {output.relative_to(ROOT)}")
        print(f"Portfolio brief is current: {output.relative_to(ROOT)}")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(generated)
    print(f"Wrote portfolio brief to {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
