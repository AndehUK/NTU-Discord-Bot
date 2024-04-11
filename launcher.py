# Core Imports
import asyncio
import os

# Third Party Packages
import dotenv

# Local Imports
from bot import DevSocBot


async def main() -> None:
    dotenv.load_dotenv()

    bot_token = os.environ.get("BOT_TOKEN")

    if not bot_token:
        raise ValueError("No BOT_TOKEN found in environment variables.")

    bot = DevSocBot()
    await bot.start(token=os.environ["BOT_TOKEN"])


asyncio.run(main())
