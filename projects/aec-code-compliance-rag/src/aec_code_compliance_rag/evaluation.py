from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from time import perf_counter

from shared.ai import SearchResult

from .assistant import RAGAssistant
from .chunking import DocumentChunk


@dataclass(frozen=True)
class RetrievalEvalCase:
    question: str
    expected_source: str
    expected_terms: list[str]
    expected_section: str | None = None
    expected_no_answer: bool = False
    expected_status: str = "answered"
    case_type: str = "answerable_direct"
    case_id: str = ""
    expected_clause_ids: list[str] = field(default_factory=list)
    expected_pages: list[int] = field(default_factory=list)
    expected_chunk_ids: list[str] = field(default_factory=list)
    label_source: str = ""
    notes: str = ""


@dataclass(frozen=True)
class RetrievalEvalResult:
    case_id: str
    case_type: str
    question: str
    expected_source: str
    expected_section: str | None
    expected_pages: list[int]
    expected_chunk_ids: list[str]
    label_source: str
    retrieved_chunk_ids: list[str]
    retrieved_sources: list[str]
    retrieved_sections: list[str]
    retrieved_pages: list[int | None]
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
    answer_sentence_count: int
    answer_sentence_support_rate: float
    unsupported_sentence_count: int
    citation_warning_count: int
    latency_ms: int
    simple_grounding_check: bool
    evidence_target_hit_at_1: bool | None
    evidence_target_hit_at_3: bool | None
    evidence_target_hit_at_k: bool | None
    evidence_target_reciprocal_rank: float | None
    page_target_hit_at_1: bool | None
    page_target_hit_at_3: bool | None
    page_target_hit_at_k: bool | None
    page_target_reciprocal_rank: float | None
    missing_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "case_type": self.case_type,
            "question": self.question,
            "expected_source": self.expected_source,
            "expected_section": self.expected_section,
            "expected_pages": self.expected_pages,
            "expected_chunk_ids": self.expected_chunk_ids,
            "label_source": self.label_source,
            "retrieved_chunk_ids": self.retrieved_chunk_ids,
            "retrieved_sources": self.retrieved_sources,
            "retrieved_sections": self.retrieved_sections,
            "retrieved_pages": self.retrieved_pages,
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
            "answer_sentence_count": self.answer_sentence_count,
            "answer_sentence_support_rate": self.answer_sentence_support_rate,
            "unsupported_sentence_count": self.unsupported_sentence_count,
            "citation_warning_count": self.citation_warning_count,
            "latency_ms": self.latency_ms,
            "simple_grounding_check": self.simple_grounding_check,
            "evidence_target_hit_at_1": self.evidence_target_hit_at_1,
            "evidence_target_hit_at_3": self.evidence_target_hit_at_3,
            "evidence_target_hit_at_k": self.evidence_target_hit_at_k,
            "evidence_target_reciprocal_rank": self.evidence_target_reciprocal_rank,
            "page_target_hit_at_1": self.page_target_hit_at_1,
            "page_target_hit_at_3": self.page_target_hit_at_3,
            "page_target_hit_at_k": self.page_target_hit_at_k,
            "page_target_reciprocal_rank": self.page_target_reciprocal_rank,
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
            case_id=row.get("id", ""),
            expected_clause_ids=list(row.get("expected_clause_ids", [])),
            expected_pages=[int(page) for page in row.get("expected_pages", [])],
            expected_chunk_ids=list(row.get("expected_chunk_ids", [])),
            label_source=str(row.get("label_source", "")),
            notes=row.get("notes", ""),
        )
        for row in rows
    ]


