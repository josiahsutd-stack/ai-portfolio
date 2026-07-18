from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_CONTRACT_CHECKS = [
    "scripts/check_repo_health.py",
    "scripts/check_claims.py",
    "scripts/check_documented_commands.py",
    "scripts/check_profile_readme.py",
    "scripts/check_visual_contract.py",
    "scripts/check_portfolio_site.py",
    "scripts/check_markdown_links.py",
    "scripts/check_evidence_claims.py",
]
REVIEW_TEST_FILES = [
    "tests/test_rag.py",
    "tests/test_rag_service.py",
    "tests/test_vla_embodied_agent.py",
    "tests/test_massing_explorer.py",
    "tests/test_aec_workflow_integration.py",
    "tests/test_evidence_claims.py",
    "tests/test_manifest_commands.py",
    "tests/test_public_claims.py",
    "tests/test_documented_commands.py",
    "tests/test_profile_readme.py",
    "tests/test_visual_contract.py",
]


def commands() -> list[list[str]]:
    checks = [[sys.executable, path] for path in PUBLIC_CONTRACT_CHECKS]
    tests = [sys.executable, "-m", "pytest", *REVIEW_TEST_FILES]
    return [*checks, tests]


def main() -> None:
    print("Portfolio reviewer check: public contract and selected-work evidence")
    for command in commands():
        print("+", " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    print("Reviewer check passed without regenerating tracked artifacts.")


if __name__ == "__main__":
    main()
