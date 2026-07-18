from __future__ import annotations

import io

from pypdf import PdfReader

from scripts.check_portfolio_brief import collect_issues
from scripts.generate_portfolio_brief import DEFAULT_OUTPUT, build_context, generated_bytes


def test_portfolio_brief_metrics_come_from_current_artifacts() -> None:
    context = build_context()

    assert context["aec"]["document_hit_at_1"] == 0.952
    assert context["aec"]["exact_hit_at_1"] == 0.81
    assert context["embodied"]["filtered_success"] == 0.76
    assert context["embodied"]["raw_contacts"] == 51
    assert context["massing"]["feasible_rate"] == 0.976852


def test_portfolio_brief_is_deterministic_and_current() -> None:
    first = generated_bytes()
    second = generated_bytes()

    assert first == second
    assert DEFAULT_OUTPUT.read_bytes() == first
    assert collect_issues() == []


def test_portfolio_brief_has_two_readable_pages_and_boundaries() -> None:
    reader = PdfReader(io.BytesIO(generated_bytes()))
    text = " ".join("\n".join(page.extract_text() or "" for page in reader.pages).split())

    assert len(reader.pages) == 2
    assert "Three projects, three kinds of engineering evidence" in text
    assert "Hit@1 0.952" in text
    assert "Success 0.760" in text
    assert "Feasible 0.977" in text
    assert "No customer adoption" in text
    assert "No physical camera, ROS, robot hardware" in text
    assert "Neither source is third-party validation" in text


def test_portfolio_brief_contains_clickable_review_routes() -> None:
    reader = PdfReader(io.BytesIO(generated_bytes()))
    urls: set[str] = set()
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get("/URI"):
                urls.add(str(action["/URI"]))

    assert "https://josiahsutd-stack.github.io/ai-portfolio/" in urls
    assert "https://github.com/josiahsutd-stack/ai-portfolio" in urls
    assert "https://www.linkedin.com/in/josiah-lau-8041822b6/" in urls
    assert any(url.endswith("pages/aec-rag.html") for url in urls)
    assert any(url.endswith("pages/embodied-ai.html") for url in urls)
    assert any(url.endswith("pages/massing-explorer.html") for url in urls)
