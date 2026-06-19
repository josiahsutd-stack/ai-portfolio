from __future__ import annotations

from pathlib import Path

from shared.ai import SearchResult, get_llm_provider
from shared.ai.providers import LLMProvider

from .chunking import DocumentChunk, load_markdown_chunks
from .faithfulness import check_citation_faithfulness
from .retrieval import HybridRetriever, TfidfRetriever, tokenize

UNSUPPORTED_SCOPE_TERMS = {
    "current code",
    "live code",
    "legal interpretation",
    "sign off",
    "sign-off",
    "certify",
    "approval",
    "permit approval",
    "jurisdiction",
    "2026",
    "today",
}


class RAGAssistant:
    def __init__(
        self,
        chunks: list[DocumentChunk],
        provider: LLMProvider | None = None,
        *,
        retrieval_mode: str = "hybrid",
        min_score: float = 0.04,
        min_lexical_coverage: float = 0.25,
    ) -> None:
        self.chunks = chunks
        self.provider = provider or get_llm_provider()
        self.retrieval_mode = retrieval_mode
        self.min_score = min_score
        self.min_lexical_coverage = min_lexical_coverage
        self.retriever = (
            TfidfRetriever(chunks) if retrieval_mode == "tfidf" else HybridRetriever(chunks)
        )

    def retrieve(self, question: str, *, k: int = 4, min_score: float = 0.01) -> list[SearchResult]:
        threshold = self.min_score if min_score == 0.01 else min_score
        return self.retriever.search(question, k=k, min_score=threshold)

    def format_citation(self, result: SearchResult, index: int) -> dict[str, object]:
        page = result.metadata.get("page") or None
        citation_id = f"C{index}"
        return {
            "citation_id": citation_id,
            "source": result.source,
            "section": result.metadata.get("section", ""),
            "heading": result.metadata.get("heading", ""),
            "clause_id": result.metadata.get("clause_id", ""),
            "page": page,
            "chunk_id": result.metadata.get("chunk_id", ""),
            "retriever": result.metadata.get("retriever", self.retrieval_mode),
            "tfidf_score": result.metadata.get("tfidf_score"),
            "bm25_score": result.metadata.get("bm25_score"),
            "query_term_coverage": result.metadata.get("query_term_coverage"),
            "score": round(result.score, 3),
            "excerpt": result.text[:360],
            "reference": self._citation_reference(result, citation_id),
        }

    def _citation_reference(self, result: SearchResult, citation_id: str) -> str:
        page = result.metadata.get("page")
        page_label = f", page {page}" if page else ""
        return (
            f"[{citation_id}] {result.source}"
            f" > {result.metadata.get('heading', result.metadata.get('section', ''))}"
            f" ({result.metadata.get('clause_id', 'no-clause-id')}{page_label})"
        )

    def answer(self, question: str, *, k: int = 4) -> dict[str, object]:
        if not question.strip():
            return {
                "answer": "Please provide a code, guidance, or design-standard question.",
                "status": "no_evidence",
                "confidence": "low",
                "sources": [],
                "limitations": ["empty_question"],
            }
        unsupported_status = self._unsupported_status(question)
        if unsupported_status:
            return {
                "answer": (
                    "Unsupported scope: the local synthetic corpus cannot provide live legal, "
                    "jurisdictional, certification, or professional compliance sign-off."
                ),
                "status": unsupported_status,
                "confidence": "low",
                "sources": [],
                "retrieval": {"k": k, "result_count": 0},
                "limitations": ["requires_current_jurisdiction_or_professional_review"],
            }
        results = self.retrieve(question, k=k)
        weak_coverage = self._weak_lexical_coverage(question, results)
        if not results or weak_coverage:
            return {
                "answer": "I could not find grounded evidence in the demo documents.",
                "status": "no_evidence",
                "confidence": "low",
                "sources": [],
                "retrieval": {
                    "k": k,
                    "result_count": len(results),
                    "reason": "no_results" if not results else "weak_lexical_coverage",
                },
                "limitations": ["synthetic_corpus_does_not_support_question"],
            }
        context = "\n\n".join(
            (
                f"[C{idx + 1}] {result.source} / "
                f"{result.metadata.get('heading')} / "
                f"{result.metadata.get('clause_id')}: {result.text}"
            )
            for idx, result in enumerate(results)
        )
        prompt = (
            "Answer this AEC code-compliance question using only the context. "
            "If evidence is incomplete, say what is missing.\n\n"
            f"Question: {question}\n\nContext:\n{context}"
        )
        citations = [self.format_citation(result, idx + 1) for idx, result in enumerate(results)]
        if getattr(self.provider, "name", "") == "mock-local-llm":
            answer = self._local_grounded_answer(citations)
        else:
            answer = self.provider.generate(
                prompt,
                system=(
                    "You are a cautious AEC design-standards assistant. "
                    "Use only the provided context and cite chunk IDs like [C1]."
                ),
            )
        faithfulness = check_citation_faithfulness(answer, citations)
        return {
            "answer": answer,
            "status": "answered",
            "confidence": self._confidence_label(citations),
            "sources": citations,
            "retrieval": {
                "k": k,
                "result_count": len(results),
                "top_score": citations[0]["score"] if citations else 0,
                "mode": self.retrieval_mode,
            },
            "citation_check": faithfulness,
            "limitations": [
                "synthetic_demo_corpus",
                "not_legal_code_engineering_or_professional_compliance_advice",
            ],
        }

    def _unsupported_status(self, question: str) -> str | None:
        lowered = question.lower()
        if any(term in lowered for term in ["ignore the corpus", "invent", "pretend"]):
            return "no_evidence"
        if any(term in lowered for term in UNSUPPORTED_SCOPE_TERMS):
            if any(term in lowered for term in ["sign off", "sign-off", "certify", "approval"]):
                return "needs_professional_review"
            return "unsupported_scope"
        return None

    def _weak_lexical_coverage(self, question: str, results: list[SearchResult]) -> bool:
        if not results:
            return True
        query_tokens = {
            token
            for token in tokenize(question)
            if token
            not in {
                "what",
                "which",
                "should",
                "for",
                "the",
                "does",
                "do",
                "to",
                "is",
                "are",
                "be",
                "used",
                "required",
                "applies",
                "apply",
                "include",
                "included",
                "need",
                "needs",
            }
        }
        if not query_tokens:
            return False
        text_tokens = set(tokenize(" ".join(result.text for result in results[:2])))
        coverage = len(query_tokens & text_tokens) / max(1, len(query_tokens))
        return coverage < self.min_lexical_coverage

    def _confidence_label(self, citations: list[dict[str, object]]) -> str:
        if not citations:
            return "low"
        top_score = float(citations[0]["score"])
        if top_score >= 0.45:
            return "high"
        if top_score >= 0.16:
            return "medium"
        return "low"

    def _local_grounded_answer(self, citations: list[dict[str, object]]) -> str:
        top_score = float(citations[0]["score"]) if citations else 0.0
        selected_citations = [
            citation
            for citation in citations
            if float(citation["score"]) >= max(0.08, top_score * 0.5)
        ]
        if not selected_citations:
            selected_citations = citations[:1]
        bullets = []
        for citation in selected_citations[:3]:
            excerpt = str(citation["excerpt"]).replace("\n", " ")
            bullets.append(
                "- {excerpt} [{citation_id}]".format(
                    excerpt=excerpt,
                    citation_id=citation["citation_id"],
                )
            )
        return (
            "Based on the synthetic demo guidance retrieved locally, review these items:\n"
            + "\n".join(bullets)
            + "\n\nThis is decision-support text only; a qualified reviewer would still "
            "check the governing jurisdiction, current code version, and project-specific constraints."
        )


def build_assistant_from_paths(paths: list[str | Path]) -> RAGAssistant:
    chunks: list[DocumentChunk] = []
    for path in paths:
        chunks.extend(load_markdown_chunks(path))
    return RAGAssistant(chunks)
