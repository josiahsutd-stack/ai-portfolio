from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

from .assistant import RAGAssistant


@dataclass(frozen=True)
class RetrievalEvalCase:
    question: str
    expected_source: str
    expected_terms: list[str]
    expected_section: str | None = None
    expected_no_answer: bool = False
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
            "simple_grounding_check": self.simple_grounding_check,
            "missing_terms": self.missing_terms,
        }


def load_eval_cases(path: str | Path) -> list[RetrievalEvalCase]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        RetrievalEvalCase(
            question=row["question"],
            expected_source=row["expected_source"],
            expected_terms=list(row.get("expected_terms", [])),
            expected_section=row.get("expected_section"),
            expected_no_answer=bool(row.get("expected_no_answer", False)),
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
        retrieved = assistant.retrieve(case.question, k=k)
        if case.expected_no_answer:
            no_answer_correct = not retrieved
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
        "no_answer_accuracy": (
            round(
                mean(
                    [
                        1.0 if result.no_answer_correct else 0.0
                        for result in results
                        if result.expected_source == "__NO_ANSWER__"
                    ]
                ),
                3,
            )
            if any(result.expected_source == "__NO_ANSWER__" for result in results)
            else None
        ),
    }
    return {"summary": summary, "results": [result.to_dict() for result in results]}
