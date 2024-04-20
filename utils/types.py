from typing import Union

import discord

GUILD_MESSAGEABLE = Union[
    discord.TextChannel, discord.Thread, discord.StageChannel, discord.VoiceChannel
]
