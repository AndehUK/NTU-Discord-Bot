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
    try:
        await bot.start(token=os.environ["BOT_TOKEN"])
    except:
        # Allows us to shutdown the bot gracefully
        bot.logger.info("Shutting down bot... (In launcher)")
        await bot.close()
    finally:
        bot.logger.info("Shutdown bot.")


asyncio.run(main())
