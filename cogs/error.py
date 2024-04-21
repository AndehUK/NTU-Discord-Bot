from __future__ import annotations

import sys
from datetime import timedelta
from typing import Any, TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.cog import Cog
from utils.enums import Channels, Colours

if TYPE_CHECKING:
    from bot import DevSocBot


class ErrorHandler(Cog):
    async def respond(
        self,
        itr: discord.Interaction[DevSocBot],
        content: str = discord.utils.MISSING,
        embed: discord.Embed = discord.utils.MISSING,
    ) -> None:
        if itr.response.is_done():
            return await itr.followup.send(content, embed=embed, ephemeral=True)
        return await itr.response.send_message(content, embed=embed, ephemeral=True)

    @Cog.listener("on_app_command_error")
    async def on_app_command_error(
        self, itr: discord.Interaction[DevSocBot], error: app_commands.AppCommandError
    ) -> None:
        if hasattr(itr.command, "on_error"):
            return

        if isinstance(error, app_commands.CommandOnCooldown):
            dt = discord.utils.utcnow() + timedelta(seconds=error.retry_after)
            dt_fmt = discord.utils.format_dt(dt, style="R")
            await self.respond(
                itr,
                f"**This command is on cooldown, you can run this command again {dt_fmt}**",
            )
        elif isinstance(error, app_commands.MissingPermissions):
            # Provide user with list of permissions they need
            missing_perms = "\n ".join([f"- {mp}" for mp in error.missing_permissions])
            await self.respond(
                itr,
                "**ERROR:** You are missing the required permissions to run this command."
                f"\n{missing_perms}",
            )
        elif isinstance(error, app_commands.CheckFailure):
            await self.respond(
                itr, "**ERROR:** You failed the checks to run this command."
            )
        else:
            self.bot.logger.error(
                f"Ignoring exception in command {itr.command}: "
                f"{type(error)}: {error}\n{error.__traceback__}"
            )

    @Cog.listener("on_command_error")
    async def on_command_error(
        self, ctx: commands.Context[DevSocBot], error: commands.CommandError
    ) -> None:
        """
        This event is triggered whenever an error occurs during a message command.
        """
        if hasattr(ctx.command, "on_error"):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.")
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass

        else:
            self.bot.logger.error(
                f"Ignoring exception in command {ctx.command}: "
                f"{type(error)}: {error}\n{error.__traceback__}"
            )

    @Cog.listener("on_error")
    async def on_error(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        This event is triggered whenever an error occurs outside of a command.
        """
        _, error, _ = sys.exc_info()
        if not error:
            raise

        embed = discord.Embed(
            title="An error occurred!",
            description=f"## Event\n`{event}`\n```py\n{error}\n```",
            colour=Colours.RED,
        )

        channel = self.bot.get_channel(Channels.BOT_LOGS)
        if not isinstance(channel, discord.TextChannel):
            self.bot.logger.critical(
                "Bot logs channel is not an instance of discord.TextChannel"
            )
            return
        await channel.send(embed=embed)

        return await self.bot.on_error(event, *args, **kwargs)


async def setup(bot: DevSocBot) -> None:
    await bot.add_cog(ErrorHandler(bot))
