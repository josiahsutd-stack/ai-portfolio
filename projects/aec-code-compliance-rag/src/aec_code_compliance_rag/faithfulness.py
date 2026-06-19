from __future__ import annotations

import re
from collections.abc import Iterable

from .retrieval import tokenize

CITATION_RE = re.compile(r"\[(C\d+)\]")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def check_citation_faithfulness(
    answer: str, citations: Iterable[dict[str, object]]
) -> dict[str, object]:
    citation_map = {str(citation["citation_id"]): citation for citation in citations}
    sentence_records = _sentence_records(answer)
    unsupported_sentences: list[str] = []
    warnings: list[str] = []
    citation_ids_used: set[str] = set()
    no_answer_like = any(
        phrase in answer.lower()
        for phrase in ["could not find", "no grounded evidence", "unsupported scope"]
    )
    for sentence, inherited_markers in sentence_records:
        markers = CITATION_RE.findall(sentence) or inherited_markers
        citation_ids_used.update(markers)
        if _is_limitation_sentence(sentence):
            continue
        if no_answer_like:
            continue
        if not markers:
            unsupported_sentences.append(sentence)
            continue
        for marker in markers:
            citation = citation_map.get(marker)
            if citation is None:
                warnings.append(f"citation_marker_not_found:{marker}")
                unsupported_sentences.append(sentence)
                continue
            excerpt_tokens = set(tokenize(str(citation.get("excerpt", ""))))
            sentence_tokens = {
                token
                for token in tokenize(sentence)
                if token not in {"based", "synthetic", "guidance", "review", "items"}
            }
            overlap = len(sentence_tokens & excerpt_tokens) / max(1, len(sentence_tokens))
            if overlap < 0.2:
                warnings.append(f"low_lexical_support:{marker}")
                unsupported_sentences.append(sentence)
    fake_markers = sorted(marker for marker in citation_ids_used if marker not in citation_map)
    cited_sentence_count = sum(
        1
        for sentence, inherited_markers in sentence_records
        if CITATION_RE.search(sentence) or inherited_markers
    )
    return {
        "passed": not unsupported_sentences and not fake_markers,
        "sentence_count": len(sentence_records),
        "cited_sentence_count": cited_sentence_count,
        "unsupported_sentences": unsupported_sentences,
        "citation_ids_used": sorted(citation_ids_used),
        "fake_citation_ids": fake_markers,
        "warnings": warnings,
    }


def _is_limitation_sentence(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(
        phrase in lowered
        for phrase in [
            "decision-support text only",
            "qualified reviewer",
            "governing jurisdiction",
            "current code version",
            "project-specific constraints",
            "professional compliance advice",
            "based on the synthetic demo guidance",
            "review these items",
        ]
    )


def _sentence_records(answer: str) -> list[tuple[str, list[str]]]:
    records: list[tuple[str, list[str]]] = []
    for line in answer.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        line_markers = CITATION_RE.findall(line)
        for sentence in SENTENCE_RE.split(line):
            sentence = sentence.strip()
            if len(tokenize(sentence)) >= 4:
                records.append((sentence, line_markers))
    return records
