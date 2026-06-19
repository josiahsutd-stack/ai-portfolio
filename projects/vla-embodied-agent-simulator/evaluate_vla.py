from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from vla_embodied_agent_simulator import write_evaluation_artifacts  # noqa: E402


def main() -> None:
    payload = write_evaluation_artifacts(PROJECT_ROOT / "demo_outputs")
    print(json.dumps(payload["policies"], indent=2))
    print(f"Wrote VLA artifacts to {PROJECT_ROOT / 'demo_outputs'}")


if __name__ == "__main__":
    main()
