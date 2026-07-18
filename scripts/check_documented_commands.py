from __future__ import annotations

import re
import shlex
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_claims import public_text_files  # noqa: E402

COMMAND_PREFIXES = (
    "python ",
    "python3 ",
    "pytest ",
    "streamlit ",
    "pip ",
    "pip3 ",
    "docker ",
)
PLACEHOLDER_PATTERN = re.compile(r"<[^>]+>|\$\{?\w+\}?")


@dataclass(frozen=True)
class DocumentedCommand:
    source: Path
    line: int
    text: str

    @property
    def label(self) -> str:
        return f"{self.source.relative_to(ROOT)}:{self.line}"


class CodeCommandParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__()
        self.source = source
        self.in_code = False
        self.commands: list[DocumentedCommand] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "code":
            self.in_code = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "code":
            self.in_code = False

    def handle_data(self, data: str) -> None:
        if not self.in_code:
            return
        for offset, line in enumerate(data.splitlines() or [data]):
            stripped = line.strip()
            if _is_command(stripped):
                self.commands.append(
                    DocumentedCommand(self.source, self.getpos()[0] + offset, stripped)
                )


def _is_command(text: str) -> bool:
    lowered = text.lower()
    return any(lowered.startswith(prefix) for prefix in COMMAND_PREFIXES)


def documented_commands() -> list[DocumentedCommand]:
    commands: list[DocumentedCommand] = []
    for path in public_text_files():
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".html":
            parser = CodeCommandParser(path)
            parser.feed(text)
            commands.extend(parser.commands)
            continue
        in_fence = False
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence and _is_command(stripped):
                commands.append(DocumentedCommand(path, line_number, stripped))
    return commands


def _resolve_path(source: Path, token: str) -> Path | None:
    cleaned = token.strip("'\"")
    if not cleaned or PLACEHOLDER_PATTERN.search(cleaned):
        return None
    candidates = [ROOT / cleaned, source.parent / cleaned]
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


def _missing_path_issue(command: DocumentedCommand, token: str, purpose: str) -> str | None:
    path = _resolve_path(command.source, token)
    if path is None or path.exists():
        return None
    return f"{command.label}: missing {purpose} `{token}` in `{command.text}`"


def _option_values(tokens: list[str], option: str) -> list[str]:
    values: list[str] = []
    for index, token in enumerate(tokens[:-1]):
        if token == option:
            values.append(tokens[index + 1])
    return values


def _validate_requirements(command: DocumentedCommand, tokens: list[str]) -> list[str]:
    return [
        issue
        for token in _option_values(tokens, "-r") + _option_values(tokens, "--requirement")
        if (issue := _missing_path_issue(command, token, "requirements file"))
    ]


def _validate_pytest(command: DocumentedCommand, tokens: list[str]) -> list[str]:
    issues: list[str] = []
    for token in tokens:
        test_path = token.split("::", maxsplit=1)[0]
        if test_path.endswith(".py"):
            issue = _missing_path_issue(command, test_path, "pytest file")
            if issue:
                issues.append(issue)
    return issues


def _validate_uvicorn(command: DocumentedCommand, tokens: list[str]) -> list[str]:
    issues: list[str] = []
    try:
        module_index = tokens.index("uvicorn") + 1
        target = tokens[module_index]
    except (ValueError, IndexError):
        return [f"{command.label}: Uvicorn command has no application target `{command.text}`"]

    app_dirs = _option_values(tokens, "--app-dir")
    app_dir_token = app_dirs[0] if app_dirs else "."
    app_dir = _resolve_path(command.source, app_dir_token)
    if app_dir is None:
        return issues
    if not app_dir.is_dir():
        return [
            f"{command.label}: missing Uvicorn app directory `{app_dir_token}` in `{command.text}`"
        ]

    module_name, separator, symbol = target.partition(":")
    if not separator or not module_name or not symbol:
        return [f"{command.label}: invalid Uvicorn target `{target}` in `{command.text}`"]
    module_path = app_dir / (module_name.replace(".", "/") + ".py")
    if not module_path.is_file():
        return [f"{command.label}: missing Uvicorn module `{module_path.relative_to(ROOT)}`"]
    module_text = module_path.read_text(encoding="utf-8")
    if not re.search(rf"(?m)^\s*{re.escape(symbol)}\s*=", module_text):
        issues.append(
            f"{command.label}: Uvicorn symbol `{symbol}` is not assigned in "
            f"`{module_path.relative_to(ROOT)}`"
        )
    return issues


def validate_command(command: DocumentedCommand) -> list[str]:
    try:
        tokens = shlex.split(command.text, posix=True)
    except ValueError as exc:
        return [f"{command.label}: command cannot be parsed ({exc}): `{command.text}`"]
    if not tokens:
        return []

    executable = tokens[0].lower()
    if executable in {"python", "python3"}:
        if len(tokens) < 2:
            return [f"{command.label}: Python command has no target `{command.text}`"]
        if tokens[1].startswith("-") and tokens[1] != "-m":
            return []
        if tokens[1] != "-m":
            issue = _missing_path_issue(command, tokens[1], "Python script")
            return [issue] if issue else []
        if len(tokens) < 3:
            return [f"{command.label}: Python module command has no module `{command.text}`"]
        module = tokens[2]
        if module == "pytest":
            return _validate_pytest(command, tokens[3:])
        if module == "pip":
            return _validate_requirements(command, tokens[3:])
        if module == "uvicorn":
            return _validate_uvicorn(command, tokens[2:])
        if module == "http.server":
            return [
                issue
                for token in _option_values(tokens, "--directory")
                if (issue := _missing_path_issue(command, token, "HTTP server directory"))
            ]
        return []

    if executable == "pytest":
        return _validate_pytest(command, tokens[1:])
    if executable in {"pip", "pip3"}:
        return _validate_requirements(command, tokens[1:])
    if executable == "streamlit":
        if len(tokens) < 3 or tokens[1] != "run":
            return [f"{command.label}: invalid Streamlit command `{command.text}`"]
        issue = _missing_path_issue(command, tokens[2], "Streamlit app")
        return [issue] if issue else []
    if executable == "docker":
        return [
            issue
            for token in _option_values(tokens, "-f")
            if (issue := _missing_path_issue(command, token, "Docker file"))
        ]
    return []


def collect_issues() -> list[str]:
    return [issue for command in documented_commands() for issue in validate_command(command)]


def main() -> None:
    commands = documented_commands()
    issues = collect_issues()
    if issues:
        print("Documented command check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    sources = {command.source for command in commands}
    print(
        f"Documented command check passed for {len(commands)} commands "
        f"across {len(sources)} public files."
    )


if __name__ == "__main__":
    main()
