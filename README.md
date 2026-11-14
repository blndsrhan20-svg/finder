# NANDO FINDER

Telegram bot for basic, privacy-respecting public-information checks.

## Deploy

Deploy this repository to a worker/background service. Set the secret environment variable BOT_TOKEN to a newly generated Telegram bot token. Never commit tokens to Git.

## Commands

- /start, /help
- /id — show the current user's own Telegram ID and chat ID
- /phone +964... — validate number format only; does not identify its owner
- /url example.com — basic URL syntax indicators only
- /lookup username — link to a public Telegram username

The bot does not access leaked databases, reveal private information, or identify phone-number owners.
