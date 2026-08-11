from __future__ import annotations

import shutil
import subprocess
import sys
import venv
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"


def environment_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(command: list[str]) -> None:
    print("\n>", " ".join(command))
    subprocess.run(command, cwd=PROJECT_DIR, check=True)


def main() -> int:
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11 or newer is required.", file=sys.stderr)
        return 1

    try:
        if not environment_python().is_file():
            print(f"Creating a Python environment in {VENV_DIR}...")
            venv.EnvBuilder(with_pip=True).create(VENV_DIR)

        python = str(environment_python())
        run([python, "-m", "pip", "install", "--upgrade", "pip"])
        run([python, "-m", "pip", "install", "-r", "requirements.txt"])

        config_path = PROJECT_DIR / "config.json"
        if not config_path.exists():
            shutil.copy2(PROJECT_DIR / "config.example.json", config_path)
            print("\nCreated config.json.")

        print("\nInstallation complete.")
        print("1. Complete config.json.")
        print("2. Add logo.png containing your character reference.")
        print("3. Validate: python start.py --check")
        print("4. Generate without publishing: python start.py --dry-run")
        print("5. Publish: python start.py")
        return 0
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"\nINSTALLATION ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
