# ruff: noqa: E402, I001
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from aec_code_compliance_rag.service import ServiceSettings, create_service_app

app = create_service_app(ServiceSettings.from_environment(PROJECT_ROOT))
