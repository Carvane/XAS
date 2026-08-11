# Security policy

## Supported versions

Security fixes are currently provided for the latest `1.0.x` release.

## Reporting a vulnerability

Do not open a public issue for an exploitable vulnerability or an accidentally committed secret.
Use the repository's private GitHub Security Advisory reporting feature when it is available.
Include the affected version, impact, reproduction steps, and any suggested mitigation.

## Protecting credentials

- Never commit or share `config.json`.
- Do not paste real API keys into issues, logs, screenshots, or test fixtures.
- Keep OpenAI and X credentials limited to the access required by XAA.
- If a credential is exposed, revoke it at the provider immediately and generate a replacement.
- Review Git history as well as the current files after an accidental commit; deleting a secret
  from the latest revision does not remove it from earlier commits.

The included `.gitignore` excludes the live config, character reference, generated output, history,
logs, virtual environment, and release archives. This is a safeguard, not a substitute for checking
every commit before pushing it.
