import json
from pathlib import Path

from aec_code_compliance_rag import (
    BM25Retriever,
    DenseLsaRetriever,
    HybridRetriever,
    RAGAssistant,
    RetrievalEvalCase,
    build_assistant_from_paths,
    check_citation_faithfulness,
    chunk_text,
    evaluate_retrieval,
    evaluate_retrieval_modes,
    load_document_chunks,
    load_source_manifest,
)


def _write_pdf_fixture(path: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    pdf = canvas.Canvas(str(path), pagesize=letter)
    pdf.setTitle("Test PDF Accessibility Addendum")
    pages = [
        (
            "PDF Parking Access Notes",
            [
                "document_id: test_pdf_access",
                "jurisdiction: test-city",
                "code_year: 2025",
                "document_version: pdf-test-v1",
                "superseded: false",
                "PDF parking access notes should record wet-weather transfer path, gradient assumptions, and bollard clearance before review.",
            ],
        ),
        (
            "PDF Stair Discharge Notes",
            [
                "PDF stair notes should preserve the second page citation and identify protected lobby assumptions.",
            ],
        ),
    ]
    for page_number, (heading, lines) in enumerate(pages, start=1):
        y = letter[1] - inch
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(inch, y, heading)
        y -= 0.3 * inch
        pdf.setFont("Helvetica", 10)
        for line in lines:
            pdf.drawString(inch, y, line)
            y -= 0.22 * inch
        pdf.drawString(inch, 0.55 * inch, f"Page {page_number}")
        pdf.showPage()
    pdf.save()


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


def test_chunking_preserves_document_status_metadata() -> None:
    text = """
    document_id: access_v1
    jurisdiction: demo-city
    code_year: 2024
    document_version: v1
    superseded: true

    ## Accessible Routes

    Accessible routes should include doorway and threshold review notes.
    """

    metadata = chunk_text(text, source="access-v1.md")[0].metadata()

    assert metadata["document_id"] == "access_v1"
    assert metadata["jurisdiction"] == "demo-city"
    assert metadata["code_year"] == "2024"
    assert metadata["document_version"] == "v1"
    assert metadata["superseded"] == "true"


def test_pdf_ingestion_preserves_page_numbers_and_metadata(tmp_path: Path) -> None:
    pdf_path = tmp_path / "fixture.pdf"
    _write_pdf_fixture(pdf_path)

    chunks = load_document_chunks(pdf_path, max_words=36)
    parking_chunk = next(chunk for chunk in chunks if chunk.heading == "PDF Parking Access Notes")
    stair_chunk = next(chunk for chunk in chunks if chunk.heading == "PDF Stair Discharge Notes")
    metadata = parking_chunk.metadata()

    assert {chunk.page for chunk in chunks} == {1, 2}
    assert metadata["source"] == "fixture.pdf"
    assert metadata["document_id"] == "test_pdf_access"
    assert metadata["jurisdiction"] == "test-city"
    assert metadata["code_year"] == "2025"
    assert metadata["document_version"] == "pdf-test-v1"
    assert metadata["page"] == "1"
    assert metadata["chunk_id"].startswith("fixture-pdf-parking-access-notes-p1-")
    assert stair_chunk.metadata()["page"] == "2"


def test_source_manifest_overrides_metadata_and_catalog(tmp_path: Path) -> None:
    doc_path = tmp_path / "manifested.md"
    doc_path.write_text(
        """
        document_version: stale-header

        ## Manifested Door Checks

        Door checks should identify latch offsets and access assumptions.
        """,
        encoding="utf-8",
    )
    manifest_path = tmp_path / "source_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source": "manifested.md",
                        "title": "Manifested Access Guide",
                        "document_id": "manifested_access",
                        "source_type": "markdown",
                        "jurisdiction": "manifest-city",
                        "code_year": "2025",
                        "document_version": "manifest-v2",
                        "superseded": False,
                        "allowed_use": "synthetic_manifest_test",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assistant = build_assistant_from_paths([doc_path], manifest_path=manifest_path)
    catalog = assistant.source_catalog()
    metadata = assistant.chunks[0].metadata()
    manifest = load_source_manifest(manifest_path)

    assert manifest["manifested.md"]["document_version"] == "manifest-v2"
    assert catalog == [
        {
            "source": "manifested.md",
            "title": "Manifested Access Guide",
            "source_type": "markdown",
            "jurisdiction": "manifest-city",
            "code_year": "2025",
            "document_version": "manifest-v2",
            "superseded": "false",
            "allowed_use": "synthetic_manifest_test",
        }
    ]
    assert metadata["document_id"] == "manifested_access"
    assert metadata["document_version"] == "manifest-v2"
    assert metadata["jurisdiction"] == "manifest-city"


def test_source_filters_limit_retrieval_and_answer_citations() -> None:
    old = chunk_text(
        """
        ## Door Latch Offsets

        Door latch offsets should be checked against the legacy review path.
        """,
        source="legacy.md",
        metadata_overrides={
            "document_version": "legacy-v1",
            "superseded": True,
            "source_type": "markdown",
        },
    )
    current = chunk_text(
        """
        ## Door Latch Offsets

        Door latch offsets should be checked against the current review path.
        """,
        source="current.pdf",
        metadata_overrides={
            "document_version": "current-v2",
            "superseded": False,
            "source_type": "pdf",
        },
    )
    assistant = RAGAssistant(old + current, min_score=0)

    response = assistant.answer(
        "What should door latch offsets be checked against?",
        k=3,
        source_filters={"source_type": "pdf", "superseded": False},
    )

    assert response["status"] == "answered"
    assert response["sources"]
    assert all(source["source_type"] == "pdf" for source in response["sources"])
    assert all(source["superseded"] is False for source in response["sources"])
    assert response["sources"][0]["source"] == "current.pdf"
    assert response["retrieval"]["source_filters"] == {
        "source_type": "pdf",
        "superseded": False,
    }


def test_rag_answers_with_page_aware_pdf_citation(tmp_path: Path) -> None:
    pdf_path = tmp_path / "fixture.pdf"
    _write_pdf_fixture(pdf_path)
    assistant = build_assistant_from_paths([pdf_path])

    response = assistant.answer("Which wet-weather transfer path assumptions are in the PDF?", k=2)

    assert response["status"] == "answered"
    assert "wet-weather transfer path" in response["answer"].lower()
    assert response["sources"][0]["source"] == "fixture.pdf"
    assert response["sources"][0]["page"] == "1"
    assert response["sources"][0]["chunk_id"].startswith("fixture-pdf-parking-access-notes-p1-")
    assert response["citation_check"]["passed"]


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


def test_dense_lsa_retrieval_returns_expected_metadata() -> None:
    chunks = chunk_text(
        """
        ## Daylight Strategy

        Deep floor plates should use atria, borrowed light, and zoning to improve daylight.

        ## Fire Strategy

        Stair discharge diagrams should identify protected lobby assumptions.
        """,
        source="design.md",
    )

    results = DenseLsaRetriever(chunks).search("borrowed light daylight zoning", k=2)

    assert results
    assert results[0].source == "design.md"
    assert results[0].metadata["retriever"] == "dense_lsa"
    assert results[0].metadata["dense_score"] is not None
    assert results[0].metadata["embedding_model"].startswith("local_tfidf")
    assert "daylight" in results[0].text.lower()


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


def test_rag_flags_superseded_and_mixed_version_sources() -> None:
    old = """
    document_id: access_old
    jurisdiction: synthetic-demo
    code_year: synthetic
    document_version: demo-v1
    superseded: true

    ## Doorway And Threshold Checks

    Doorways serving accessible rooms should provide doorway clearance and threshold notes.
    """
    current = """
    document_id: access_current
    jurisdiction: synthetic-demo
    code_year: synthetic
    document_version: demo-v2
    superseded: false

    ## Doorway And Threshold Checks

    Doorways serving accessible rooms should provide doorway clearance and threshold notes.
    Threshold changes greater than 12 mm should be resolved before issue.
    """
    chunks = chunk_text(old, source="access-old.md") + chunk_text(
        current, source="access-current.md"
    )
    assistant = RAGAssistant(chunks, min_score=0)

    response = assistant.answer("What doorway clearance and threshold checks apply?", k=2)

    assert response["status"] == "answered"
    assert response["source_status"]["requires_review"]
    assert "retrieved_superseded_sources" in response["source_status"]["warnings"]
    assert "mixed_document_versions" in response["source_status"]["warnings"]
    assert "source_status_review_required" in response["limitations"]
    assert "Source status note" in response["answer"]
    assert response["sources"][0]["document_version"] in {"demo-v1", "demo-v2"}
    assert response["citation_check"]["passed"]


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


def test_retrieval_mode_ablation_reports_all_modes(tmp_path: Path) -> None:
    text_path = tmp_path / "mock.md"
    text_path.write_text(
        """
        ## Planning Review Checklist

        Planning packages should explain setbacks, servicing strategy, and waste collection.
        """,
        encoding="utf-8",
    )
    cases = [
        RetrievalEvalCase(
            question="Which planning topics should be explained?",
            expected_source="mock.md",
            expected_section="Planning Review Checklist",
            expected_terms=["setbacks", "servicing strategy"],
        )
    ]
    payload = evaluate_retrieval_modes([text_path], cases, k=1)

    assert payload["modes"] == ["tfidf", "bm25", "dense_lsa", "hybrid"]
    assert {row["mode"] for row in payload["ranked_modes"]} == set(payload["modes"])
    assert payload["results"]["hybrid"]["summary"]["case_count"] == 1
    assert payload["results"]["dense_lsa"]["summary"]["status_accuracy"] == 1.0


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