def validate_retrieval_eval_targets(
    cases: list[RetrievalEvalCase],
    chunks: list[DocumentChunk],
    *,
    require_answerable_targets: bool = False,
) -> dict[str, object]:
    """Validate manually labeled target IDs against the indexed corpus."""
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    if len(chunks_by_id) != len(chunks):
        raise ValueError("Indexed chunks must have unique chunk IDs for target validation.")
    seen_case_ids: set[str] = set()
    answerable_count = 0
    labeled_answerable_count = 0
    page_labeled_answerable_count = 0
    target_chunk_count = 0
    label_sources: dict[str, int] = {}
    for index, case in enumerate(cases, start=1):
        case_id = case.case_id or f"case-{index:03d}"
        if case_id in seen_case_ids:
            raise ValueError(f"Duplicate evaluation case ID: {case_id}")
        seen_case_ids.add(case_id)
        expected_status = (
            "no_evidence"
            if case.expected_no_answer and case.expected_status == "answered"
            else case.expected_status
        )
        answerable = expected_status == "answered" and case.expected_source != "__NO_ANSWER__"
        if answerable:
            answerable_count += 1
            if require_answerable_targets and not case.expected_chunk_ids:
                raise ValueError(f"Answerable case {case_id} is missing expected_chunk_ids.")
        elif case.expected_chunk_ids or case.expected_pages:
            raise ValueError(f"Non-answerable case {case_id} must not define retrieval targets.")
        if not case.expected_chunk_ids:
            continue
        if len(set(case.expected_chunk_ids)) != len(case.expected_chunk_ids):
            raise ValueError(f"Case {case_id} contains duplicate expected_chunk_ids.")
        if not case.label_source:
            raise ValueError(f"Case {case_id} must identify the target label source.")
        target_chunks: list[DocumentChunk] = []
        for chunk_id in case.expected_chunk_ids:
            chunk = chunks_by_id.get(chunk_id)
            if chunk is None:
                raise ValueError(f"Case {case_id} references missing target chunk {chunk_id}.")
            if chunk.source != case.expected_source:
                raise ValueError(
                    f"Case {case_id} target chunk {chunk_id} belongs to {chunk.source}, "
                    f"not {case.expected_source}."
                )
            target_chunks.append(chunk)
        target_pages = {chunk.page for chunk in target_chunks if chunk.page is not None}
        if target_pages != set(case.expected_pages):
            raise ValueError(
                f"Case {case_id} expected_pages {case.expected_pages} do not match target "
                f"chunk pages {sorted(target_pages)}."
            )
        labeled_answerable_count += int(answerable)
        page_labeled_answerable_count += int(answerable and bool(case.expected_pages))
        target_chunk_count += len(target_chunks)
        label_sources[case.label_source] = label_sources.get(case.label_source, 0) + 1
    return {
        "case_count": len(cases),
        "answerable_case_count": answerable_count,
        "labeled_answerable_case_count": labeled_answerable_count,
        "page_labeled_answerable_case_count": page_labeled_answerable_count,
        "target_chunk_count": target_chunk_count,
        "label_sources": dict(sorted(label_sources.items())),
        "answerable_target_coverage": round(labeled_answerable_count / max(1, answerable_count), 3),
    }


