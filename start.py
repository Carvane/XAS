from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"


def environment_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def main() -> int:
    python = environment_python()
    if not python.is_file():
        print("Run this first: python install.py", file=sys.stderr)
        return 1

    if sys.argv[1:] == ["--test"]:
        command = [
            str(python),
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v",
        ]
    else:
        command = [str(python), str(PROJECT_DIR / "main.py"), *sys.argv[1:]]
    try:
        completed = subprocess.run(command, cwd=PROJECT_DIR, check=False)
    except OSError as exc:
        print(f"Could not start XAA: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
