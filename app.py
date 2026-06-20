from __future__ import annotations

import runpy
from pathlib import Path

PROJECT_APP = Path(__file__).resolve().parent / "projects" / "aec-code-compliance-rag" / "app.py"

runpy.run_path(str(PROJECT_APP), run_name="__main__")
