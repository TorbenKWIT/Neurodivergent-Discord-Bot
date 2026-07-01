import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
import database
import config

class Notices(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_due_notices.start()

    def cog_unload(self):
        self.check_due_notices.cancel()

    @app_commands.command(name="create-notice", description="Schedule an announcement to be posted in this channel at a future date/time")
    @app_commands.describe(
        date="Date to post on, formatted MM/DD/YYYY (e.g. 07/04/2026)",
        time="Time to post at (24-hour, bot server time), formatted HH:MM (e.g. 18:30)",
        message="The announcement text"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def create_notice(self, interaction: discord.Interaction, date: str, time: str, message: str):
        if not message.strip():
            await interaction.response.send_message("Please provide a message to announce.", ephemeral=True)
            return

        try:
            scheduled_time = datetime.strptime(f"{date} {time}", "%m/%d/%Y %H:%M")
        except ValueError:
            await interaction.response.send_message(
                "Couldn't parse that date/time. Please use `MM/DD/YYYY` for the date and `HH:MM` (24-hour) for the time, "
                "e.g. `/create-notice 07/04/2026 18:30 Club meeting tonight!`.",
                ephemeral=True
            )
            return

        if scheduled_time <= datetime.now():
            await interaction.response.send_message("That date/time is in the past. Please schedule it for a future time.", ephemeral=True)
            return

        database.create_scheduled_notice(
            guild_id=interaction.guild_id,
            channel_id=interaction.channel_id,
            author_id=interaction.user.id,
            message=message,
            scheduled_time=scheduled_time
        )

        embed = discord.Embed(
            title="Notice Scheduled",
            description=message,
            color=config.COLOR_NOTICE
        )
        embed.add_field(
            name="Will be posted",
            value=f"<t:{int(scheduled_time.timestamp())}:F> in {interaction.channel.mention}"
        )
        embed.set_footer(text=f"Scheduled by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @create_notice.error
    async def create_notice_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You need the **Manage Messages** permission to schedule announcements.",
                ephemeral=True
            )
        else:
            print(f"Error in /create-notice: {error}")
            if interaction.response.is_done():
                await interaction.followup.send("Something went wrong while scheduling that notice.", ephemeral=True)
            else:
                await interaction.response.send_message("Something went wrong while scheduling that notice.", ephemeral=True)

    @tasks.loop(seconds=30)
    async def check_due_notices(self):
        due_notices = database.get_due_notices(datetime.now())
        for notice in due_notices:
            try:
                channel = self.bot.get_channel(notice["channel_id"])
                if channel is None:
                    channel = await self.bot.fetch_channel(notice["channel_id"])

                embed = discord.Embed(
                    title="\U0001F4E2 Club Notice",
                    description=notice["message"],
                    color=config.COLOR_NOTICE
                )
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Failed to deliver scheduled notice {notice['id']}: {e}")
            finally:
                # Mark as sent even on failure (e.g. deleted channel) to avoid retry loops
                database.mark_notice_sent(notice["id"])

    @check_due_notices.before_loop
    async def before_check_due_notices(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Notices(bot))
