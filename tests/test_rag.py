from aec_code_compliance_rag import (
    BM25Retriever,
    HybridRetriever,
    RAGAssistant,
    RetrievalEvalCase,
    check_citation_faithfulness,
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
    assert metadata["jurisdiction"] == "synthetic-demo"
    assert metadata["code_year"] == "synthetic"
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
    assert results[0].metadata["retriever"] == "hybrid"


def test_bm25_retrieval_returns_expected_metadata() -> None:
    chunks = chunk_text(
        """
        ## Drawing QA Checklist

        Drawing packages should cross-check door tags, room names, thresholds, and accessibility notes.
        """,
        source="qa.md",
    )
    results = BM25Retriever(chunks).search("door tags accessibility notes", k=2)

    assert results
    assert results[0].source == "qa.md"
    assert results[0].metadata["retriever"] == "bm25"
    assert results[0].metadata["chunk_id"] == "qa-drawing-qa-checklist-000"


def test_hybrid_retrieval_deduplicates_chunks() -> None:
    chunks = chunk_text(
        """
        ## Daylight And Energy Notes

        West glazing should trigger glare, cooling load, shading, and daylight review.
        """,
        source="daylight.md",
    )
    results = HybridRetriever(chunks).search("west glazing daylight", k=4)

    chunk_ids = [result.metadata["chunk_id"] for result in results]
    assert chunk_ids == list(dict.fromkeys(chunk_ids))
    assert results[0].metadata["tfidf_score"] is not None
    assert results[0].metadata["bm25_score"] is not None


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
    assert response["status"] == "no_evidence"
    assert "provide" in response["answer"].lower()


def test_rag_handles_no_result_question() -> None:
    assistant = RAGAssistant(chunk_text("Door clearances need checking.", source="mock.md"))

    response = assistant.answer("quantum banana spectroscopy", k=2)

    assert response["sources"] == []
    assert response["status"] == "no_evidence"
    assert response["retrieval"]["result_count"] == 0
    assert "could not find" in response["answer"].lower()


def test_rag_rejects_live_code_and_professional_signoff_questions() -> None:
    assistant = RAGAssistant(chunk_text("Door clearances need checking.", source="mock.md"))

    live = assistant.answer("What is the current code for this jurisdiction today?")
    signoff = assistant.answer("Can you certify this design for permit approval?")

    assert live["status"] == "unsupported_scope"
    assert signoff["status"] == "needs_professional_review"
    assert live["sources"] == []
    assert signoff["sources"] == []


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
    assert payload["summary"]["status_accuracy"] == 1.0
    assert payload["summary"]["citation_check_pass_rate"] == 1.0
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


def test_citation_faithfulness_checks_markers_and_support() -> None:
    citation = {
        "citation_id": "C1",
        "excerpt": "Accessible routes should provide a clear path and threshold transitions.",
    }
    passing = check_citation_faithfulness(
        "Accessible routes should provide a clear path [C1].",
        [citation],
    )
    missing = check_citation_faithfulness(
        "Accessible routes should provide a clear path.",
        [citation],
    )
    fake = check_citation_faithfulness(
        "Accessible routes should provide a clear path [C9].",
        [citation],
    )

    assert passing["passed"]
    assert not missing["passed"]
    assert not fake["passed"]
    assert fake["fake_citation_ids"] == ["C9"]
