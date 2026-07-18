from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.portfolio_visuals import (  # noqa: E402
    EvidencePanel,
    Stage,
    SystemMap,
    render_system_map,
)


def _load(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def _pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def build_specs() -> dict[str, SystemMap]:
    rag = _load(
        "projects/aec-code-compliance-rag/demo_outputs/public_sources/"
        "retrieval_eval_summary.json"
    )
    massing = _load(
        "projects/constraint-aware-massing-explorer/demo_outputs/evaluation_summary.json"
    )
    specification = _load(
        "projects/project-specification-copilot/demo_outputs/evaluation_summary.json"
    )
    language = _load(
        "projects/project-specification-copilot/demo_outputs/language_stress_summary.json"
    )
    qs = _load("projects/qs-takeoff-tender-analysis/demo_outputs/evaluation_summary.json")
    embodied = _load(
        "projects/vla-embodied-agent-simulator/demo_outputs/behavior_cloning_eval_summary.json"
    )

    rag_summary = rag["summary"]
    massing_summary = massing["aggregate"]
    language_metrics = language["metrics"]
    qs_metrics = qs["metrics"]
    policies = embodied["policies"]

    return {
        "projects/aec-code-compliance-rag/demo_outputs/system_map.svg": SystemMap(
            title="AEC Code Compliance RAG",
            subtitle="How a question becomes cited evidence or an explicit abstention",
            badges=("LOCAL-FIRST", "PUBLIC + SYNTHETIC", "NO PAID API"),
            stages=(
                Stage(
                    "sources",
                    ("Bounded document", "inventory"),
                    ("synthetic default corpus", "15 public documents", "hash + rights metadata"),
                    "validated source records",
                ),
                Stage(
                    "ingestion",
                    ("Page-aware", "evidence chunks"),
                    ("heading and clause ids", "page and word offsets", "stable chunk identifiers"),
                    "metadata-rich index",
                ),
                Stage(
                    "retrieval",
                    ("Inspectable local", "ranking"),
                    ("TF-IDF / BM25 / LSA", "hybrid + source filters", "exact-target evaluation"),
                    "ranked evidence set",
                ),
                Stage(
                    "answer gate",
                    ("Ground, cite,", "or abstain"),
                    ("support threshold", "source-status warnings", "structured citations"),
                    "answer status + citations",
                ),
                Stage(
                    "service",
                    ("Tested local", "API boundary"),
                    ("API key + request ids", "redacted SQLite logs", "durable telemetry"),
                    "reviewable request trace",
                ),
            ),
            connectors=("validate", "index", "rank", "serve"),
            evidence=(
                EvidencePanel(
                    "document retrieval",
                    f"Hit@1 {rag_summary['retrieval_hit_at_1']:.3f}",
                    (
                        f"{rag_summary['answerable_case_count']} answerable public cases",
                        f"MRR {rag_summary['mean_reciprocal_rank']:.3f}; top-4 recall {_pct(rag_summary['recall_at_k'])}",
                    ),
                    "#00A896",
                ),
                EvidencePanel(
                    "harder evidence target",
                    f"Exact chunk {rag_summary['evidence_target_hit_at_1']:.3f}",
                    (
                        f"page target Hit@1 {rag_summary['page_target_hit_at_1']:.3f}",
                        "lower result remains visible",
                    ),
                    "#F2B134",
                ),
                EvidencePanel(
                    "control boundary",
                    "Cite or refuse",
                    (
                        f"no-answer accuracy {_pct(rag_summary['no_answer_accuracy'])}",
                        "not code approval or legal advice",
                    ),
                    "#E66A47",
                ),
            ),
            boundary="A qualified professional verifies currency, applicability, and every decision.",
            sources=("retrieval_eval_summary.json", "service evidence"),
        ),
        "projects/constraint-aware-massing-explorer/demo_outputs/system_map.svg": SystemMap(
            title="Constraint-Aware Massing Explorer",
            subtitle="How supplied site rules become comparable early-stage geometry",
            badges=("SEEDED SEARCH", "SYNTHETIC SITES", "PROXY METRICS"),
            stages=(
                Stage(
                    "brief",
                    ("Explicit site and", "project inputs"),
                    ("setbacks and height", "coverage and max GFA", "access + objective weights"),
                    "validated scenario",
                ),
                Stage(
                    "generation",
                    ("Four bounded", "typologies"),
                    ("slab and twin bar", "courtyard and stepped", "fixed-seed candidates"),
                    "candidate geometry set",
                ),
                Stage(
                    "hard gate",
                    ("Reject invalid", "options"),
                    (
                        "site and setback bounds",
                        "height / GFA / coverage",
                        "open-site access routes",
                    ),
                    "feasible + failure sets",
                ),
                Stage(
                    "comparison",
                    ("Pareto and", "weighted ranking"),
                    ("solar orientation proxy", "daylight / wind proxies", "target-area fit"),
                    "ranked option frontier",
                ),
                Stage(
                    "review",
                    ("Inspectable plan", "and isometric"),
                    (
                        "candidate ids retained",
                        "metrics beside geometry",
                        "invalid cases published",
                    ),
                    "design review record",
                ),
            ),
            connectors=("parameterize", "sample", "assess", "render"),
            evidence=(
                EvidencePanel(
                    "constraint-aware",
                    f"{_pct(massing_summary['constraint_aware_feasible_rate'])} feasible",
                    (
                        f"{massing['evaluated_candidates_per_mode']} evaluated candidates",
                        f"mean best GFA error {massing_summary['constraint_aware_mean_best_gfa_error_percent']:.2f}%",
                    ),
                    "#00A896",
                ),
                EvidencePanel(
                    "comparison baseline",
                    f"{_pct(massing_summary['baseline_feasible_rate'])} feasible",
                    (
                        "same validator and run count",
                        f"mean best GFA error {massing_summary['baseline_mean_best_gfa_error_percent']:.2f}%",
                    ),
                    "#F2B134",
                ),
                EvidencePanel(
                    "model boundary",
                    "Geometry, not design approval",
                    ("environmental values are proxies", "no code inference or internal egress"),
                    "#E66A47",
                ),
            ),
            boundary="A designer supplies every rule and judges architectural, regulatory, and engineering quality.",
            sources=("evaluation_summary.json", "candidate geometry"),
        ),
        "projects/project-specification-copilot/demo_outputs/system_map.svg": SystemMap(
            title="Project Communication and Specification Assistant",
            subtitle="How team messages become approved, source-linked draft clauses",
            badges=("ROLE-TAGGED", "SYNTHETIC CHAT", "FAIL-CLOSED"),
            stages=(
                Stage(
                    "conversation",
                    ("Shared project", "messages"),
                    ("immutable message ids", "client + team roles", "sequence retained"),
                    "provenance-linked events",
                ),
                Stage(
                    "extraction",
                    ("Bounded requirement", "parser"),
                    (
                        "documented phrase forms",
                        "question / history refusal",
                        "no silent inference",
                    ),
                    "proposed requirements",
                ),
                Stage(
                    "ledger",
                    ("Version and", "conflict state"),
                    ("proposed / approved", "superseded values", "open conflict register"),
                    "auditable requirement state",
                ),
                Stage(
                    "approval",
                    ("Role-scoped", "decision gate"),
                    ("category permissions", "denied attempts logged", "only approved values pass"),
                    "authorized clause inputs",
                ),
                Stage(
                    "draft",
                    ("Source-linked", "specification"),
                    ("message citations", "open decisions retained", "append-only audit events"),
                    "draft for human review",
                ),
            ),
            connectors=("record", "extract", "govern", "draft"),
            evidence=(
                EvidencePanel(
                    "workflow regression",
                    f"{specification['case_count']} cases / {specification['message_count']} messages",
                    ("all authored workflow checks pass", "five denied approvals reproduced"),
                    "#00A896",
                ),
                EvidencePanel(
                    "language stress set",
                    f"F1 {language_metrics['requirement_f1']:.3f}",
                    (
                        f"{language['case_count']} manually labeled cases",
                        f"recall {language_metrics['requirement_recall']:.3f}; two misses retained",
                    ),
                    "#F2B134",
                ),
                EvidencePanel(
                    "control boundary",
                    "Approval before drafting",
                    ("roles are supplied, not authenticated", "not a professional specification"),
                    "#E66A47",
                ),
            ),
            boundary="The project team resolves ambiguity and approves every requirement and final clause.",
            sources=("evaluation_summary.json", "language_stress_summary.json"),
        ),
        "projects/qs-takeoff-tender-analysis/demo_outputs/system_map.svg": SystemMap(
            title="QS Takeoff and Tender Analysis Workbench",
            subtitle="How explicit vector geometry becomes traceable quantities and review exceptions",
            badges=("VECTOR INPUT", "SYNTHETIC RATES", "NO AWARD RANKING"),
            stages=(
                Stage(
                    "plan",
                    ("Typed floor-plan", "geometry"),
                    ("scale + room ids", "walls and openings", "axis-aligned rectangles"),
                    "validated plan schema",
                ),
                Stage(
                    "geometry",
                    ("Atomic wall", "segmentation"),
                    (
                        "split shared boundaries",
                        "classify ext. / partition",
                        "reject invalid openings",
                    ),
                    "measured source segments",
                ),
                Stage(
                    "takeoff",
                    ("Formula-backed", "quantity lines"),
                    ("opening deductions", "seven bounded items", "source geometry ids"),
                    "auditable quantities",
                ),
                Stage(
                    "cost",
                    ("Unit-safe rate", "build-up"),
                    ("versioned rate records", "provenance + currency", "illustrative uncertainty"),
                    "bounded cost estimate",
                ),
                Stage(
                    "tender review",
                    ("Explainable", "exception queue"),
                    ("missing / extra lines", "high / low ratio flags", "no bidder ranking"),
                    "human review cases",
                ),
            ),
            connectors=("validate", "measure", "price", "compare"),
            evidence=(
                EvidencePanel(
                    "authored fixtures",
                    "21 quantity lines",
                    (
                        f"exact-match rate {_pct(qs_metrics['quantity_line_exact_match_rate'])}",
                        f"cost total MAE SGD {qs_metrics['cost_total_mean_absolute_error']:.2f}",
                    ),
                    "#00A896",
                ),
                EvidencePanel(
                    "geometry baseline",
                    f"Naive wall MAE {qs_metrics['naive_perimeter_wall_mean_absolute_error_m']:.3f} m",
                    ("implemented shared-wall MAE 0.000 m", "small deterministic fixture set"),
                    "#F2B134",
                ),
                EvidencePanel(
                    "commercial boundary",
                    "Exceptions, not advice",
                    ("rates and tenders are synthetic", "qualified QS review required"),
                    "#E66A47",
                ),
            ),
            boundary="A qualified QS verifies measurement rules, rates, scope, risk, and commercial decisions.",
            sources=("evaluation_summary.json", "sample plan + rates"),
        ),
        "projects/vla-embodied-agent-simulator/demo_outputs/system_map.svg": SystemMap(
            title="Construction Embodied Agent Simulator",
            subtitle="How observation choice and an action filter change closed-loop behavior",
            badges=("FIXED HOLDOUT", "STATE-RENDERED PIXELS", "MUJOCO REPLAY"),
            stages=(
                Stage(
                    "task + world",
                    ("Language task and", "grid state"),
                    ("delivery / inspection", "charging scenarios", "privileged simulator state"),
                    "typed task + observation",
                ),
                Stage(
                    "demonstrations",
                    ("Shared A* expert", "trajectories"),
                    ("192 training scenarios", "1,830 expert steps", "disjoint holdout seeds"),
                    "state-action dataset",
                ),
                Stage(
                    "policies",
                    ("Four observation", "families"),
                    ("engineered random forest", "world + local MLPs", "rendered RGB MLP"),
                    "ranked discrete actions",
                ),
                Stage(
                    "action boundary",
                    ("Raw or full-state", "filtered command"),
                    ("rule-based rejection", "interventions counted", "no expert route fallback"),
                    "executed grid trace",
                ),
                Stage(
                    "evaluation",
                    ("Holdout rollouts", "and physics replay"),
                    ("success + unsafe rate", "appearance shift", "rigid contact telemetry"),
                    "failures + model cards",
                ),
            ),
            connectors=("parse", "imitate", "rank", "replay"),
            evidence=(
                EvidencePanel(
                    "best learned rollout",
                    f"{_pct(policies['egocentric_mlp_shielded']['success_rate'])} success",
                    (
                        f"{policies['egocentric_mlp_shielded']['episode_count']} unseen grid scenarios",
                        f"{policies['egocentric_mlp_shielded']['intervention_count']} filter interventions",
                    ),
                    "#00A896",
                ),
                EvidencePanel(
                    "appearance shift",
                    f"RGB raw success {_pct(policies['synthetic_rgb_mlp_shifted_raw']['success_rate'])}",
                    (
                        f"filtered shift success {_pct(policies['synthetic_rgb_mlp_shifted_shielded']['success_rate'])}",
                        "failed result remains published",
                    ),
                    "#F2B134",
                ),
                EvidencePanel(
                    "simulation boundary",
                    "Planar replay only",
                    ("pixels come from state", "no ROS, hardware, or safety claim"),
                    "#E66A47",
                ),
            ),
            boundary="Simulation results do not establish perception, robot control, or physical-site safety.",
            sources=("behavior_cloning_eval_summary.json", "physics replay"),
        ),
    }


def generate_system_maps() -> list[Path]:
    written = []
    for relative_path, spec in build_specs().items():
        output_path = ROOT / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_system_map(spec), encoding="utf-8", newline="\n")
        written.append(output_path)
    return written


def main() -> None:
    written = generate_system_maps()
    print(f"Generated {len(written)} selected-project system maps.")
    for path in written:
        print(f"- {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
