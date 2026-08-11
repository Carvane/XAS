from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from xaa.config import load_config
from xaa.errors import ConfigError


def valid_config(root: Path) -> dict[str, object]:
    Image.new("RGB", (32, 32), "white").save(root / "logo.png", format="PNG")
    return {
        "openai": {
            "api_key": "test-openai-key",
            "text_model": "gpt-5.6",
            "image_model": "gpt-image-2",
            "conversation_id": "",
            "allowed_domains": [],
            "blocked_domains": [],
        },
        "x": {
            "api_key": "test-x-key",
            "api_secret": "test-x-secret",
            "access_token": "test-access-token",
            "access_token_secret": "test-access-secret",
        },
        "brand": {
            "coin_name": "Hamsty",
            "ticker": "$HAMSTY",
            "description": "A deadpan hooded hamster surviving crypto culture.",
        },
        "generation": {
            "logo_path": "logo.png",
            "output_dir": "output",
            "history_file": "data/history.json",
            "timezone": "Europe/Warsaw",
        },
        "publishing": {
            "enabled": True,
            "dry_run": False,
            "min_hours_between_posts": 6,
            "add_alt_text": True,
        },
    }


def write_config(root: Path, data: dict[str, object]) -> Path:
    path = root / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class ConfigTests(unittest.TestCase):
    def test_loads_valid_release_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_config(write_config(root, valid_config(root)))
            self.assertEqual(config.brand.coin_name, "Hamsty")
            self.assertEqual(config.generation.logo_path, root / "logo.png")

    def test_rejects_placeholder_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = valid_config(root)
            raw["openai"]["api_key"] = "PASTE_OPENAI_API_KEY_HERE"  # type: ignore[index]
            with self.assertRaises(ConfigError):
                load_config(write_config(root, raw))

    def test_rejects_string_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = valid_config(root)
            raw["publishing"]["enabled"] = "false"  # type: ignore[index]
            with self.assertRaises(ConfigError):
                load_config(write_config(root, raw))

    def test_rejects_invalid_character_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = valid_config(root)
            (root / "logo.png").write_text("not an image", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(write_config(root, raw))

    def test_saves_conversation_id_without_losing_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_config(root, valid_config(root))
            config = load_config(path)
            config.save_conversation_id("conv_release_test")
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["openai"]["conversation_id"], "conv_release_test")
            self.assertEqual(saved["brand"]["coin_name"], "Hamsty")


if __name__ == "__main__":
    unittest.main()
