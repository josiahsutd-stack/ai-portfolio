from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from aec_code_compliance_rag import (  # noqa: E402
    build_assistant_from_paths,
    evaluate_retrieval,
    load_eval_cases,
)


def _write_markdown_report(payload: dict[str, object], output_path: Path) -> None:
    summary = payload["summary"]
    rows = payload["results"]
    lines = [
        "# Retrieval Evaluation Report",
        "",
        "Synthetic demo evaluation for the AEC Code Compliance RAG Assistant.",
        "",
        "## Summary",
        "",
        f"- Cases: {summary['case_count']}",
        f"- Top-k: {summary['k']}",
        f"- Recall@k: {summary['recall_at_k']}",
        f"- Precision@k: {summary['precision_at_k']}",
        f"- Hit rate: {summary['hit_rate']}",
        f"- Mean reciprocal rank: {summary['mean_reciprocal_rank']}",
        f"- Section hit rate: {summary['section_hit_rate']}",
        f"- Citation coverage: {summary['citation_coverage']}",
        f"- Grounding check rate: {summary['grounding_check_rate']}",
        f"- No-answer accuracy: {summary['no_answer_accuracy']}",
        "",
        "## Per-Question Results",
        "",
        "| Question | Expected section | Retrieved chunks | Recall@k | MRR | Grounding/no-answer check | Missing terms |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        chunks = ", ".join(row["retrieved_chunk_ids"])
        missing = ", ".join(row["missing_terms"]) or "None"
        lines.append(
            "| {question} | {section} | {chunks} | {recall} | {mrr} | {grounded} | {missing} |".format(
                question=str(row["question"]).replace("|", "\\|"),
                section=str(row["expected_section"]).replace("|", "\\|"),
                chunks=chunks.replace("|", "\\|"),
                recall=row["recall_at_k"],
                mrr=row["reciprocal_rank"],
                grounded=row["simple_grounding_check"],
                missing=missing.replace("|", "\\|"),
            )
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_answer_demo(assistant, output_path: Path) -> None:
    question = "What clear width should be checked for high traffic accessible routes?"
    result = assistant.answer(question, k=4)
    lines = [
        "# Demo Answer: Accessible Route Review",
        "",
        "Synthetic demo output. Not legal, code, or professional compliance advice.",
        "",
        f"**Question:** {question}",
        "",
        "## Grounded Answer",
        "",
        str(result["answer"]),
        "",
        "## Citations",
        "",
    ]
    for source in result["sources"]:
        page = f", page {source['page']}" if source["page"] else ""
        lines.extend(
            [
                f"- {source['reference']} - score `{source['score']}`",
                f"  - Chunk: `{source['chunk_id']}`{page}",
                f"  - Excerpt: {source['excerpt']}",
            ]
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_failure_demo(assistant, output_path: Path) -> None:
    question = "What drone landing pad radius applies to rooftop aircraft operations?"
    result = assistant.answer(question, k=4)
    lines = [
        "# Demo Failure Case: Missing Evidence",
        "",
        "Synthetic demo output. Not legal, code, or professional compliance advice.",
        "",
        f"**Question:** {question}",
        "",
        "## Expected Behavior",
        "",
        "The synthetic corpus does not contain aviation or rooftop aircraft requirements, so the assistant should not invent a numeric answer.",
        "",
        "## Actual Local Response",
        "",
        str(result["answer"]),
        "",
        "## Retrieval Metadata",
        "",
        f"- Retrieved chunks: {result['retrieval']['result_count']}",
        f"- Sources: {result['sources']}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    docs = sorted((PROJECT_ROOT / "sample_data").glob("*.md"))
    eval_path = PROJECT_ROOT / "sample_data" / "evaluation_questions.json"
    output_dir = PROJECT_ROOT / "demo_outputs"
    output_dir.mkdir(exist_ok=True)

    assistant = build_assistant_from_paths(docs)
    cases = load_eval_cases(eval_path)
    payload = evaluate_retrieval(assistant, cases, k=4)

    (output_dir / "retrieval_eval_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_markdown_report(payload, output_dir / "retrieval_eval_report.md")
    _write_answer_demo(assistant, output_dir / "accessible_route_answer.md")
    _write_failure_demo(assistant, output_dir / "no_answer_failure_case.md")

    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote demo outputs to {output_dir}")


if __name__ == "__main__":
    main()
