from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from shared.ai import TfidfVectorStore, get_llm_provider

from .trace_store import SQLiteTraceStore, default_trace_db, evaluate_trace, utc_now


class ToolCall(BaseModel):
    name: str
    args: dict[str, str] = Field(default_factory=dict)
    output: str
    status: str = "ok"
    attempts: int = 1
    latency_ms: int = 0
    error: str | None = None
    errors: list[str] = Field(default_factory=list)
    requires_approval: bool = False


class WorkflowTrace(BaseModel):
    trace_id: str
    started_at: str
    task: str
    planner_reason: str = ""
    task_intent: str = "report"
    plan: list[str]
    tool_calls: list[ToolCall]
    citations: list[str]
    approval_required: bool
    final_report: str
    evaluation: dict[str, object] = Field(default_factory=dict)


class ToolSpec(BaseModel):
    name: str
    description: str
    requires_approval: bool = False


class ResearchWorkflow:
    def __init__(
        self,
        docs_dir: str | Path,
        memory_path: str | Path | None = None,
        *,
        trace_db_path: str | Path | None = None,
        allowed_tools: set[str] | None = None,
        max_retries: int = 1,
    ) -> None:
        self.docs_dir = Path(docs_dir)
        self.memory_path = Path(memory_path or self.docs_dir.parent / "workflow_memory.json")
        self.trace_store = SQLiteTraceStore(trace_db_path or default_trace_db(self.docs_dir))
        self.allowed_tools = allowed_tools
        self.max_retries = max_retries
        self.provider = get_llm_provider()
        self.docs = self._load_documents()
        self.store = TfidfVectorStore()
        self.store.add_texts(self.docs.values(), sources=self.docs.keys())
        self.tool_specs = {
            "search_local_docs": ToolSpec(
                name="search_local_docs",
                description="Retrieve locally indexed documents for the task.",
            ),
            "summarize_document": ToolSpec(
                name="summarize_document",
                description="Summarize retrieved evidence into reviewable snippets.",
            ),
            "extract_entities": ToolSpec(
                name="extract_entities",
                description="Extract relevant AI/operations entities from evidence.",
            ),
            "compare_sources": ToolSpec(
                name="compare_sources",
                description="Compare retrieved sources and expose evidence coverage.",
            ),
            "create_report": ToolSpec(
                name="create_report",
                description="Create a cited research brief.",
            ),
            "ask_human_approval": ToolSpec(
                name="ask_human_approval",
                description="Require human approval before external use.",
                requires_approval=True,
            ),
            "save_memory": ToolSpec(
                name="save_memory",
                description="Persist the run trace and evaluation.",
            ),
        }

    def _load_documents(self) -> dict[str, str]:
        documents: dict[str, str] = {}
        for pattern in ("*.md", "*.txt"):
            for path in self.docs_dir.glob(pattern):
                documents[path.name] = path.read_text(encoding="utf-8")
        return documents

    def classify_intent(self, task: str) -> str:
        lowered = task.lower()
        if any(word in lowered for word in ["web", "internet", "live", "current"]):
            return "unsupported"
        if any(word in lowered for word in ["compare", "versus", "vs", "tradeoff"]):
            return "compare"
        if any(word in lowered for word in ["extract", "entities", "keywords"]):
            return "extract"
        if any(word in lowered for word in ["summarize", "summary"]):
            return "summarize"
        return "report"

    def planner_reason(self, task: str, intent: str) -> str:
        if intent == "unsupported":
            return "Default local planner rejects live-web/current-information tasks."
        return f"Default deterministic local planner selected `{intent}` workflow over local documents."

    def plan(self, task: str) -> list[str]:
        intent = self.classify_intent(task)
        if intent == "unsupported":
            return ["create_report", "ask_human_approval", "save_memory"]
        plan = ["search_local_docs", "summarize_document", "extract_entities", "create_report"]
        if intent == "compare":
            plan.insert(3, "compare_sources")
        plan.extend(["ask_human_approval", "save_memory"])
        return [tool for tool in plan if self._tool_allowed(tool)]

    def _tool_allowed(self, name: str) -> bool:
        return self.allowed_tools is None or name in self.allowed_tools

    def _run_tool(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        tool_args: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> tuple[Any, ToolCall]:
        spec = self.tool_specs.get(name)
        if not self._tool_allowed(name):
            return None, ToolCall(
                name=name,
                args=tool_args or {},
                output=f"Tool `{name}` is not allowed for this run.",
                status="denied",
                attempts=0,
                requires_approval=bool(spec.requires_approval) if spec else False,
                error="permission_denied",
            )
        attempts = 0
        started = time.perf_counter()
        last_error: Exception | None = None
        errors: list[str] = []
        while attempts <= self.max_retries:
            attempts += 1
            try:
                result = func(*args, **kwargs)
                latency_ms = int((time.perf_counter() - started) * 1000)
                return result, ToolCall(
                    name=name,
                    args=tool_args or {},
                    output=self._tool_output_summary(result),
                    attempts=attempts,
                    latency_ms=latency_ms,
                    errors=errors,
                    requires_approval=bool(spec.requires_approval) if spec else False,
                )
            except Exception as exc:  # noqa: BLE001 - trace failed tool behavior.
                last_error = exc
                errors.append(str(exc))
        latency_ms = int((time.perf_counter() - started) * 1000)
        return None, ToolCall(
            name=name,
            args=tool_args or {},
            output=str(last_error),
            status="error",
            attempts=attempts,
            latency_ms=latency_ms,
            error=str(last_error) if last_error else "unknown_error",
            errors=errors,
            requires_approval=bool(spec.requires_approval) if spec else False,
        )

    def _tool_output_summary(self, result: Any) -> str:
        if isinstance(result, list):
            return f"{len(result)} items"
        text = str(result)
        return text if len(text) <= 180 else text[:177] + "..."

    def available_tools(self) -> list[ToolSpec]:
        return [spec for name, spec in self.tool_specs.items() if self._tool_allowed(name)]

    def search_local_docs(self, query: str) -> list[tuple[str, str]]:
        return [
            (result.source, result.text) for result in self.store.search(query, k=3, min_score=0.05)
        ]

    def summarize_document(self, text: str) -> str:
        return text.strip().replace("\n", " ")[:360]

    def extract_entities(self, text: str) -> list[str]:
        keywords = ["AI", "deployment", "multimodal", "model", "workflow", "monitoring", "edge"]
        return [keyword for keyword in keywords if keyword.lower() in text.lower()]

    def compare_sources(self, sources: list[tuple[str, str]]) -> str:
        names = ", ".join(source for source, _text in sources) or "no sources"
        return f"Compared evidence from: {names}."

    def create_report(self, task: str, sources: list[tuple[str, str]]) -> str:
        if not sources:
            return (
                "# Research Brief\n\n"
                f"Task: {task}\n\n"
                "No grounded local evidence was found in the demo document set. "
                "The workflow should not invent findings or cite unavailable sources."
            )
        evidence = "\n".join(
            f"- {source}: {self.summarize_document(text)}" for source, text in sources
        )
        return f"# Research Brief\n\nTask: {task}\n\n## Cited Findings\n\n{evidence}\n\n## Recommendation\n\nUse the cited evidence as a starting point and request human approval before finalizing."

    def ask_human_approval(self) -> str:
        return "Human approval required before sending or publishing the report."

    def save_memory(self, trace: WorkflowTrace) -> None:
        self.memory_path.write_text(trace.model_dump_json(indent=2), encoding="utf-8")
        self.trace_store.save(
            trace_id=trace.trace_id,
            task=trace.task,
            approval_required=trace.approval_required,
            trace=trace.model_dump(),
            evaluation=trace.evaluation,
        )

    def retrieve_memory(self) -> dict[str, object]:
        if not self.memory_path.exists():
            return {}
        return json.loads(self.memory_path.read_text(encoding="utf-8"))

    def run(self, task: str) -> WorkflowTrace:
        intent = self.classify_intent(task)
        plan = self.plan(task)
        tool_calls: list[ToolCall] = []
        if "search_local_docs" in plan:
            sources, search_call = self._run_tool(
                "search_local_docs",
                self.search_local_docs,
                task,
                tool_args={"query": task},
            )
            sources = sources or []
            tool_calls.append(search_call)
        else:
            sources = []
        sources = sources or []
        if "summarize_document" in plan:
            _summaries, summary_call = self._run_tool(
                "summarize_document",
                lambda values: [self.summarize_document(text) for _source, text in values],
                sources,
            )
            tool_calls.append(summary_call)
        entities: list[str] = []
        if "extract_entities" in plan:
            entities, entity_call = self._run_tool(
                "extract_entities",
                self.extract_entities,
                " ".join(text for _source, text in sources),
            )
            tool_calls.append(entity_call)
        if "compare_sources" in plan:
            _comparison, compare_call = self._run_tool(
                "compare_sources", self.compare_sources, sources
            )
            tool_calls.append(compare_call)
        report = ""
        if "create_report" in plan:
            report, report_call = self._run_tool(
                "create_report",
                self.create_report,
                task,
                sources,
                tool_args={"entities": ", ".join(entities)},
            )
            report = report or ""
            tool_calls.append(report_call)
        if not report:
            report = (
                "# Research Brief\n\n"
                f"Task: {task}\n\n"
                "The deterministic local planner could not create a cited report from available tools."
            )
        approval_required = "ask_human_approval" in plan
        if approval_required:
            _approval, approval_call = self._run_tool(
                "ask_human_approval",
                self.ask_human_approval,
            )
            tool_calls.append(approval_call)
        trace = WorkflowTrace(
            trace_id=str(uuid.uuid4()),
            started_at=utc_now(),
            task=task,
            planner_reason=self.planner_reason(task, intent),
            task_intent=intent,
            plan=plan,
            tool_calls=tool_calls,
            citations=[source for source, _text in sources],
            approval_required=approval_required,
            final_report=report,
        )
        trace.evaluation = evaluate_trace(trace.model_dump())
        if "save_memory" in plan:
            self.save_memory(trace)
        return trace

    def recent_traces(self, *, limit: int = 10) -> list[dict[str, object]]:
        return self.trace_store.list_recent(limit=limit)


def run_research_workflow(task: str, docs_dir: str | Path) -> WorkflowTrace:
    return ResearchWorkflow(docs_dir).run(task)
