# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Discord bot (discord.py) providing accessibility features for neurodivergent users: tone indicator
lookup/suggestion, ADHD task breakdowns, and readability simplification. AI features are powered by
Google Gemini (`google-genai`).

## Commands

- Install deps: `pip install -r requirements.txt`
- Run the bot: `python main.py`
- Quick manual smoke test of the Gemini integration (mocks the client, no real API call): `python scratch_test.py`

There is no test framework configured (no pytest, no test suite) and no lint/format tooling defined in
this repo.

### Environment setup

Copy `.env.example` to `.env` and set:
- `DISCORD_TOKEN` — required; the bot exits early in `main.py` if missing.
- `GEMINI_API_KEY` — optional; if unset, `ai_helper.client` is `None` and all AI-backed commands return
  an error string instead of raising.

## Architecture

**Entry point (`main.py`)** — `NeuroBot` subclasses `commands.Bot`. On `setup_hook()` it calls
`database.init_db()`, loads all three cogs in `cogs/`, then globally syncs the slash command tree.
Cogs are hardcoded in a list (`cogs.tones`, `cogs.adhd`, `cogs.readability`) — new cogs must be added
to this list in `main.py` to be loaded.

**Cogs (`cogs/*.py`)** — each cog is a `commands.Cog` registering Discord slash commands
(`app_commands`) and/or context menus, and calls into `ai_helper` for any AI-backed behavior. Each cog
module ends with an `async def setup(bot)` that discord.py's `load_extension` calls.
- `cogs/tones.py` — `/tone lookup`, `/tone list`, `/tone suggest` (AI), plus an "Explain Tone
  Indicators" message context menu. Looks up data from `tone_data.TONE_INDICATORS`.
- `cogs/adhd.py` — `/breakdown` (AI task breakdown).
- `cogs/readability.py` — `/simplify`, `/readability_delivery` (sets a per-user DB preference), plus
  "Format Readability" / "Summarize Text" context menus. Also has `on_message` (reacts with 📖 to
  messages >500 chars) and `on_raw_reaction_add` (when a user reacts 📖, fetches the message, simplifies
  it via Gemini, and delivers the result by DM or by spawning a thread depending on the user's stored
  `readability_delivery` preference — see `_deliver_via_thread`).

**`ai_helper.py`** — single point of contact with the Gemini API (`gemini-2.5-flash`). All public
functions (`get_task_breakdown`, `reformat_readability`, `summarize_text`, `suggest_tone_indicator`)
funnel through the private `_query_gemini(prompt)`, which checks `database`'s SQLite-backed response
cache (keyed by SHA-256 hash of the prompt) before calling the API, and writes successful responses back
to the cache. If `GEMINI_API_KEY` is unset, every call short-circuits to an error string rather than
calling the API.

**`database.py`** — raw `sqlite3` access (no ORM) against `neurodivergent_bot.db` (path from
`config.DATABASE_PATH`). Two tables: `user_preferences` (per-user `readability_delivery` setting,
default `'dm'`) and `ai_cache` (prompt-hash → response text). Each function opens its own connection via
`get_db_connection()`.

**`config.py`** — loads `.env` via `python-dotenv` and exposes `DISCORD_TOKEN`, `GEMINI_API_KEY`,
`DATABASE_PATH`, and the per-feature embed colors (`COLOR_TONE`, `COLOR_ADHD`, `COLOR_READABILITY`)
used across cogs for consistent, low-sensory Discord embed theming.

**`tone_data.py`** — static dict of tone indicators (e.g. `/j`, `/srs`, `/lh`) with name, description,
and example; the data source for `cogs/tones.py`.

### Adding a new AI-backed feature

1. Add a prompt-building function to `ai_helper.py` that calls `_query_gemini(prompt)` (gets caching for
   free).
2. Add/extend a cog under `cogs/` with the slash command or context menu, using
   `interaction.response.defer()` before the AI call (since Gemini calls are not instant) and
   `interaction.followup.send(embed=...)` after.
3. If the cog is new, register its module path in the `cogs` list in `main.py`.
