from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_documented_reviewer_check_runs_end_to_end() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/reviewer_check.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Reviewer check passed without regenerating tracked artifacts." in result.stdout
