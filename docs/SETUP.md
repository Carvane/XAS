# XAA setup guide

This guide takes XAA from a clean download to a reviewed dry run and optional publication on X.

## 1. Install Python

Install Python 3.11 or newer and make sure it is available in your terminal:

```bash
python --version
```

On Windows, the command may be:

```powershell
py --version
```

## 2. Install XAA

From the project directory, run:

```bash
python install.py
```

The installer:

- creates a private virtual environment in `.venv`;
- upgrades `pip` inside that environment;
- installs packages from `requirements.txt`;
- creates `config.json` from `config.example.json` when needed.

The installer never overwrites an existing `config.json`.

## 3. Configure OpenAI

Create an API key in your OpenAI account and paste it into:

```json
{
  "openai": {
    "api_key": "YOUR_REAL_KEY"
  }
}
```

The default models are:

- `gpt-5.6` for research, caption writing, and the structured creative brief;
- `gpt-image-2` for editing the supplied character into the meme scene.

XAA uses Responses API web search and Conversations API state. Leave `conversation_id` empty on
the first run. XAA creates a conversation and writes its ID back to `config.json` automatically.
Keep that ID to preserve context between runs. Delete only the value, not the field, if you want XAA
to start a fresh conversation.

OpenAI API access is separate from a ChatGPT subscription. Your account must have access and
billing for the configured models.

### Optional web domain filters

`allowed_domains` and `blocked_domains` accept domain names without paths. Use only one strategy at
a time. When `allowed_domains` is non-empty, it takes precedence.

```json
"allowed_domains": ["example.com", "another.example"],
"blocked_domains": []
```

Leaving both lists empty gives the research step the broadest reach.

## 4. Configure X

Create an app in the X developer portal and configure user authentication with Read and Write
permission. Add its OAuth 1.0a credentials to the `x` section:

```json
"x": {
  "api_key": "...",
  "api_secret": "...",
  "access_token": "...",
  "access_token_secret": "..."
}
```

Important:

- XAA uses OAuth 1.0a user context through Tweepy.
- If you change app permissions from Read to Read and Write, regenerate the access token and
  access-token secret afterwards. Old user tokens may retain the old permission scope.
- Your X API plan must permit the operations used by the app.
- Do not use a bearer token in any of the four fields above.

To generate without publishing, either use `--dry-run` or set `publishing.dry_run` to `true`.

## 5. Describe the brand

The `brand` section controls what the text model knows about the account. A Hamsty/Solana example:

```json
"brand": {
  "coin_name": "Hamsty",
  "ticker": "$HAMSTY",
  "description": "A Solana memecoin built around Hamsty, a deadpan hooded hamster surviving crypto culture, chart chaos and everyday internet life.",
  "contract_address": "",
  "website": "",
  "x_handle": "@hamsty",
  "tone": "dry, concise, internet-native and self-aware; awkward degen humor; never corporate, desperate or overexplained",
  "call_to_action": "",
  "forbidden_topics": [
    "death and tragedy",
    "war",
    "politics",
    "financial return promises"
  ]
}
```

The contract address and website are optional. XAA does not automatically insert them into every
caption. This is intentional: forced promotion usually weakens the joke and can make posts look
like spam.

## 6. Add the character reference

Place the canonical character image at:

```text
logo.png
```

Despite the filename, it is not used as a watermark. The entire visible character is a mandatory
identity reference for the image edit.

For best results:

- use the highest-resolution source you own;
- show the exact face, outfit, colors, body type, and characteristic expression;
- avoid extra characters and unnecessary text;
- a white background is acceptable because the prompt tells the model to remove it;
- keep only one canonical version of the character in the file.

XAA allows the character to sit, stand, hold props, or interact with a setting. It does not permit
the model to redesign the face, clothing, palette, species-like appearance, proportions, or visual
style. If a requested action conflicts with identity preservation, the prompt tells the model to
simplify the action.

## 7. Review generation settings

