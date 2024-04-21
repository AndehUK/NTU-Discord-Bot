from __future__ import annotations

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING, Union

import discord
from discord import app_commands

from utils.cog import Cog
from utils.enums import Channels, Colours, Roles

if TYPE_CHECKING:
    from bot import DevSocBot


class General(Cog):
    statuses: Dict[str, str] = {
        "online": "Online",
        "offline": "Offline",
        "idle": "Idle",
        "dnd": "Do Not Disturb",
        "invisible": "Invisible",
    }

    async def _count_members(
        self, itr: discord.Interaction[DevSocBot], role_tuples: List[Tuple[str, int]]
    ) -> List[Tuple[str, str]]:
        assert itr.guild
        await itr.response.defer()

        role_counts: List[Tuple[str, str]] = []
        for role_name, role_id in role_tuples:
            role = itr.guild.get_role(role_id)
            member_count = (
                len(role.members) if role else f"Failed to retrieve {role_name} role"
            )
            role_counts.append((role_name, str(member_count)))

        return role_counts

    @app_commands.command(name="help", description="Show the General help menu")
    @app_commands.guild_only()
    async def admin_help(self, itr: discord.Interaction[DevSocBot]) -> None:
        cog = itr.client.get_cog("General")

        if not cog:
            # This shouldn't ever trigger, but just in case
            return await itr.response.send_message(
                "The General cog is not loaded.", ephemeral=True
            )

        embed = discord.Embed(
            title="General Commands",
            description="*This dialog gives you all the general commands for DevBot.*",
            color=Colours.YELLOW,
        )

        for command in cog.walk_app_commands():
            name = (
                f"/{command.name}"
                if not command.parent
                else f"/{command.parent.name} {command.name}"
            )
            embed.add_field(
                name=name,
                value=f"```{command.description}```",
                inline=False,
            )

        await itr.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="whois", description="Get information about a user.")
    @app_commands.guild_only()
    async def whois(
        self,
        itr: discord.Interaction[DevSocBot],
        user: Optional[Union[discord.User, discord.Member]] = None,
    ) -> None:
        await itr.response.defer()
        member = user or itr.user

        embed = discord.Embed(colour=Colours.YELLOW)
        embed.set_author(
            name=str(member),
            icon_url=member.display_avatar.url,
            url=f"https://discord.com/users/{member.id}",
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        nickname = (
            "None"
            if isinstance(member, discord.User) or not member.nick
            else member.nick
        )
        status = (
            self.statuses.get(str(member.status), "Unknown")
            if isinstance(member, discord.Member)
            else "Unknown"
        )
        joined_at = (
            "User not in Server"
            if not isinstance(member, discord.Member)
            else (
                discord.utils.format_dt(member.joined_at)
                if member.joined_at
                else "Unknown"
            )
        )
        joined_discord = discord.utils.format_dt(member.created_at)
        user_roles = (
            ", ".join([r.mention for r in member.roles[1:]])
            if isinstance(member, discord.Member)
            else "User not in Server"
        )

        embed.add_field(name="Nickname", value=nickname, inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Joined Server", value=joined_at, inline=True)
        embed.add_field(name="Joined Discord", value=joined_discord, inline=True)
        embed.add_field(name="Roles", value=user_roles, inline=False)
        embed.set_footer(text=f"ID: {member.id}")

        await itr.followup.send(embed=embed)

    @app_commands.command(name="source", description="Get the source code for the bot.")
    @app_commands.guild_only()
    async def get_source(self, itr: discord.Interaction[DevSocBot]) -> None:
        embed = discord.Embed(
            title="Here is a link to the bot's source code",
            url="https://github.com/NTUDevSoc/Discord-Bot",
            colour=Colours.YELLOW,
        )
        embed.set_author(
            name="Discord Bot Source Code",
            icon_url="https://i.imgur.com/NhVjX8S.png",
            url="https://github.com/NTUDevSoc",
        )
        embed.set_footer(text=f"V2 Rewrite developed by Andrew")

        await itr.response.send_message(embed=embed)

    @app_commands.command(
        name="socials",
        description="Get the social media links for DevSoc.",
    )
    @app_commands.guild_only()
    async def socials(self, itr: discord.Interaction[DevSocBot]) -> None:
        embed = discord.Embed(
            title="DevSoc Social Links",
            description="Here are all the links to official DevSoc Social Media pages",
            colour=Colours.YELLOW,
        )
        embed.set_thumbnail(url="https://i.imgur.com/NhVjX8S.png")
        embed.add_field(
            name="Twitter", value="https://twitter.com/devsoc", inline=False
        )
        embed.add_field(
            name="Facebook", value="https://facebook.com/devsoc", inline=False
        )
        embed.add_field(
            name="Instagram", value="https://instagram.com/ntudevsoc", inline=False
        )

        await itr.response.send_message(embed=embed)

    members = app_commands.Group(
        name="members",
        description="Get the number of members in certain categories within the server.",
        guild_only=True,
    )

    @members.command(
        name="year-groups",
        description="Get the number of members in each year group in the server.",
    )
    @app_commands.guild_only()
    async def members_year_count(self, itr: discord.Interaction[DevSocBot]) -> None:
        role_tuples: List[Tuple[str, int]] = [
            ("First Year", Roles.FIRST_YEAR),
            ("Second Year", Roles.SECOND_YEAR),
            ("Placement Year", Roles.PLACEMENT_YEAR),
            ("Third Year", Roles.THIRD_YEAR),
            ("Fourth Year", Roles.FOURTH_YEAR),
            ("MSc Student", Roles.MSC_STUDENT),
            ("Alumni", Roles.ALUMNI),
        ]

        role_counts = await self._count_members(itr, role_tuples)
        final_year_count = sum(
            int(count) for _, count in role_counts if count.isdigit()
        )

        embed = discord.Embed(
            title="DevSoc Members | Year Groups",
            description="*Here are the members of each year group within this server.*",
            colour=discord.Colour.yellow(),
        )
        for role_name, count in role_counts:
            embed.add_field(name=role_name, value=f"{count} members", inline=True)
        embed.add_field(
            name="Third/Final Year", value=f"{final_year_count} members", inline=True
        )

        await itr.followup.send(embed=embed)

    @members.command(
        name="courses",
        description="Get the number of members in each course in the server.",
    )
    @app_commands.guild_only()
    async def members_course_count(self, itr: discord.Interaction[DevSocBot]) -> None:
        role_tuples: List[Tuple[str, int]] = [
            ("Computer Science", Roles.COMPUTER_SCIENCE),
            ("Software Engineering", Roles.SOFTWARE_ENGINEERING),
            ("Games Technology", Roles.GAMES_TECHNOLOGY),
            ("Artificial Intelligence", Roles.ARTIFICIAL_INTELLIGENCE),
            ("Cyber Security", Roles.CYBER_SECURITY),
            ("Computing", Roles.COMPUTING),
            ("Other", Roles.OTHER),
        ]

        role_counts = await self._count_members(itr, role_tuples)

        embed = discord.Embed(
            title="DevSoc Members | Courses",
            description="*Here are the members of each course within this server.*",
            colour=discord.Colour.yellow(),
        )
        for role_name, count in role_counts:
            embed.add_field(name=role_name, value=f"{count} members", inline=True)

        await itr.followup.send(embed=embed)

    @Cog.listener("on_member_join")
    async def welcome_member(self, member: discord.Member) -> None:
        err_prefix = "[General.on_member_join]"
        role = member.guild.get_role(Roles.ANNOUNCEMENT)
        if not role:
            self.bot.logger.critical(f"{err_prefix} Failed to find announcement role!")
            return
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            self.bot.logger.critical(
                f"{err_prefix} I don't have permission to add the announcement role!"
            )
            return

        arrival_channel = member.guild.get_channel(Channels.ARRIVALS)
        if not isinstance(arrival_channel, discord.TextChannel):
            self.bot.logger.critical(
                f"{err_prefix} Failed to find valid arrivals channel!"
            )
            return
        role_channel = member.guild.get_channel(Channels.ROLE_CHANNEL)
        if not isinstance(role_channel, discord.TextChannel):
            self.bot.logger.critical(f"{err_prefix} Failed to find valid role channel!")
            return
        rules_channel = member.guild.get_channel(Channels.RULES_CHANNEL)
        if not isinstance(rules_channel, discord.TextChannel):
            self.bot.logger.critical(
                f"{err_prefix} Failed to find valid rules channel!"
            )
            return

        await arrival_channel.send(
            f"Welcome {member.mention}! Head to {rules_channel.mention} to accept our "
            f"server rules, then head to {role_channel.mention} to set your roles using "
            "the Role Menu and access the rest of the server.",
        )
        embed = discord.Embed(
            title="Welcome to DevSoc!",
            description=(
                f"**Make sure to read and accept the [rules]({rules_channel.jump_url}) then "
                f"head to [self-roles]({role_channel.jump_url}) to set your roles!**"
            ),
            colour=Colours.YELLOW,
        )
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            self.bot.logger.debug(
                f"{err_prefix} Failed to DM {member} with welcome message! (DMs Closed)"
            )


async def setup(bot: DevSocBot) -> None:
    await bot.add_cog(General(bot))