def _target_metrics(
    case: RetrievalEvalCase,
    retrieved: list[SearchResult],
    *,
    k: int,
) -> dict[str, object]:
    retrieved_chunk_ids = [str(result.metadata.get("chunk_id", "")) for result in retrieved]
    retrieved_pages = [
        int(result.metadata["page"]) if result.metadata.get("page") not in {None, ""} else None
        for result in retrieved
    ]
    expected_chunk_ids = set(case.expected_chunk_ids)
    chunk_ranks = [
        index
        for index, chunk_id in enumerate(retrieved_chunk_ids, start=1)
        if chunk_id in expected_chunk_ids
    ]
    expected_pages = set(case.expected_pages)
    page_ranks = [
        index
        for index, result in enumerate(retrieved, start=1)
        if result.source == case.expected_source
        and result.metadata.get("page") not in {None, ""}
        and int(result.metadata["page"]) in expected_pages
    ]

    def ranked_metrics(ranks: list[int], *, labeled: bool, prefix: str) -> dict[str, object]:
        if not labeled:
            return {
                f"{prefix}_hit_at_1": None,
                f"{prefix}_hit_at_3": None,
                f"{prefix}_hit_at_k": None,
                f"{prefix}_reciprocal_rank": None,
            }
        first_rank = min(ranks) if ranks else None
        return {
            f"{prefix}_hit_at_1": bool(first_rank and first_rank <= 1),
            f"{prefix}_hit_at_3": bool(first_rank and first_rank <= 3),
            f"{prefix}_hit_at_k": bool(first_rank and first_rank <= k),
            f"{prefix}_reciprocal_rank": round(1.0 / first_rank, 3) if first_rank else 0.0,
        }

    return {
        "expected_pages": list(case.expected_pages),
        "expected_chunk_ids": list(case.expected_chunk_ids),
        "label_source": case.label_source,
        "retrieved_pages": retrieved_pages,
        **ranked_metrics(
            chunk_ranks,
            labeled=bool(case.expected_chunk_ids),
            prefix="evidence_target",
        ),
        **ranked_metrics(
            page_ranks,
            labeled=bool(case.expected_pages),
            prefix="page_target",
        ),
    }


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
        citation_check = answer_payload.get(
            "citation_check", {"passed": actual_status != "answered"}
        )
        citation_check_passed = bool(citation_check.get("passed"))
        sentence_count = int(citation_check.get("sentence_count", 0))
        unsupported_sentence_count = len(citation_check.get("unsupported_sentences", []))
        citation_warning_count = len(citation_check.get("warnings", []))
        answer_sentence_support_rate = (
            round((sentence_count - unsupported_sentence_count) / sentence_count, 3)
            if sentence_count
            else 1.0
        )
        if actual_status in {"unsupported_scope", "needs_professional_review"}:
            retrieved = []
        else:
            retrieved = assistant.retrieve(case.question, k=k)
        if case.expected_no_answer:
            no_answer_correct = actual_status == "no_evidence"
            results.append(
                RetrievalEvalResult(
                    case_id=case.case_id,
                    case_type=case.case_type,
                    question=case.question,
                    expected_source=case.expected_source,
                    expected_section=case.expected_section,
                    **_target_metrics(case, retrieved, k=k),
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
                    answer_sentence_count=sentence_count,
                    answer_sentence_support_rate=answer_sentence_support_rate,
                    unsupported_sentence_count=unsupported_sentence_count,
                    citation_warning_count=citation_warning_count,
                    latency_ms=latency_ms,
                    simple_grounding_check=no_answer_correct,
                    missing_terms=[],
                )
            )
            continue
        if expected_status in {"unsupported_scope", "needs_professional_review"}:
            status_correct = actual_status == expected_status
            results.append(
                RetrievalEvalResult(
                    case_id=case.case_id,
                    case_type=case.case_type,
                    question=case.question,
                    expected_source=case.expected_source,
                    expected_section=case.expected_section,
                    **_target_metrics(case, retrieved, k=k),
                    retrieved_chunk_ids=[],
                    retrieved_sources=[],
                    retrieved_sections=[],
                    recall_at_k=0.0,
                    precision_at_k=0.0,
                    hit_rate=0.0,
                    reciprocal_rank=0.0,
                    section_hit=status_correct,
                    citation_coverage=1.0 if status_correct else 0.0,
                    no_answer_correct=False,
                    expected_status=expected_status,
                    actual_status=actual_status,
                    status_correct=status_correct,
                    citation_check_passed=citation_check_passed,
                    answer_sentence_count=sentence_count,
                    answer_sentence_support_rate=answer_sentence_support_rate,
                    unsupported_sentence_count=unsupported_sentence_count,
                    citation_warning_count=citation_warning_count,
                    latency_ms=latency_ms,
                    simple_grounding_check=status_correct,
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
                case_id=case.case_id,
                case_type=case.case_type,
                question=case.question,
                expected_source=case.expected_source,
                expected_section=case.expected_section,
                **_target_metrics(case, retrieved, k=k),
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
                answer_sentence_count=sentence_count,
                answer_sentence_support_rate=answer_sentence_support_rate,
                unsupported_sentence_count=unsupported_sentence_count,
                citation_warning_count=citation_warning_count,
                latency_ms=latency_ms,
                simple_grounding_check=simple_grounding_check,
                missing_terms=missing_terms,
            )
        )
    answerable_results = [
        result
        for result in results
        if result.expected_status == "answered" and result.expected_source != "__NO_ANSWER__"
    ]
    evidence_target_results = [
        result for result in answerable_results if result.evidence_target_hit_at_1 is not None
    ]
    page_target_results = [
        result for result in answerable_results if result.page_target_hit_at_1 is not None
    ]
    case_type_metrics: dict[str, dict[str, object]] = {}
    for case_type in sorted({result.case_type for result in results}):
        typed_results = [result for result in results if result.case_type == case_type]
        typed_answerable = [
            result
            for result in typed_results
            if result.expected_status == "answered" and result.expected_source != "__NO_ANSWER__"
        ]
        typed_evidence_targets = [
            result for result in typed_answerable if result.evidence_target_hit_at_1 is not None
        ]
        case_type_metrics[case_type] = {
            "case_count": len(typed_results),
            "answerable_case_count": len(typed_answerable),
            "recall_at_k": (
                round(mean([result.recall_at_k for result in typed_answerable]), 3)
                if typed_answerable
                else None
            ),
            "mean_reciprocal_rank": (
                round(mean([result.reciprocal_rank for result in typed_answerable]), 3)
                if typed_answerable
                else None
            ),
            "evidence_target_case_count": len(typed_evidence_targets),
            "evidence_target_hit_at_1": (
                round(
                    mean(
                        [
                            1.0 if result.evidence_target_hit_at_1 else 0.0
                            for result in typed_evidence_targets
                        ]
                    ),
                    3,
                )
                if typed_evidence_targets
                else None
            ),
            "evidence_target_mean_reciprocal_rank": (
                round(
                    mean(
                        [
                            float(result.evidence_target_reciprocal_rank)
                            for result in typed_evidence_targets
                        ]
                    ),
                    3,
                )
                if typed_evidence_targets
                else None
            ),
            "status_accuracy": round(
                mean([1.0 if result.status_correct else 0.0 for result in typed_results]), 3
            ),
        }
    summary = {
        "case_count": len(results),
        "answerable_case_count": len(answerable_results),
        "no_evidence_case_count": sum(
            result.expected_status == "no_evidence" for result in results
        ),
        "professional_review_case_count": sum(
            result.expected_status == "needs_professional_review" for result in results
        ),
        "evidence_target_case_count": len(evidence_target_results),
        "page_target_case_count": len(page_target_results),
        "case_type_metrics": case_type_metrics,
        "k": k,
        "recall_at_k": (
            round(mean([result.recall_at_k for result in answerable_results]), 3)
            if answerable_results
            else 0.0
        ),
        "precision_at_k": (
            round(mean([result.precision_at_k for result in answerable_results]), 3)
            if answerable_results
            else 0.0
        ),
        "hit_rate": (
            round(mean([result.hit_rate for result in answerable_results]), 3)
            if answerable_results
            else 0.0
        ),
        "mean_reciprocal_rank": (
            round(mean([result.reciprocal_rank for result in answerable_results]), 3)
            if answerable_results
            else 0.0
        ),
        "evidence_target_hit_at_1": (
            round(
                mean(
                    [
                        1.0 if result.evidence_target_hit_at_1 else 0.0
                        for result in evidence_target_results
                    ]
                ),
                3,
            )
            if evidence_target_results
            else None
        ),
        "evidence_target_hit_at_3": (
            round(
                mean(
                    [
                        1.0 if result.evidence_target_hit_at_3 else 0.0
                        for result in evidence_target_results
                    ]
                ),
                3,
            )
            if evidence_target_results
            else None
        ),
        "evidence_target_hit_at_k": (
            round(
                mean(
                    [
                        1.0 if result.evidence_target_hit_at_k else 0.0
                        for result in evidence_target_results
                    ]
                ),
                3,
            )
            if evidence_target_results
            else None
        ),
        "evidence_target_mean_reciprocal_rank": (
            round(
                mean(
                    [
                        float(result.evidence_target_reciprocal_rank)
                        for result in evidence_target_results
                    ]
                ),
                3,
            )
            if evidence_target_results
            else None
        ),
        "page_target_hit_at_1": (
            round(
                mean(
                    [1.0 if result.page_target_hit_at_1 else 0.0 for result in page_target_results]
                ),
                3,
            )
            if page_target_results
            else None
        ),
        "page_target_hit_at_3": (
            round(
                mean(
                    [1.0 if result.page_target_hit_at_3 else 0.0 for result in page_target_results]
                ),
                3,
            )
            if page_target_results
            else None
        ),
        "page_target_hit_at_k": (
            round(
                mean(
                    [1.0 if result.page_target_hit_at_k else 0.0 for result in page_target_results]
                ),
                3,
            )
            if page_target_results
            else None
        ),
        "page_target_mean_reciprocal_rank": (
            round(
                mean([float(result.page_target_reciprocal_rank) for result in page_target_results]),
                3,
            )
            if page_target_results
            else None
        ),
        "section_hit_rate": (
            round(
                mean([1.0 if result.section_hit else 0.0 for result in answerable_results]),
                3,
            )
            if answerable_results
            else 0.0
        ),
        "citation_coverage": (
            round(mean([result.citation_coverage for result in answerable_results]), 3)
            if answerable_results
            else 0.0
        ),
        "grounding_check_rate": (
            round(
                mean(
                    [1.0 if result.simple_grounding_check else 0.0 for result in answerable_results]
                ),
                3,
            )
            if answerable_results
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
        "answer_sentence_support_rate": (
            round(mean([result.answer_sentence_support_rate for result in results]), 3)
            if results
            else 0.0
        ),
        "unsupported_sentence_rate": (
            round(
                sum(result.unsupported_sentence_count for result in results)
                / max(1, sum(result.answer_sentence_count for result in results)),
                3,
            )
            if results
            else 0.0
        ),
        "citation_warning_count": sum(result.citation_warning_count for result in results),
        "average_latency_ms": (
            round(mean([result.latency_ms for result in results]), 2) if results else 0.0
        ),
        "retrieval_hit_at_1": (
            round(
                mean(
                    [
                        (1.0 if result.expected_source in result.retrieved_sources[:1] else 0.0)
                        for result in answerable_results
                    ]
                ),
                3,
            )
            if answerable_results
            else 0.0
        ),
        "retrieval_hit_at_3": (
            round(
                mean(
                    [
                        (1.0 if result.expected_source in result.retrieved_sources[:3] else 0.0)
                        for result in answerable_results
                    ]
                ),
                3,
            )
            if answerable_results
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
    manifest_path: str | Path | None = None,
    chunks: list[DocumentChunk] | None = None,
) -> dict[str, object]:
    from .assistant import build_assistant_from_paths

    if chunks is None:
        chunks = build_assistant_from_paths(
            paths,
            manifest_path=manifest_path,
            retrieval_mode=modes[0],
        ).chunks
    mode_payloads: dict[str, dict[str, object]] = {}
    for mode in modes:
        assistant = RAGAssistant(chunks, retrieval_mode=mode)
        payload = evaluate_retrieval(assistant, cases, k=k)
        mode_payloads[mode] = {
            "summary": payload["summary"],
            "result_count": len(payload["results"]),
            "case_metrics": [
                {
                    "case_id": str(row["case_id"] or f"case-{index:03d}"),
                    "case_type": row["case_type"],
                    "expected_status": row["expected_status"],
                    "expected_no_answer": row["expected_source"] == "__NO_ANSWER__",
                    "reciprocal_rank": row["reciprocal_rank"],
                    "hit_at_1": float(row["expected_source"] in row["retrieved_sources"][:1]),
                    "evidence_target_hit_at_1": row["evidence_target_hit_at_1"],
                    "evidence_target_reciprocal_rank": row["evidence_target_reciprocal_rank"],
                    "page_target_hit_at_1": row["page_target_hit_at_1"],
                    "page_target_reciprocal_rank": row["page_target_reciprocal_rank"],
                    "citation_coverage": row["citation_coverage"],
                    "simple_grounding_check": row["simple_grounding_check"],
                    "status_correct": row["status_correct"],
                    "no_answer_correct": row["no_answer_correct"],
                }
                for index, row in enumerate(payload["results"], start=1)
            ],
        }
    ranked_modes = sorted(
        (
            {
                "mode": mode,
                "recall_at_k": summary["summary"]["recall_at_k"],
                "mean_reciprocal_rank": summary["summary"]["mean_reciprocal_rank"],
                "retrieval_hit_at_3": summary["summary"]["retrieval_hit_at_3"],
                "retrieval_hit_at_1": summary["summary"]["retrieval_hit_at_1"],
                "evidence_target_hit_at_1": summary["summary"]["evidence_target_hit_at_1"],
                "evidence_target_mean_reciprocal_rank": summary["summary"][
                    "evidence_target_mean_reciprocal_rank"
                ],
                "page_target_hit_at_1": summary["summary"]["page_target_hit_at_1"],
                "page_target_mean_reciprocal_rank": summary["summary"][
                    "page_target_mean_reciprocal_rank"
                ],
                "citation_coverage": summary["summary"]["citation_coverage"],
                "status_accuracy": summary["summary"]["status_accuracy"],
            }
            for mode, summary in mode_payloads.items()
        ),
        key=lambda row: (
            float(row["status_accuracy"]),
            float(
                row["evidence_target_hit_at_1"]
                if row["evidence_target_hit_at_1"] is not None
                else row["retrieval_hit_at_3"]
            ),
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
