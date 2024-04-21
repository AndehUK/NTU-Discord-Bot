from __future__ import annotations

from random import randrange
from typing import TYPE_CHECKING

import discord

from data.memes import rat_fact
from utils.cog import Cog
from utils.enums import Colours
from utils.types import GUILD_MESSAGEABLE

if TYPE_CHECKING:
    from bot import DevSocBot


class Meme(Cog):
    @Cog.listener("on_message")
    async def rat_fact_listener(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not isinstance(message.channel, GUILD_MESSAGEABLE):
            return

        if message.embeds:
            return

        if "rat fact" in message.content.lower():
            index = randrange(len(rat_fact))
            await message.author.send(rat_fact[index])

        elif "hello there" in message.content.lower():
            await message.author.send(
                "https://tenor.com/view/grevious-general-kenobi-star-wars-gif-11406339"
            )

        elif "beans" in message.content.lower():
            embed = discord.Embed(color=Colours.YELLOW)
            embed.set_image(url="https://i.imgur.com/GkyCNCH.jpg")
            embed.set_footer(text="You thought i was gone? Shh")
            await message.author.send(embed=embed)


async def setup(bot: DevSocBot) -> None:
    await bot.add_cog(Meme(bot))
