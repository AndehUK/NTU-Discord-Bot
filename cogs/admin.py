from __future__ import annotations

import io
from typing import List, TYPE_CHECKING

import discord
from discord import app_commands

from utils.cog import Cog

if TYPE_CHECKING:
    from bot import DevSocBot


class Admin(Cog):
    @app_commands.command(
        name="unassigned",
        description="Checks for members that do not have a required role",
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def unassigned_check(self, itr: discord.Interaction[DevSocBot]) -> None:
        try:
            # We can safely assert here because we are using the guild_only decorator
            assert itr.guild

            roleless_members: List[str] = []
            announcement_role = itr.guild.get_role(668158580716732456)
            if not announcement_role:
                await itr.response.send_message(
                    "ERROR: `Announcement role not found`", ephemeral=True
                )
                return

            # Defer the interaction response because this could take longer than 3 seconds.
            await itr.response.defer()

            for member in itr.guild.members:
                if len(member.roles) == 1 or (
                    len(member.roles) == 2 and announcement_role in member.roles
                ):
                    member_string = (
                        f"{member.nick or member.display_name} ({member.name})"
                    )
                    roleless_members.append(member_string)

            if not len(roleless_members):
                await itr.followup.send(
                    "All members have a role on the server.", ephemeral=True
                )
                return

            # Create a file with the list of members without a role
            bytes_data = "\n".join(roleless_members).encode("utf-8")
            bytes_io = io.BytesIO(bytes_data)
            file = discord.File(fp=bytes_io, filename="results.txt")

            await itr.followup.send(
                f"There are {len(roleless_members)} members without a role on the server. "
                "Here are the members without roles:",
                file=file,
            )
        except Exception as e:
            await itr.followup.send(str(e), ephemeral=True)


async def setup(bot: DevSocBot) -> None:
    await bot.add_cog(Admin(bot))
