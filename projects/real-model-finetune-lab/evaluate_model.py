from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from real_model_finetune_lab import write_default_examples, write_training_artifacts  # noqa: E402


def main() -> None:
    examples_path = PROJECT_ROOT / "sample_data" / "training_examples.json"
    if not examples_path.exists():
        write_default_examples(examples_path)
    result = write_training_artifacts(examples_path, PROJECT_ROOT / "demo_outputs")
    print(json.dumps(asdict(result), indent=2))
    print(f"Wrote real model artifacts to {PROJECT_ROOT / 'demo_outputs'}")


if __name__ == "__main__":
    main()
