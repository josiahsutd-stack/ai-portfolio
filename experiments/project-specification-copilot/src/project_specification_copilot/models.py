from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ROLES = (
    "client",
    "architect",
    "structural_engineer",
    "mep_engineer",
    "quantity_surveyor",
    "project_manager",
    "contractor",
)


@dataclass(frozen=True)
class Message:
    message_id: str
    sequence: int
    role: str
    author: str
    text: str
    data_status: str = "synthetic"

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"Unsupported project role: {self.role}")
        if not self.text.strip():
            raise ValueError("Message text cannot be empty.")


@dataclass
class Requirement:
    requirement_id: str
    category: str
    key: str
    value: str | float | int | bool
    unit: str | None
    statement: str
    status: str
    proposed_by_role: str
    source_message_ids: list[str] = field(default_factory=list)
    approved_by_role: str | None = None
    approval_message_id: str | None = None
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Conflict:
    conflict_id: str
    requirement_key: str
    requirement_ids: list[str]
    status: str = "open"
    resolution_requirement_id: str | None = None
    resolution_message_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuditEvent:
    event_id: int
    event_type: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class SpecificationClause:
    clause_id: str
    section: str
    requirement_id: str
    text: str
    source_message_ids: tuple[str, ...]
    approved_by_role: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SpecificationDraft:
    status: str
    version: str
    clauses: tuple[SpecificationClause, ...]
    open_conflict_ids: tuple[str, ...]
    unapproved_requirement_ids: tuple[str, ...]
    completeness: dict[str, bool]
    markdown: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProjectSnapshot:
    messages: tuple[Message, ...]
    requirements: tuple[Requirement, ...]
    conflicts: tuple[Conflict, ...]
    denied_approval_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
