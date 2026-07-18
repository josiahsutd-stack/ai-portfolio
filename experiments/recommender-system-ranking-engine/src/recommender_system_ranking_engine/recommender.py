from __future__ import annotations

import math

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def generate_interactions() -> tuple[pd.DataFrame, pd.DataFrame]:
    items = pd.DataFrame(
        [
            {"item_id": "course-llm", "title": "LLM Systems", "tags": "llm rag agents"},
            {"item_id": "course-vlm", "title": "Multimodal VLMs", "tags": "vision vlm multimodal"},
            {"item_id": "course-mlops", "title": "MLOps", "tags": "deployment monitoring drift"},
            {
                "item_id": "job-rl",
                "title": "RL Engineer",
                "tags": "reinforcement learning optimization",
            },
            {
                "item_id": "job-vla",
                "title": "Robotics VLA Engineer",
                "tags": "robotics embodied vla",
            },
        ]
    )
    interactions = pd.DataFrame(
        [
            {"user_id": "u1", "item_id": "course-llm", "rating": 5},
            {"user_id": "u1", "item_id": "course-vlm", "rating": 4},
            {"user_id": "u2", "item_id": "course-mlops", "rating": 5},
            {"user_id": "u2", "item_id": "job-vla", "rating": 4},
            {"user_id": "u3", "item_id": "job-rl", "rating": 5},
            {"user_id": "u3", "item_id": "course-mlops", "rating": 3},
        ]
    )
    return items, interactions


def popularity_recommend(interactions: pd.DataFrame, k: int = 3) -> list[str]:
    return (
        interactions.groupby("item_id")["rating"]
        .mean()
        .sort_values(ascending=False)
        .head(k)
        .index.tolist()
    )


def content_recommend(
    items: pd.DataFrame, profile_text: str, k: int = 3
) -> list[dict[str, object]]:
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(items["tags"].tolist() + [profile_text])
    scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
    ranked = scores.argsort()[::-1][:k]
    return [
        {"item_id": str(items.iloc[index]["item_id"]), "score": round(float(scores[index]), 3)}
        for index in ranked
    ]


def precision_at_k(recommended: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive.")
    return round(len(set(recommended[:k]) & relevant) / k, 3)


def ndcg_at_k(recommended: list[str], relevant: set[str], k: int) -> float:
    dcg = 0.0
    for index, item in enumerate(recommended[:k]):
        if item in relevant:
            dcg += 1 / math.log2(index + 2)
    ideal = sum(1 / math.log2(index + 2) for index in range(min(k, len(relevant))))
    return round(dcg / ideal if ideal else 0.0, 3)
