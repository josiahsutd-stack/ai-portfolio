from __future__ import annotations

import re
from pathlib import Path

from shared.ai import SearchResult, get_llm_provider
from shared.ai.providers import LLMProvider

from .chunking import DocumentChunk, load_document_chunks
from .faithfulness import check_citation_faithfulness
from .retrieval import (
    BM25Retriever,
    CrossEncoderRerankedRetriever,
    DenseLsaRetriever,
    HybridRetriever,
    SentenceTransformerRetriever,
    TfidfRetriever,
    tokenize,
)
from .source_manifest import default_source_manifest_path, load_source_manifest

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

PROJECT_SPECIFIC_EVIDENCE_MARKERS = {
    "my project",
    "our project",
    "this project",
    "unnamed",
    "specific site",
    "site-specific",
    "parcel ",
    "lot number",
    "granted for",
}

SourceFilterValue = str | bool | list[str] | tuple[str, ...] | set[str]
SourceFilters = dict[str, SourceFilterValue]

AUTHORITY_PUBLISHER_ALIASES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "BCA",
        ("bca", "building and construction authority", "code on accessibility", "green mark"),
        ("Building and Construction Authority, Singapore",),
    ),
    (
        "URA",
        ("ura", "urban redevelopment authority", "gross floor area", "gfa"),
        ("Urban Redevelopment Authority, Singapore",),
    ),
    (
        "NEA",
        ("nea", "national environment agency", "environmental health", "copeh"),
        ("National Environment Agency, Singapore",),
    ),
    (
        "SCDF",
        ("scdf", "singapore civil defence force", "fire code", "fire precautions"),
        ("Singapore Civil Defence Force",),
    ),
    (
        "LTA",
        ("lta", "land transport authority", "public streets", "railway protection"),
        ("Land Transport Authority, Singapore",),
    ),
    (
        "PUB",
        (
            "pub",
            "public utilities board",
            "surface water drainage",
            "sewerage",
            "sanitary works",
            "coastal protection",
            "public sewer",
        ),
        ("PUB, Singapore's National Water Agency",),
    ),
    (
        "NParks",
        (
            "nparks",
            "national parks board",
            "greenery provision",
            "tree conservation",
            "tree planting",
            "green buffer",
        ),
        ("National Parks Board, Singapore",),
    ),
)

