"""
Background task: pings all monitored URLs every 5 minutes.
Notifies the user if a URL goes down or comes back up.
"""
import asyncio
import logging
from pyrogram import Client

from database import db
from utils import ping_url

log = logging.getLogger(__name__)
PING_INTERVAL = 300  # seconds (5 minutes)


async def monitor_loop(client: Client):
    """Main monitoring loop — runs forever."""
    await asyncio.sleep(10)  # Wait for bot to fully start
    log.info("🔄 Uptime monitor scheduler started.")

    while True:
        try:
            apps = await db.get_all_apps()
            tasks = [check_app(client, app) for app in apps]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            log.exception(f"Error in monitor_loop: {e}")

        await asyncio.sleep(PING_INTERVAL)


async def check_app(client: Client, app: dict):
    user_id = app["user_id"]
    url = app["url"]
    old_status = app.get("status", "unknown")

    reachable = await ping_url(url)
    new_status = "online" if reachable else "offline"

    if new_status != old_status:
        await db.update_app_status(user_id, url, new_status)
        # Notify user of status change
        try:
            if new_status == "offline":
                await client.send_message(
                    user_id,
                    f"🔴 <b>ᴅᴏᴡɴ ᴀʟᴇʀᴛ!</b>\n\n"
                    f"🔗 <code>{url}</code>\n\n"
                    f"ʏᴏᴜʀ ᴀᴘᴘ ᴀᴘᴘᴇᴀʀs ᴛᴏ ʙᴇ <b>ᴏFFʟɪɴᴇ</b>. ɪ'ʟʟ ᴋᴇᴇᴘ ᴄʜᴇᴄᴋɪɴɢ ᴀɴᴅ ɴᴏᴛɪFʏ ʏᴏᴜ ᴡʜᴇɴ ɪᴛ's ʙᴀᴄᴋ ✅"
                )
            else:
                await client.send_message(
                    user_id,
                    f"🟢 <b>ʙᴀᴄᴋ ᴏɴʟɪɴᴇ!</b>\n\n"
                    f"🔗 <code>{url}</code>\n\n"
                    f"ʏᴏᴜʀ ᴀᴘᴘ ɪs <b>ᴏɴʟɪɴᴇ</b> ᴀɢᴀɪɴ 🎉"
                )
        except Exception:
            pass
    elif new_status == "offline":
        # Still offline — ping again to keep alive attempt
        pass
    else:
        # Still online — silent keep-alive ping already done
        pass
