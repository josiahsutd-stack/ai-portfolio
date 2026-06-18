from __future__ import annotations

from pathlib import Path

from shared.ai import SearchResult, TfidfVectorStore, get_llm_provider
from shared.ai.providers import LLMProvider

from .chunking import DocumentChunk, load_markdown_chunks


class RAGAssistant:
    def __init__(self, chunks: list[DocumentChunk], provider: LLMProvider | None = None) -> None:
        self.chunks = chunks
        self.provider = provider or get_llm_provider()
        self.store = TfidfVectorStore()
        self.store.add_texts(
            [chunk.text for chunk in chunks],
            sources=[chunk.source for chunk in chunks],
            metadata=[{"section": chunk.section, "chunk_id": chunk.chunk_id} for chunk in chunks],
        )

    def retrieve(self, question: str, *, k: int = 4) -> list[SearchResult]:
        return self.store.search(question, k=k, min_score=0.01)

    def answer(self, question: str, *, k: int = 4) -> dict[str, object]:
        if not question.strip():
            return {
                "answer": "Please provide a code, guidance, or design-standard question.",
                "sources": [],
            }
        results = self.retrieve(question, k=k)
        if not results:
            return {
                "answer": "I could not find grounded evidence in the demo documents.",
                "sources": [],
            }
        context = "\n\n".join(
            f"[{idx + 1}] {result.source} / {result.metadata.get('section')}: {result.text}"
            for idx, result in enumerate(results)
        )
        prompt = (
            "Answer this AEC code-compliance question using only the context. "
            "If evidence is incomplete, say what is missing.\n\n"
            f"Question: {question}\n\nContext:\n{context}"
        )
        answer = self.provider.generate(
            prompt,
            system="You are a cautious AEC design-standards assistant. Cite source numbers.",
        )
        citations = [
            {
                "source": result.source,
                "section": result.metadata.get("section", ""),
                "score": round(result.score, 3),
                "excerpt": result.text[:240],
            }
            for result in results
        ]
        return {"answer": answer, "sources": citations}


def build_assistant_from_paths(paths: list[str | Path]) -> RAGAssistant:
    chunks: list[DocumentChunk] = []
    for path in paths:
        chunks.extend(load_markdown_chunks(path))
    return RAGAssistant(chunks)
