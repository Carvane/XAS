from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from PIL import Image, UnidentifiedImageError

from .errors import ConfigError


PLACEHOLDER_MARKERS = (
    "YOUR_",
    "PUT_",
    "PASTE_",
    "CHANGE_ME",
    "SK-...",
)


@dataclass(slots=True)
class OpenAIConfig:
    api_key: str = field(repr=False)
    text_model: str = "gpt-5.6"
    image_model: str = "gpt-image-2"
    conversation_id: str = ""
    allowed_domains: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=list)


@dataclass(slots=True)
class XConfig:
    api_key: str = field(repr=False)
    api_secret: str = field(repr=False)
    access_token: str = field(repr=False)
    access_token_secret: str = field(repr=False)


@dataclass(slots=True)
class BrandConfig:
    coin_name: str
    ticker: str
    description: str
    contract_address: str = ""
    website: str = ""
    x_handle: str = ""
    tone: str = "fast, witty, internet-native, self-aware degen humor"
    call_to_action: str = ""
    forbidden_topics: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GenerationConfig:
    logo_path: Path
    output_dir: Path
    history_file: Path
    timezone: str = "Europe/Warsaw"
    post_language: str = "English"
    max_post_chars: int = 260
    trend_window_hours: int = 72
    trend_sources: list[str] = field(default_factory=list)
    image_size: str = "1536x1024"
    image_quality: str = "medium"
    max_upload_mb: float = 4.8
    duplicate_lookback: int = 30
    generation_attempts: int = 3


@dataclass(slots=True)
class PublishingConfig:
    enabled: bool = True
    dry_run: bool = False
    min_hours_between_posts: float = 6.0
    add_alt_text: bool = True


@dataclass(slots=True)
class AppConfig:
    openai: OpenAIConfig
    x: XConfig
    brand: BrandConfig
    generation: GenerationConfig
    publishing: PublishingConfig
    config_path: Path
    raw: dict[str, Any] = field(repr=False)

    def save_conversation_id(self, conversation_id: str) -> None:
        self.raw.setdefault("openai", {})["conversation_id"] = conversation_id
        temporary = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(self.raw, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.config_path)
        self.openai.conversation_id = conversation_id


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ConfigError(f'Missing "{name}" section in config.json.')
    return value


def _string(section: dict[str, Any], key: str, section_name: str, default: str | None = None) -> str:
    value = section.get(key, default)
    if not isinstance(value, str):
        raise ConfigError(f'Field "{section_name}.{key}" must be a string.')
    return value.strip()


def _list_of_strings(section: dict[str, Any], key: str) -> list[str]:
    value = section.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f'Field "{key}" must be a list of strings.')
    return [item.strip() for item in value if item.strip()]


def _integer(section: dict[str, Any], key: str, default: int) -> int:
    value = section.get(key, default)
    if isinstance(value, bool):
        raise ConfigError(f'Field "{key}" must be an integer.')
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f'Field "{key}" must be an integer.') from exc


def _number(section: dict[str, Any], key: str, default: float) -> float:
    value = section.get(key, default)
    if isinstance(value, bool):
        raise ConfigError(f'Field "{key}" must be a number.')
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f'Field "{key}" must be a number.') from exc


def _boolean(section: dict[str, Any], key: str, default: bool) -> bool:
    value = section.get(key, default)
    if not isinstance(value, bool):
        raise ConfigError(f'Field "{key}" must be true or false.')
    return value


def _require_secret(value: str, field_name: str) -> None:
    upper = value.upper()
    if not value or any(marker in upper for marker in PLACEHOLDER_MARKERS):
        raise ConfigError(f'Enter a real value for "{field_name}" in config.json.')


