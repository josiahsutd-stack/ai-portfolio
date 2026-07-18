from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_portfolio_brief import DEFAULT_OUTPUT, generated_bytes  # noqa: E402


def collect_issues() -> list[str]:
    if not DEFAULT_OUTPUT.exists():
        return [f"missing generated portfolio brief: {DEFAULT_OUTPUT.name}"]
    if DEFAULT_OUTPUT.read_bytes() != generated_bytes():
        return [f"generated portfolio brief is stale: {DEFAULT_OUTPUT.name}"]
    return []


def main() -> None:
    issues = collect_issues()
    if issues:
        print("Portfolio brief check failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Portfolio brief check passed for the two-page artifact-backed PDF.")


if __name__ == "__main__":
    main()