| Field | Default | Purpose |
|---|---:|---|
| `logo_path` | `logo.png` | Character reference path. |
| `output_dir` | `output` | Per-run artifact directory. |
| `history_file` | `data/history.json` | Duplicate and cooldown history. |
| `timezone` | `Europe/Warsaw` | Local time used for research context and output names. |
| `post_language` | `English` | Requested caption language. |
| `max_post_chars` | `260` | Caption limit; must be from 1 to 280. |
| `trend_window_hours` | `72` | Preferred recency window for trend research. |
| `trend_sources` | mixed web sources | Research priorities, not guaranteed direct API feeds. |
| `image_size` | `1536x1024` | Landscape image output size. |
| `image_quality` | `medium` | Image-model quality setting. |
| `max_upload_mb` | `4.8` | Local JPEG compression target. |
| `duplicate_lookback` | `30` | Published history entries checked for repetition. |
| `generation_attempts` | `3` | Attempts to find a sufficiently different trend; 1 to 5. |

XAA does not connect to a private TikTok API. It uses OpenAI web search to find public, current
reporting and pages associated with sources listed in `trend_sources`. Availability and recency
vary across the open web.

## 8. Review publishing settings

```json
"publishing": {
  "enabled": true,
  "dry_run": false,
  "min_hours_between_posts": 6,
  "add_alt_text": true
}
```

- `enabled: false` always prevents publishing.
- `dry_run: true` always prevents publishing but still generates content.
- `min_hours_between_posts` protects against accidental repeated execution.
- `add_alt_text` attaches the generated accessibility description to the uploaded media.

The `--force` command-line flag bypasses the cooldown only. It does not bypass disabled publishing
or dry-run mode.

## 9. Validate without API calls

```bash
python start.py --check
```

This validates the JSON structure, placeholder values, ranges, time zone, and character-image
path. It does not verify credentials with OpenAI or X and does not spend API credits.

## 10. Perform a dry run

```bash
python start.py --dry-run
```

This performs live research and image generation, so OpenAI charges may apply. It does not publish
to X. Review:

- the setup/punchline spacing printed in the terminal;
- `content.json` for trend reasoning and source URLs;
- `meme_final.jpg` for character fidelity and artifacts;
- factual statements and potential copyright, trademark, privacy, or safety issues.

## 11. Publish

After a successful review:

```bash
python start.py
```

XAA uploads the JPEG, applies alt text when enabled, creates the post, records the response IDs,
and prints the post URL.

## 12. Configure automatic publishing on Linux

The optional `auto.py` scheduler can run `start.py` repeatedly without cron or an additional
Python package. It waits before every run, including the first one.

Configure these values near the top of `auto.py`:

```python
BASE_INTERVAL_HOURS = 2
RANDOM_MINUTES_MIN = 1
RANDOM_MINUTES_MAX = 60
BYPASS_XAA_COOLDOWN = True
```

With these settings, XAA waits for 2 hours plus a randomly selected delay from 1 to 60 minutes.
The total delay before each publication is therefore between 2 hours 1 minute and 3 hours.

Each scheduler cycle works as follows:

1. Select a random number of minutes from the configured range.
2. Print the delay and exact planned run time.
3. Wait for the complete delay.
4. Run `start.py` and wait until it finishes.
5. Print the exit code, select a new delay and repeat.

`RANDOM_MINUTES_MIN` may be set to `0`. `RANDOM_MINUTES_MAX` must be equal to or greater than the
minimum. `BASE_INTERVAL_HOURS` and both minute values must not be negative.

When `BYPASS_XAA_COOLDOWN` is `True`, the scheduler runs:

```bash
python start.py --force
```

This prevents `publishing.min_hours_between_posts` from blocking the interval explicitly selected
in `auto.py`. The flag bypasses only the cooldown. It does not override `enabled: false` or
`dry_run: true` in `config.json`.

Set `BYPASS_XAA_COOLDOWN` to `False` if the normal cooldown from `config.json` should remain in
effect. In that case, make sure `min_hours_between_posts` is not longer than the intended schedule,
or XAA may skip a planned publication.

Start the scheduler in the foreground:

```bash
cd ~/XAA
python3 -u auto.py
```

