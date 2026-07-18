from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py"],
    [sys.executable, "projects/agentic-research-ops-assistant/scripts/evaluate_agent.py"],
    [sys.executable, "projects/mlops-model-serving-monitoring/scripts/evaluate_model.py"],
    [sys.executable, "projects/real-model-finetune-lab/evaluate_model.py"],
    [sys.executable, "projects/vla-embodied-agent-simulator/evaluate_vla.py"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command))
        subprocess.run(command, cwd=ROOT, check=True)
    print(
        "Review artifacts generated for AEC RAG, Agentic Research Ops, MLOps, real model training, and VLA simulation."
    )


if __name__ == "__main__":
    main()
