from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Protocol

from shared.ai import SearchResult, TfidfVectorStore

from .chunking import DocumentChunk

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


class Retriever(Protocol):
    def search(self, query: str, *, k: int = 4, min_score: float = 0.0) -> list[SearchResult]: ...


@dataclass(frozen=True)
class RetrieverConfig:
    tfidf_weight: float = 0.55
    bm25_weight: float = 0.45


class TfidfRetriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.store = TfidfVectorStore()
        self.store.add_texts(
            [chunk.text for chunk in chunks],
            sources=[chunk.source for chunk in chunks],
            metadata=[chunk.metadata() for chunk in chunks],
        )

    def search(self, query: str, *, k: int = 4, min_score: float = 0.0) -> list[SearchResult]:
        return self.store.search(query, k=k, min_score=min_score)


class BM25Retriever:
    """Small local BM25 implementation for transparent lexical retrieval."""

    def __init__(self, chunks: list[DocumentChunk], *, k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.documents = [tokenize(chunk.text) for chunk in chunks]
        self.doc_lengths = [len(document) for document in self.documents]
        self.avg_doc_length = (
            sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        )
        self.doc_freq: Counter[str] = Counter()
        for document in self.documents:
            self.doc_freq.update(set(document))

    def _idf(self, token: str) -> float:
        corpus_size = len(self.documents)
        if corpus_size == 0:
            return 0.0
        freq = self.doc_freq.get(token, 0)
        return math.log(1 + (corpus_size - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, *, k: int = 4, min_score: float = 0.0) -> list[SearchResult]:
        query_tokens = tokenize(query)
        if not query_tokens or not self.documents:
            return []
        scores: list[tuple[int, float]] = []
        for index, document in enumerate(self.documents):
            counts = Counter(document)
            score = 0.0
            for token in query_tokens:
                frequency = counts.get(token, 0)
                if frequency == 0:
                    continue
                length_norm = (
                    1 - self.b + self.b * (self.doc_lengths[index] / max(1e-9, self.avg_doc_length))
                )
                numerator = frequency * (self.k1 + 1)
                denominator = frequency + self.k1 * length_norm
                score += self._idf(token) * (numerator / denominator)
            if score >= min_score:
                scores.append((index, score))
        if not scores:
            return []
        max_score = max(score for _index, score in scores) or 1.0
        ranked = sorted(scores, key=lambda item: item[1], reverse=True)[:k]
        return [
            SearchResult(
                text=self.chunks[index].text,
                source=self.chunks[index].source,
                score=round(score / max_score, 6),
                metadata={
                    **self.chunks[index].metadata(),
                    "retriever": "bm25",
                    "bm25_score": str(round(score, 6)),
                },
            )
            for index, score in ranked
        ]


class HybridRetriever:
    def __init__(
        self,
        chunks: list[DocumentChunk],
        *,
        config: RetrieverConfig | None = None,
        rerank: bool = True,
    ) -> None:
        self.config = config or RetrieverConfig()
        self.tfidf = TfidfRetriever(chunks)
        self.bm25 = BM25Retriever(chunks)
        self.rerank = rerank

    def search(self, query: str, *, k: int = 4, min_score: float = 0.0) -> list[SearchResult]:
        if not query.strip():
            return []
        pool_size = max(k * 3, 8)
        merged: dict[str, dict[str, object]] = {}
        for retriever_name, weight, results in [
            ("tfidf", self.config.tfidf_weight, self.tfidf.search(query, k=pool_size)),
            ("bm25", self.config.bm25_weight, self.bm25.search(query, k=pool_size)),
        ]:
            for result in results:
                chunk_id = str(
                    result.metadata.get("chunk_id") or f"{result.source}:{result.text[:30]}"
                )
                record = merged.setdefault(
                    chunk_id,
                    {
                        "text": result.text,
                        "source": result.source,
                        "metadata": dict(result.metadata),
                        "components": defaultdict(float),
                    },
                )
                components = record["components"]
                assert isinstance(components, defaultdict)
                components[retriever_name] = max(float(components[retriever_name]), result.score)
                record["metadata"] = {**dict(record["metadata"]), **dict(result.metadata)}
                record["score"] = float(record.get("score", 0.0)) + result.score * weight

        query_tokens = set(tokenize(query))
        ranked: list[SearchResult] = []
        for record in merged.values():
            metadata = dict(record["metadata"])
            components = dict(record["components"])
            score = float(record.get("score", 0.0))
            if self.rerank:
                score += lexical_rerank_boost(query, str(record["text"]), metadata)
            if score < min_score:
                continue
            text_tokens = set(tokenize(str(record["text"])))
            metadata["retriever"] = "hybrid"
            metadata["tfidf_score"] = str(round(float(components.get("tfidf", 0.0)), 6))
            metadata["bm25_score"] = str(round(float(components.get("bm25", 0.0)), 6))
            metadata["query_term_coverage"] = str(
                round(len(query_tokens & text_tokens) / max(1, len(query_tokens)), 3)
            )
            ranked.append(
                SearchResult(
                    text=str(record["text"]),
                    source=str(record["source"]),
                    score=round(score, 6),
                    metadata=metadata,
                )
            )
        return sorted(ranked, key=lambda result: result.score, reverse=True)[:k]


def lexical_rerank_boost(query: str, text: str, metadata: dict[str, str]) -> float:
    query_tokens = set(tokenize(query))
    text_tokens = set(tokenize(text))
    if not query_tokens:
        return 0.0
    boost = 0.0
    coverage = len(query_tokens & text_tokens) / len(query_tokens)
    boost += min(0.08, coverage * 0.08)
    heading_tokens = set(tokenize(metadata.get("heading", "")))
    if query_tokens & heading_tokens:
        boost += 0.04
    clause_id = metadata.get("clause_id", "").lower()
    if clause_id and clause_id in query.lower():
        boost += 0.08
    domain_terms = {"access", "accessible", "fire", "daylight", "planning", "threshold"}
    if query_tokens & domain_terms and text_tokens & domain_terms:
        boost += 0.03
    return boost
