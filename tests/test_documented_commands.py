from __future__ import annotations

from scripts.check_documented_commands import (
    DocumentedCommand,
    collect_issues,
    documented_commands,
    validate_command,
)
from scripts.reviewer_check import PUBLIC_CONTRACT_CHECKS, REVIEW_TEST_FILES, ROOT, commands


def command(text: str) -> DocumentedCommand:
    return DocumentedCommand(ROOT / "README.md", 1, text)


def test_public_documented_commands_resolve() -> None:
    assert documented_commands()
    assert collect_issues() == []


def test_missing_python_and_pytest_paths_fail() -> None:
    assert any(
        "missing Python script" in issue for issue in validate_command(command("python missing.py"))
    )
    assert any(
        "missing pytest file" in issue
        for issue in validate_command(command("python -m pytest tests/missing.py"))
    )


def test_missing_streamlit_and_uvicorn_targets_fail() -> None:
    assert any(
        "missing Streamlit app" in issue
        for issue in validate_command(command("streamlit run projects/missing/app.py"))
    )
    assert any(
        "missing Uvicorn module" in issue
        for issue in validate_command(
            command("python -m uvicorn missing.api:app --app-dir projects")
        )
    )


def test_placeholder_paths_are_not_treated_as_broken_commands() -> None:
    assert validate_command(command("streamlit run projects/<project-folder>/app.py")) == []


def test_reviewer_check_is_non_mutating_and_covers_selected_work() -> None:
    command_text = "\n".join(" ".join(item) for item in commands())
    assert all((ROOT / path).is_file() for path in PUBLIC_CONTRACT_CHECKS)
    assert all((ROOT / path).is_file() for path in REVIEW_TEST_FILES)
    assert "test_rag.py" in command_text
    assert "test_vla_embodied_agent.py" in command_text
    assert "test_massing_explorer.py" in command_text
    assert "generate_" not in command_text
    assert "--write" not in command_text
