from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\((?P<target>[^)]+)\)")


def public_markdown_files() -> list[Path]:
    files = list(ROOT.glob("*.md"))
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / "projects").rglob("*.md"))
    return sorted(set(files))


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().strip("<>")
    parsed = urlparse(target)
    if parsed.scheme or target.startswith("#"):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    return (source.parent / path).resolve()


def main() -> None:
    issues: list[str] = []
    files = public_markdown_files()
    for source in files:
        text = source.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = match.group("target")
            resolved = local_target(source, target)
            if resolved is None:
                continue
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                issues.append(
                    f"{source.relative_to(ROOT)}: local link escapes repository: {target}"
                )
                continue
            if not resolved.exists():
                line = text.count("\n", 0, match.start()) + 1
                issues.append(f"{source.relative_to(ROOT)}:{line}: missing local target: {target}")
    if issues:
        print("Markdown link check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Markdown link check passed for {len(files)} public files.")


if __name__ == "__main__":
    main()
