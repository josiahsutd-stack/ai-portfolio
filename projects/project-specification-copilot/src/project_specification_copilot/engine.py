from __future__ import annotations

import hashlib
import re
from dataclasses import asdict
from typing import Any

from .extractor import ExtractedRequirement, extract_requirements, is_approval_message
from .models import (
    Conflict,
    Message,
    ProjectSnapshot,
    Requirement,
    SpecificationClause,
    SpecificationDraft,
)
from .store import AuditStore

APPROVAL_SCOPES = {
    "client": {"program", "budget", "schedule", "site", "access"},
    "architect": {"program", "design", "access", "compliance", "coordination"},
    "structural_engineer": {"structure"},
    "mep_engineer": {"performance", "building_services"},
    "quantity_surveyor": {"budget", "cost"},
    "project_manager": {"schedule", "coordination"},
    "contractor": set(),
}

SECTION_TITLES = {
    "site": "Site Parameters",
    "program": "Programme",
    "design": "Design Intent",
    "access": "Access And Movement",
    "structure": "Structural Requirements",
    "performance": "Performance Targets",
    "building_services": "Building Services",
    "budget": "Cost Parameters",
    "schedule": "Programme And Delivery",
    "compliance": "Compliance Coordination",
    "coordination": "Coordination",
}

COMPLETENESS_CATEGORIES = ("program", "site", "budget", "schedule", "access", "performance")


def _same_value(first: Any, second: Any) -> bool:
    if isinstance(first, (int, float)) and isinstance(second, (int, float)):
        return abs(float(first) - float(second)) < 1e-9
    return str(first).strip().lower() == str(second).strip().lower()


def _format_value(value: str | float | int | bool, unit: str | None) -> str:
    if isinstance(value, bool):
        rendered = "required" if value else "excluded"
    elif isinstance(value, float) and value.is_integer():
        rendered = f"{value:,.0f}"
    elif isinstance(value, (int, float)):
        rendered = f"{value:,}"
    else:
        rendered = str(value)
    return f"{rendered} {unit}" if unit else rendered