The `-u` option keeps terminal output unbuffered. The selected delay, next run time and process
result appear immediately. Press `Ctrl+C` to stop the scheduler safely.

### Keep XAA running after closing SSH

Install `screen` if needed:

```bash
sudo apt update
sudo apt install -y screen
```

Create a named session and start the scheduler:

```bash
cd ~/XAA
screen -S xaa
python3 -u auto.py
```

Detach without stopping XAA:

1. Press `Ctrl+A`.
2. Release the keys.
3. Press `D`.

List active sessions:

```bash
screen -ls
```

Return to the XAA session:

```bash
screen -r xaa
```

To stop automatic publishing, return to the session and press `Ctrl+C`.

`screen` keeps the scheduler running when the SSH connection closes. It does not restart XAA after
a VPS reboot. Configure a `systemd` service separately if automatic startup after reboot is
required.

## Output and history

Each generation creates a unique timestamped directory under `output/`. The untouched image-model
result is stored as `meme_generated.png`; the compressed upload version is `meme_final.jpg`.

`data/history.json` retains up to 500 recent generation records. Duplicate comparison uses only
published records. Dry runs remain in history for inspection but do not trigger the publication
cooldown.

## Caption and image prompt customization

Edit the constants in `xaa/openai_service.py` only when you intentionally want to change global
behavior:

- `POST_STYLE_INSTRUCTIONS` controls the sparse two-block X caption.
- `CHARACTER_LOCK_INSTRUCTIONS` protects the supplied character's identity.
- `ANTI_AI_SLOP_INSTRUCTIONS` controls the found-photo, manually composited meme aesthetic.

Brand-specific voice belongs in `config.json`, not in those shared constants.

## Troubleshooting

### `Character image not found`

Confirm that `logo.png` is in the project root or update `generation.logo_path`. Relative paths are
resolved from the directory containing the selected config file.

### OpenAI authentication or model error

Check the API key, billing status, model access, and model names. ChatGPT access does not
automatically include API credits.

### OpenAI conversation error

The configured conversation may be invalid, deleted, or associated with different credentials.
Clear only the `conversation_id` value and run XAA again to create a new one.

### X returns an authorization error

Confirm OAuth 1.0a user credentials, Read and Write permission, regenerated user tokens, and an API
plan that supports publishing and media upload.

### XAA says it is already running

Only one process may use a history file at once. Wait for the active process. If a process crashed,
the `.xaa.lock` file is considered stale after six hours and is removed automatically.

### `auto.py` starts but does not publish

Check `publishing.enabled` and `publishing.dry_run` in `config.json`. Also check the terminal log for
the exit code returned by `start.py`. If `BYPASS_XAA_COOLDOWN` is `False`, the configured cooldown
may intentionally skip the run.

### `auto.py` stops after closing SSH

Run it inside `screen`, detach with `Ctrl+A` followed by `D`, and confirm the session with
`screen -ls`. Closing the terminal without `screen`, `systemd`, or another process manager stops the
program.

### The scheduler did not restart after a VPS reboot

This is expected when using only `screen`. Start a new session manually after the reboot or create
a `systemd` service for automatic startup.

### The meme changes the character too much

Use a cleaner, larger reference and simplify the requested action. Strengthen the relevant wording
inside `CHARACTER_LOCK_INSTRUCTIONS`; do not describe a conflicting redesign in brand settings.

### The result still looks synthetic

Use `medium` or a supported higher image quality, keep the scene mundane, ask for fewer props, and
make the central joke visually simple. The built-in anti-slop prompt already suppresses cinematic
light, neon crypto clichés, glossy 3D, fake interfaces, clutter, and excessive polish.

### Run tests

```bash
python start.py --test
```

For a full traceback from the app:

```bash
python start.py --dry-run --debug
```

## Updating

Back up `config.json`, `logo.png`, and any runtime history you want to retain. Replace the source
files, run `python install.py` to refresh dependencies, then run `--check` and `--dry-run` before
publishing again.

The automatic scheduler does not add any required field to `config.json`. Existing v1.0.0
configurations remain compatible with the scheduler update.
