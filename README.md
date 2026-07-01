# Neurodivergent-Discord-Bot

A Discord bot (built with `discord.py`) that provides accessibility features for neurodivergent
users: tone indicator lookup, ADHD-friendly task breakdowns, text readability simplification, and
scheduled channel announcements. AI-backed features are powered by Google Gemini (`gemini-2.5-flash`
via the `google-genai` SDK).

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set:
   - `DISCORD_TOKEN` — **required**. The bot exits immediately on startup if this is missing.
   - `GEMINI_API_KEY` — optional. If unset, all AI-backed commands still respond, but return an
     error string instead of calling the Gemini API.
3. Run the bot:
   ```
   python main.py
   ```

A quick manual smoke test of the Gemini integration (mocks the client, makes no real API call) is
available via `python scratch_test.py`. There is no automated test suite or lint/format tooling
configured in this repo.

## Commands

All commands are Discord slash commands (`/...`) unless noted as a message context menu (accessed
by right-clicking a message → Apps).

### Tone indicators (`cogs/tones.py`)

| Command | Description |
| --- | --- |
| `/tone lookup indicator:<text>` | Looks up a specific tone indicator (e.g. `j`, `srs`, `lh`) and shows its name, description, and an example sentence. |
| `/tone list` | Lists every supported tone indicator alphabetically. |
| `/tone suggest message:<text>` | Uses Gemini to analyze a message's emotional tone and suggest 1–2 tone indicators that match the writer's intent. |
| **Explain Tone Indicators** (context menu) | Scans a message for `/word` patterns and, for any that match known tone indicators, shows their definitions. |

Tone indicator data (name, description, example) lives in the static dictionary
`tone_data.TONE_INDICATORS` — no database or API call is needed for lookup/list.

### ADHD task breakdown (`cogs/adhd.py`)

| Command | Description |
| --- | --- |
| `/breakdown task:<text>` | Uses Gemini to split an intimidating task into small, concrete, checkbox-style steps. |

### Readability (`cogs/readability.py`)

| Command | Description |
| --- | --- |
| `/simplify text:<text>` | Uses Gemini to reformat pasted text into short paragraphs, bolded key terms, and lists, without changing its meaning. |
| `/readability_delivery method:<DM\|Public Thread>` | Sets how *you* want simplified text delivered when you react to a long message (see below). Stored per-user in the database. |
| **Format Readability** (context menu) | Runs the same reformatting as `/simplify` on the target message. |
| **Summarize Text** (context menu) | Uses Gemini to produce a short bulleted TL;DR of the target message. |

Automatic behavior (no command needed):
- **`on_message`** — the bot reacts with 📖 to any non-bot message longer than 500 characters.
- **`on_raw_reaction_add`** — when *any* user reacts 📖 to a message, the bot fetches that message,
  simplifies its content via Gemini, and delivers the result according to the reacting user's stored
  delivery preference:
  - `dm` (default) — sent as a DM to the reacting user; if the DM fails (e.g. DMs closed), it falls
    back to a public thread.
  - `thread` — a public thread is created under the original message and the result posted there; if
    thread creation isn't possible, it falls back to a temporary reply in the channel (auto-deleted
    after 2 minutes).

### Scheduled notices (`cogs/notices.py`)

| Command | Description |
| --- | --- |
| `/create-notice date:<MM/DD/YYYY> time:<HH:MM> message:<text>` | Schedules an announcement to be posted in the current channel at a future date/time (24-hour, bot server time). Requires the **Manage Messages** permission. |

A background task (`check_due_notices`) polls the database every 30 seconds and posts any notice
whose scheduled time has passed, in an embed, then marks it as sent so it isn't posted again (even if
delivery fails, e.g. the channel was deleted).

## Architecture

- **`main.py`** — defines `NeuroBot` (a `commands.Bot` subclass). On startup (`setup_hook`), it
  initializes the database, loads all cogs (`cogs.tones`, `cogs.adhd`, `cogs.readability`,
  `cogs.notices`), and globally syncs the slash command tree. New cogs must be added to the `cogs`
  list here to be loaded.
- **`cogs/`** — one module per feature area. Each is a `commands.Cog` registering slash commands
  and/or context menus, and each ends with an `async def setup(bot)` entry point that
  `load_extension` calls. Context menus are defined at module level (discord.py doesn't allow them as
  Cog methods) and manually added to the command tree inside `setup()`.
- **`ai_helper.py`** — the single point of contact with the Gemini API. Every public function
  (`get_task_breakdown`, `reformat_readability`, `summarize_text`, `suggest_tone_indicator`) builds a
  prompt and funnels it through the private `_query_gemini(prompt)`, which checks the database cache
  before calling the API and writes successful responses back to the cache. If `GEMINI_API_KEY` is
  unset, calls short-circuit to an error string instead of touching the network.
- **`database.py`** — raw `sqlite3` access (no ORM) against the file at `config.DATABASE_PATH`
  (`neurodivergent_bot.db`). Each function opens and closes its own connection. See **Data storage**
  below for the schema.
- **`config.py`** — loads `.env` via `python-dotenv` and exposes `DISCORD_TOKEN`, `GEMINI_API_KEY`,
  `DATABASE_PATH`, and the per-feature embed colors (`COLOR_TONE`, `COLOR_ADHD`, `COLOR_READABILITY`,
  `COLOR_NOTICE`) used for consistent, low-sensory Discord embed theming.
- **`tone_data.py`** — static dictionary of tone indicators (name, description, example) used by
  `cogs/tones.py`.

## Data storage

The bot uses a single SQLite database file (`neurodivergent_bot.db`, path configurable via
`config.DATABASE_PATH`), created and migrated (in a very simple `CREATE TABLE IF NOT EXISTS` sense) by
`database.init_db()` on every startup. There are three tables:

### `user_preferences`

Stores each user's readability delivery preference, set via `/readability_delivery`.

| Column | Type | Notes |
| --- | --- | --- |
| `user_id` | `INTEGER PRIMARY KEY` | Discord user ID. |
| `readability_delivery` | `TEXT` | `'dm'` (default) or `'thread'`. |

### `ai_cache`

Caches Gemini responses so identical prompts don't re-hit the API. Keyed by a SHA-256 hash of the
full prompt text (not just the user's input — different features build different prompt wrappers
around the same input, so they cache independently).

| Column | Type | Notes |
| --- | --- | --- |
| `prompt_hash` | `TEXT PRIMARY KEY` | `sha256(prompt)` hex digest. |
| `response_text` | `TEXT` | The cached Gemini response. |
| `created_at` | `TIMESTAMP` | Defaults to `CURRENT_TIMESTAMP`. |

### `scheduled_notices`

Stores announcements created via `/create-notice`, polled by the `Notices` cog's background loop.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | |
| `guild_id` | `INTEGER` | Server the notice was scheduled from. |
| `channel_id` | `INTEGER` | Channel to post the notice in. |
| `author_id` | `INTEGER` | Discord user ID of whoever scheduled it. |
| `message` | `TEXT` | The announcement text. |
| `scheduled_time` | `TIMESTAMP` | ISO-formatted; when the notice should be posted. |
| `sent` | `INTEGER` | `0` (pending) or `1` (delivered); prevents re-sending. |
