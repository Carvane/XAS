from __future__ import annotations

import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from xaa.core import ContentPlan, clamp_post, format_two_block_post, is_duplicate
from xaa.image_tools import prepare_final_image
from xaa.openai_service import ANTI_AI_SLOP_INSTRUCTIONS, CHARACTER_LOCK_INSTRUCTIONS


def plan(title: str, post: str) -> ContentPlan:
    return ContentPlan(
        trend_title=title,
        trend_summary="summary",
        why_it_is_viral="reason",
        post_text=post,
        image_prompt="prompt",
        alt_text="alt",
        source_urls=[],
    )


class CoreTests(unittest.TestCase):
    def test_character_lock_protects_reference_appearance(self) -> None:
        rules = CHARACTER_LOCK_INSTRUCTIONS.lower()
        self.assertIn("exact face", rules)
        self.assertIn("white background", rules)
        self.assertIn("do not beautify, redraw", rules)
        self.assertIn("only scene-fitting transformations", rules)

    def test_anti_ai_slop_rules_prefer_believable_photomontage(self) -> None:
        rules = ANTI_AI_SLOP_INSTRUCTIONS.lower()
        self.assertIn("real internet meme", rules)
        self.assertIn("ordinary found photograph", rules)
        self.assertIn("avoid cinematic lighting", rules)
        self.assertIn("slightly raw and believable", rules)

    def test_clamp_post_keeps_short_text(self) -> None:
        self.assertEqual(clamp_post("hello   world", 20), "hello world")

    def test_clamp_post_never_exceeds_limit(self) -> None:
        result = clamp_post("one two three four five six", 16)
        self.assertLessEqual(len(result), 16)
        self.assertTrue(result.endswith("…"))

    def test_two_block_post_has_exact_middle_blank_line(self) -> None:
        result = format_two_block_post(
            "  short   setup  ",
            " dry   punchline ",
            260,
        )
        self.assertEqual(result, "short setup\n\ndry punchline")

    def test_two_block_post_preserves_up_to_two_lines_per_block(self) -> None:
        result = format_two_block_post(
            "setup line one\nsetup line two\nignored line",
            "payoff line one\npayoff line two",
            260,
        )
        self.assertEqual(
            result,
            "setup line one\nsetup line two\n\npayoff line one\npayoff line two",
        )

    def test_two_block_post_keeps_layout_under_limit(self) -> None:
        result = format_two_block_post(
            "a very long setup about an ordinary internet event",
            "an equally long payoff about the consequences",
            60,
        )
        self.assertLessEqual(len(result), 60)
        self.assertEqual(result.count("\n\n"), 1)

    def test_duplicate_title_is_detected(self) -> None:
        candidate = plan("Golden glow trend", "A completely fresh caption")
        history = [{"trend_title": "Golden Glow Trend!", "post_text": "old"}]
        self.assertTrue(is_duplicate(candidate, history))

    def test_different_plan_is_not_duplicate(self) -> None:
        candidate = plan("New dance format", "The trenches finally learned choreography")
        history = [{"trend_title": "Phone fold meme", "post_text": "wallet folded first"}]
        self.assertFalse(is_duplicate(candidate, history))

    def test_final_image_compression_creates_small_jpeg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = Image.new("RGB", (1024, 768), "navy")
            base_bytes = BytesIO()
            base.save(base_bytes, format="PNG")
            output = root / "meme.jpg"
            prepare_final_image(
                base_bytes.getvalue(),
                output,
                max_upload_mb=4.8,
            )
            self.assertTrue(output.is_file())
            self.assertLess(output.stat().st_size, 4.8 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
