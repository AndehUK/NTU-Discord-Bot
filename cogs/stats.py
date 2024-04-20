from __future__ import annotations

from datetime import timedelta
from typing import List, TYPE_CHECKING

import discord
from discord import app_commands

from utils.cog import Cog

if TYPE_CHECKING:
    from bot import DevSocBot


class Stats(Cog):
    @app_commands.command(name="room", description="Update the DevSoc room status")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id))
    async def room(self, itr: discord.Interaction[DevSocBot], status: str) -> None:
        assert itr.guild

        if status.lower() not in ["open", "closed"]:
            return await itr.response.send_message(
                "**ERROR:** The status must be either `open` or `closed`. "
                "Please use the autocomplete menu provided with this command.",
                ephemeral=True,
            )

        room_channel = itr.guild.get_channel(1228116411172393022)
        if not room_channel:
            return await itr.response.send_message(
                "**ERROR:** The room channel was not found. Please contact an administrator.",
                ephemeral=True,
            )

        await itr.response.defer()

        await room_channel.edit(name=f"DevSoc Room: {status.title()}")
        await itr.followup.send(f"Updated DevSoc Room status to: {status.title()}!")

    @room.autocomplete(name="status")
    async def room_autocomplete(
        self, itr: discord.Interaction[DevSocBot], current: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=status.title(), value=status)
            for status in ["open", "closed"]
            if current.lower() in status
        ]

    @room.error
    async def on_room_error(
        self, itr: discord.Interaction[DevSocBot], error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            dt = discord.utils.utcnow() + timedelta(seconds=error.retry_after)
            dt_fmt = discord.utils.format_dt(dt, style="R")
            await itr.response.send_message(
                f"**This command is on cooldown, you can run this command again {dt_fmt}**",
                ephemeral=True,
            )


async def setup(bot: DevSocBot) -> None:
    await bot.add_cog(Stats(bot))
