from ai_aec_job_fit_analyzer import analyze_job_description, classify_role, extract_skills


def test_classifies_ai_plus_aec_role() -> None:
    description = (
        "Build LLM RAG workflows and computer vision pipelines for BIM and construction analytics."
    )

    analysis = analyze_job_description(description)

    assert classify_role(description) == "AI + architecture / AEC"
    assert analysis.fit_score >= 60
    assert "llm" in extract_skills(description)


def test_empty_job_description_is_weak_fit() -> None:
    analysis = analyze_job_description(" ")

    assert analysis.role_type == "weak fit"
    assert analysis.fit_score == 0
    assert "job description content" in analysis.missing_skills
