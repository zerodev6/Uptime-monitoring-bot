import re
import asyncio
import aiohttp
import logging
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

log = logging.getLogger(__name__)


# ─── TEMP STATE ─────────────────────────────────────────────────────────────

class temp:
    B_USERS_CANCEL = False
    B_GROUPS_CANCEL = False
    B_LINK = ""


# ─── TIME HELPERS ────────────────────────────────────────────────────────────

async def get_seconds(time_str: str) -> int:
    """Convert time string like '1 month', '3 days', '2 hours' to seconds."""
    time_str = time_str.strip().lower()
    match = re.match(r"(\d+)\s*(second|minute|min|hour|day|week|month|year)s?", time_str)
    if not match:
        return 0
    amount = int(match.group(1))
    unit = match.group(2)
    multipliers = {
        "second": 1,
        "minute": 60,
        "min": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
        "month": 2592000,   # 30 days
        "year": 31536000,   # 365 days
    }
    return amount * multipliers.get(unit, 0)


def get_readable_time(seconds: float) -> str:
    seconds = int(seconds)
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    parts = []
    for name, duration in periods:
        value, seconds = divmod(seconds, duration)
        if value:
            parts.append(f"{value}{name}")
    return " ".join(parts) or "0s"


# ─── PING / MONITORING ───────────────────────────────────────────────────────

async def ping_url(url: str) -> bool:
    """Ping a URL and return True if reachable."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as resp:
                return resp.status < 500
    except Exception:
        return False


# ─── BROADCAST HELPERS ───────────────────────────────────────────────────────

async def users_broadcast(user_id: int, message, is_pin: bool = False):
    try:
        sent = await message.copy(user_id)
        if is_pin:
            try:
                await sent.pin(disable_notification=True)
            except Exception:
                pass
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return False, "Error"
    except UserIsBlocked:
        return False, "Blocked"
    except InputUserDeactivated:
        return False, "Deleted"
    except Exception:
        return False, "Error"


async def groups_broadcast(chat_id: int, message, is_pin: bool = False):
    try:
        sent = await message.copy(chat_id)
        if is_pin:
            try:
                await sent.pin(disable_notification=True)
            except Exception:
                pass
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return "Error"
    except Exception:
        return "Error"


async def clear_junk(user_id: int, b_msg):
    try:
        await b_msg.copy(user_id)
        return True, "Success"
    except UserIsBlocked:
        return False, "Blocked"
    except InputUserDeactivated:
        return False, "Deleted"
    except Exception:
        return False, "Error"


async def junk_group(chat_id: int, b_msg):
    try:
        await b_msg.copy(chat_id)
        return True, "Success", ""
    except Exception as e:
        return False, "deleted", str(e)


# ─── RANDOM ID ───────────────────────────────────────────────────────────────

import random
import string

def get_random_mix_id(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
