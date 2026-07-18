from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIRS = [
    ROOT / "projects" / "aec-code-compliance-rag" / "demo_outputs",
    ROOT / "projects" / "constraint-aware-massing-explorer" / "demo_outputs",
    ROOT / "projects" / "project-specification-copilot" / "demo_outputs",
    ROOT / "projects" / "qs-takeoff-tender-analysis" / "demo_outputs",
    ROOT / "integrations" / "aec-design-to-cost" / "demo_outputs",
    ROOT / "experiments" / "agentic-research-ops-assistant" / "demo_outputs",
    ROOT / "experiments" / "mlops-model-serving-monitoring" / "demo_outputs",
    ROOT / "experiments" / "building-energy-ml-pipeline" / "demo_outputs",
    ROOT / "experiments" / "site-robot-safety-monitor" / "demo_outputs",
    ROOT / "experiments" / "multimodal-vlm-visual-qa" / "demo_outputs",
    ROOT / "experiments" / "real-model-finetune-lab" / "demo_outputs",
    ROOT / "projects" / "vla-embodied-agent-simulator" / "demo_outputs",
]
ARTIFACT_FILES = [
    ROOT / "docs" / "EVIDENCE_LEDGER.md",
    ROOT / "portfolio-site" / "assets" / "aec-workflow-trace.svg",
    ROOT / "portfolio-site" / "assets" / "semantic-raster-comparison.svg",
    ROOT / "portfolio-site" / "assets" / "physics-replay-comparison.svg",
]
VERSIONED_SUFFIXES = {".json", ".md", ".svg"}


def artifact_hashes() -> dict[Path, str]:
    candidates = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            *[str(path.relative_to(ROOT)) for path in [*ARTIFACT_DIRS, *ARTIFACT_FILES]],
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    paths = sorted(
        ROOT / path
        for path in candidates
        if (ROOT / path).is_file() and (ROOT / path).suffix in VERSIONED_SUFFIXES
    )
    return {path.relative_to(ROOT): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def main() -> None:
    before = artifact_hashes()
    subprocess.run(
        [sys.executable, "scripts/generate_review_artifacts.py"],
        cwd=ROOT,
        check=True,
    )
    after = artifact_hashes()
    changed = sorted(
        path for path in before.keys() | after.keys() if before.get(path) != after.get(path)
    )
    if changed:
        print("Review artifact idempotence check failed:")
        for path in changed:
            print(f"- {path}")
        raise SystemExit(1)
    print(f"Review artifact idempotence check passed for {len(after)} text artifacts.")


if __name__ == "__main__":
    main()
