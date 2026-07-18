from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from constraint_aware_massing_explorer import (  # noqa: E402
    load_scenarios,
    write_evaluation_artifacts,
)


def main() -> None:
    scenarios = load_scenarios(PROJECT_ROOT / "sample_data" / "synthetic_site_scenarios.json")
    summary = write_evaluation_artifacts(scenarios, PROJECT_ROOT / "demo_outputs")
    print(json.dumps(summary["aggregate"], indent=2))
    print(f"Wrote massing evaluation artifacts to {PROJECT_ROOT / 'demo_outputs'}")


if __name__ == "__main__":
    main()
