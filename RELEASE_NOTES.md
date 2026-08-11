# XAA v1.0.0

XAA (X Auto Agent) is the first public release of a Python workflow that researches current
internet trends, writes a sparse two-block English meme caption, creates an original character-led
meme, and optionally publishes the result to X.

## Highlights

- Live, source-aware web research through OpenAI Responses API.
- Original meme creation with GPT Image 2 and a user-supplied `logo.png` character reference.
- Strong visual identity preservation: the character participates in each scene without becoming
  a watermark, sticker, redesigned mascot, or unrelated AI character.
- Anti-AI-slop prompt direction for raw, believable, intentionally edited internet memes.
- Exact setup/blank-line/punchline caption layout.
- Tweepy publishing with media upload and alt text.
- Dry-run, local validation, duplicate protection, cooldown, process lock, and run history.

## Install

1. Download and extract `XAA-v1.0.0.zip`.
2. Open a terminal in the `XAA` directory.
3. Run `python install.py`.
4. Complete `config.json` and add `logo.png`.
5. Run `python start.py --check`.
6. Run `python start.py --dry-run` and review the result.
7. Run `python start.py` only when ready to publish.

Python 3.11 or newer is required. OpenAI API and X API credentials are not included.

## Important notes

- A dry run does not publish, but it does call OpenAI and may incur charges.
- XAA uses public web search; it does not include a private TikTok API integration.
- Trend discovery and generated content do not guarantee virality or factual accuracy.
- Review every post for safety, accuracy, intellectual-property issues, and platform compliance.
- Keep `config.json` private. It contains live credentials and is excluded from Git by default.
- No software license is included. Repository owners should choose one before permitting third-party
  use, modification, or redistribution.

See `README.md`, `docs/SETUP.md`, and `CHANGELOG.md` for complete details.
