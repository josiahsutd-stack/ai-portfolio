from __future__ import annotations

from check_repo_health import check_required_docs
from validate_project_readmes import main as validate_readmes


def main() -> None:
    missing = check_required_docs()
    if missing:
        raise SystemExit("Missing required documentation:\n" + "\n".join(missing))
    validate_readmes()
    print("Project documentation checks passed.")


if __name__ == "__main__":
    main()
