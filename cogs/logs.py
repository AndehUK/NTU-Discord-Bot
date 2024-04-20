from __future__ import annotations

from typing import Optional

import discord

from utils.cog import Cog
from utils.enums import Channels
from utils.types import GUILD_MESSAGEABLE


class Logs(Cog):
    def get_message_content(self, message: discord.Message) -> str:
        return "No Content" if not message.content else message.content

    def handle_message_event(
        self, message: discord.Message, before: Optional[discord.Message] = None
    ) -> Optional[discord.Embed]:
        if not isinstance(message.channel, GUILD_MESSAGEABLE):
            return

        current_dt = discord.utils.format_dt(discord.utils.utcnow(), style="R")
        action = "Edited" if before else "Deleted"

        embed = discord.Embed(
            title=f"Message {action}",
            description=(
                f"**Message Author:** {message.author.mention} ({message.author})\n"
                f"**{action}:** {current_dt}\n"
                f"**Channel:** {message.channel.mention}"
                + (f"\n\n[`Go to message`]({message.jump_url})" if before else "")
            ),
            colour=0xE7EC11 if before else 0xE80202,
        )

        if message.content:
            if message.reference and isinstance(
                message.reference.resolved, discord.Message
            ):
                embed.add_field(
                    name=f"Replying to: {message.reference.resolved.author}'s message",
                    value=self.get_message_content(message.reference.resolved),
                    inline=False,
                )

        if before:
            embed.add_field(
                name="Message Before",
                value=self.get_message_content(before),
                inline=False,
            )
            embed.add_field(
                name="Message After",
                value=self.get_message_content(message),
                inline=False,
            )
        else:
            embed.add_field(
                name="Message Content",
                value=self.get_message_content(message),
                inline=False,
            )

        if message.embeds:
            embed.add_field(
                name="Total Embeds",
                value=str(len(message.embeds)),
            )

        if message.attachments:
            file_names = "\n".join(
                [f"[{a.filename}]({a.url})" for a in message.attachments]
            )

            embed.add_field(
                name=f"Total Attachments ({str(len(message.attachments))})",
                value=file_names,
            )

            pic_ext = [".jpg", ".png", ".jpeg", ".gif"]
            for a in message.attachments:
                if a.filename.endswith(tuple(pic_ext)):
                    embed.set_image(url=a.url)
                    break

        return embed

    async def send_log(self, embed: discord.Embed) -> None:
        channel = self.bot.get_channel(Channels.BOT_LOGS.value)
        if not isinstance(channel, GUILD_MESSAGEABLE):
            self.bot.logger.critical("Failed to get bot logs channel for logging")
            return

        await channel.send(embed=embed)

    @Cog.listener("on_member_join")
    async def log_join(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Member Joined",
            description=(
                f"### Member: {member.display_name} ({member.name})\n"
                f"### Mention: {member.mention}"
            ),
            color=0xF4A701,
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        joined_at = discord.utils.utcnow() if not member.joined_at else member.joined_at

        embed.add_field(
            name="Joined Server",
            value=discord.utils.format_dt(joined_at, style="R"),
        )
        embed.add_field(
            name="Joined Discord",
            value=discord.utils.format_dt(member.created_at, style="R"),
        )
        embed.set_footer(text=f"ID: {member.id}")

        await self.send_log(embed)

    @Cog.listener("on_member_remove")
    async def log_remove(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Member Left",
            description=(
                f"### Member: {member.display_name} ({member.name})\n"
                f"### Mention: {member.mention}"
            ),
            colour=0xF4A701,
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        removed_at = discord.utils.format_dt(discord.utils.utcnow(), style="R")

        embed.add_field(name="Left at", value=removed_at)
        embed.set_footer(text=f"ID: {member.id}")

        await self.send_log(embed)

    @Cog.listener("on_message_delete")
    async def log_deleted_message(self, message: discord.Message) -> None:
        embed = self.handle_message_event(message)

        if embed:
            await self.send_log(embed)

    @Cog.listener("on_message_edit")
    async def log_edited_message(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        if before.content == after.content:
            return

        embed = self.handle_message_event(after, before)

        if embed:
            await self.send_log(embed)
