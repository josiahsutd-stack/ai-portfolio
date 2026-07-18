from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from multimodal_vlm_visual_qa import MockVLMProvider  # noqa: E402


def build_mock_contract_artifact() -> dict[str, object]:
    question = "Extract defects as JSON"
    response = MockVLMProvider().answer(
        b"\x89PNG\r\n\x1a\nsynthetic-contract-fixture",
        question,
    )
    return {
        "note": "Mock provider contract output. No visual inference was performed.",
        "question": question,
        **response.model_dump(),
    }


def main() -> None:
    output_path = PROJECT_ROOT / "demo_outputs" / "mock_vqa_output.json"
    output_path.write_text(
        json.dumps(build_mock_contract_artifact(), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote visual-provider contract artifact to {output_path}")


if __name__ == "__main__":
    main()
