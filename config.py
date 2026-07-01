import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATABASE_PATH = "neurodivergent_bot.db"

# Color theme for the bot's Rich Embeds (low-sensory pastels)
COLOR_TONE = 0xD1C4E9      # Soft lavender
COLOR_ADHD = 0xB2DFDB      # Soft teal
COLOR_READABILITY = 0xC8E6C9 # Soft mint green
COLOR_NOTICE = 0xFFE0B2     # Soft peach
