from __future__ import annotations

import shlex
from pathlib import Path

import pytest
import yaml
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "projects" / "projects.yml"
MANIFEST_ROWS = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))["projects"]
DEPRECATED_STREAMLIT_TOKENS = (
    "use_container_width=",
    "st.experimental_",
    "st.beta_",
    "@st.cache\n",
    "@st.cache(",
)


def _row_id(row: dict[str, object]) -> str:
    return str(row["slug"])


def _expected_app_path(row: dict[str, object]) -> str:
    root = "experiments" if row["status"] == "experiment" else "projects"
    return f"{root}/{row['slug']}/app.py"


def _expected_api_path(row: dict[str, object]) -> Path:
    root = "experiments" if row["status"] == "experiment" else "projects"
    package = str(row["slug"]).replace("-", "_")
    return ROOT / root / str(row["slug"]) / "src" / package / "api.py"


API_ROWS = [row for row in MANIFEST_ROWS if _expected_api_path(row).is_file()]


@pytest.mark.parametrize("row", MANIFEST_ROWS, ids=_row_id)
def test_manifest_demo_and_test_commands_resolve(row: dict[str, object]) -> None:
    expected_app = _expected_app_path(row)
    demo_tokens = shlex.split(str(row["demo_command"]))

    assert demo_tokens == ["streamlit", "run", expected_app]
    assert (ROOT / expected_app).is_file()

    test_tokens = shlex.split(str(row["test_command"]))
    if test_tokens[:3] == ["python", "-m", "pytest"]:
        pytest_tokens = test_tokens[3:]
    else:
        assert test_tokens[:1] == ["pytest"]
        pytest_tokens = test_tokens[1:]

    test_paths = [
        token for token in pytest_tokens if token.startswith("tests/") and token.endswith(".py")
    ]
    assert test_paths, f"{row['slug']}: test command must name at least one test file"
    assert all((ROOT / path).is_file() for path in test_paths)


@pytest.mark.parametrize("row", MANIFEST_ROWS, ids=_row_id)
def test_manifest_app_loads_with_exact_title_and_current_api(row: dict[str, object]) -> None:
    relative_path = _expected_app_path(row)
    app_path = ROOT / relative_path
    source = app_path.read_text(encoding="utf-8")

    for token in DEPRECATED_STREAMLIT_TOKENS:
        assert token not in source, f"{relative_path}: deprecated Streamlit API `{token}`"

    app = AppTest.from_file(str(app_path)).run(timeout=30)

    assert not app.exception
    assert app.title
    assert app.title[0].value == row["name"]


@pytest.mark.parametrize("row", API_ROWS, ids=_row_id)
def test_manifest_api_title_matches_public_name(row: dict[str, object]) -> None:
    source = _expected_api_path(row).read_text(encoding="utf-8")

    assert f'FastAPI(title="{row["name"]}")' in source
