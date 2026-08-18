# XAA (X Auto Agent)

XAA is a Python agent that researches current internet trends, writes an English meme caption,
creates an original meme around a supplied character reference, and can publish the result to X.

The image in `logo.png` is treated as the character itself, not as a watermark. XAA instructs the
image model to preserve the face, outfit, proportions, palette, and mixed photomontage style while
changing only the pose, placement, lighting, shadows, and scene interaction required by the joke.

> XAA can help discover timely material; it cannot guarantee that a topic or post will become viral.
> Review generated content before enabling unattended publishing.

## Highlights

- Live trend research through OpenAI Responses API web search with `gpt-5.6-luna` recommended for
  efficient recurring runs.
- Persistent OpenAI conversation context through `conversation_id` without copying the same local
  history into every prompt.
- Stronger trend qualification based on recent evidence from at least two independent domains.
- Reddit and Know Your Meme are treated as secondary context, not sole proof of virality.
- Structured caption generation with exactly one blank line between setup and punchline.
- Original landscape meme generation with `gpt-image-2` image editing.
- Strict character-identity lock for `logo.png`.
- Anti-AI-slop art direction: believable found-photo aesthetics, simple visual jokes, restrained
  grading, realistic imperfections, varied locations and camera treatments, and no generic neon
  crypto spectacle.
- Automatic image conversion and compression for X uploads.
- Automatic image upload, alt text, and post publishing through Tweepy.
- Duplicate-topic and repeated-motif detection, publication cooldown, process locking, and local
  run history.
- Web source metadata capped at 20 entries per generation to keep output records compact.
- Safe `--check` and `--dry-run` modes.

## What's new in v1.2.0

- Recommended text model changed to `gpt-5.6-luna` for lower-cost recurring generation.
- OpenAI Conversation remains enabled, while `history.json` is no longer manually duplicated in
  each model prompt.
- Trend selection now requires stronger and more recent independent evidence.
- Captions rotate joke structures and naturally include a discovery anchor such as `Solana`,
  `$HAMSTY`, `memecoin`, `AI agent`, or `open source` in some posts.
- Recent overused themes such as dust, bad bags, rugs, rent, portfolios, trenches, and emotional
  damage are temporarily rejected by the local duplicate checker.
- Image prompts rotate locations, framing, camera style, character scale, and pose while preserving
  the exact character identity from `logo.png`.
- The default scheduler now waits 6 hours plus 30 to 180 random minutes and respects the cooldown
  configured in `config.json`.

## How it works

1. XAA searches the live web for one recent, broadly recognizable trend.
2. It checks for recent evidence from multiple independent sources and rejects weak or obscure
   candidates.
3. The text model connects the selected trend to the configured brand without fabricating claims.
4. It returns a short English setup and punchline plus an image brief and alt text.
5. XAA edits the supplied character reference into an original meme scene.
6. The final image is compressed to JPEG and saved with the generation metadata.
7. In publish mode, Tweepy uploads the media and creates the X post.

XAA performs one generation and publication cycle per `start.py` invocation. The optional
`auto.py` scheduler can run that cycle repeatedly after a fixed delay plus a randomized number of
minutes.

## Requirements

- Python 3.11 or newer.
- An OpenAI API key with access to the configured text and image models.
- An X developer app with user authentication, Read and Write permission, and API access that
  allows media upload and post creation.
- A `logo.png` character reference.

OpenAI and X usage may incur charges under your accounts. Model and platform availability depend
on your API tier, billing status, region, and provider policies.

## Quick start

```bash
git clone https://github.com/Carvane/XAA.git
cd XAA
python install.py
```

If you downloaded a GitHub Release archive instead, extract it and open a terminal inside its
`XAA` directory before running the installer.

The installer creates `.venv`, installs pinned dependencies, and copies `config.example.json` to
`config.json` if the latter does not exist.

Next:

1. Add your credentials and brand settings to `config.json`.
2. Place the character reference at `logo.png`.
3. Validate local files without API calls:

   ```bash
   python start.py --check
   ```

4. Generate a real caption and meme without publishing:

   ```bash
   python start.py --dry-run
   ```

5. Review the files in `output/`, then publish:

   ```bash
   python start.py
   ```

On Windows, `py install.py` and `py start.py ...` work when the Python launcher is installed.

For efficient recurring text generation, the recommended model setting is:

```json
"text_model": "gpt-5.6-luna"
```

Leave `conversation_id` empty to let XAA create and save one automatically, or keep an existing ID
to continue the established agent context.

For the full credential, configuration, and troubleshooting guide, see
[docs/SETUP.md](docs/SETUP.md).

## Character reference rules

Use a clear PNG showing the complete, canonical character. A plain background is acceptable; XAA
explicitly removes the reference-sheet background and integrates the character into the scene.

The generation prompt is designed to:

- preserve the exact face, expression, fur markings, outfit, trim, body type, palette, and style;
- prevent redesigns into anime, glossy 3D, a generic mascot, or a different animal;
- allow only scene-fitting scale, crop, pose, perspective, light, shadow, focus, and color matching;
- make the character physically participate instead of appearing as a sticker or watermark;
- simplify the composition whenever an action would require changing the character's identity.

