from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class TextExample:
    text: str
    label: str
    split: str


def default_examples() -> list[TextExample]:
    rows = [
        ("retrieve clause citations with page metadata for an accessibility query", "rag"),
        ("rank source chunks using hybrid retrieval and citation coverage", "rag"),
        ("answer no result when the local corpus has no supporting evidence", "rag"),
        ("download public guidance documents and build a source manifest", "rag"),
        ("evaluate recall at k and reciprocal rank for document retrieval", "rag"),
        ("filter retrieved clauses by jurisdiction and source status", "rag"),
        ("trace each answer sentence to a supporting source excerpt", "rag"),
        ("use page aware chunks from a building code pdf", "rag"),
        ("plan research steps then call tools with approval checkpoints", "agent"),
        ("persist an agent trace with tool calls citations and final answer", "agent"),
        ("route a task through planner executor and local search tools", "agent"),
        ("summarize local documents with human review before final output", "agent"),
        ("log tool errors and recover with a fallback search action", "agent"),
        ("store agent memory in sqlite for a repeatable workflow", "agent"),
        ("validate that unsupported tasks stop before external action", "agent"),
        ("compare tool traces against expected approval gates", "agent"),
        ("train churn model and write model metadata to a local registry", "mlops"),
        ("validate prediction schema before serving a model response", "mlops"),
        ("record inference payloads and probabilities in sqlite logs", "mlops"),
        ("calculate population stability index for drift monitoring", "mlops"),
        ("serve a model through an api with versioned metadata", "mlops"),
        ("generate monitoring report for model drift and schema checks", "mlops"),
        ("compare baseline and trained classifier metrics after fitting", "mlops"),
        ("persist fitted model weights for reproducible evaluation", "mlops"),
        ("cite the matched building guidance paragraph in the answer", "rag"),
        ("require approval before the agent sends a draft response", "agent"),
        ("check model feature schema before accepting prediction input", "mlops"),
    ]
    examples: list[TextExample] = []
    for index, (text, label) in enumerate(rows):
        split = "eval" if index in {6, 7, 14, 15, 22, 23, 24, 25, 26} else "train"
        examples.append(TextExample(text=text, label=label, split=split))
    return examples


def write_default_examples(path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([asdict(example) for example in default_examples()], indent=2) + "\n",
        encoding="utf-8",
    )


def load_examples(path: str | Path | None = None) -> list[TextExample]:
    if path is None:
        return default_examples()
    source = Path(path)
    if not source.exists():
        return default_examples()
    rows = json.loads(source.read_text(encoding="utf-8"))
    return [TextExample(**row) for row in rows]
