import discord
from discord.ext import commands
from discord import app_commands
import database
import ai_helper
import config

class Readability(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="simplify", description="Simplify and reformat any text you paste")
    @app_commands.describe(text="The long text or wall-of-text you want to make readable")
    async def simplify(self, interaction: discord.Interaction, text: str):
        if not text.strip():
            await interaction.response.send_message("Please provide some text to simplify.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        simplified = await ai_helper.reformat_readability(text)
        
        embed = discord.Embed(
            title="Simplified Readability",
            description=simplified,
            color=config.COLOR_READABILITY
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="readability_delivery", description="Choose where the bot delivers your simplified text when reacting to a message")
    @app_commands.choices(method=[
        app_commands.Choice(name="Direct Message (DM)", value="dm"),
        app_commands.Choice(name="Public Thread", value="thread")
    ])
    async def delivery_preference(self, interaction: discord.Interaction, method: app_commands.Choice[str]):
        database.set_user_delivery_pref(interaction.user.id, method.value)
        await interaction.response.send_message(
            f"Your readability preference has been updated. I will now deliver simplified text via **{method.name}**.",
            ephemeral=True
        )

    # Event: Automatic Emoji Trigger for long messages
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages to avoid self-triggers or spam
        if message.author.bot:
            return

        # React to messages longer than 500 characters
        if len(message.content) > 500:
            try:
                await message.add_reaction("📖")
            except Exception as e:
                print(f"Error adding reaction to long message: {e}")

    # Event: Reacting with 📖 emoji triggers the readability flow
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Only trigger on the book emoji
        if payload.emoji.name != "📖":
            return
            
        # Ignore reactions from the bot itself
        if payload.user_id == self.bot.user.id:
            return

        # Fetch channel and message
        try:
            channel = self.bot.get_channel(payload.channel_id)
            if not channel:
                channel = await self.bot.fetch_channel(payload.channel_id)
                
            message = await channel.fetch_message(payload.message_id)
            
            # Skip if message has no content to simplify
            if not message.content or not message.content.strip():
                return
                
            user = self.bot.get_user(payload.user_id)
            if not user:
                user = await self.bot.fetch_user(payload.user_id)

            # Get user delivery preference from db
            pref = database.get_user_delivery_pref(user.id)
            
            # Reformat the message content
            formatted_text = await ai_helper.reformat_readability(message.content)
            
            embed = discord.Embed(
                title="Simplified Readability Helper",
                description=formatted_text,
                color=config.COLOR_READABILITY
            )
            embed.set_footer(text=f"Original message by {message.author.display_name} in #{channel.name}")
            
            if pref == "dm":
                try:
                    await user.send(embed=embed)
                except discord.Forbidden:
                    # If DM fails, fall back to public thread in the channel
                    await self._deliver_via_thread(channel, message, user, embed)
            else:
                # Delivery via Thread preferred
                await self._deliver_via_thread(channel, message, user, embed)
                
        except Exception as e:
            print(f"Error handling readability reaction: {e}")

    async def _deliver_via_thread(self, channel, message, user, embed):
        """Helper to create a thread and send the readability embed."""
        if hasattr(channel, "create_thread"):
            try:
                # Create a public thread under the original message
                thread = await message.create_thread(
                    name=f"Readability for {user.display_name}",
                    auto_archive_duration=60
                )
                await thread.send(f"{user.mention}, here is your readable version:", embed=embed)
            except Exception as e:
                print(f"Failed to create readability thread: {e}")
        else:
            # Fallback to public reply in the channel if thread creation is not possible
            try:
                await message.reply(
                    content=f"{user.mention}, I couldn't DM you or create a thread. Here is the simplified text:",
                    embed=embed,
                    delete_after=120  # Delete after 2 minutes to keep channel clean
                )
            except Exception as e:
                print(f"Failed to send fallback reply: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Readability(bot))
    bot.tree.add_command(format_readability_context)
    bot.tree.add_command(summarize_context)

# Context menus are defined at module level because discord.py does not
# allow context menus to be defined as methods inside a Cog class; they
# must be added to the tree manually (see setup() above).
@app_commands.context_menu(name="Format Readability")
async def format_readability_context(interaction: discord.Interaction, message: discord.Message):
    if not message.content or not message.content.strip():
        await interaction.response.send_message("Cannot format an empty message.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    formatted = await ai_helper.reformat_readability(message.content)

    embed = discord.Embed(
        title="Formatted for Readability",
        description=formatted,
        color=config.COLOR_READABILITY
    )
    await interaction.followup.send(embed=embed)

@app_commands.context_menu(name="Summarize Text")
async def summarize_context(interaction: discord.Interaction, message: discord.Message):
    if not message.content or not message.content.strip():
        await interaction.response.send_message("Cannot summarize an empty message.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    summary = await ai_helper.summarize_text(message.content)

    embed = discord.Embed(
        title="Message Summary",
        description=summary,
        color=config.COLOR_READABILITY
    )
    await interaction.followup.send(embed=embed)
