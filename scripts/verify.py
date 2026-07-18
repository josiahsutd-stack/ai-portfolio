from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "scripts/generate_sample_data.py"],
    [sys.executable, "scripts/check_repo_health.py"],
    [sys.executable, "scripts/check_claims.py"],
    [sys.executable, "scripts/check_portfolio_site.py"],
    [sys.executable, "scripts/check_markdown_links.py"],
    [sys.executable, "scripts/run_smoke_tests.py"],
    [sys.executable, "scripts/generate_review_artifacts.py"],
    [sys.executable, "scripts/check_review_artifact_idempotence.py"],
    [sys.executable, "-m", "black", "--check", "."],
    [sys.executable, "-m", "ruff", "check", "."],
    [sys.executable, "-m", "pytest"],
]


def main() -> None:
    for command in COMMANDS:
        print("+", " ".join(command))
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
