from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class SearchResult:
    text: str
    source: str
    score: float
    metadata: dict[str, str]


class TfidfVectorStore:
    """Local vector-search style store backed by TF-IDF for demo portability."""

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = None
        self._records: list[dict[str, object]] = []

    def add_texts(
        self,
        texts: Iterable[str],
        *,
        sources: Iterable[str],
        metadata: Iterable[dict[str, str]] | None = None,
    ) -> None:
        metadatas = list(metadata or [])
        self._records = []
        for idx, (text, source) in enumerate(zip(texts, sources, strict=True)):
            self._records.append(
                {
                    "text": text,
                    "source": source,
                    "metadata": metadatas[idx] if idx < len(metadatas) else {},
                }
            )
        if not self._records:
            self._matrix = None
            return
        self._matrix = self._vectorizer.fit_transform(
            [str(record["text"]) for record in self._records]
        )

    def search(self, query: str, *, k: int = 4, min_score: float = 0.0) -> list[SearchResult]:
        if self._matrix is None or not self._records or not query.strip():
            return []
        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix)[0]
        ranked_indices = scores.argsort()[::-1][:k]
        results = []
        for index in ranked_indices:
            score = float(scores[index])
            if score < min_score:
                continue
            record = self._records[int(index)]
            results.append(
                SearchResult(
                    text=str(record["text"]),
                    source=str(record["source"]),
                    score=score,
                    metadata=dict(record["metadata"]),
                )
            )
        return results