class SpecificationEngine:
    def __init__(self, store: AuditStore | None = None) -> None:
        self.store = store or AuditStore()
        self.messages: list[Message] = []
        self.requirements: list[Requirement] = []
        self.conflicts: list[Conflict] = []
        self.denied_approval_count = 0

    def submit_message(
        self,
        role: str,
        text: str,
        author: str | None = None,
        data_status: str = "synthetic",
    ) -> Message:
        message = Message(
            message_id=f"MSG-{len(self.messages) + 1:03d}",
            sequence=len(self.messages) + 1,
            role=role,
            author=author or role.replace("_", " ").title(),
            text=text.strip(),
            data_status=data_status,
        )
        self.messages.append(message)
        self.store.append("message_added", asdict(message))

        direct_ids = re.findall(r"\bREQ-\d{3}\b", message.text.upper())
        if is_approval_message(message.text):
            for requirement_id in direct_ids:
                self.approve_requirement(requirement_id, role, message.message_id)

        for extracted in extract_requirements(message):
            existing = self._find_active(extracted.key, extracted.value)
            if existing is not None:
                if message.message_id not in existing.source_message_ids:
                    existing.source_message_ids.append(message.message_id)
                    self.store.append(
                        "requirement_source_added",
                        {
                            "requirement_id": existing.requirement_id,
                            "message_id": message.message_id,
                        },
                    )
                if is_approval_message(message.text):
                    self.approve_requirement(existing.requirement_id, role, message.message_id)
                continue
            requirement = self._create_requirement(extracted, message)
            self._register_conflicts(requirement)
            if is_approval_message(message.text):
                self.approve_requirement(requirement.requirement_id, role, message.message_id)
        return message

    def _find_active(self, key: str, value: Any) -> Requirement | None:
        return next(
            (
                requirement
                for requirement in self.requirements
                if requirement.key == key
                and requirement.status in {"proposed", "approved"}
                and _same_value(requirement.value, value)
            ),
            None,
        )

    def _create_requirement(self, extracted: ExtractedRequirement, message: Message) -> Requirement:
        requirement = Requirement(
            requirement_id=f"REQ-{len(self.requirements) + 1:03d}",
            category=extracted.category,
            key=extracted.key,
            value=extracted.value,
            unit=extracted.unit,
            statement=extracted.statement,
            status="proposed",
            proposed_by_role=message.role,
            source_message_ids=[message.message_id],
            confidence=extracted.confidence,
        )
        self.requirements.append(requirement)
        self.store.append("requirement_extracted", requirement.to_dict())
        return requirement

    def _register_conflicts(self, requirement: Requirement) -> None:
        competing = [
            item
            for item in self.requirements
            if item.requirement_id != requirement.requirement_id
            and item.key == requirement.key
            and item.status in {"proposed", "approved"}
            and not _same_value(item.value, requirement.value)
        ]
        for other in competing:
            pair = sorted([requirement.requirement_id, other.requirement_id])
            existing = next(
                (
                    conflict
                    for conflict in self.conflicts
                    if sorted(conflict.requirement_ids) == pair and conflict.status == "open"
                ),
                None,
            )
            if existing is not None:
                continue
            conflict = Conflict(
                conflict_id=f"CON-{len(self.conflicts) + 1:03d}",
                requirement_key=requirement.key,
                requirement_ids=pair,
            )
            self.conflicts.append(conflict)
            self.store.append("conflict_opened", conflict.to_dict())

    def approve_requirement(
        self, requirement_id: str, role: str, message_id: str | None = None
    ) -> bool:
        requirement = next(
            (item for item in self.requirements if item.requirement_id == requirement_id), None
        )
        if requirement is None:
            self.store.append(
                "approval_denied",
                {
                    "requirement_id": requirement_id,
                    "role": role,
                    "reason": "unknown_requirement",
                    "message_id": message_id,
                },
            )
            self.denied_approval_count += 1
            return False
        if requirement.category not in APPROVAL_SCOPES.get(role, set()):
            self.store.append(
                "approval_denied",
                {
                    "requirement_id": requirement_id,
                    "role": role,
                    "reason": "role_not_authorized",
                    "message_id": message_id,
                },
            )
            self.denied_approval_count += 1
            return False
        requirement.status = "approved"
        requirement.approved_by_role = role
        requirement.approval_message_id = message_id
        for other in self.requirements:
            if (
                other.requirement_id != requirement.requirement_id
                and other.key == requirement.key
                and other.status in {"proposed", "approved"}
                and not _same_value(other.value, requirement.value)
            ):
                other.status = "superseded"
        for conflict in self.conflicts:
            if requirement.requirement_id in conflict.requirement_ids and conflict.status == "open":
                conflict.status = "resolved"
                conflict.resolution_requirement_id = requirement.requirement_id
                conflict.resolution_message_id = message_id
                self.store.append("conflict_resolved", conflict.to_dict())
        self.store.append(
            "requirement_approved",
            {"requirement_id": requirement.requirement_id, "role": role, "message_id": message_id},
        )
        return True

    def snapshot(self) -> ProjectSnapshot:
        return ProjectSnapshot(
            messages=tuple(self.messages),
            requirements=tuple(self.requirements),
            conflicts=tuple(self.conflicts),
            denied_approval_count=self.denied_approval_count,
        )

    def draft_specification(self) -> SpecificationDraft:
        approved = sorted(
            (requirement for requirement in self.requirements if requirement.status == "approved"),
            key=lambda requirement: (requirement.category, requirement.key),
        )
        clauses = tuple(
            SpecificationClause(
                clause_id=f"SPEC-{index:03d}",
                section=SECTION_TITLES.get(requirement.category, requirement.category.title()),
                requirement_id=requirement.requirement_id,
                text=f"{requirement.statement}: {_format_value(requirement.value, requirement.unit)}.",
                source_message_ids=tuple(requirement.source_message_ids),
                approved_by_role=requirement.approved_by_role or "unrecorded",
            )
            for index, requirement in enumerate(approved, start=1)
        )
        open_conflicts = tuple(
            conflict.conflict_id for conflict in self.conflicts if conflict.status == "open"
        )
        unapproved = tuple(
            requirement.requirement_id
            for requirement in self.requirements
            if requirement.status == "proposed"
        )
        approved_categories = {requirement.category for requirement in approved}
        completeness = {
            category: category in approved_categories for category in COMPLETENESS_CATEGORIES
        }
        version_payload = "|".join(
            f"{clause.requirement_id}:{clause.text}:{','.join(clause.source_message_ids)}"
            for clause in clauses
        )
        version = hashlib.sha256(version_payload.encode("utf-8")).hexdigest()[:12]
        status = "draft_for_review" if clauses else "needs_review"
        markdown = self._render_markdown(
            status, version, clauses, open_conflicts, unapproved, completeness
        )
        return SpecificationDraft(
            status, version, clauses, open_conflicts, unapproved, completeness, markdown
        )

    @staticmethod
    def _render_markdown(
        status: str,
        version: str,
        clauses: tuple[SpecificationClause, ...],
        open_conflicts: tuple[str, ...],
        unapproved: tuple[str, ...],
        completeness: dict[str, bool],
    ) -> str:
        lines = [
            "# Project Specification Draft",
            "",
            "**Status:** Human review required",
            "**Data status:** Synthetic demonstration conversation",
            f"**Draft version:** `{version}`",
            "",
            "This draft is assembled only from role-authorized approvals. It is not issued for construction, tender, statutory submission, or professional reliance.",
        ]
        current_section = None
        for clause in clauses:
            if clause.section != current_section:
                lines.extend(["", f"## {clause.section}"])
                current_section = clause.section
            citations = ", ".join(f"`{message_id}`" for message_id in clause.source_message_ids)
            lines.append(
                f"- **{clause.clause_id}** {clause.text} Sources: {citations}. Approved by `{clause.approved_by_role}` via `{clause.requirement_id}`."
            )
        if not clauses:
            lines.extend(["", "No clauses have passed an authorized approval gate."])
        lines.extend(["", "## Open Decisions"])
        lines.append(
            f"- Open conflicts: {', '.join(f'`{item}`' for item in open_conflicts) if open_conflicts else 'None recorded.'}"
        )
        lines.append(
            f"- Proposed requirements awaiting approval: {', '.join(f'`{item}`' for item in unapproved) if unapproved else 'None recorded.'}"
        )
        lines.extend(["", "## Completeness Check"])
        for category, present in completeness.items():
            result = "approved evidence present" if present else "missing approved evidence"
            lines.append(f"- {category.replace('_', ' ').title()}: {result}")
        lines.append("")
        return "\n".join(lines)