def _relative_path(config_dir: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (config_dir / path).resolve()


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.is_file():
        raise ConfigError(
            f"Could not find {config_path}. Copy config.example.json to config.json "
            "and enter your settings."
        )

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path.name}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("The root element of config.json must be a JSON object.")

    openai_raw = _section(raw, "openai")
    x_raw = _section(raw, "x")
    brand_raw = _section(raw, "brand")
    generation_raw = _section(raw, "generation")
    publishing_raw = _section(raw, "publishing")
    config_dir = config_path.parent

    openai_config = OpenAIConfig(
        api_key=_string(openai_raw, "api_key", "openai"),
        text_model=_string(openai_raw, "text_model", "openai", "gpt-5.6"),
        image_model=_string(openai_raw, "image_model", "openai", "gpt-image-2"),
        conversation_id=_string(openai_raw, "conversation_id", "openai", ""),
        allowed_domains=_list_of_strings(openai_raw, "allowed_domains"),
        blocked_domains=_list_of_strings(openai_raw, "blocked_domains"),
    )
    x_config = XConfig(
        api_key=_string(x_raw, "api_key", "x"),
        api_secret=_string(x_raw, "api_secret", "x"),
        access_token=_string(x_raw, "access_token", "x"),
        access_token_secret=_string(x_raw, "access_token_secret", "x"),
    )
    brand_config = BrandConfig(
        coin_name=_string(brand_raw, "coin_name", "brand"),
        ticker=_string(brand_raw, "ticker", "brand"),
        description=_string(brand_raw, "description", "brand"),
        contract_address=_string(brand_raw, "contract_address", "brand", ""),
        website=_string(brand_raw, "website", "brand", ""),
        x_handle=_string(brand_raw, "x_handle", "brand", ""),
        tone=_string(
            brand_raw,
            "tone",
            "brand",
            "fast, witty, internet-native, self-aware degen humor",
        ),
        call_to_action=_string(brand_raw, "call_to_action", "brand", ""),
        forbidden_topics=_list_of_strings(brand_raw, "forbidden_topics"),
    )
    generation_config = GenerationConfig(
        logo_path=_relative_path(
            config_dir, _string(generation_raw, "logo_path", "generation", "logo.png")
        ),
        output_dir=_relative_path(
            config_dir, _string(generation_raw, "output_dir", "generation", "output")
        ),
        history_file=_relative_path(
            config_dir,
            _string(generation_raw, "history_file", "generation", "data/history.json"),
        ),
        timezone=_string(generation_raw, "timezone", "generation", "Europe/Warsaw"),
        post_language=_string(generation_raw, "post_language", "generation", "English"),
        max_post_chars=_integer(generation_raw, "max_post_chars", 260),
        trend_window_hours=_integer(generation_raw, "trend_window_hours", 72),
        trend_sources=_list_of_strings(generation_raw, "trend_sources"),
        image_size=_string(generation_raw, "image_size", "generation", "1536x1024"),
        image_quality=_string(generation_raw, "image_quality", "generation", "medium"),
        max_upload_mb=_number(generation_raw, "max_upload_mb", 4.8),
        duplicate_lookback=_integer(generation_raw, "duplicate_lookback", 30),
        generation_attempts=_integer(generation_raw, "generation_attempts", 3),
    )
    publishing_config = PublishingConfig(
        enabled=_boolean(publishing_raw, "enabled", True),
        dry_run=_boolean(publishing_raw, "dry_run", False),
        min_hours_between_posts=_number(
            publishing_raw, "min_hours_between_posts", 6.0
        ),
        add_alt_text=_boolean(publishing_raw, "add_alt_text", True),
    )

    for value, name in (
        (openai_config.api_key, "openai.api_key"),
        (x_config.api_key, "x.api_key"),
        (x_config.api_secret, "x.api_secret"),
        (x_config.access_token, "x.access_token"),
        (x_config.access_token_secret, "x.access_token_secret"),
    ):
        _require_secret(value, name)
    for value, name in (
        (brand_config.coin_name, "brand.coin_name"),
        (brand_config.ticker, "brand.ticker"),
        (brand_config.description, "brand.description"),
    ):
        if not value or any(marker in value.upper() for marker in PLACEHOLDER_MARKERS):
            raise ConfigError(f'Complete the "{name}" field in config.json.')

    if not 1 <= generation_config.max_post_chars <= 280:
        raise ConfigError("generation.max_post_chars must be between 1 and 280.")
    if generation_config.trend_window_hours < 1:
        raise ConfigError("generation.trend_window_hours must be greater than zero.")
    if generation_config.generation_attempts not in range(1, 6):
        raise ConfigError("generation.generation_attempts must be between 1 and 5.")
    if generation_config.duplicate_lookback < 1:
        raise ConfigError("generation.duplicate_lookback must be greater than zero.")
    if generation_config.max_upload_mb <= 0:
        raise ConfigError("generation.max_upload_mb must be greater than zero.")
    if publishing_config.min_hours_between_posts < 0:
        raise ConfigError("publishing.min_hours_between_posts cannot be negative.")
    try:
        ZoneInfo(generation_config.timezone)
    except ZoneInfoNotFoundError as exc:
        raise ConfigError(f"Unknown time zone: {generation_config.timezone}") from exc
    if not generation_config.logo_path.is_file():
        raise ConfigError(
            f"Character image not found: {generation_config.logo_path}. "
            "Add logo.png before running XAA."
        )
    try:
        with Image.open(generation_config.logo_path) as logo:
            logo.verify()
    except (OSError, UnidentifiedImageError) as exc:
        raise ConfigError(
            f"Character image is not a readable image: {generation_config.logo_path}"
        ) from exc

    return AppConfig(
        openai=openai_config,
        x=x_config,
        brand=brand_config,
        generation=generation_config,
        publishing=publishing_config,
        config_path=config_path,
        raw=raw,
    )
