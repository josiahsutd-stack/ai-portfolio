from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TEXT_ROOTS = [
    ROOT / "docs",
    ROOT / "projects",
    ROOT / "experiments",
    ROOT / "integrations",
    ROOT / "portfolio-site",
]
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
SIMULATED_ENDORSEMENT_PHRASES = [
    "brutally honest score",
    "earn an interview",
    "hiring verdict",
    "i would hire",
    "i would not hire",
    "interview readiness",
    "recruiter verdict",
]
DEPRECATED_PUBLIC_PHRASES = [
    "deterministic research workflow assistant",
    "project brief and specification copilot",
    "visual qa provider contract",
]
SELF_SCORE_PATTERN = re.compile(r"\b\d+(?:\.\d+)?/10\b")
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


def public_text_files() -> list[Path]:
    files = list(ROOT.glob("*.md"))
    for directory in PUBLIC_TEXT_ROOTS:
        files.extend(directory.rglob("*.md"))
        files.extend(directory.rglob("*.html"))
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


def line_issues(path: Path, lineno: int, line: str) -> list[str]:
    issues: list[str] = []
    relative = path.relative_to(ROOT)
    lowered = line.lower()
    for phrase in [*PLACEHOLDER_PHRASES, *OWNER_FACING_PHRASES]:
        if phrase in lowered:
            issues.append(
                f"{relative}:{lineno}: public owner-facing or placeholder text `{phrase}`"
            )
    for phrase in SIMULATED_ENDORSEMENT_PHRASES:
        if phrase in lowered:
            issues.append(
                f"{relative}:{lineno}: simulated hiring endorsement `{phrase}` is not evidence"
            )
    for phrase in DEPRECATED_PUBLIC_PHRASES:
        if phrase in lowered:
            issues.append(f"{relative}:{lineno}: deprecated public project name `{phrase}`")
    if SELF_SCORE_PATTERN.search(line):
        issues.append(
            f"{relative}:{lineno}: candidate-authored numeric portfolio score is not evidence"
        )
    for phrase in RISKY_PHRASES:
        if phrase in lowered and not line_allowed(line, phrase):
            issues.append(
                f"{relative}:{lineno}: risky claim `{phrase}` needs evidence or limitation context"
            )
    return issues


def collect_issues() -> list[str]:
    issues: list[str] = []
    for path in public_text_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            issues.extend(line_issues(path, lineno, line))
    return issues


def main() -> None:
    issues = collect_issues()
    if issues:
        print("Claim check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Claim check passed for {len(public_text_files())} public text files.")


if __name__ == "__main__":
    main()
