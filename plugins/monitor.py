import re
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
)

from config import Config
from database import db
from utils import ping_url

log = logging.getLogger(__name__)

URL_REGEX = re.compile(r"https?://[^\s]+", re.IGNORECASE)

# Track users waiting to send URL
WAITING_FOR_URL = set()


# ─── ADD URL COMMAND / CALLBACK ──────────────────────────────────────────────

@Client.on_message(filters.command("add") & filters.private)
async def add_url_cmd(client: Client, message: Message):
    await prompt_add_url(client, message.chat.id, message.id)


@Client.on_callback_query(filters.regex("^add_url$"))
async def add_url_cb(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await prompt_add_url(client, callback_query.message.chat.id)
    await callback_query.answer()


async def prompt_add_url(client: Client, chat_id: int, reply_id: int = None):
    WAITING_FOR_URL.add(chat_id)
    kwargs = dict(
        chat_id=chat_id,
        text="🔗 <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴜʀʟ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴍᴏɴɪᴛᴏʀ:</b>\n\n"
             "<i>ᴇxᴀᴍᴘʟᴇ: https://myapp.onrender.com</i>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_add")]])
    )
    if reply_id:
        kwargs["reply_to_message_id"] = reply_id
    await client.send_message(**kwargs)


@Client.on_callback_query(filters.regex("^cancel_add$"))
async def cancel_add_cb(client: Client, callback_query: CallbackQuery):
    WAITING_FOR_URL.discard(callback_query.message.chat.id)
    await callback_query.message.edit_text("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    await callback_query.answer()


# ─── HANDLE URL INPUT ────────────────────────────────────────────────────────

@Client.on_message(filters.text & filters.private)
async def handle_text(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()

    # Only process if user is in waiting state
    if chat_id not in WAITING_FOR_URL:
        return

    match = URL_REGEX.match(text)
    if not match:
        await message.reply_text(
            "⚠️ ᴛʜᴀᴛ ᴅᴏᴇsɴ'ᴛ ʟᴏᴏᴋ ʟɪᴋᴇ ᴀ ᴠᴀʟɪᴅ ᴜʀʟ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴜʀʟ sᴛᴀʀᴛɪɴɢ ᴡɪᴛʜ https://",
            reply_to_message_id=message.id,
        )
        return

    url = match.group(0)
    WAITING_FOR_URL.discard(chat_id)

    # Check limit
    added = await db.add_app(user_id, url)
    if not added:
        is_prem = await db.is_premium(user_id)
        if not is_prem:
            await message.reply_text(
                f"⚠️ <b>ʏᴏᴜ'ᴠᴇ ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ғʀᴇᴇ ʟɪᴍɪᴛ ᴏғ {Config.FREE_USER_LIMIT} ᴀᴘᴘs.</b>\n\n"
                "ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴘᴘs! 💎",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ", callback_data="premium_info")]]),
                reply_to_message_id=message.id,
            )
        return

    # Ping immediately to confirm
    status_msg = await message.reply_text("⏳ ᴘɪɴɢɪɴɢ ᴜʀʟ...", reply_to_message_id=message.id)
    reachable = await ping_url(url)
    status = "🟢 ᴏɴʟɪɴᴇ" if reachable else "🔴 ᴏғғʟɪɴᴇ"
    await db.update_app_status(user_id, url, "online" if reachable else "offline")

    await status_msg.edit_text(
        f"✅ <b>ᴜʀʟ ᴀᴅᴅᴇᴅ ᴛᴏ ᴍᴏɴɪᴛᴏʀɪɴɢ!</b>\n\n"
        f"🔗 <code>{url}</code>\n"
        f"📡 ꜱᴛᴀᴛᴜꜱ: {status}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 ᴍʏ ᴀᴘᴘs", callback_data="my_apps")]])
    )


# ─── /apps — LIST MONITORED URLS ─────────────────────────────────────────────

@Client.on_message(filters.command("apps") & filters.private)
async def apps_cmd(client: Client, message: Message):
    await show_apps(client, message.chat.id, message.from_user.id, reply_id=message.id)


@Client.on_callback_query(filters.regex("^my_apps$"))
async def my_apps_cb(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await show_apps(client, callback_query.message.chat.id, callback_query.from_user.id)
    await callback_query.answer()


async def show_apps(client: Client, chat_id: int, user_id: int, reply_id: int = None):
    apps = await db.get_user_apps(user_id)
    if not apps:
        kwargs = dict(
            chat_id=chat_id,
            text="📭 <b>ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴀᴘᴘs ʏᴇᴛ.</b>\n\nᴜsᴇ /add ᴛᴏ sᴛᴀʀᴛ ᴍᴏɴɪᴛᴏʀɪɴɢ!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ ᴀᴅᴅ ᴜʀʟ", callback_data="add_url")]]),
        )
    else:
        text = "<b>📋 ʏᴏᴜʀ ᴍᴏɴɪᴛᴏʀᴇᴅ ᴀᴘᴘs:</b>\n\n"
        buttons = []
        for i, app in enumerate(apps, 1):
            status_icon = "🟢" if app.get("status") == "online" else "🔴"
            text += f"{i}. {status_icon} <code>{app['url']}</code>\n"
            buttons.append([
                InlineKeyboardButton(f"🗑 ʀᴇᴍᴏᴠᴇ #{i}", callback_data=f"del_app:{app['url'][:50]}")
            ])
        buttons.append([InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴏʀᴇ", callback_data="add_url")])
        kwargs = dict(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(buttons))

    if reply_id:
        kwargs["reply_to_message_id"] = reply_id
    await client.send_message(**kwargs)


@Client.on_callback_query(filters.regex(r"^del_app:"))
async def del_app_cb(client: Client, callback_query: CallbackQuery):
    url_prefix = callback_query.data.split(":", 1)[1]
    user_id = callback_query.from_user.id
    apps = await db.get_user_apps(user_id)
    # Find the full URL by prefix
    for app in apps:
        if app["url"].startswith(url_prefix):
            await db.remove_app(user_id, app["url"])
            await callback_query.answer("✅ ᴀᴘᴘ ʀᴇᴍᴏᴠᴇᴅ!", show_alert=True)
            # Refresh the apps list
            await callback_query.message.delete()
            await show_apps(client, callback_query.message.chat.id, user_id)
            return
    await callback_query.answer("⚠️ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
