from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discord
from discord import app_commands

from utils.cog import Cog
from utils.data import get_rules, set_message_data
from .views import RulesView

if TYPE_CHECKING:
    from bot import DevSocBot


class Rules(Cog):
    @app_commands.command(name="rules", description="Sends the rules of the server")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def send_rules(
        self,
        itr: discord.Interaction[DevSocBot],
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        assert itr.guild
        await itr.response.defer(ephemeral=True)

        channel = channel or (
            itr.channel if isinstance(itr.channel, discord.TextChannel) else None
        )

        if not channel:
            await itr.followup.send("Please provide a valid channel", ephemeral=True)
            return

        image = discord.File("docs/devsocrules.png", filename="rules.png")

        try:
            await channel.send(file=image)
        except discord.Forbidden:
            await itr.followup.send(
                f"I don't have permission to send messages in {channel.mention}",
                ephemeral=True,
            )
            return
        except discord.HTTPException:
            await itr.followup.send("Failed to send rules image", ephemeral=True)
            return

        rules_results = await get_rules(self.bot.loop)

        rules = [
            f"**{index + 1} -** {rule}" for index, rule in enumerate(rules_results)
        ]
        rule_groups = discord.utils.as_chunks(rules, 10)

        for rg in rule_groups:
            await channel.send("\n\n".join(rg))
        message = await channel.send(
            "**Do not attempt to circumvent or find loopholes in these rules or use the "
            "\"well, it's not technically breaking the rules” excuse. It's the spirit of "
            "your actions that matters. No-one likes a rules lawyer.**\n\nIf you see "
            "something, say something. If you notice someone breaking rules, or if you "
            "have an issue with anyone or anything, feel free to DM a committee member about it!"
            '\n\n**Please press the "I Accept" button below to accept these rules.**',
            view=RulesView(),
        )

        await set_message_data(self.bot.loop, "rules", message.id)


async def setup(bot: DevSocBot) -> None:
    await bot.add_cog(Rules(bot))
