from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any


@dataclass(slots=True)
class ContentPlan:
    trend_title: str
    trend_summary: str
    why_it_is_viral: str
    post_text: str
    image_prompt: str
    alt_text: str
    source_urls: list[dict[str, str]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "trend_title": self.trend_title,
            "trend_summary": self.trend_summary,
            "why_it_is_viral": self.why_it_is_viral,
            "post_text": self.post_text,
            "image_prompt": self.image_prompt,
            "alt_text": self.alt_text,
            "source_urls": self.source_urls,
        }


def normalize_text(text: str) -> str:
    text = re.sub(r"https?://\S+", " ", text.lower())
    text = re.sub(r"[^a-z0-9$]+", " ", text)
    return " ".join(text.split())


def clamp_post(text: str, max_chars: int) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean
    if max_chars <= 1:
        return clean[:max_chars]
    shortened = clean[: max_chars - 1].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]
    return shortened.rstrip(".,;:!?") + "…"


def _clean_post_block(text: str) -> str:
    lines = []
    for raw_line in str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = " ".join(raw_line.split())
        if line:
            lines.append(line)
    return "\n".join(lines[:2])


def _truncate_post_block(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 1:
        return text[:max_chars]
    shortened = text[: max_chars - 1].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]
    return shortened.rstrip(".,;:!?\n") + "…"


def format_two_block_post(setup: str, punchline: str, max_chars: int) -> str:
    """Build an X post with exactly one empty line between two compact text blocks."""
    first = _clean_post_block(setup)
    second = _clean_post_block(punchline)
    if not first or not second:
        return clamp_post(f"{first} {second}", max_chars)

    separator = "\n\n"
    combined = first + separator + second
    if len(combined) <= max_chars:
        return combined

    content_budget = max_chars - len(separator)
    if content_budget < 2:
        return clamp_post(combined, max_chars)

    first_budget = min(len(first), content_budget // 2)
    second_budget = content_budget - first_budget
    if len(second) < second_budget:
        first_budget += second_budget - len(second)
        second_budget = len(second)
    elif len(first) < first_budget:
        second_budget += first_budget - len(first)
        first_budget = len(first)

    first = _truncate_post_block(first, first_budget)
    second = _truncate_post_block(second, second_budget)
    return first + separator + second


def is_duplicate(plan: ContentPlan, recent_entries: list[dict[str, Any]]) -> bool:
    current_post = normalize_text(plan.post_text)
    current_trend = normalize_text(plan.trend_title)
    for entry in recent_entries:
        old_post = normalize_text(str(entry.get("post_text", "")))
        old_trend = normalize_text(str(entry.get("trend_title", "")))
        if current_trend and old_trend and current_trend == old_trend:
            return True
        if current_post and old_post:
            similarity = SequenceMatcher(None, current_post, old_post).ratio()
            if similarity >= 0.82:
                return True
    return False