The central prompt rules are in `xaa/openai_service.py`:

- `CHARACTER_LOCK_INSTRUCTIONS`
- `ANTI_AI_SLOP_INSTRUCTIONS`
- `POST_STYLE_INSTRUCTIONS`

## Caption style

Every caption is assembled as exactly two compact blocks:

```text
short setup

dry payoff
```

XAA avoids headings, URLs, promotional sign-offs, ticker spam, and emoji clutter. It may use zero
or one relevant hashtag when it reads naturally. It also rotates sentence shape, point of view, and
joke mechanism instead of repeatedly using the same trend-report formula. The sample captions used
while designing this format influenced only its spacing and silhouette; their wording and subject
matter are not embedded in the program.

## Commands

| Command | Result |
|---|---|
| `python start.py --check` | Validate config and `logo.png`; make no API calls. |
| `python start.py --dry-run` | Research and generate; do not publish. |
| `python start.py` | Research, generate, and publish to X. |
| `python start.py --force` | Publish despite the configured cooldown. |
| `python start.py --config path.json` | Use another configuration file. |
| `python start.py --debug` | Print full tracebacks for failures. |
| `python start.py --test` | Run the unit test suite. |
| `python main.py --version` | Print the XAA version. |
| `python3 -u auto.py` | Run XAA repeatedly using the automatic scheduler. |

`--dry-run` still calls OpenAI and can incur API costs. `--check` is the no-API validation command.

## Automatic scheduling on Linux

`auto.py` can publish repeatedly without requiring cron or another Python package. Configure the
schedule near the top of the file:

```python
BASE_INTERVAL_HOURS = 6
RANDOM_MINUTES_MIN = 30
RANDOM_MINUTES_MAX = 180
BYPASS_XAA_COOLDOWN = False
```

With the recommended settings above, each cycle waits for 6 hours plus a random delay between 30
and 180 minutes. The average interval is 7 hours and 45 minutes. The first cycle also waits, so
starting `auto.py` does not publish immediately.

The scheduler works as follows:

1. Select a random number of minutes from the configured range.
2. Wait for the base interval plus the selected random delay.
3. Run `start.py` and wait until generation and publication finish.
4. Select a new random delay and repeat the cycle.

Keep `BYPASS_XAA_COOLDOWN` set to `False` for normal unattended operation. The scheduler then
respects `publishing.min_hours_between_posts` from `config.json`. Setting it to `True` makes
`auto.py` run `start.py --force` and should be used only as an intentional temporary override.

Start the scheduler in the foreground with:

```bash
cd ~/XAA
python3 -u auto.py
```

The `-u` option keeps log output unbuffered, so status messages appear immediately. The scheduler
prints the selected delay, the exact planned run time and the exit code returned by `start.py`.
Press `Ctrl+C` to stop it safely.

### Keep the scheduler running with screen

Install `screen` if it is not already available:

```bash
sudo apt update
sudo apt install -y screen
```

Create a named session and start XAA:

```bash
cd ~/XAA
screen -S xaa
python3 -u auto.py
```

Detach from the session without stopping XAA by pressing `Ctrl+A`, releasing the keys, and then
pressing `D`.

List running sessions:

```bash
screen -ls
```

Return to the scheduler:

```bash
screen -r xaa
```

To stop it, return to the session and press `Ctrl+C`.

`screen` keeps XAA running after the SSH connection closes, but it does not automatically restart
the scheduler after a VPS reboot. Use a `systemd` service if automatic startup after reboot is
required.

## Files created at runtime

```text
data/history.json
output/YYYYMMDD_HHMMSS_microseconds/
  content.json
  meme_generated.png
  meme_final.jpg
```

`content.json` records the selected trend, sources returned by web search, caption, image brief,
alt text, conversation ID, and publication status. `history.json` is used for duplicate detection
and cooldown checks. It is not copied into the OpenAI prompt because Conversation already preserves
the model context. The local file remains necessary for deterministic cooldown and duplicate checks.

## Security

Never commit `config.json`, `logo.png`, `data/`, or `output/`. They are ignored by Git. The example
config contains placeholders only. If a key is exposed, revoke it with the provider immediately
and create a replacement. See [SECURITY.md](SECURITY.md).

## Tests

```bash
python start.py --test
```

GitHub Actions runs compilation and unit tests on supported Python versions for every push and
pull request.

## API references

- [OpenAI web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [OpenAI conversation state](https://developers.openai.com/api/docs/guides/conversation-state)
- [GPT-5.6 Luna model](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [OpenAI image generation and editing](https://developers.openai.com/api/docs/guides/image-generation)
- [GPT Image 2 model](https://developers.openai.com/api/docs/models/gpt-image-2)
- [Tweepy documentation](https://docs.tweepy.org/)
- [X developer documentation](https://docs.x.com/)

## Responsible use

XAA blocks several risky content patterns in its generation brief, including promises of financial
returns, fabricated endorsements, fake scarcity, impersonation, invented statistics, and the
exploitation of tragedy. Generated output can still be wrong or inappropriate. You are responsible
for fact-checking, complying with applicable law and platform rules, respecting intellectual
property, and deciding what your account publishes.