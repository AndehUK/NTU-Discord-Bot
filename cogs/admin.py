from __future__ import annotations

import io
from typing import List, TYPE_CHECKING, Union

import discord
from discord import app_commands

from utils.cog import Cog
from utils.enums import Colours
from utils.types import GUILD_MESSAGEABLE

if TYPE_CHECKING:
    from bot import DevSocBot


class Admin(Cog):
    @app_commands.command(name="adminhelp", description="Show the admin help menu")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def admin_help(self, itr: discord.Interaction[DevSocBot]) -> None:
        cog = itr.client.get_cog("Admin")

        if not cog:
            # This shouldn't ever trigger, but just in case
            return await itr.response.send_message(
                "The Admin cog is not loaded.", ephemeral=True
            )

        embed = discord.Embed(
            title="Admin Commands",
            description="*This dialog gives you all the admin commands for DevBot.*",
            color=Colours.YELLOW,
        )

        for command in cog.walk_app_commands():
            embed.add_field(
                name=f"/{command.name}",
                value=f"```{command.description}```",
                inline=False,
            )

        await itr.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="mute", description="Mute a member in the server")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def mute_member(
        self,
        itr: discord.Interaction[DevSocBot],
        member: Union[discord.Member, discord.User],
    ) -> None:
        # We can safely assert here because we are using the guild_only decorator
        assert itr.guild

        if not isinstance(member, discord.Member):
            return await itr.response.send_message(
                f"**ERROR:** {member.mention} ({member}) is not in this server.",
                ephemeral=True,
            )

        await itr.response.defer()

        # TODO: Replace role IDs with actual values
        servermute_role = itr.guild.get_role(123)
        devsoc_role = itr.guild.get_role(123)
        booster_role = itr.guild.get_role(123)

        if not servermute_role:
            return await itr.followup.send(
                "**ERROR:** Server mute role not found", ephemeral=True
            )
        if not devsoc_role:
            return await itr.followup.send(
                "**ERROR:** DevSoc role not found", ephemeral=True
            )
        if not booster_role:
            return await itr.followup.send(
                "**ERROR:** Booster role not found", ephemeral=True
            )

        if servermute_role in member.roles:
            await member.remove_roles(servermute_role)
            await member.add_roles(devsoc_role)
            await itr.followup.send(f"Unmuted {member.mention} ({member})!")
        else:
            roles_to_remove = [r for r in member.roles[1:] if r.id != booster_role.id]
            await member.remove_roles(*roles_to_remove)
            await member.add_roles(servermute_role)
            await itr.followup.send(f"Muted {member.mention} ({member})!")

    @app_commands.command(
        name="clear",
        description="Clears a specified number of messages from the channel",
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def clear(
        self,
        itr: discord.Interaction[DevSocBot],
        amount: app_commands.Range[int, 1, 24],
    ) -> None:
        if not isinstance(itr.channel, GUILD_MESSAGEABLE):
            return await itr.response.send_message(
                "This command cannot be used in this channel.", ephemeral=True
            )

        await itr.response.defer(ephemeral=True)

        try:
            messages = await itr.channel.purge(limit=amount)
            embed = discord.Embed(
                title="Chat Cleared",
                description=(
                    f"{len(messages)} messages cleared from {itr.channel.mention}!\n"
                    f"{discord.utils.format_dt(discord.utils.utcnow(), 'R')}"
                ),
                color=Colours.YELLOW,
            )
            for message in messages:
                embed.add_field(
                    name=message.author.display_name,
                    value="Embedded Message" if message.embeds else message.content,
                    inline=False,
                )
            await itr.followup.send(embed=embed)
            # TODO: Send a log to bot log channel
        except Exception as e:
            return await itr.followup.send(
                f"An error occurred while trying to clear messages: {e}",
                ephemeral=True,
            )

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
                    "**ERROR:** Announcement role not found", ephemeral=True
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
