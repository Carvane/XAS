from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any

from .config import AppConfig
from .core import ContentPlan, clamp_post, format_two_block_post
from .errors import GenerationError


CONTENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "trend_title": {"type": "string"},
        "trend_summary": {"type": "string"},
        "why_it_is_viral": {"type": "string"},
        "post_setup": {
            "type": "string",
            "description": "First short text block: the setup, one or at most two compact lines.",
        },
        "post_punchline": {
            "type": "string",
            "description": "Second short text block: the payoff, one or at most two compact lines.",
        },
        "image_prompt": {"type": "string"},
        "alt_text": {"type": "string"},
    },
    "required": [
        "trend_title",
        "trend_summary",
        "why_it_is_viral",
        "post_setup",
        "post_punchline",
        "image_prompt",
        "alt_text",
    ],
    "additionalProperties": False,
}


# The primary instruction that preserves the character's visual identity.
# Update it only if the source character itself changes in the future.
CHARACTER_LOCK_INSTRUCTIONS = """
CHARACTER IDENTITY LOCK — highest visual priority:
- Use the exact character from the supplied reference image, not a similar or redesigned version.
- The white background belongs only to the reference sheet. Remove it and replace it with the
  meme environment; never include a white rectangle around the character.
- Preserve the character's exact face and head: the same eye placement and shape, nose, muzzle,
  mouth, characteristic smile, fur markings, colors, texture, proportions and recognizable
  three-quarter viewing angle. Keep the same facial expression. Do not beautify, redraw,
  reinterpret or substitute the face.
- Preserve the exact dark hooded outfit: the same hood shape, fabric pattern, zipper, blue trim,
  purple/pink accent edging, colors, proportions and chunky silhouette. Preserve the original
  mixed photo-collage/meme aesthetic; do not convert the character into a cartoon, anime,
  glossy 3D render, generic mascot or fully realistic animal.
- Do not change the character's identity, species-like appearance, age, body type, clothing,
  palette, materials or art style. Do not add or remove permanent character features.
- Only scene-fitting transformations are allowed: isolate the character from the white
  background; scale, crop and position it; adapt the body/limb pose so it can sit, stand, hold
  props or interact with the scene; and match perspective, lighting, shadows, color grade,
  focus and camera grain. Keep the head and face as visually unchanged as possible.
- Make the result look like a deliberate, high-quality photomontage in which this unchanged
  character physically participates in the meme. It must remain immediately recognizable as
  the very same source character at first glance.
- If the requested action conflicts with identity preservation, preserve the character and
  simplify the action or composition instead.
""".strip()


# Art direction for simple, intentionally edited photomontage memes.
ANTI_AI_SLOP_INSTRUCTIONS = """
ANTI-AI-SLOP ART DIRECTION — mandatory:
- Make the image feel like a real internet meme assembled from an ordinary found photograph and
  a carefully composited character, not like a fully synthetic AI illustration.
- Prefer a mundane, specific, believable location with real materials and a few purposeful props.
  Use candid consumer-camera or phone-photo aesthetics when suitable: imperfect framing, natural
  clutter, practical room light or direct flash, mild sensor noise, compression, restrained color
  and believable wear on objects.
- Keep one instantly readable visual joke. Favor awkward specificity and human-made simplicity
  over spectacle, epic storytelling or an overloaded scene.
- Avoid cinematic lighting, dramatic rim light, volumetric rays, excessive depth of field, bloom,
  teal-and-orange grading, purple neon, glowing coins, floating holograms, generic candlestick
  charts, luxury cars, astronauts, cyberpunk skylines and motivational-ad aesthetics.
- Avoid glossy plastic surfaces, over-smoothed skin or fur, perfect symmetry, excessive sharpness,
  hyper-detailed clutter, repeated objects, malformed hands/paws, impossible geometry, fake app
  interfaces, garbled lettering, tiny decorative text and meaningless crypto symbols.
- Do not add captions, labels, logos or UI unless the creative brief absolutely requires one short,
  readable element for the joke. The scene and character action should communicate the meme.
- Preserve small photographic imperfections. The final result should look intentionally edited by
  a skilled meme creator, slightly raw and believable—not polished into commercial concept art.
""".strip()


