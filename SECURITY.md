# Security policy

## Supported versions

Security fixes are currently provided for the latest `1.2.x` release.

## Reporting a vulnerability

Do not open a public issue for an exploitable vulnerability or an accidentally committed secret.
Use the repository's private GitHub Security Advisory reporting feature when it is available.
Include the affected version, impact, reproduction steps, and any suggested mitigation.

## Protecting credentials

- Never commit or share `config.json`.
- Do not paste real API keys into issues, logs, screenshots, or test fixtures.
- Keep OpenAI and X credentials limited to the access required by XAA.
- Protect the live configuration on Linux with `chmod 600 config.json`.
- Treat `conversation_id` and other account-linked identifiers as private operational metadata even
  though they do not replace API authentication.
- If a credential is exposed, revoke it at the provider immediately and generate a replacement.
- Review Git history as well as the current files after an accidental commit; deleting a secret
  from the latest revision does not remove it from earlier commits.

The included `.gitignore` excludes the live config, character reference, generated output, history,
logs, virtual environment, and release archives. This is a safeguard, not a substitute for checking
every commit before pushing it.

## Unattended publishing

- Run `python start.py --check` after configuration changes.
- Use `python start.py --dry-run` and review several outputs before enabling automatic publishing.
- Keep `BYPASS_XAA_COOLDOWN = False` during normal scheduler operation.
- Use `--force` only as an intentional temporary override of the publication cooldown.
- Restrict access to the VPS account, keep the operating system updated, and stop the scheduler if
  the X or OpenAI account shows unexpected activity.
- Generated captions and images can still be inaccurate or inappropriate. The operator remains
  responsible for the content published by the account.

## Generated files and logs

Files under `output/` and `data/history.json` may contain post text, source URLs, conversation IDs,
publication IDs, and operational timestamps. Do not expose these directories through a public web
server or include them in support bundles without reviewing their contents first.