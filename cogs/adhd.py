import discord
from discord.ext import commands
from discord import app_commands
import ai_helper
import config

class ADHD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="breakdown", description="Split a large, intimidating task into small actionable steps using Gemini AI")
    @app_commands.describe(task="The task you want to break down (e.g. cleaning my room, writing a paper)")
    async def breakdown(self, interaction: discord.Interaction, task: str):
        if not task.strip():
            await interaction.response.send_message("Please provide a task to break down.", ephemeral=True)
            return

        # Defer because AI takes a moment to think
        await interaction.response.defer(ephemeral=True)
        
        breakdown_text = await ai_helper.get_task_breakdown(task)
        
        # Format breakdown text directly into the description to support up to 4096 characters (avoiding the 1024-character field value limit)
        description_text = f"Here is a step-by-step breakdown for **{task}** to help you get started:\n\n{breakdown_text}"
        if len(description_text) > 4000:
            description_text = description_text[:3997] + "..."

        embed = discord.Embed(
            title="Task Breakdown",
            description=description_text,
            color=config.COLOR_ADHD
        )
        embed.set_footer(text="Take it one step at a time. You've got this!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ADHD(bot))
