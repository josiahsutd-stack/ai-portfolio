from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from project_specification_copilot import (  # noqa: E402
    load_evaluation_cases,
    load_language_stress_cases,
    write_evaluation_artifacts,
    write_language_stress_artifacts,
)


def main() -> None:
    cases = load_evaluation_cases(PROJECT_ROOT / "sample_data" / "synthetic_conversations.json")
    summary = write_evaluation_artifacts(cases, PROJECT_ROOT / "demo_outputs")
    stress_metadata, stress_cases = load_language_stress_cases(
        PROJECT_ROOT / "sample_data" / "language_stress_cases.json"
    )
    stress_summary = write_language_stress_artifacts(
        stress_cases, stress_metadata, PROJECT_ROOT / "demo_outputs"
    )
    print(json.dumps(summary["metrics"], indent=2))
    print(json.dumps(stress_summary["metrics"], indent=2))
    print(f"Wrote specification-copilot artifacts to {PROJECT_ROOT / 'demo_outputs'}")


if __name__ == "__main__":
    main()
