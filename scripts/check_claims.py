from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TEXT_ROOTS = [ROOT / "docs", ROOT / "projects", ROOT / "portfolio-site"]
RISKY_PHRASES = [
    "production-ready",
    "production-grade",
    "enterprise-grade",
    "state-of-the-art",
    "sota",
    "used by customers",
    "customer-proven",
    "validated compliance",
    "real-time robot deployment",
    "expert-level compliance advice",
    "guaranteed",
]
PLACEHOLDER_PHRASES = [
    "fill in",
    "your-linkedin",
    "your.email",
    "your-name",
    "your-username",
]
OWNER_FACING_PHRASES = [
    "## todo",
    "replace the root readme",
    "finalize public contact links",
]
ALLOWED_CONTEXT = [
    "do not claim",
    "not ",
    "not-",
    "not to claim",
    "not a ",
    "not an ",
    "disallowed",
    "avoid",
    "without",
    "no ",
    "should not",
    "research notes",
]


def markdown_files() -> list[Path]:
    files = list(ROOT.glob("*.md"))
    for directory in PUBLIC_TEXT_ROOTS[:2]:
        files.extend(directory.rglob("*.md"))
    return sorted(
        {
            path
            for path in files
            if path.exists() and path.relative_to(ROOT).as_posix() != "docs/CLAIMS_POLICY.md"
        }
    )


def line_allowed(line: str, phrase: str) -> bool:
    lowered = line.lower()
    if "sota_research_notes.md" in lowered:
        return True
    index = lowered.find(phrase)
    prefix = lowered[:index]
    return any(marker in prefix for marker in ALLOWED_CONTEXT)


def main() -> None:
    issues: list[str] = []
    for path in markdown_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lowered = line.lower()
            for phrase in [*PLACEHOLDER_PHRASES, *OWNER_FACING_PHRASES]:
                if phrase in lowered:
                    issues.append(
                        f"{path.relative_to(ROOT)}:{lineno}: public owner-facing or placeholder text `{phrase}`"
                    )
            for phrase in RISKY_PHRASES:
                if phrase in lowered and not line_allowed(line, phrase):
                    issues.append(
                        f"{path.relative_to(ROOT)}:{lineno}: risky claim `{phrase}` needs evidence or limitation context"
                    )
    if issues:
        print("Claim check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Claim check passed for {len(markdown_files())} markdown files.")


if __name__ == "__main__":
    main()
