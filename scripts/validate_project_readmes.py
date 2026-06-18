from __future__ import annotations

from check_repo_health import check_project_readmes


def main() -> None:
    issues = check_project_readmes()
    if issues:
        raise SystemExit("\n".join(issues))
    print("Project README validation passed.")


if __name__ == "__main__":
    main()
