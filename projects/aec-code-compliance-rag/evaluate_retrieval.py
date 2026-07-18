from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from aec_code_compliance_rag import (  # noqa: E402
    build_assistant_from_paths,
    downloaded_public_paths,
    evaluate_retrieval,
    evaluate_retrieval_modes,
    load_eval_cases,
)


def _stable_review_payload(payload: dict[str, object]) -> dict[str, object]:
    """Remove machine-dependent timings from versioned review artifacts."""
    stable = copy.deepcopy(payload)

    def strip_timings(value: object) -> None:
        if isinstance(value, dict):
            value.pop("latency_ms", None)
            value.pop("average_latency_ms", None)
            for child in value.values():
                strip_timings(child)
        elif isinstance(value, list):
            for child in value:
                strip_timings(child)

    strip_timings(stable)
    return stable


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _evaluation_provenance(
    *,
    corpus: str,
    corpus_label: str,
    docs: list[Path],
    manifest_path: Path | None,
    eval_path: Path,
) -> dict[str, object]:
    file_rows = [
        {"source": path.name, "sha256": _sha256_file(path)}
        for path in sorted(docs, key=lambda item: item.name)
    ]
    provenance: dict[str, object] = {
        "corpus": corpus,
        "corpus_label": corpus_label,
        "document_count": len(docs),
        "corpus_sha256": _canonical_sha256(file_rows),
        "eval_set": eval_path.name,
        "eval_set_sha256": _sha256_file(eval_path),
        "retrieval_k": 4,
        "versioned_latency_policy": "omitted_machine_dependent_timings",
    }
    if manifest_path:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        provenance.update(
            {
                "source_inventory_sha256": manifest["source_inventory_sha256"],
                "download_manifest_schema_version": manifest["schema_version"],
                "download_manifest_complete": manifest["is_complete"],
            }
        )
        if provenance["corpus_sha256"] != manifest["corpus_sha256"]:
            raise SystemExit(
                "Public corpus files do not match source_manifest.json. "
                "Run the public-source downloader again before evaluation."
            )
    return provenance


