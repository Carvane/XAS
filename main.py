from __future__ import annotations

import argparse
import sys
import traceback

from xaa import __version__
from xaa.app import run_agent
from xaa.config import load_config
from xaa.errors import XAAError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Research a current trend, create a meme post, and publish it to X."
    )
    parser.add_argument("--config", default="config.json", help="Path to the JSON config file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the caption and image without publishing them to X.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the config and character image without making API calls.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass the minimum interval between posts. Use with care.",
    )
    parser.add_argument("--debug", action="store_true", help="Show the full error traceback.")
    parser.add_argument("--version", action="version", version=f"XAA {__version__}")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        if args.check:
            print(
                "Configuration and character image look valid. "
                "No API calls were made."
            )
            return 0
        run_agent(config, dry_run=args.dry_run, force=args.force)
        return 0
    except XAAError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        return 1
    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"UNEXPECTED ERROR: {exc}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
