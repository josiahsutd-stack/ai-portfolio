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


FEATURES = {
    "community hall": ("program", "community_hall"),
    "childcare centre": ("program", "childcare_centre"),
    "childcare center": ("program", "childcare_centre"),
    "pharmacy": ("program", "pharmacy"),
    "basement parking": ("program", "basement_parking"),
    "roof garden": ("program", "roof_garden"),
}

APPROVAL_MARKERS = re.compile(
    r"\b(approve|approved|confirm|confirmed|agreed|accept|accepted)\b", re.I
)
REQUIREMENT_MARKERS = re.compile(
    r"\b(must|shall|need(?:s)?|require(?:s|d)?|provide|include|target|cap|limit|is to be)\b",
    re.I,
)
NEGATIVE_MARKERS = re.compile(r"\b(do not include|must not include|exclude|without)\b", re.I)


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


def extract_requirements(message: Message) -> list[ExtractedRequirement]:
    text = message.text.strip()
    lowered = text.lower()
    extracted: list[ExtractedRequirement] = []

    site_match = re.search(
        r"\bsite\s+area(?:\s+target)?\s*(?:is|of|=|:)?\s*([\d,]+(?:\.\d+)?)\s*(?:m2|sqm|square metres?)\b",
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
        r"\b(?:gross\s+floor\s+area|gfa)(?:\s+target)?\s*(?:is|of|=|:)?\s*([\d,]+(?:\.\d+)?)\s*(?:m2|sqm|square metres?)\b",
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
        r"\b(?:budget(?:\s+cap)?|cost\s+(?:cap|limit))\b[^\d]{0,24}(?:sgd|s\$|\$)?\s*([\d,]+(?:\.\d+)?)\s*(million|thousand|m|k)?\b",
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
        r"\b(?:across\s+)?(\d+)\s*[- ]?storey(?:s)?\b|\bstorey\s+count\s*(?:is|=|:)?\s*(\d+)\b",
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
        r"\b(?:occupancy|capacity)(?:\s+(?:target|is|of))?\s*(?:=|:)?\s*(\d+)\s*(?:people|occupants|users)?\b|\b(\d+)\s*(?:people|occupants|users)\b",
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

    eui_match = re.search(
        r"\b(?:energy\s+use\s+intensity|eui)(?:\s+target)?\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*kwh\s*/?\s*m2(?:\s*/?\s*year)?\b",
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
        (r"\b(\d+)\s+parking\s+spaces?\b", "access", "parking_space_count", "parking spaces"),
    )
    for pattern, category, key, unit in count_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            extracted.append(
                ExtractedRequirement(category, key, int(match.group(1)), unit, unit.title(), 0.96)
            )

    if "step-free access" in lowered or "step free access" in lowered:
        extracted.append(
            ExtractedRequirement(
                "access",
                "step_free_access",
                not bool(NEGATIVE_MARKERS.search(text)),
                None,
                "Step-free access",
                0.92,
            )
        )

    structural_match = re.search(
        r"\b(?:structural\s+system|primary\s+structure)\s+(?:must\s+be|shall\s+be|is\s+to\s+be|is)\s+([^.;]+)|\bapprove(?:d)?\s+(?:the\s+)?(?:structural\s+system|primary\s+structure)(?:\s+as)?\s+([^.;]+)",
        text,
        re.I,
    )
    if structural_match:
        structural_value = structural_match.group(1) or structural_match.group(2)
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
        r"\b(?:facade|external\s+wall)\s+(?:must\s+(?:use|be)|shall\s+(?:use|be)|is\s+to\s+(?:use|be)|is)\s+([^.;]+)|\bapprove(?:d)?\s+(?:the\s+)?(?:facade|external\s+wall)(?:\s+as)?\s+([^.;]+)",
        text,
        re.I,
    )
    if facade_match:
        material = _clean_material(facade_match.group(1) or facade_match.group(2))
        if re.search(r"\b(?:must\s+not|do\s+not)\b", lowered):
            material = f"not {material}"
        extracted.append(
            ExtractedRequirement(
                "design", "facade_material", material, None, "Facade material", 0.88
            )
        )

    if REQUIREMENT_MARKERS.search(text) or APPROVAL_MARKERS.search(text):
        for phrase, (category, key) in FEATURES.items():
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
