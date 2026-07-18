from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Message


@dataclass(frozen=True)
class ExtractedRequirement:
    category: str
    key: str
    value: str | float | int | bool
    unit: str | None
    statement: str
    confidence: float


FEATURE_ALIASES = {
    "community hall": ("program", "community_hall"),
    "multipurpose community room": ("program", "community_hall"),
    "childcare centre": ("program", "childcare_centre"),
    "childcare center": ("program", "childcare_centre"),
    "day-care facility": ("program", "childcare_centre"),
    "day care facility": ("program", "childcare_centre"),
    "pharmacy": ("program", "pharmacy"),
    "basement parking": ("program", "basement_parking"),
    "roof garden": ("program", "roof_garden"),
    "rooftop garden": ("program", "roof_garden"),
}

APPROVAL_MARKERS = re.compile(
    r"\b(approve|approved|confirm|confirmed|agreed|accept|accepted)\b", re.I
)
REQUIREMENT_MARKERS = re.compile(
    r"\b(must|shall|need(?:s)?|require(?:s|d)?|provide|include|target|cap|limit|is to be)\b",
    re.I,
)
NEGATIVE_MARKERS = re.compile(
    r"\b(do not include|must not include|do not provide|must not provide|exclude|omit|without)\b",
    re.I,
)
QUESTION_PREFIX = re.compile(
    r"^\s*(can|could|would|should|may|might|what|when|where|why|how|do|does|did|is|are|was|were)\b",
    re.I,
)
NON_REQUIREMENT_CONTEXT = re.compile(
    r"\b(previous scheme|historical context|for reference only|old email|client rejected|was rejected)\b|^\s*ignore\b",
    re.I,
)


def is_approval_message(text: str) -> bool:
    return bool(APPROVAL_MARKERS.search(text))


def _number(raw: str) -> float:
    return float(raw.replace(",", ""))


def _money_value(amount: str, suffix: str | None) -> int:
    value = _number(amount)
    normalized_suffix = (suffix or "").lower()
    if normalized_suffix in {"m", "million"}:
        value *= 1_000_000
    elif normalized_suffix in {"k", "thousand"}:
        value *= 1_000
    return round(value)


def _clean_material(value: str) -> str:
    cleaned = re.split(r"[.;]|\b(?:and|but)\b", value, maxsplit=1, flags=re.I)[0]
    return re.sub(r"\s+", " ", cleaned).strip(" ,.-").lower()


def _is_non_requirement_context(text: str) -> bool:
    return bool(
        NON_REQUIREMENT_CONTEXT.search(text) or ("?" in text and QUESTION_PREFIX.search(text))
    )


