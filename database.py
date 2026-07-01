import sqlite3
import hashlib
from datetime import datetime
from config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database, creating tables if they do not exist."""
    with get_db_connection() as conn:
        # Create user preferences table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                readability_delivery TEXT DEFAULT 'dm'
            )
        """)
        
        # Create AI cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_cache (
                prompt_hash TEXT PRIMARY KEY,
                response_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create scheduled notices table (for /create-notice announcements)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                sent INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def get_user_delivery_pref(user_id: int) -> str:
    """Gets the user's readability summary delivery preference ('dm' or 'thread')."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT readability_delivery FROM user_preferences WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if row:
            return row['readability_delivery']
        return 'dm'

def set_user_delivery_pref(user_id: int, pref: str):
    """Sets the user's readability summary delivery preference ('dm' or 'thread')."""
    if pref not in ('dm', 'thread'):
        raise ValueError("Preference must be 'dm' or 'thread'")
        
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_preferences (user_id, readability_delivery) VALUES (?, ?)",
            (user_id, pref)
        )
        conn.commit()

def hash_prompt(prompt: str) -> str:
    """Helper to generate a SHA-256 hash of a prompt string."""
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()

def get_cached_ai_response(prompt: str) -> str:
    """Retrieves cached AI response if it exists, otherwise returns None."""
    prompt_hash = hash_prompt(prompt)
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT response_text FROM ai_cache WHERE prompt_hash = ?",
            (prompt_hash,)
        ).fetchone()
        if row:
            return row['response_text']
    return None

def cache_ai_response(prompt: str, response_text: str):
    """Caches an AI response keyed by the prompt's hash."""
    prompt_hash = hash_prompt(prompt)
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO ai_cache (prompt_hash, response_text) VALUES (?, ?)",
            (prompt_hash, response_text)
        )
        conn.commit()

def create_scheduled_notice(guild_id: int, channel_id: int, author_id: int, message: str, scheduled_time: datetime) -> int:
    """Stores a notice to be posted to a channel at a future time. Returns the new notice's id."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO scheduled_notices (guild_id, channel_id, author_id, message, scheduled_time) VALUES (?, ?, ?, ?, ?)",
            (guild_id, channel_id, author_id, message, scheduled_time.isoformat())
        )
        conn.commit()
        return cursor.lastrowid

def get_due_notices(now: datetime) -> list:
    """Returns all unsent notices whose scheduled_time has passed."""
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM scheduled_notices WHERE sent = 0 AND scheduled_time <= ?",
            (now.isoformat(),)
        ).fetchall()
        return [dict(row) for row in rows]

def mark_notice_sent(notice_id: int):
    """Marks a scheduled notice as delivered so it is not sent again."""
    with get_db_connection() as conn:
        conn.execute("UPDATE scheduled_notices SET sent = 1 WHERE id = ?", (notice_id,))
        conn.commit()
