from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py"],
    [sys.executable, "projects/constraint-aware-massing-explorer/evaluate_massing.py"],
    [sys.executable, "projects/project-specification-copilot/evaluate_specification.py"],
    [sys.executable, "projects/qs-takeoff-tender-analysis/evaluate_qs.py"],
    [sys.executable, "integrations/aec-design-to-cost/run_workflow.py"],
    [sys.executable, "experiments/agentic-research-ops-assistant/scripts/evaluate_agent.py"],
    [sys.executable, "experiments/mlops-model-serving-monitoring/scripts/evaluate_model.py"],
    [sys.executable, "experiments/building-energy-ml-pipeline/evaluate_model.py"],
    [sys.executable, "experiments/site-robot-safety-monitor/generate_demo_report.py"],
    [sys.executable, "experiments/multimodal-vlm-visual-qa/generate_contract_artifact.py"],
    [sys.executable, "experiments/real-model-finetune-lab/evaluate_model.py"],
    [sys.executable, "projects/vla-embodied-agent-simulator/evaluate_vla.py"],
    [sys.executable, "scripts/check_evidence_claims.py", "--write"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command))
        subprocess.run(command, cwd=ROOT, check=True)
    print(
        "Review artifacts and the headline evidence ledger were generated from current project outputs."
    )


if __name__ == "__main__":
    main()
