from __future__ import annotations

import re
from dataclasses import dataclass

SKILL_TERMS: dict[str, set[str]] = {
    "llm_systems": {
        "llm",
        "rag",
        "retrieval",
        "prompt",
        "langchain",
        "agents",
        "structured outputs",
    },
    "machine_learning": {
        "machine learning",
        "ml",
        "model evaluation",
        "feature engineering",
        "sklearn",
        "pytorch",
    },
    "computer_vision": {
        "computer vision",
        "cv",
        "image",
        "segmentation",
        "object detection",
        "site photos",
    },
    "backend": {"python", "fastapi", "api", "docker", "sql", "postgresql", "sqlite"},
    "data": {"pandas", "etl", "analytics", "pipeline", "dataset", "evaluation"},
    "aec_domain": {
        "aec",
        "architecture",
        "construction",
        "bim",
        "digital twin",
        "proptech",
        "building",
        "revit",
        "spatial",
    },
    "product": {"product", "prototype", "customer", "workflow", "automation", "stakeholder"},
}

CANDIDATE_STRENGTHS = {
    "python",
    "machine learning",
    "computer vision",
    "llm",
    "rag",
    "architecture",
    "aec",
    "bim",
    "design automation",
    "fastapi",
    "pandas",
    "scikit-learn",
    "spatial",
}


@dataclass(frozen=True)
class JobFitAnalysis:
    role_type: str
    fit_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    application_strategy: str

    def to_dict(self) -> dict[str, object]:
        return {
            "role_type": self.role_type,
            "fit_score": self.fit_score,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "application_strategy": self.application_strategy,
        }


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(description: str) -> list[str]:
    text = normalize(description)
    found: set[str] = set()
    for terms in SKILL_TERMS.values():
        for term in terms:
            if term in text:
                found.add(term)
    return sorted(found)


def classify_role(description: str) -> str:
    skills = set(extract_skills(description))
    ai_signal = bool(
        skills
        & (
            SKILL_TERMS["llm_systems"]
            | SKILL_TERMS["machine_learning"]
            | SKILL_TERMS["computer_vision"]
        )
    )
    aec_signal = bool(skills & SKILL_TERMS["aec_domain"])
    product_signal = bool(skills & SKILL_TERMS["product"])
    if ai_signal and aec_signal:
        return "AI + architecture / AEC"
    if ai_signal:
        return "pure AI"
    if aec_signal and product_signal:
        return "architecture-heavy but AI-relevant"
    if aec_signal:
        return "architecture-heavy but AI-relevant"
    return "weak fit"


def analyze_job_description(description: str) -> JobFitAnalysis:
    if not description.strip():
        return JobFitAnalysis(
            role_type="weak fit",
            fit_score=0,
            matched_skills=[],
            missing_skills=["job description content"],
            application_strategy="Paste a job description to evaluate fit and generate a targeted strategy.",
        )
    skills = set(extract_skills(description))
    role_type = classify_role(description)
    matched = sorted(skill for skill in skills if skill in CANDIDATE_STRENGTHS)
    missing = sorted(skill for skill in skills if skill not in CANDIDATE_STRENGTHS)
    base = 25 + len(matched) * 7 - len(missing) * 2
    if role_type == "AI + architecture / AEC":
        base += 25
    elif role_type == "pure AI":
        base += 12
    elif role_type == "architecture-heavy but AI-relevant":
        base += 8
    else:
        base -= 10
    score = max(0, min(100, base))
    strategy = _strategy(role_type, matched, missing)
    return JobFitAnalysis(role_type, score, matched, missing, strategy)


def _strategy(role_type: str, matched: list[str], missing: list[str]) -> str:
    if role_type == "AI + architecture / AEC":
        return (
            "Lead with the AI plus built-environment positioning. Show RAG, BIM QA, CV progress, "
            "and energy ML projects as evidence that the domain shift is already translated into software."
        )
    if role_type == "pure AI":
        return (
            "Lead with Python, ML evaluation, LLM systems, API delivery, and project depth. Use the AEC "
            "background as a differentiator, not the main qualification."
        )
    if role_type == "architecture-heavy but AI-relevant":
        return (
            "Position as a designer who can automate workflows and build AI tools. Ask whether the team "
            "needs prototypes, BIM QA, analytics, or internal AI adoption."
        )
    gaps = ", ".join(missing[:4]) if missing else "the core role requirements"
    return f"Treat as a low-priority application unless you can connect the role to {gaps}."