def extract_requirements(message: Message) -> list[ExtractedRequirement]:
    text = message.text.strip()
    lowered = text.lower()
    extracted: list[ExtractedRequirement] = []
    if _is_non_requirement_context(text):
        return extracted

    site_match = re.search(
        r"\b(?:site\s+area|plot\s+(?:area|size))(?:\s+target)?\s*(?:is|of|=|:)?\s*([\d,]+(?:\.\d+)?)\s*(?:m2|sqm|square metres?)\b",
        text,
        re.I,
    )
    if site_match:
        extracted.append(
            ExtractedRequirement(
                "site", "site_area_m2", _number(site_match.group(1)), "m2", "Site area", 0.98
            )
        )

    gfa_match = re.search(
        r"\b(?:gross\s+floor\s+area|gfa|total\s+floor\s+(?:space|area))(?:\s+target)?\s*(?:is|of|to|=|:)?\s*([\d,]+(?:\.\d+)?)\s*(?:m2|sqm|square metres?)\b",
        text,
        re.I,
    )
    if gfa_match:
        extracted.append(
            ExtractedRequirement(
                "program",
                "gross_floor_area_m2",
                _number(gfa_match.group(1)),
                "m2",
                "Gross floor area",
                0.98,
            )
        )

    budget_match = re.search(
        r"\b(?:budget(?:\s+cap)?|cost\s+(?:cap|limit)|maximum\s+spend)\b[^\d]{0,24}(?:sgd|s\$|\$)?\s*([\d,]+(?:\.\d+)?)\s*(million|thousand|m|k)?\b",
        text,
        re.I,
    )
    if budget_match:
        extracted.append(
            ExtractedRequirement(
                "budget",
                "budget_cap_sgd",
                _money_value(budget_match.group(1), budget_match.group(2)),
                "SGD",
                "Project budget cap",
                0.97,
            )
        )

    storey_match = re.search(
        r"\b(?:across\s+)?(\d+)\s*[- ]?(?:storey|level)(?:s)?\b|\bstorey\s+count\s*(?:is|=|:)?\s*(\d+)\b",
        text,
        re.I,
    )
    if storey_match:
        extracted.append(
            ExtractedRequirement(
                "program",
                "storey_count",
                int(storey_match.group(1) or storey_match.group(2)),
                "storeys",
                "Storey count",
                0.97,
            )
        )

    occupancy_match = re.search(
        r"\b(?:occupancy|capacity)(?:\s+(?:target|is|of))?\s*(?:=|:)?\s*(\d+)\s*(?:people|occupants|users|visitors)?\b|\b(\d+)\s*(?:people|occupants|users|visitors)\b",
        text,
        re.I,
    )
    if occupancy_match:
        extracted.append(
            ExtractedRequirement(
                "program",
                "occupancy_count",
                int(occupancy_match.group(1) or occupancy_match.group(2)),
                "people",
                "Design occupancy",
                0.94,
            )
        )

    schedule_match = re.search(
        r"\b(?:handover|completion)(?:\s+(?:target|date))?\s*(?:must\s+be|is|by|:)?\s*(?:by\s+)?(q[1-4]\s+20\d{2}|(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+20\d{2})\b",
        text,
        re.I,
    )
    if schedule_match:
        extracted.append(
            ExtractedRequirement(
                "schedule",
                "handover_target",
                schedule_match.group(1).upper(),
                None,
                "Handover target",
                0.94,
            )
        )

    quarter_match = re.search(
        r"\b(?:handover|completion|keys?)\b[^.;]{0,36}\b(first|second|third|fourth)\s+quarter\s+of\s+(20\d{2})\b",
        text,
        re.I,
    )
    if quarter_match:
        quarter = {"first": 1, "second": 2, "third": 3, "fourth": 4}[quarter_match.group(1).lower()]
        extracted.append(
            ExtractedRequirement(
                "schedule",
                "handover_target",
                f"Q{quarter} {quarter_match.group(2)}",
                None,
                "Handover target",
                0.88,
            )
        )

    eui_match = re.search(
        r"\b(?:energy\s+use\s+intensity|eui|operational\s+energy\s+intensity)(?:\s+target)?\s*(?:is|at|=|:)?\s*(\d+(?:\.\d+)?)\s*kwh\s*(?:/|per)\s*(?:m2|square\s+metres?)(?:\s*(?:/|per)?\s*(?:year|annually))?\b",
        text,
        re.I,
    )
    if eui_match:
        extracted.append(
            ExtractedRequirement(
                "performance",
                "energy_use_intensity_kwh_m2_year",
                _number(eui_match.group(1)),
                "kWh/m2/year",
                "Energy use intensity target",
                0.98,
            )
        )

    count_patterns = (
        (
            r"\b(\d+)\s+consultation\s+rooms?\b",
            "program",
            "consultation_room_count",
            "consultation rooms",
        ),
        (r"\b(\d+)\s+loading\s+bays?\b", "access", "loading_bay_count", "loading bays"),
        (r"\b(\d+)\s+service\s+docks?\b", "access", "loading_bay_count", "loading bays"),
        (r"\b(\d+)\s+parking\s+spaces?\b", "access", "parking_space_count", "parking spaces"),
        (r"\b(\d+)\s+car\s+lots?\b", "access", "parking_space_count", "parking spaces"),
    )
    for pattern, category, key, unit in count_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            extracted.append(
                ExtractedRequirement(category, key, int(match.group(1)), unit, unit.title(), 0.96)
            )

    without_steps = bool(
        re.search(r"\b(?:entrance|access)\b[^.;]{0,32}\bwithout\s+steps\b", text, re.I)
    )
    if "step-free access" in lowered or "step free access" in lowered or without_steps:
        extracted.append(
            ExtractedRequirement(
                "access",
                "step_free_access",
                True if without_steps else not bool(NEGATIVE_MARKERS.search(text)),
                None,
                "Step-free access",
                0.92,
            )
        )

    structural_match = re.search(
        r"\b(?:structural\s+system|primary\s+structure)\s+(?:must\s+be|shall\s+be|is\s+to\s+be|is)\s+([^.;]+)|\bapprove(?:d)?\s+(?:the\s+)?(?:structural\s+system|primary\s+structure)(?:\s+as)?\s+([^.;]+)|\buse\s+([^.;]+?)\s+for\s+(?:the\s+)?(?:structural\s+system|primary\s+structure)\b",
        text,
        re.I,
    )
    if structural_match:
        structural_value = (
            structural_match.group(1) or structural_match.group(2) or structural_match.group(3)
        )
        extracted.append(
            ExtractedRequirement(
                "structure",
                "structural_system",
                _clean_material(structural_value),
                None,
                "Primary structural system",
                0.90,
            )
        )

    facade_match = re.search(
        r"\b(?:facade|external\s+wall|envelope)\s+(?:must\s+(?:use|be)|shall\s+(?:use|be)|is\s+to\s+(?:use|be)|is)\s+([^.;]+)|\bapprove(?:d)?\s+(?:the\s+)?(?:facade|external\s+wall|envelope)(?:\s+as)?\s+([^.;]+)|\b([^.;]+?)\s+is\s+preferred\s+for\s+(?:the\s+)?(?:facade|external\s+wall|envelope)\b",
        text,
        re.I,
    )
    if facade_match:
        material = _clean_material(
            facade_match.group(1) or facade_match.group(2) or facade_match.group(3)
        )
        if re.search(r"\b(?:must\s+not|do\s+not)\b", lowered):
            material = f"not {material}"
        extracted.append(
            ExtractedRequirement(
                "design", "facade_material", material, None, "Facade material", 0.88
            )
        )

    if REQUIREMENT_MARKERS.search(text) or APPROVAL_MARKERS.search(text):
        for phrase, (category, key) in FEATURE_ALIASES.items():
            if phrase not in lowered:
                continue
            extracted.append(
                ExtractedRequirement(
                    category,
                    key,
                    not bool(NEGATIVE_MARKERS.search(text)),
                    None,
                    phrase.title(),
                    0.86,
                )
            )

    unique: dict[tuple[str, str], ExtractedRequirement] = {}
    for item in extracted:
        unique[(item.key, repr(item.value))] = item
    return list(unique.values())
