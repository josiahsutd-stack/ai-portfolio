from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from time import perf_counter

from .assistant import RAGAssistant


@dataclass(frozen=True)
class RetrievalEvalCase:
    question: str
    expected_source: str
    expected_terms: list[str]
    expected_section: str | None = None
    expected_no_answer: bool = False
    expected_status: str = "answered"
    case_type: str = "answerable_direct"
    expected_clause_ids: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class RetrievalEvalResult:
    question: str
    expected_source: str
    expected_section: str | None
    retrieved_chunk_ids: list[str]
    retrieved_sources: list[str]
    retrieved_sections: list[str]
    recall_at_k: float
    precision_at_k: float
    hit_rate: float
    reciprocal_rank: float
    section_hit: bool
    citation_coverage: float
    no_answer_correct: bool
    expected_status: str
    actual_status: str
    status_correct: bool
    citation_check_passed: bool
    latency_ms: int
    simple_grounding_check: bool
    missing_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "question": self.question,
            "expected_source": self.expected_source,
            "expected_section": self.expected_section,
            "retrieved_chunk_ids": self.retrieved_chunk_ids,
            "retrieved_sources": self.retrieved_sources,
            "retrieved_sections": self.retrieved_sections,
            "recall_at_k": self.recall_at_k,
            "precision_at_k": self.precision_at_k,
            "hit_rate": self.hit_rate,
            "reciprocal_rank": self.reciprocal_rank,
            "section_hit": self.section_hit,
            "citation_coverage": self.citation_coverage,
            "no_answer_correct": self.no_answer_correct,
            "expected_status": self.expected_status,
            "actual_status": self.actual_status,
            "status_correct": self.status_correct,
            "citation_check_passed": self.citation_check_passed,
            "latency_ms": self.latency_ms,
            "simple_grounding_check": self.simple_grounding_check,
            "missing_terms": self.missing_terms,
        }


