from aec_code_compliance_rag import RAGAssistant, chunk_text


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


def test_rag_handles_empty_question() -> None:
    assistant = RAGAssistant(chunk_text("Door clearances need checking.", source="mock.md"))

    response = assistant.answer("")

    assert response["sources"] == []
    assert "provide" in response["answer"].lower()