# X caption format: two text blocks separated by exactly one blank line.
POST_STYLE_INSTRUCTIONS = """
X POST STYLE AND LAYOUT — mandatory:
- Return the caption as exactly two compact text blocks: `post_setup` and `post_punchline`.
- Each block should normally be one short line; a maximum of two short lines is allowed only when
  the joke genuinely benefits from it. Do not put an empty line inside either JSON field.
- The application inserts exactly one blank line between the two blocks. Write both blocks so the
  final post reads as a clean setup, blank line, then a dry payoff.
- Keep the visual shape sparse and left-aligned: no heading, list, bullets, labels, Markdown,
  decorative separators or paragraph before/after the two blocks.
- Use concise, natural English internet voice, usually sentence-case with a lowercase opening when
  natural. Preserve required capitalization for names and acronyms. Use minimal punctuation.
- Do not add hashtags, URLs, ticker promotion, a call to action, sign-off or emoji clutter. At most
  one emoji is allowed only when it is essential to the punchline.
- Treat any supplied style samples only as a reference for spacing, line length and two-block
  silhouette. Never copy their wording, subject matter, setup, punchline or factual claims.
""".strip()


class OpenAIService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise GenerationError(
                "The openai package is missing. Run: python -m pip install -r requirements.txt"
            ) from exc
        self.client = OpenAI(api_key=config.openai.api_key, timeout=180.0, max_retries=2)

    def ensure_conversation(self) -> tuple[str, bool]:
        if self.config.openai.conversation_id:
            return self.config.openai.conversation_id, False
        try:
            conversation = self.client.conversations.create()
        except Exception as exc:
            raise GenerationError(f"Could not create an OpenAI conversation_id: {exc}") from exc
        conversation_id = str(conversation.id)
        self.config.save_conversation_id(conversation_id)
        return conversation_id, True

    def generate_content(
        self,
        now: datetime,
        recent_entries: list[dict[str, Any]],
        rejected_trends: list[str],
    ) -> ContentPlan:
        cfg = self.config
        web_tool: dict[str, Any] = {
            "type": "web_search",
            "external_web_access": True,
        }
        if cfg.openai.allowed_domains:
            web_tool["filters"] = {"allowed_domains": cfg.openai.allowed_domains[:100]}
        elif cfg.openai.blocked_domains:
            web_tool["filters"] = {"blocked_domains": cfg.openai.blocked_domains[:100]}

        history_summary = [
            {
                "trend_title": entry.get("trend_title", ""),
                "post_text": entry.get("post_text", ""),
            }
            for entry in recent_entries[-cfg.generation.duplicate_lookback :]
        ]
        brand = cfg.brand
        generation = cfg.generation
        sources = generation.trend_sources or [
            "TikTok and TikTok trend reporting",
            "X",
            "Reddit",
            "YouTube",
            "Google Trends",
            "current meme and culture reporting",
        ]
        prompt = f"""
Current local date and time: {now.isoformat()}

Search the live web before answering. Find ONE genuinely current, broadly recognizable,
fast-growing internet trend from approximately the last {generation.trend_window_hours} hours.
Prioritize: {', '.join(sources)}. It may come from crypto culture, TikTok, memes, gaming,
creator culture, consumer tech, or adjacent internet culture. Do not force a technical crypto
story if a more naturally memeable adjacent trend is stronger.

Brand:
- Coin name: {brand.coin_name}
- Ticker: {brand.ticker}
- Description: {brand.description}
- X account: {brand.x_handle or 'not provided'}
- Website: {brand.website or 'not provided'}
- Contract address: {brand.contract_address or 'not provided'}
- Desired voice: {brand.tone}
- Optional CTA: {brand.call_to_action or 'none'}
- Forbidden topics: {', '.join(brand.forbidden_topics) or 'none beyond the rules below'}

Previously published material to avoid repeating:
{json.dumps(history_summary, ensure_ascii=False)}
Rejected as too similar during this run: {json.dumps(rejected_trends, ensure_ascii=False)}

Return:
1. A short factual summary of the trend and why it is viral.
2. One English X post in the requested voice, maximum {generation.max_post_chars} characters,
   split into separate `post_setup` and `post_punchline` fields.
3. A detailed prompt for an original landscape meme image in which the brand character is the
   clearly visible protagonist. State exactly what the character is doing, what body pose and
   props are required, and what it is reacting to. Do not invent a new face, facial expression,
   outfit, body type, color palette or visual style for the character; its appearance is locked
   by the supplied reference image.
4. Concise English alt text describing the final concept.

{POST_STYLE_INSTRUCTIONS}

Quality and safety rules:
- The post must work as a joke even for someone who is not a developer.
- Sound like a sharp human social account, not corporate copy and not generic AI prose.
- No financial-return promises, fake scarcity, fabricated partnership/endorsement, fake quote,
  invented statistic, impersonation, or misleading claim about the trend.
- Do not exploit death, disaster, war, illness, private individuals, or breaking tragedy.
- Do not closely copy a copyrighted character, artwork, photograph, or existing meme template.
  Create a transformed, original visual idea inspired by the cultural pattern.
- Design the concept as a simple, believable meme photomontage: a mundane real-world setting,
  natural imperfections, a few purposeful props and one instantly readable joke. Avoid cinematic
  concept art, generic crypto spectacle and other AI-slop aesthetics.
- The image prompt must use the supplied character reference as an active participant, not as a
  logo, watermark, sticker, corner mascot or passive decoration.
- Treat the character appearance as immutable. The meme concept may change the environment,
  action, body/limb pose and props, but must never redesign or restyle the character.
- Do not ask the image model to render the ticker, contract address or website as text.
- Do not include source URLs in the X post.
""".strip()

        try:
            response = self.client.responses.create(
                model=cfg.openai.text_model,
                conversation=cfg.openai.conversation_id,
                tools=[web_tool],
                tool_choice="required",
                include=["web_search_call.action.sources"],
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a real-time cultural researcher and senior meme creative "
                            "for an internet-native memecoin account. Verify recency with web search "
                            "and favor an original, funny connection over a forced advertisement."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "viral_memecoin_content",
                        "strict": True,
                        "schema": CONTENT_SCHEMA,
                    }
                },
            )
        except Exception as exc:
            raise GenerationError(f"OpenAI could not generate the content plan: {exc}") from exc

        try:
            payload = json.loads(response.output_text)
            source_urls = _extract_sources(response)
            plan = ContentPlan(
                trend_title=str(payload["trend_title"]).strip(),
                trend_summary=str(payload["trend_summary"]).strip(),
                why_it_is_viral=str(payload["why_it_is_viral"]).strip(),
                post_text=format_two_block_post(
                    str(payload["post_setup"]),
                    str(payload["post_punchline"]),
                    generation.max_post_chars,
                ),
                image_prompt=str(payload["image_prompt"]).strip(),
                alt_text=clamp_post(str(payload["alt_text"]), 900),
                source_urls=source_urls,
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GenerationError(f"OpenAI returned an invalid data format: {exc}") from exc
        if not all((plan.trend_title, plan.post_text, plan.image_prompt, plan.alt_text)):
            raise GenerationError("OpenAI returned an empty required field.")
        return plan

    def generate_meme(self, plan: ContentPlan) -> bytes:
        cfg = self.config
        prompt = f"""
Create a polished, original, landscape internet meme based on this creative brief:
{plan.image_prompt}

Trend context: {plan.trend_summary}
Brand context: {cfg.brand.coin_name} ({cfg.brand.ticker}) — {cfg.brand.description}

The supplied image is the mandatory character reference for {cfg.brand.coin_name}. Apply every
rule below even if the creative brief suggests otherwise:

{CHARACTER_LOCK_INSTRUCTIONS}

{ANTI_AI_SLOP_INSTRUCTIONS}

The character must appear clearly as an active participant in the scene—not as a logo, watermark,
sticker, flat pasted rectangle, corner mascot or passive decoration. Make it physically present
through coherent scale, perspective, lighting, shadows and interaction with nearby objects, while
leaving its defining appearance unchanged.

The result must feel like an intentionally art-directed viral post: one instantly readable joke,
strong composition, believable textures, restrained color grading, and no stock-template look.
Do not use generic glowing coins, candlestick charts, astronauts, excessive neon, glossy plastic
3D, fake app interfaces, watermarks, long captions, or illegible typography. Do not reproduce a
copyrighted meme image or unrelated character. Prefer a transformed, original scene. Render no
ticker text, contract address, website or extra brand logo.
""".strip()
        try:
            with cfg.generation.logo_path.open("rb") as logo_file:
                result = self.client.images.edit(
                    model=cfg.openai.image_model,
                    image=logo_file,
                    prompt=prompt,
                    size=cfg.generation.image_size,
                    quality=cfg.generation.image_quality,
                )
            encoded = result.data[0].b64_json
            if not encoded:
                raise ValueError("missing image data")
            return base64.b64decode(encoded)
        except Exception as exc:
            raise GenerationError(f"OpenAI could not generate the meme: {exc}") from exc


def _extract_sources(response: Any) -> list[dict[str, str]]:
    try:
        raw = response.model_dump(mode="json")
    except Exception:
        return []
    found: dict[str, str] = {}

    def walk(value: Any, inside_web_call: bool = False) -> None:
        if isinstance(value, dict):
            is_web = inside_web_call or value.get("type") == "web_search_call"
            if is_web and isinstance(value.get("url"), str):
                found[value["url"]] = str(value.get("title") or value["url"])
            for child in value.values():
                walk(child, is_web)
        elif isinstance(value, list):
            for child in value:
                walk(child, inside_web_call)

    walk(raw)
    return [{"url": url, "title": title} for url, title in found.items()]
