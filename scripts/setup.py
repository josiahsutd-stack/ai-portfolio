from __future__ import annotations

import argparse
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"


def venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a local venv and install repo dependencies."
    )
    parser.add_argument(
        "--no-venv",
        action="store_true",
        help="Install into the current Python environment instead of .venv.",
    )
    args = parser.parse_args()

    python = Path(sys.executable)
    if not args.no_venv:
        if not VENV_DIR.exists():
            venv.EnvBuilder(with_pip=True).create(VENV_DIR)
        python = venv_python()

    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "-r",
            "requirements-dev.txt",
        ]
    )
    run([str(python), "scripts/generate_sample_data.py"])


if __name__ == "__main__":
    main()