def load_eval_cases(path: str | Path) -> list[RetrievalEvalCase]:
    target = Path(path)
    if target.suffix == ".jsonl":
        rows = [
            json.loads(line)
            for line in target.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        rows = json.loads(target.read_text(encoding="utf-8"))
    return [
        RetrievalEvalCase(
            question=row["question"],
            expected_source=row["expected_source"],
            expected_terms=list(row.get("expected_terms", [])),
            expected_section=row.get("expected_section"),
            expected_no_answer=bool(row.get("expected_no_answer", False)),
            expected_status=row.get(
                "expected_status", "no_evidence" if row.get("expected_no_answer") else "answered"
            ),
            case_type=row.get("case_type", "answerable_direct"),
            expected_clause_ids=list(row.get("expected_clause_ids", [])),
            notes=row.get("notes", ""),
        )
        for row in rows
    ]


def evaluate_retrieval(
    assistant: RAGAssistant,
    cases: list[RetrievalEvalCase],
    *,
    k: int = 4,
) -> dict[str, object]:
    results: list[RetrievalEvalResult] = []
    for case in cases:
        expected_status = (
            "no_evidence"
            if case.expected_no_answer and case.expected_status == "answered"
            else case.expected_status
        )
        started = perf_counter()
        answer_payload = assistant.answer(case.question, k=k)
        latency_ms = int((perf_counter() - started) * 1000)
        actual_status = str(answer_payload.get("status", "answered"))
        citation_check_passed = bool(
            answer_payload.get("citation_check", {"passed": actual_status != "answered"}).get(
                "passed"
            )
        )
        retrieved = assistant.retrieve(case.question, k=k)
        if case.expected_no_answer:
            no_answer_correct = actual_status == "no_evidence"
            results.append(
                RetrievalEvalResult(
                    question=case.question,
                    expected_source=case.expected_source,
                    expected_section=case.expected_section,
                    retrieved_chunk_ids=[
                        str(result.metadata.get("chunk_id", "")) for result in retrieved
                    ],
                    retrieved_sources=[result.source for result in retrieved],
                    retrieved_sections=[
                        str(result.metadata.get("section", "")) for result in retrieved
                    ],
                    recall_at_k=1.0 if no_answer_correct else 0.0,
                    precision_at_k=1.0 if no_answer_correct else 0.0,
                    hit_rate=1.0 if no_answer_correct else 0.0,
                    reciprocal_rank=1.0 if no_answer_correct else 0.0,
                    section_hit=no_answer_correct,
                    citation_coverage=1.0 if no_answer_correct else 0.0,
                    no_answer_correct=no_answer_correct,
                    expected_status=expected_status,
                    actual_status=actual_status,
                    status_correct=actual_status == expected_status,
                    citation_check_passed=citation_check_passed,
                    latency_ms=latency_ms,
                    simple_grounding_check=no_answer_correct,
                    missing_terms=[],
                )
            )
            continue
        retrieved_sources = [result.source for result in retrieved]
        retrieved_sections = [str(result.metadata.get("section", "")) for result in retrieved]
        retrieved_text = "\n".join(result.text.lower() for result in retrieved)
        source_hits = [source == case.expected_source for source in retrieved_sources]
        section_hit = (
            True
            if not case.expected_section
            else any(
                section.lower() == case.expected_section.lower() for section in retrieved_sections
            )
        )
        missing_terms = [term for term in case.expected_terms if term.lower() not in retrieved_text]
        precision = sum(source_hits) / max(1, len(retrieved))
        recall = 1.0 if any(source_hits) else 0.0
        first_relevant_rank = next(
            (index + 1 for index, hit in enumerate(source_hits) if hit),
            None,
        )
        reciprocal_rank = 1.0 / first_relevant_rank if first_relevant_rank else 0.0
        coverage = (len(case.expected_terms) - len(missing_terms)) / max(
            1, len(case.expected_terms)
        )
        simple_grounding_check = bool(retrieved) and not missing_terms and section_hit
        results.append(
            RetrievalEvalResult(
                question=case.question,
                expected_source=case.expected_source,
                expected_section=case.expected_section,
                retrieved_chunk_ids=[
                    str(result.metadata.get("chunk_id", "")) for result in retrieved
                ],
                retrieved_sources=retrieved_sources,
                retrieved_sections=retrieved_sections,
                recall_at_k=round(recall, 3),
                precision_at_k=round(precision, 3),
                hit_rate=round(recall, 3),
                reciprocal_rank=round(reciprocal_rank, 3),
                section_hit=section_hit,
                citation_coverage=round(coverage, 3),
                no_answer_correct=False,
                expected_status=expected_status,
                actual_status=actual_status,
                status_correct=actual_status == expected_status,
                citation_check_passed=citation_check_passed,
                latency_ms=latency_ms,
                simple_grounding_check=simple_grounding_check,
                missing_terms=missing_terms,
            )
        )
    summary = {
        "case_count": len(results),
        "k": k,
        "recall_at_k": (
            round(mean([result.recall_at_k for result in results]), 3) if results else 0.0
        ),
        "precision_at_k": (
            round(mean([result.precision_at_k for result in results]), 3) if results else 0.0
        ),
        "hit_rate": round(mean([result.hit_rate for result in results]), 3) if results else 0.0,
        "mean_reciprocal_rank": (
            round(mean([result.reciprocal_rank for result in results]), 3) if results else 0.0
        ),
        "section_hit_rate": (
            round(mean([1.0 if result.section_hit else 0.0 for result in results]), 3)
            if results
            else 0.0
        ),
        "citation_coverage": (
            round(mean([result.citation_coverage for result in results]), 3) if results else 0.0
        ),
        "grounding_check_rate": (
            round(mean([1.0 if result.simple_grounding_check else 0.0 for result in results]), 3)
            if results
            else 0.0
        ),
        "status_accuracy": (
            round(mean([1.0 if result.status_correct else 0.0 for result in results]), 3)
            if results
            else 0.0
        ),
        "citation_check_pass_rate": (
            round(mean([1.0 if result.citation_check_passed else 0.0 for result in results]), 3)
            if results
            else 0.0
        ),
        "average_latency_ms": (
            round(mean([result.latency_ms for result in results]), 2) if results else 0.0
        ),
        "retrieval_hit_at_1": (
            round(
                mean(
                    [
                        (
                            1.0
                            if result.expected_source in result.retrieved_sources[:1]
                            or result.expected_source == "__NO_ANSWER__"
                            else 0.0
                        )
                        for result in results
                    ]
                ),
                3,
            )
            if results
            else 0.0
        ),
        "retrieval_hit_at_3": (
            round(
                mean(
                    [
                        (
                            1.0
                            if result.expected_source in result.retrieved_sources[:3]
                            or result.expected_source == "__NO_ANSWER__"
                            else 0.0
                        )
                        for result in results
                    ]
                ),
                3,
            )
            if results
            else 0.0
        ),
        "no_answer_accuracy": (
            round(
                mean(
                    [
                        1.0 if result.no_answer_correct else 0.0
                        for result in results
                        if result.expected_status == "no_evidence"
                    ]
                ),
                3,
            )
            if any(result.expected_status == "no_evidence" for result in results)
            else None
        ),
        "unsupported_scope_accuracy": (
            round(
                mean(
                    [
                        1.0 if result.status_correct else 0.0
                        for result in results
                        if result.expected_status
                        in {"unsupported_scope", "needs_professional_review"}
                    ]
                ),
                3,
            )
            if any(
                result.expected_status in {"unsupported_scope", "needs_professional_review"}
                for result in results
            )
            else None
        ),
    }
    return {"summary": summary, "results": [result.to_dict() for result in results]}


def evaluate_retrieval_modes(
    paths: list[str | Path],
    cases: list[RetrievalEvalCase],
    *,
    modes: tuple[str, ...] = ("tfidf", "bm25", "dense_lsa", "hybrid"),
    k: int = 4,
) -> dict[str, object]:
    from .assistant import build_assistant_from_paths

    mode_payloads: dict[str, dict[str, object]] = {}
    for mode in modes:
        assistant = build_assistant_from_paths(paths, retrieval_mode=mode)
        payload = evaluate_retrieval(assistant, cases, k=k)
        mode_payloads[mode] = {
            "summary": payload["summary"],
            "result_count": len(payload["results"]),
        }
    ranked_modes = sorted(
        (
            {
                "mode": mode,
                "recall_at_k": summary["summary"]["recall_at_k"],
                "mean_reciprocal_rank": summary["summary"]["mean_reciprocal_rank"],
                "retrieval_hit_at_3": summary["summary"]["retrieval_hit_at_3"],
                "citation_coverage": summary["summary"]["citation_coverage"],
                "status_accuracy": summary["summary"]["status_accuracy"],
            }
            for mode, summary in mode_payloads.items()
        ),
        key=lambda row: (
            float(row["status_accuracy"]),
            float(row["retrieval_hit_at_3"]),
            float(row["recall_at_k"]),
            float(row["mean_reciprocal_rank"]),
        ),
        reverse=True,
    )
    return {
        "k": k,
        "modes": list(modes),
        "ranked_modes": ranked_modes,
        "results": mode_payloads,
    }
