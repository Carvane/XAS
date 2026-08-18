from __future__ import annotations

import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


# Wait time before every run, including the first one.
BASE_INTERVAL_HOURS = 6
RANDOM_MINUTES_MIN = 30
RANDOM_MINUTES_MAX = 180

# True makes the scheduler pass --force to start.py so config.json's publication
# cooldown does not block the interval configured above.
BYPASS_XAA_COOLDOWN = True

PROJECT_DIR = Path(__file__).resolve().parent
START_SCRIPT = PROJECT_DIR / "start.py"


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"[{timestamp}] {message}", flush=True)


def next_delay() -> tuple[int, int]:
    if BASE_INTERVAL_HOURS < 0:
        raise ValueError("BASE_INTERVAL_HOURS cannot be negative.")
    if RANDOM_MINUTES_MIN < 0 or RANDOM_MINUTES_MAX < RANDOM_MINUTES_MIN:
        raise ValueError("Invalid random minute range.")

    random_minutes = random.SystemRandom().randint(
        RANDOM_MINUTES_MIN,
        RANDOM_MINUTES_MAX,
    )
    total_seconds = BASE_INTERVAL_HOURS * 60 * 60 + random_minutes * 60
    return total_seconds, random_minutes


def run_xaa() -> int:
    log("Starting start.py...")
    command = [sys.executable, str(START_SCRIPT)]
    if BYPASS_XAA_COOLDOWN:
        command.append("--force")

    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_DIR,
            check=False,
        )
    except OSError as exc:
        log(f"Could not start XAA: {exc}")
        return 1

    log(f"start.py finished with exit code {completed.returncode}.")
    return completed.returncode


def main() -> int:
    if not START_SCRIPT.is_file():
        log(f"Missing file: {START_SCRIPT}")
        return 1

    log("XAA scheduler started. Press Ctrl+C to stop it.")

    try:
        while True:
            delay_seconds, random_minutes = next_delay()
            run_at = datetime.now().astimezone() + timedelta(seconds=delay_seconds)
            log(
                "Next run in "
                f"{BASE_INTERVAL_HOURS}h + {random_minutes}m "
                f"({run_at.strftime('%Y-%m-%d %H:%M:%S %Z')})."
            )
            time.sleep(delay_seconds)
            run_xaa()
    except KeyboardInterrupt:
        log("Scheduler stopped.")
        return 0
    except ValueError as exc:
        log(f"CONFIGURATION ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
