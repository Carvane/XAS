from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import AppConfig
from .core import ContentPlan, is_duplicate
from .errors import GenerationError, XAAError
from .history import HistoryStore, RunLock
from .image_tools import prepare_final_image
from .openai_service import OpenAIService
from .x_service import XPublisher


def run_agent(config: AppConfig, *, dry_run: bool, force: bool) -> dict[str, object]:
    try:
        timezone = ZoneInfo(config.generation.timezone)
    except ZoneInfoNotFoundError as exc:
        raise XAAError(f"Unknown time zone: {config.generation.timezone}") from exc
    now = datetime.now(timezone)
    history = HistoryStore(config.generation.history_file)
    lock_path = config.generation.history_file.parent / ".xaa.lock"

    with RunLock(lock_path):
        actual_dry_run = dry_run or config.publishing.dry_run or not config.publishing.enabled
        if not actual_dry_run and not force:
            elapsed = history.hours_since_last_publish(now)
            minimum = config.publishing.min_hours_between_posts
            if elapsed is not None and elapsed < minimum:
                wait = minimum - elapsed
                raise XAAError(
                    f"Duplicate-post protection: the last post was published {elapsed:.1f} h ago. "
                    f"Try again in {wait:.1f} h or intentionally use --force."
                )

        service = OpenAIService(config)
        conversation_id, created = service.ensure_conversation()
        if created:
            print(f"Created and saved conversation_id: {conversation_id}")

        recent = history.recent_published(config.generation.duplicate_lookback)
        rejected: list[str] = []
        plan: ContentPlan | None = None
        for attempt in range(1, config.generation.generation_attempts + 1):
            print(
                f"[{attempt}/{config.generation.generation_attempts}] "
                "Researching a fresh trend and writing the post..."
            )
            candidate = service.generate_content(now, recent, rejected)
            if not is_duplicate(candidate, recent):
                plan = candidate
                break
            rejected.append(candidate.trend_title)
            print("The trend is too similar to recent history; trying another one.")
        if plan is None:
            raise GenerationError("Could not find a sufficiently fresh topic.")

        run_dir = config.generation.output_dir / now.strftime("%Y%m%d_%H%M%S_%f")
        run_dir.mkdir(parents=True, exist_ok=False)
        print(f"Selected trend: {plan.trend_title}")
        print("Generating a meme in which the logo.png character participates in the scene...")
        raw_image = service.generate_meme(plan)
        raw_path = run_dir / "meme_generated.png"
        raw_path.write_bytes(raw_image)
        final_path = run_dir / "meme_final.jpg"
        prepare_final_image(
            raw_image,
            final_path,
            max_upload_mb=config.generation.max_upload_mb,
        )

        record: dict[str, object] = {
            "created_at": now.isoformat(),
            "status": "generated" if actual_dry_run else "publishing",
            **plan.as_dict(),
            "image_path": str(final_path),
            "conversation_id": conversation_id,
        }
        _write_json(run_dir / "content.json", record)

        print("\nPOST:\n" + plan.post_text + "\n")
        if actual_dry_run:
            history.append(record)
            print(f"DRY RUN: nothing was published. Files: {run_dir}")
            return {"status": "generated", "run_dir": str(run_dir), "post_text": plan.post_text}

        print("Uploading the image and publishing the post to X...")
        publisher = XPublisher(config.x)
        try:
            published = publisher.publish(
                plan.post_text,
                final_path,
                plan.alt_text if config.publishing.add_alt_text else None,
            )
        except Exception as exc:
            record["status"] = "publish_failed"
            record["error"] = str(exc)
            history.append(record)
            _write_json(run_dir / "content.json", record)
            raise

        record.update(published)
        record["status"] = "published"
        tweet_id = str(published["tweet_id"])
        handle = config.brand.x_handle.lstrip("@")
        record["post_url"] = (
            f"https://x.com/{handle}/status/{tweet_id}"
            if handle
            else f"https://x.com/i/web/status/{tweet_id}"
        )
        history.append(record)
        _write_json(run_dir / "content.json", record)
        print(f"Published: {record['post_url']}")
        return {"status": "published", "run_dir": str(run_dir), **published}


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
