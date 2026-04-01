import asyncio
import logging
import os
from pyrogram import Client, idle

from config import Config
from scheduler import monitor_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# Collect all plugins
plugins = {"root": "plugins"}

bot = Client(
    "UptimeMonitorBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=plugins,
    workers=Config.WORKERS,
)


async def main():
    async with bot:
        log.info("✅ Bot started successfully!")
        # Start background monitor
        asyncio.create_task(monitor_loop(bot))
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