def _write_markdown_report(
    payload: dict[str, object], output_path: Path, *, corpus_label: str
) -> None:
    summary = payload["summary"]
    rows = payload["results"]
    lines = [
        "# Retrieval Evaluation Report",
        "",
        f"{corpus_label} evaluation for the AEC Code Compliance RAG Assistant.",
        "",
        "## Reproducibility Evidence",
        "",
        f"- Corpus documents: {payload['provenance']['document_count']}",
        f"- Corpus SHA-256: `{payload['provenance']['corpus_sha256']}`",
        f"- Eval-set SHA-256: `{payload['provenance']['eval_set_sha256']}`",
        f"- Eval set: `{payload['provenance']['eval_set']}`",
        "- Machine-dependent latency is measured at runtime and omitted from committed artifacts.",
        "",
        "## Summary",
        "",
        f"- Cases: {summary['case_count']}",
        f"- Answerable retrieval cases: {summary['answerable_case_count']}",
        f"- No-evidence cases: {summary['no_evidence_case_count']}",
        f"- Professional-review cases: {summary['professional_review_case_count']}",
        f"- Top-k: {summary['k']}",
        f"- Recall@k: {summary['recall_at_k']}",
        f"- Precision@k: {summary['precision_at_k']}",
        f"- Hit rate: {summary['hit_rate']}",
        f"- Mean reciprocal rank: {summary['mean_reciprocal_rank']}",
        f"- Section hit rate: {summary['section_hit_rate']}",
        f"- Citation coverage: {summary['citation_coverage']}",
        f"- Grounding check rate: {summary['grounding_check_rate']}",
        f"- Status accuracy: {summary['status_accuracy']}",
        f"- Citation check pass rate: {summary['citation_check_pass_rate']}",
        f"- Answer sentence support rate: {summary['answer_sentence_support_rate']}",
        f"- Unsupported answer sentence rate: {summary['unsupported_sentence_rate']}",
        f"- Hit@1: {summary['retrieval_hit_at_1']}",
        f"- Hit@3: {summary['retrieval_hit_at_3']}",
        f"- No-answer accuracy: {summary['no_answer_accuracy']}",
        f"- Unsupported-scope accuracy: {summary['unsupported_scope_accuracy']}",
        "",
        "## Results By Case Type",
        "",
        "| Case type | Cases | Answerable | Recall@k | MRR | Status accuracy |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case_type, metrics in summary["case_type_metrics"].items():
        lines.append(
            f"| {case_type} | {metrics['case_count']} | {metrics['answerable_case_count']} | "
            f"{metrics['recall_at_k']} | {metrics['mean_reciprocal_rank']} | "
            f"{metrics['status_accuracy']} |"
        )
    lines.extend(
        [
            "",
            "## Per-Question Results",
            "",
            "| ID | Type | Question | Expected status | Actual status | Expected section | Retrieved chunks | Recall@k | MRR | Grounding/no-answer check | Missing terms |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        chunks = ", ".join(row["retrieved_chunk_ids"])
        missing = ", ".join(row["missing_terms"]) or "None"
        lines.append(
            "| {case_id} | {case_type} | {question} | {expected_status} | {actual_status} | {section} | {chunks} | {recall} | {mrr} | {grounded} | {missing} |".format(
                case_id=row["case_id"],
                case_type=row["case_type"],
                question=str(row["question"]).replace("|", "\\|"),
                expected_status=row["expected_status"],
                actual_status=row["actual_status"],
                section=str(row["expected_section"]).replace("|", "\\|"),
                chunks=chunks.replace("|", "\\|"),
                recall=row["recall_at_k"],
                mrr=row["reciprocal_rank"],
                grounded=row["simple_grounding_check"],
                missing=missing.replace("|", "\\|"),
            )
        )
    while lines and not lines[-1]:
        lines.pop()
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_failure_analysis(
    payload: dict[str, object], output_path: Path, *, corpus_label: str
) -> None:
    failures = [
        row
        for row in payload["results"]
        if not row["status_correct"]
        or (row["expected_status"] == "answered" and row["recall_at_k"] < 1.0)
        or not row["citation_check_passed"]
        or row["missing_terms"]
    ]
    lines = [
        "# AEC RAG Failure Analysis",
        "",
        (
            f"{corpus_label} evaluation failures and weak spots. These are not "
            "hidden; they are the next engineering work items."
        ),
        "",
        f"- Total cases: {payload['summary']['case_count']}",
        f"- Flagged cases: {len(failures)}",
        f"- Corpus SHA-256: `{payload['provenance']['corpus_sha256']}`",
        "",
    ]
    if not failures:
        lines.append(f"No failures were flagged in the current {corpus_label.lower()} eval set.")
    for row in failures[:20]:
        lines.extend(
            [
                f"## {row['question']}",
                "",
                f"- Expected status: {row['expected_status']}",
                f"- Actual status: {row['actual_status']}",
                f"- Expected source: {row['expected_source']}",
                f"- Retrieved sources: {', '.join(row['retrieved_sources']) or 'None'}",
                f"- Missing terms: {', '.join(row['missing_terms']) or 'None'}",
                f"- Citation check passed: {row['citation_check_passed']}",
                "",
            ]
        )
    while lines and not lines[-1]:
        lines.pop()
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_ablation_report(
    payload: dict[str, object], output_path: Path, *, corpus_label: str
) -> None:
    lines = [
        "# Retrieval Mode Ablation",
        "",
        f"{corpus_label} comparison of local retrieval modes over the same AEC eval set.",
        "",
        f"Corpus SHA-256: `{payload['provenance']['corpus_sha256']}`",
        f"Eval-set SHA-256: `{payload['provenance']['eval_set_sha256']}`",
        "",
        "| Mode | Recall@k | MRR | Hit@3 | Citation coverage | Status accuracy |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["ranked_modes"]:
        lines.append(
            "| {mode} | {recall} | {mrr} | {hit3} | {coverage} | {status} |".format(
                mode=row["mode"],
                recall=row["recall_at_k"],
                mrr=row["mean_reciprocal_rank"],
                hit3=row["retrieval_hit_at_3"],
                coverage=row["citation_coverage"],
                status=row["status_accuracy"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `tfidf` and `bm25` are transparent lexical baselines.",
            "- `dense_lsa` is a local dense baseline using TF-IDF projected into latent semantic analysis space.",
            "- `hybrid` is the default app mode because it combines lexical evidence and a lightweight rerank boost.",
            "- These numbers are local regression checks, not production compliance accuracy.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_source_lines(lines: list[str], sources: list[dict[str, object]]) -> None:
    if not sources:
        lines.append("- No sources returned.")
        return
    for source in sources:
        page = f", page {source['page']}" if source["page"] else ""
        publisher = f" ({source['publisher']})" if source.get("publisher") else ""
        source_url = source.get("source_url")
        lines.extend(
            [
                f"- {source['reference']}{publisher} - score `{source['score']}`",
                f"  - Chunk: `{source['chunk_id']}`{page}",
                f"  - Excerpt: {source['excerpt']}",
            ]
        )
        if source_url:
            lines.append(f"  - Official source: {source_url}")


def _write_answer_demo(
    assistant,
    output_path: Path,
    *,
    question: str,
    title: str,
    corpus_label: str,
    provenance: dict[str, object],
) -> None:
    result = assistant.answer(question, k=4)
    lines = [
        f"# Demo Answer: {title}",
        "",
        (
            f"{corpus_label} demo output. Not legal, code, engineering, "
            "architectural, or professional compliance advice."
        ),
        "",
        f"**Corpus SHA-256:** `{provenance['corpus_sha256']}`",
        "",
        f"**Question:** {question}",
        "",
        "## Grounded Answer",
        "",
        str(result["answer"]),
        "",
        "## Source Status",
        "",
        "```json",
        json.dumps(result.get("source_status", {}), indent=2),
        "```",
        "",
        "## Citations",
        "",
    ]
    _append_source_lines(lines, result["sources"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_failure_demo(
    assistant,
    output_path: Path,
    *,
    question: str,
    expected_behavior: str,
    corpus_label: str,
    provenance: dict[str, object],
) -> None:
    result = assistant.answer(question, k=4)
    lines = [
        "# Demo Abstention Case",
        "",
        (
            f"{corpus_label} demo output. Not legal, code, engineering, "
            "architectural, or professional compliance advice."
        ),
        "",
        f"**Corpus SHA-256:** `{provenance['corpus_sha256']}`",
        "",
        f"**Question:** {question}",
        "",
        "## Expected Behavior",
        "",
        expected_behavior,
        "",
        "## Actual Local Response",
        "",
        str(result["answer"]),
        "",
        "## Retrieval Metadata",
        "",
        f"- Retrieved chunks: {result['retrieval']['result_count']}",
        f"- Status: {result['status']}",
        "",
        "## Sources",
        "",
    ]
    _append_source_lines(lines, result.get("sources", []))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _corpus_paths(corpus: str) -> tuple[list[Path], Path | None, Path, str]:
    if corpus == "public":
        docs = downloaded_public_paths(PROJECT_ROOT / "public_sources" / "downloaded")
        if not docs:
            raise SystemExit(
                "Singapore public-source corpus is missing. Run "
                "`python projects/aec-code-compliance-rag/scripts/download_public_sources.py` first."
            )
        manifest_path = PROJECT_ROOT / "public_sources" / "downloaded" / "source_manifest.json"
        if not manifest_path.exists():
            raise SystemExit("Public source_manifest.json is missing. Run the downloader again.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not manifest.get("is_complete") or manifest.get("document_count") != len(docs):
            raise SystemExit(
                "Public corpus download is incomplete. Resolve downloader failures before evaluation."
            )
        return (
            docs,
            manifest_path,
            PROJECT_ROOT / "eval" / "public_eval_cases.jsonl",
            "Singapore public-source",
        )
    docs = sorted(
        [
            *(PROJECT_ROOT / "sample_data").glob("*.md"),
            *(PROJECT_ROOT / "sample_data").glob("*.pdf"),
        ]
    )
    return docs, None, PROJECT_ROOT / "eval" / "eval_cases.jsonl", "Synthetic demo"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the AEC RAG retrieval workflow.")
    parser.add_argument(
        "--corpus",
        choices=["synthetic", "public"],
        default="synthetic",
        help="Use synthetic regression docs or downloaded Singapore public sources.",
    )
    args = parser.parse_args()
    docs, manifest_path, eval_path, corpus_label = _corpus_paths(args.corpus)
    if not eval_path.exists():
        eval_path = PROJECT_ROOT / "sample_data" / "evaluation_questions.json"
    output_dir = PROJECT_ROOT / "demo_outputs"
    if args.corpus == "public":
        output_dir = output_dir / "public_sources"
    output_dir.mkdir(parents=True, exist_ok=True)

    assistant = build_assistant_from_paths(docs, manifest_path=manifest_path)
    cases = load_eval_cases(eval_path)
    provenance = _evaluation_provenance(
        corpus=args.corpus,
        corpus_label=corpus_label,
        docs=docs,
        manifest_path=manifest_path,
        eval_path=eval_path,
    )
    payload = evaluate_retrieval(assistant, cases, k=4)
    ablation_payload = evaluate_retrieval_modes(
        docs,
        cases,
        k=4,
        manifest_path=manifest_path,
        chunks=assistant.chunks,
    )
    stable_payload = {
        "artifact_schema_version": "2.0",
        "provenance": provenance,
        **_stable_review_payload(payload),
    }
    stable_ablation_payload = {
        "artifact_schema_version": "2.0",
        "provenance": provenance,
        **_stable_review_payload(ablation_payload),
    }

    (output_dir / "retrieval_eval_summary.json").write_text(
        json.dumps(stable_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "retrieval_ablation_summary.json").write_text(
        json.dumps(stable_ablation_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "evaluation_manifest.json").write_text(
        json.dumps(
            {
                "artifact_schema_version": "2.0",
                "provenance": provenance,
                "summary": stable_payload["summary"],
                "ranked_modes": stable_ablation_payload["ranked_modes"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_markdown_report(
        stable_payload, output_dir / "retrieval_eval_report.md", corpus_label=corpus_label
    )
    _write_ablation_report(
        stable_ablation_payload,
        output_dir / "retrieval_ablation_report.md",
        corpus_label=corpus_label,
    )
    _write_failure_analysis(
        stable_payload,
        output_dir / "failure_analysis.md",
        corpus_label=corpus_label,
    )
    if args.corpus == "public":
        answer_question = (
            "What does the BCA Code on Accessibility 2025 set out for accessible "
            "and inclusive buildings?"
        )
        abstention_question = (
            "Can this assistant certify a Singapore building plan for BCA approval?"
        )
        abstention_expected = (
            "The assistant should refuse certification or approval language and route the "
            "question to professional review instead of implying authority."
        )
        title = "BCA Accessibility Source Review"
    else:
        answer_question = "What clear width should be checked for high traffic accessible routes?"
        abstention_question = (
            "What drone landing pad radius applies to rooftop aircraft operations?"
        )
        abstention_expected = (
            "The synthetic corpus does not contain aviation or rooftop aircraft requirements, "
            "so the assistant should not invent a numeric answer."
        )
        title = "Accessible Route Review"
    _write_answer_demo(
        assistant,
        output_dir / "accessible_route_answer.md",
        question=answer_question,
        title=title,
        corpus_label=corpus_label,
        provenance=provenance,
    )
    _write_answer_demo(
        assistant,
        output_dir / "sample_answer_accessible_route.md",
        question=answer_question,
        title=title,
        corpus_label=corpus_label,
        provenance=provenance,
    )
    _write_failure_demo(
        assistant,
        output_dir / "no_answer_failure_case.md",
        question=abstention_question,
        expected_behavior=abstention_expected,
        corpus_label=corpus_label,
        provenance=provenance,
    )
    _write_failure_demo(
        assistant,
        output_dir / "sample_answer_no_evidence.md",
        question=abstention_question,
        expected_behavior=abstention_expected,
        corpus_label=corpus_label,
        provenance=provenance,
    )

    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote demo outputs to {output_dir}")


if __name__ == "__main__":
    main()
