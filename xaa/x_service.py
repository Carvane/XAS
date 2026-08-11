from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import XConfig
from .errors import PublishingError


class XPublisher:
    def __init__(self, config: XConfig) -> None:
        try:
            import tweepy
        except ImportError as exc:
            raise PublishingError(
                "The tweepy package is missing. Run: python -m pip install -r requirements.txt"
            ) from exc
        self.tweepy = tweepy
        try:
            auth = tweepy.OAuth1UserHandler(
                config.api_key,
                config.api_secret,
                config.access_token,
                config.access_token_secret,
            )
            self.media_api = tweepy.API(auth, wait_on_rate_limit=True)
            self.client = tweepy.Client(
                consumer_key=config.api_key,
                consumer_secret=config.api_secret,
                access_token=config.access_token,
                access_token_secret=config.access_token_secret,
                wait_on_rate_limit=True,
            )
        except Exception as exc:
            raise PublishingError(f"Could not configure the X client: {exc}") from exc

    def publish(self, text: str, image_path: Path, alt_text: str | None) -> dict[str, Any]:
        try:
            media = self.media_api.media_upload(filename=str(image_path))
            if alt_text:
                self.media_api.create_media_metadata(media.media_id, alt_text[:1000])
            response = self.client.create_tweet(
                text=text,
                media_ids=[str(media.media_id)],
                user_auth=True,
            )
        except self.tweepy.TweepyException as exc:
            raise PublishingError(
                "Publishing to X failed. Check Read and Write permission, "
                f"your API plan, and credentials: {exc}"
            ) from exc
        except Exception as exc:
            raise PublishingError(f"Publishing to X failed: {exc}") from exc

        data = response.data or {}
        tweet_id = str(data.get("id", ""))
        if not tweet_id:
            raise PublishingError("X did not return the ID of the published post.")
        return {"tweet_id": tweet_id, "media_id": str(media.media_id)}
