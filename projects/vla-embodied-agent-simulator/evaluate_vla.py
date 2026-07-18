from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from vla_embodied_agent_simulator import (  # noqa: E402
    write_behavior_cloning_artifacts,
    write_evaluation_artifacts,
)


def main() -> None:
    output_dir = PROJECT_ROOT / "demo_outputs"
    model_output_dir = REPO_ROOT / ".artifacts" / "vla-embodied-agent-simulator"
    payload = write_evaluation_artifacts(output_dir)
    behavior_payload = write_behavior_cloning_artifacts(
        output_dir,
        model_output_dir=model_output_dir,
    )
    print(json.dumps(payload["policies"], indent=2))
    print(json.dumps(behavior_payload["policies"], indent=2))
    print(f"Wrote embodied-agent artifacts to {PROJECT_ROOT / 'demo_outputs'}")


if __name__ == "__main__":
    main()