DOCUMENT_ID_ALIASES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("code on accessibility", "bca accessibility"), "bca_code_on_accessibility_2025"),
    (("approved document",), "bca_approved_document_v7_07"),
    (
        ("green mark 2021 certification", "green mark certification standard"),
        "bca_green_mark_2021_certification_standard_2nd_ed",
    ),
    (("scdf fire code", "fire precautions in buildings"), "scdf_fire_code_2023"),
    (
        ("gross floor area handbook", "gfa handbook", "advisory notes"),
        "ura_gfa_handbook_advisory_notes",
    ),
    (("gfa glance", "guidelines at a glance", "items excluded"), "ura_gfa_guidelines_at_a_glance"),
    (
        ("nea copeh", "code of practice on environmental health"),
        "nea_code_of_practice_environmental_health_2025",
    ),
    (("works on public streets",), "lta_code_of_practice_works_on_public_streets_2025"),
    (("railway protection",), "lta_code_of_practice_railway_protection_2024"),
    (("surface water drainage",), "pub_surface_water_drainage_cop_2025"),
    (
        ("sewerage and sanitary works", "sewerage information plan"),
        "pub_sewerage_sanitary_works_2025",
    ),
    (("coastal protection",), "pub_codes_of_practice_and_standard_drawings"),
    (
        ("greenery provision and tree conservation", "tree conservation guidelines"),
        "nparks_greenery_tree_conservation_2025",
    ),
    (("development plan submission",), "nparks_development_plan_submission"),
)


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
        self.retriever = self._retriever_for(chunks)

    def retrieve(
        self,
        question: str,
        *,
        k: int = 4,
        min_score: float = 0.01,
        source_filters: SourceFilters | None = None,
    ) -> list[SearchResult]:
        threshold = self.min_score if min_score == 0.01 else min_score
        effective_filters = self._effective_source_filters(question, source_filters)
        chunks = self._filtered_chunks(effective_filters)
        if not chunks:
            return []
        retriever = self.retriever if not effective_filters else self._retriever_for(chunks)
        return retriever.search(question, k=k, min_score=threshold)

    def source_catalog(self) -> list[dict[str, str]]:
        catalog: dict[str, dict[str, str]] = {}
        for chunk in self.chunks:
            metadata = chunk.metadata()
            catalog[chunk.source] = {
                "source": chunk.source,
                "title": metadata.get("title", ""),
                "source_type": metadata.get("source_type", ""),
                "publisher": metadata.get("publisher", ""),
                "source_url": metadata.get("source_url", ""),
                "rights": metadata.get("rights", ""),
                "source_note": metadata.get("source_note", ""),
                "jurisdiction": metadata.get("jurisdiction", ""),
                "code_year": metadata.get("code_year", ""),
                "document_version": metadata.get("document_version", ""),
                "superseded": metadata.get("superseded", "false"),
                "allowed_use": metadata.get("allowed_use", ""),
            }
        return sorted(catalog.values(), key=lambda record: record["source"])

    def _filtered_chunks(self, source_filters: SourceFilters | None) -> list[DocumentChunk]:
        if not source_filters:
            return self.chunks
        return [
            chunk
            for chunk in self.chunks
            if self._matches_source_filters(chunk.metadata(), source_filters)
        ]

    def _effective_source_filters(
        self,
        question: str,
        source_filters: SourceFilters | None,
    ) -> SourceFilters | None:
        base_filters: SourceFilters = dict(source_filters or {})
        inferred_filters = self._infer_document_source_filters(
            question
        ) or self._infer_authority_source_filters(question)
        if not inferred_filters or self._has_explicit_authority_filter(base_filters):
            return base_filters or None
        candidate_filters = {**base_filters, **inferred_filters}
        if self._filtered_chunks(candidate_filters):
            return candidate_filters
        return base_filters or None

    def _has_explicit_authority_filter(self, source_filters: SourceFilters) -> bool:
        authority_keys = {"publisher", "source", "document_id"}
        return any(
            key.strip().lower().replace(" ", "_").replace("-", "_") in authority_keys
            for key in source_filters
        )

    def _infer_authority_source_filters(self, question: str) -> SourceFilters | None:
        lowered = question.lower()
        publishers: list[str] = []
        for _authority, aliases, authority_publishers in AUTHORITY_PUBLISHER_ALIASES:
            if any(self._question_mentions_alias(lowered, alias) for alias in aliases):
                publishers.extend(authority_publishers)
        unique_publishers = sorted(dict.fromkeys(publishers))
        if not unique_publishers:
            return None
        if len(unique_publishers) == 1:
            return {"publisher": unique_publishers[0]}
        return {"publisher": unique_publishers}

    def _infer_document_source_filters(self, question: str) -> SourceFilters | None:
        lowered = question.lower()
        document_ids = [
            document_id
            for aliases, document_id in DOCUMENT_ID_ALIASES
            if any(self._question_mentions_alias(lowered, alias) for alias in aliases)
        ]
        unique_document_ids = sorted(dict.fromkeys(document_ids))
        if not unique_document_ids:
            return None
        if len(unique_document_ids) == 1:
            return {"document_id": unique_document_ids[0]}
        return {"document_id": unique_document_ids}

    def _question_mentions_alias(self, lowered_question: str, alias: str) -> bool:
        lowered_alias = alias.lower()
        if " " in lowered_alias:
            return lowered_alias in lowered_question
        return bool(
            re.search(rf"(?<![a-z0-9]){re.escape(lowered_alias)}(?![a-z0-9])", lowered_question)
        )

    def _retriever_for(self, chunks: list[DocumentChunk]):
        if self.retrieval_mode == "tfidf":
            return TfidfRetriever(chunks)
        if self.retrieval_mode == "bm25":
            return BM25Retriever(chunks)
        if self.retrieval_mode == "dense_lsa":
            return DenseLsaRetriever(chunks)
        if self.retrieval_mode == "semantic":
            return SentenceTransformerRetriever(chunks)
        if self.retrieval_mode == "hybrid_cross_encoder":
            return CrossEncoderRerankedRetriever(chunks)
        return HybridRetriever(chunks)

    def _matches_source_filters(
        self, metadata: dict[str, str], source_filters: SourceFilters
    ) -> bool:
        for raw_key, expected in source_filters.items():
            key = raw_key.strip().lower().replace(" ", "_").replace("-", "_")
            actual = metadata.get(key, "")
            if isinstance(expected, bool):
                if (actual.lower() == "true") is not expected:
                    return False
            elif isinstance(expected, list | tuple | set):
                if actual not in {str(value) for value in expected}:
                    return False
            elif actual != str(expected):
                return False
        return True

    def format_citation(self, result: SearchResult, index: int) -> dict[str, object]:
        page = result.metadata.get("page") or None
        citation_id = f"C{index}"
        return {
            "citation_id": citation_id,
            "source": result.source,
            "title": result.metadata.get("title", ""),
            "source_type": result.metadata.get("source_type", ""),
            "allowed_use": result.metadata.get("allowed_use", ""),
            "publisher": result.metadata.get("publisher", ""),
            "source_url": result.metadata.get("source_url", ""),
            "rights": result.metadata.get("rights", ""),
            "downloaded_at": result.metadata.get("downloaded_at", ""),
            "source_note": result.metadata.get("source_note", ""),
            "document_id": result.metadata.get("document_id", ""),
            "jurisdiction": result.metadata.get("jurisdiction", ""),
            "code_year": result.metadata.get("code_year", ""),
            "document_version": result.metadata.get("document_version", ""),
            "superseded": result.metadata.get("superseded", "false") == "true",
            "section": result.metadata.get("section", ""),
            "heading": result.metadata.get("heading", ""),
            "clause_id": result.metadata.get("clause_id", ""),
            "page": page,
            "chunk_id": result.metadata.get("chunk_id", ""),
            "retriever": result.metadata.get("retriever", self.retrieval_mode),
            "tfidf_score": result.metadata.get("tfidf_score"),
            "bm25_score": result.metadata.get("bm25_score"),
            "dense_score": result.metadata.get("dense_score"),
            "embedding_model": result.metadata.get("embedding_model"),
            "embedding_score": result.metadata.get("embedding_score"),
            "rerank_model": result.metadata.get("rerank_model"),
            "rerank_score": result.metadata.get("rerank_score"),
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

    def answer(
        self,
        question: str,
        *,
        k: int = 4,
        source_filters: SourceFilters | None = None,
    ) -> dict[str, object]:
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
                    "Unsupported scope: this local retrieval assistant cannot provide live "
                    "legal, jurisdictional, certification, approval, or professional "
                    "compliance sign-off."
                ),
                "status": unsupported_status,
                "confidence": "low",
                "sources": [],
                "retrieval": {"k": k, "result_count": 0, "source_filters": source_filters or {}},
                "limitations": ["requires_current_jurisdiction_or_professional_review"],
            }
        if self._requires_project_specific_evidence(question):
            return {
                "answer": (
                    "I could not find project-specific evidence in the local reference corpus. "
                    "Provide the relevant project records or route the question to the responsible "
                    "qualified professional."
                ),
                "status": "no_evidence",
                "confidence": "low",
                "sources": [],
                "retrieval": {
                    "k": k,
                    "result_count": 0,
                    "reason": "project_specific_evidence_missing",
                    "source_filters": source_filters or {},
                },
                "limitations": ["project_specific_evidence_not_in_reference_corpus"],
            }
        requested_source_filters = source_filters or {}
        effective_source_filters = self._effective_source_filters(question, source_filters)
        inferred_source_filters = {
            key: value
            for key, value in (effective_source_filters or {}).items()
            if requested_source_filters.get(key) != value
        }
        results = self.retrieve(question, k=k, source_filters=effective_source_filters)
        weak_coverage = self._weak_lexical_coverage(question, results)
        if not results or weak_coverage:
            return {
                "answer": "I could not find grounded evidence in the local corpus.",
                "status": "no_evidence",
                "confidence": "low",
                "sources": [],
                "retrieval": {
                    "k": k,
                    "result_count": len(results),
                    "reason": "no_results" if not results else "weak_lexical_coverage",
                    "source_filters": effective_source_filters or {},
                    "inferred_source_filters": inferred_source_filters,
                    "filtered_corpus_size": len(self._filtered_chunks(effective_source_filters)),
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
        source_status = self._source_status(citations)
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
        if source_status["requires_review"]:
            answer = f"{answer}\n\n{source_status['note']}"
        faithfulness = check_citation_faithfulness(answer, citations)
        limitations = [
            "local_reference_corpus",
            "not_legal_code_engineering_architectural_or_professional_compliance_advice",
        ]
        if any("official_public" in str(citation.get("allowed_use", "")) for citation in citations):
            limitations.append("official_public_sources_for_local_reference_only")
        else:
            limitations.append("synthetic_demo_corpus")
        if source_status["requires_review"]:
            limitations.append("source_status_review_required")
        return {
            "answer": answer,
            "status": "answered",
            "confidence": self._confidence_label(citations),
            "sources": citations,
            "source_status": source_status,
            "retrieval": {
                "k": k,
                "result_count": len(results),
                "top_score": citations[0]["score"] if citations else 0,
                "mode": self.retrieval_mode,
                "source_filters": effective_source_filters or {},
                "inferred_source_filters": inferred_source_filters,
                "filtered_corpus_size": len(self._filtered_chunks(effective_source_filters)),
            },
            "citation_check": faithfulness,
            "limitations": limitations,
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

    def _requires_project_specific_evidence(self, question: str) -> bool:
        lowered = question.lower()
        return any(marker in lowered for marker in PROJECT_SPECIFIC_EVIDENCE_MARKERS)

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

    def _source_status(self, citations: list[dict[str, object]]) -> dict[str, object]:
        superseded = [
            {
                "citation_id": citation["citation_id"],
                "source": citation["source"],
                "document_version": citation.get("document_version", ""),
            }
            for citation in citations
            if citation.get("superseded") is True
        ]
        versions = sorted(
            {
                str(citation.get("document_version", ""))
                for citation in citations
                if citation.get("document_version")
            }
        )
        jurisdictions = sorted(
            {
                str(citation.get("jurisdiction", ""))
                for citation in citations
                if citation.get("jurisdiction")
            }
        )
        code_years = sorted(
            {
                str(citation.get("code_year", ""))
                for citation in citations
                if citation.get("code_year")
            }
        )
        warnings: list[str] = []
        if superseded:
            warnings.append("retrieved_superseded_sources")
        if len(versions) > 1:
            warnings.append("mixed_document_versions")
        if len(jurisdictions) > 1:
            warnings.append("mixed_jurisdictions")
        if len(code_years) > 1:
            warnings.append("mixed_code_years")
        note = ""
        if warnings:
            reason_labels = {
                "retrieved_superseded_sources": "superseded sources",
                "mixed_document_versions": "multiple document versions",
                "mixed_jurisdictions": "multiple jurisdictions",
                "mixed_code_years": "multiple code years",
            }
            reasons = ", ".join(reason_labels[warning] for warning in warnings)
            note = (
                f"Source status note: retrieved evidence includes {reasons}. "
                "Treat the answer as review input and verify the governing source set "
                "before relying on it."
            )
        return {
            "requires_review": bool(warnings),
            "warnings": warnings,
            "superseded_sources": superseded,
            "document_versions": versions,
            "jurisdictions": jurisdictions,
            "code_years": code_years,
            "note": note,
        }

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
            "Based on the retrieved local guidance, review these items:\n"
            + "\n".join(bullets)
            + "\n\nThis is decision-support text only; a qualified reviewer would still "
            "check the governing jurisdiction, current code version, and project-specific constraints."
        )


def build_assistant_from_paths(
    paths: list[str | Path],
    *,
    manifest_path: str | Path | None = None,
    retrieval_mode: str = "hybrid",
) -> RAGAssistant:
    source_paths = list(paths)
    candidate_manifest = (
        Path(manifest_path) if manifest_path else default_source_manifest_path(source_paths)
    )
    manifest = load_source_manifest(candidate_manifest) if candidate_manifest else {}
    chunks: list[DocumentChunk] = []
    for path in source_paths:
        chunks.extend(
            load_document_chunks(
                path,
                metadata_overrides=manifest.get(Path(path).name),
            )
        )
    return RAGAssistant(chunks, retrieval_mode=retrieval_mode)
