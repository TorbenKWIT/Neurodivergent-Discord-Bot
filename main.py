import discord
from discord.ext import commands
import config
import database

class NeuroBot(commands.Bot):
    def __init__(self):
        # Configure the required gateway intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Initialize database tables
        database.init_db()
        print("Database initialized.")

        # Load our features cogs
        cogs = ["cogs.tones", "cogs.adhd", "cogs.readability", "cogs.notices"]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded extension: {cog}")
            except Exception as e:
                print(f"Failed to load extension {cog}: {e}")

        # Sync the command tree globally (makes slash commands and context menus available in all servers)
        print("Syncing slash commands globally...")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} application commands globally.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_ready(self):
        print(f"\n--- Logged in as {self.user.name}#{self.user.discriminator} (ID: {self.user.id}) ---")
        print("Neurodivergent Discord Bot is active and listening for interactions!")

def main():
    if not config.DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN is missing. Please set it in your .env file.")
        return

    # Instantiating and running the bot
    bot = NeuroBot()
    
    try:
        bot.run(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        print("Error: Invalid DISCORD_TOKEN. Please verify your token in the .env file.")
    except Exception as e:
        print(f"An unexpected error occurred while starting the bot: {e}")

if __name__ == "__main__":
    main()
