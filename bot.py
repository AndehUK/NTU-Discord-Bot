from __future__ import annotations

# Core Imports
import traceback

# Third Party Packages
import aiohttp
import discord
from discord.ext import commands

# Local Imports
from cogs import COGS
from utils.logger import Logger
from utils.tree import Tree


class DevSocBot(commands.Bot):
    """The main Discord Bot class"""

    _is_ready: bool
    logger: Logger
    session: aiohttp.ClientSession

    def __init__(self) -> None:
        self._is_ready = False
        self.logger = Logger("DevSocBot", console=True)

        super().__init__(
            command_prefix=".",
            description="Discord Bot for the DevSoc Discord Server. Rewritten by @AndehUK on GitHub",
            intents=discord.Intents.all(),  # Be more specific with intents once we figure out which exact intents we need
            tree_cls=Tree,
            owner_ids={
                957437570546012240,  # andehx.
            },
        )

    async def setup_hook(self) -> None:
        """
        A coroutine to be called to setup the bot after logging in
        but before we connect to the Discord Websocket.

        Mainly used to load our cogs / extensions.
        """

        # Jishaku is our debugging tool installed from PyPi (See README.md)
        await self.load_extension("jishaku")
        loaded_cogs = 1

        # Loop through our COGS Tuple and load each cog
        for cog in COGS:
            try:
                await self.load_extension(cog)
                loaded_cogs += 1
                cog_name = cog.removeprefix("cogs.")
                self.logger.info(f"Loaded {cog_name} cog successfully!")
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"{type(e)} Exception in loading {cog}\n{tb}")
                continue

        self.logger.info(f"Successfully loaded {loaded_cogs}/{len(COGS)+1} cogs!")

    async def on_ready(self) -> None:
        """
        A coroutine to be called every time the bot connects to the
        Discord Websocket.

        This can be called multiple times if the bot disconnects and
        reconnects, hence why we create the `_is_ready` class variable
        to prevent functionality that should only take place on our first
        start-up from happening again.
        """

        if self._is_ready:
            return self.logger.critical("Bot reconnected to Discord gateway")

        self._is_ready = True
        if self.user:
            self.logger.info(f"Bot logged in as {self.user}")
        else:
            self.logger.critical("Bot failed to login. Safely exiting...")
            await self.close()

    async def start(self, *, token: str) -> None:
        """
        Logs in the client with the specified credentials and calls the :meth:`setup_hook` method
        then creates a websocket connection and lets the websocket listen to messages / events
        from Discord.
        """

        self.logger.info("Starting bot...")
        async with aiohttp.ClientSession() as self.session:
            try:
                await super().start(token)
            finally:
                self.logger.info("Shutdown bot.")
