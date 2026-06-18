from aec_code_compliance_rag import (
    RAGAssistant,
    RetrievalEvalCase,
    chunk_text,
    evaluate_retrieval,
)


def test_chunking_preserves_review_metadata() -> None:
    text = """
    # Synthetic Guide

    <!-- page: 7 -->
    ## Accessible Routes

    Accessible routes should provide a clear path and door thresholds should be resolved.
    """

    chunks = chunk_text(text, source="mock.md", max_words=16, overlap=3)
    accessibility_chunk = next(chunk for chunk in chunks if chunk.heading == "Accessible Routes")
    metadata = accessibility_chunk.metadata()

    assert metadata["section"] == "Accessible Routes"
    assert metadata["heading"] == "Accessible Routes"
    assert metadata["clause_id"] == "AEC-ACCESSIBLE-ROUTES"
    assert metadata["page"] == "7"
    assert metadata["chunk_id"].startswith("mock-accessible-routes-")
    assert int(metadata["end_word"]) > int(metadata["start_word"])


def test_chunking_and_retrieval_returns_accessibility_source() -> None:
    text = """
    # Accessibility
    Accessible routes should provide a clear path. Doorways serving accessible
    rooms should provide enough clear opening width and threshold transitions
    should be resolved.

    # Fire
    Fire-rated corridors should include rating notes and compartment strategy.
    """
    chunks = chunk_text(text, source="mock.md", max_words=22, overlap=4)
    assistant = RAGAssistant(chunks)

    results = assistant.retrieve("What should I check for accessible doorways?", k=2)

    assert chunks
    assert results
    assert "accessible" in results[0].text.lower()
    assert results[0].metadata["chunk_id"]


def test_citation_format_exposes_clause_and_chunk_metadata() -> None:
    text = """
    <!-- page: 2 -->
    ## Fire Compartment Notes

    Residential corridors should include compartmentation intent and smoke control assumptions.
    """
    assistant = RAGAssistant(chunk_text(text, source="mock.md"))

    result = assistant.retrieve("What smoke control notes are needed?", k=1)[0]
    citation = assistant.format_citation(result, 1)

    assert citation["citation_id"] == "C1"
    assert citation["clause_id"] == "AEC-FIRE-COMPARTMENT-NOTES"
    assert citation["page"] == "2"
    assert citation["chunk_id"] == "mock-fire-compartment-notes-000"
    assert "[C1]" in citation["reference"]


def test_rag_handles_empty_question() -> None:
    assistant = RAGAssistant(chunk_text("Door clearances need checking.", source="mock.md"))

    response = assistant.answer("")

    assert response["sources"] == []
    assert "provide" in response["answer"].lower()


def test_rag_handles_no_result_question() -> None:
    assistant = RAGAssistant(chunk_text("Door clearances need checking.", source="mock.md"))

    response = assistant.answer("quantum banana spectroscopy", k=2)

    assert response["sources"] == []
    assert response["retrieval"]["result_count"] == 0
    assert "could not find" in response["answer"].lower()


def test_retrieval_evaluation_reports_section_and_term_coverage() -> None:
    text = """
    ## Planning Review Checklist

    Planning packages should explain setbacks, servicing strategy, and waste collection.
    Missing assumptions should be logged before submission.
    """
    assistant = RAGAssistant(chunk_text(text, source="mock.md"))
    cases = [
        RetrievalEvalCase(
            question="Which planning assumptions should be logged?",
            expected_source="mock.md",
            expected_section="Planning Review Checklist",
            expected_terms=["setbacks", "servicing strategy", "waste collection"],
        )
    ]

    payload = evaluate_retrieval(assistant, cases, k=2)

    assert payload["summary"]["recall_at_k"] == 1.0
    assert payload["summary"]["mean_reciprocal_rank"] == 1.0
    assert payload["summary"]["section_hit_rate"] == 1.0
    assert payload["results"][0]["missing_terms"] == []


def test_retrieval_evaluation_scores_no_answer_case() -> None:
    assistant = RAGAssistant(chunk_text("Door clearances need checking.", source="mock.md"))
    cases = [
        RetrievalEvalCase(
            question="What drone landing pad radius applies to rooftop aircraft operations?",
            expected_source="__NO_ANSWER__",
            expected_terms=[],
            expected_no_answer=True,
        )
    ]

    payload = evaluate_retrieval(assistant, cases, k=2)

    assert payload["summary"]["no_answer_accuracy"] == 1.0
    assert payload["results"][0]["no_answer_correct"]
