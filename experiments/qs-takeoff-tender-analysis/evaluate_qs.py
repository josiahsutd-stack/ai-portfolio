from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from qs_takeoff_tender_analysis import write_evaluation_artifacts  # noqa: E402


def main() -> None:
    summary = write_evaluation_artifacts(PROJECT_ROOT, PROJECT_ROOT / "demo_outputs")
    print(json.dumps(summary["metrics"], indent=2))
    print(f"Wrote QS evaluation artifacts to {PROJECT_ROOT / 'demo_outputs'}")


if __name__ == "__main__":
    main()
