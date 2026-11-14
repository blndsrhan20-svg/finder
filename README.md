# NANDO FINDER

Telegram bot for basic public-information checks.

## Features
- /start and /help
- /id shows the ID of the person interacting with the bot
- /phone checks international number format, region and approximate line type
- /url flags a few suspicious URL patterns (not a safety guarantee)
- /lookup explains Telegram lookup and privacy limitations

## Run locally
1. Install Python 3.12 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Set the environment variable `BOT_TOKEN` to a newly issued token.
4. Run: `python bot.py`

## Deploy
Deploy this repository as a worker/container on a service that supports persistent processes. Set `BOT_TOKEN` as a private environment variable in the hosting dashboard. Do not commit your token or an `.env` file.

GitHub stores the source code; it does not keep a polling bot running continuously by itself.

## Privacy and safety
This bot does not identify private people from phone numbers or Telegram IDs, bypass Telegram privacy settings, access leaked databases, or track people. Phone checks are metadata only; URL checks are heuristic and cannot certify a site as safe.
