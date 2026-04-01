import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import Config
from database import db
from script import script

log = logging.getLogger(__name__)
ADMINS = Config.ADMINS


# ─── /stats (admin) ───────────────────────────────────────────────────────────

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_cmd(client: Client, message: Message):
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    apps = await db.total_apps_count()
    await message.reply_text(
        script.STATS_TXT.format(users=users, chats=chats, apps=apps),
        reply_to_message_id=message.id,
    )


# ─── /users (admin alias) ────────────────────────────────────────────────────

@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users_count_cmd(client: Client, message: Message):
    users = await db.total_users_count()
    await message.reply_text(
        f"👥 <b>Total Users:</b> <code>{users}</code>",
        reply_to_message_id=message.id,
    )


# ─── start_back callback ─────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^start_back$"))
async def start_back_cb(client, callback_query):
    from plugins.start import get_welcome_image, get_greeting, WELCOME_STICKER
    from script import script
    import asyncio

    user = callback_query.from_user
    greeting = get_greeting()
    image_url = await get_welcome_image()

    start_btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴜʀʟ", callback_data="add_url"),
            InlineKeyboardButton("📋 ᴍʏ ᴀᴘᴘs", callback_data="my_apps"),
        ],
        [
            InlineKeyboardButton("ℹ️ ʜᴇʟᴘ", callback_data="help_data"),
            InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_info"),
        ],
        [
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/Venuboyy"),
        ]
    ])

    try:
        await callback_query.message.delete()
    except Exception:
        pass

    await client.send_photo(
        callback_query.message.chat.id,
        photo=image_url,
        caption=script.START_TXT.format(user.mention, greeting),
        reply_markup=start_btn,
    )
    await callback_query.answer()
