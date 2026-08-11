# Changelog

All notable changes to XAA are documented here.

## [1.0.0] — 2026-08-11

### Added

- Live trend research with OpenAI Responses API web search.
- Persistent context using an automatically created OpenAI conversation ID.
- Strict JSON-schema output for trend analysis, caption blocks, image brief, and alt text.
- English captions formatted as setup, one blank line, then punchline.
- GPT Image 2 editing with `logo.png` as a mandatory character-identity reference.
- Character-lock prompt that preserves the source face, expression, outfit, palette, proportions,
  and photomontage style while allowing scene-fitting pose and lighting changes.
- Anti-AI-slop direction favoring believable found photos, natural imperfections, simple jokes,
  and restrained visual treatment.
- Automatic JPEG compression for X media uploads.
- Tweepy-based OAuth 1.0a media upload, alt text, and post creation.
- Duplicate-topic detection, configurable publication cooldown, run locking, and JSON history.
- Check, dry-run, force, debug, version, and test commands.
- Cross-platform installer and launcher for Windows, macOS, and Linux.
- English README, setup guide, security policy, release notes, and GitHub Actions tests.
