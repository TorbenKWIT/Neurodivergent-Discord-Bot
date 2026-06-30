import discord
from discord.ext import commands
from discord import app_commands
import re
import tone_data
import ai_helper
import config

class Tones(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Define the slash command group /tone
    tone_group = app_commands.Group(name="tone", description="Tone indicator commands")

    @tone_group.command(name="lookup", description="Look up the meaning of a specific tone indicator (e.g. j)")
    @app_commands.describe(indicator="The indicator letter(s), e.g., j, srs, lh")
    async def lookup(self, interaction: discord.Interaction, indicator: str):
        # Normalize: strip spaces, lowercase, and remove leading slash if typed
        clean_indicator = indicator.strip().lower().lstrip('/')
        
        if clean_indicator in tone_data.TONE_INDICATORS:
            data = tone_data.TONE_INDICATORS[clean_indicator]
            embed = discord.Embed(
                title=f"Tone Indicator: /{clean_indicator}",
                color=config.COLOR_TONE
            )
            embed.add_field(name="Name", value=data["name"], inline=False)
            embed.add_field(name="Description", value=data["description"], inline=False)
            embed.add_field(name="Example", value=f"*{data['example']}*", inline=False)
            embed.set_footer(text="Help make conversations clearer!")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"Sorry, I couldn't find the tone indicator `/{clean_indicator}`. Use `/tone list` to see all supported ones.",
                ephemeral=True
            )

    @tone_group.command(name="list", description="Display all supported tone indicators")
    async def list_tones(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Standard Tone Indicators List",
            description="Tone indicators are appended to the end of messages to clarify the writer's emotional intent.",
            color=config.COLOR_TONE
        )
        
        # Sort keys alphabetically
        sorted_keys = sorted(tone_data.TONE_INDICATORS.keys())
        
        # Format the list cleanly
        indicators_str = ""
        for key in sorted_keys:
            name = tone_data.TONE_INDICATORS[key]["name"]
            indicators_str += f"`/{key}`: **{name}**\n"
            
        embed.add_field(name="Supported Indicators", value=indicators_str, inline=False)
        embed.set_footer(text="Use /tone lookup <indicator> for detailed explanations and examples.")
        await interaction.response.send_message(embed=embed)

    @tone_group.command(name="suggest", description="Uses Gemini AI to suggest a tone indicator for a message")
    @app_commands.describe(message="The text of the message you want to analyze")
    async def suggest(self, interaction: discord.Interaction, message: str):
        if not message.strip():
            await interaction.response.send_message("Please provide a message to analyze.", ephemeral=True)
            return

        # Defer response since AI request takes some time
        await interaction.response.defer(ephemeral=True)
        
        suggestions = await ai_helper.suggest_tone_indicator(message)
        
        # Format suggestions directly in the description to support up to 4096 characters (avoiding the 1024-character field value limit)
        description_text = f"Based on your message:\n*\"{message}\"*\n\n**AI Recommendations:**\n{suggestions}"
        if len(description_text) > 4000:
            description_text = description_text[:3997] + "..."

        embed = discord.Embed(
            title="Suggested Tone Indicators",
            description=description_text,
            color=config.COLOR_TONE
        )
        embed.set_footer(text="Note: AI suggestions are guides; use the indicator that best matches your true intent.")
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tones(bot))
    bot.tree.add_command(explain_tone_indicators_context)

# Context menu to scan a message and explain tone indicators inside it.
# Defined at module level because discord.py does not allow context menus
# to be defined as methods inside a Cog class; it must be added to the
# tree manually (see setup() above).
@app_commands.context_menu(name="Explain Tone Indicators")
async def explain_tone_indicators_context(interaction: discord.Interaction, message: discord.Message):
    content = message.content
    if not content:
        await interaction.response.send_message(
            "Cannot scan an empty message or a system message.",
            ephemeral=True
        )
        return

    # Find words starting with /
    words = re.findall(r'/([a-zA-Z]+)', content)

    found_indicators = []
    for word in words:
        clean_word = word.lower()
        if clean_word in tone_data.TONE_INDICATORS:
            # De-duplicate
            if clean_word not in [ind[0] for ind in found_indicators]:
                found_indicators.append((clean_word, tone_data.TONE_INDICATORS[clean_word]))

    if not found_indicators:
        await interaction.response.send_message(
            "No standard tone indicators (like `/j` or `/srs`) were detected in that message.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Tone Indicators Explained",
        description="Definitions for indicators found in the message:",
        color=config.COLOR_TONE
    )

    for key, data in found_indicators:
        embed.add_field(
            name=f"/{key} ({data['name']})",
            value=f"{data['description']}\n*Example: {data['example']}*",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)
