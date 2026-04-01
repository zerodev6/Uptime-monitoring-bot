import pytz
import asyncio
import datetime
import aiohttp
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message
)
from pyrogram.errors import UserNotParticipant, ChatAdminRequired

from config import Config
from database import db
from script import script
from utils import get_random_mix_id

log = logging.getLogger(__name__)

WELCOME_STICKER = "CAACAgIAAxkBAAIBq2aZQVLHDtdoHLG9sGJ_k9bkjsK-AAJPAAMw1J0R5HjFtTDLqRUeBA"  # animated sticker file_id (change if desired)


# ─── FORCE SUBSCRIBE HELPER ─────────────────────────────────────────────────

async def check_force_sub(client: Client, user_id: int) -> bool:
    """Return True if user has joined all required channels."""
    channels = [Config.FORCE_SUB_CHANNEL_1, Config.FORCE_SUB_CHANNEL_2]
    for ch in channels:
        if not ch:
            continue
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status.value in ("left", "kicked", "banned"):
                return False
        except UserNotParticipant:
            return False
        except Exception:
            pass
    return True


async def force_sub_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if Config.FORCE_SUB_CHANNEL_1:
        buttons.append([InlineKeyboardButton("📢 Channel 1", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL_1}")])
    if Config.FORCE_SUB_CHANNEL_2:
        buttons.append([InlineKeyboardButton("📢 Channel 2", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL_2}")])
    buttons.append([InlineKeyboardButton("✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)


# ─── GREETING BASED ON TIME ─────────────────────────────────────────────────

def get_greeting() -> str:
    current_time = datetime.datetime.now(pytz.timezone(Config.TIMEZONE))
    hour = current_time.hour
    if hour < 12:
        return "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞"
    elif hour < 17:
        return "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 🌓"
    elif hour < 21:
        return "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘"
    else:
        return "ɢᴏᴏᴅ ɴɪɢʜᴛ 🌑"


# ─── WELCOME IMAGE URL ───────────────────────────────────────────────────────

async def get_welcome_image() -> str:
    url = f"{Config.WELCOME_IMAGE}?r={get_random_mix_id()}"
    return url


# ─── /start ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    user = message.from_user
    await db.add_user(user.id)

    # Force subscribe check
    if not await check_force_sub(client, user.id):
        await message.reply_photo(
            photo=Config.FORCE_SUB_IMAGE,
            caption=script.FORCE_SUB_TXT,
            reply_markup=await force_sub_keyboard(),
        )
        return

    greeting = get_greeting()

    # Send animated sticker for 2 seconds then delete
    try:
        sticker_msg = await message.reply_sticker(WELCOME_STICKER)
        await asyncio.sleep(2)
        await sticker_msg.delete()
    except Exception:
        pass

    # Fetch random welcome image
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

    await message.reply_photo(
        photo=image_url,
        caption=script.START_TXT.format(user.mention, greeting),
        reply_markup=start_btn,
        reply_to_message_id=message.id,
    )


@Client.on_message(filters.command("start") & filters.group)
async def start_group(client: Client, message: Message):
    user = message.from_user
    chat = message.chat
    await db.add_chat(chat.id)
    if user:
        await db.add_user(user.id)

    greeting = get_greeting()
    mention = user.mention if user else "ᴛʜᴇʀᴇ"

    await message.reply_text(
        script.GSTART_TXT.format(mention, greeting),
        reply_to_message_id=message.id,
    )


# ─── /help ───────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_back")]])
    await message.reply_text(script.HELP_TXT, reply_markup=btn, reply_to_message_id=message.id)


# ─── /about ──────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client: Client, message: Message):
    me = await client.get_me()
    await message.reply_text(
        script.ABOUT_TXT.format(me.mention),
        disable_web_page_preview=True,
        reply_to_message_id=message.id,
    )


# ─── /info ───────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("info") & filters.private)
async def info_cmd(client: Client, message: Message):
    user = message.from_user

    # Get Data Centre via pyrogram (it's in the peer object; fallback to N/A)
    dc = getattr(user, "dc_id", "N/A")
    username = f"@{user.username}" if user.username else "ɴᴏɴᴇ"
    user_link = f"<a href='tg://user?id={user.id}'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>"
    last_name = user.last_name or "ɴᴏɴᴇ"

    caption = (
        f"➲<b>Fɪʀsᴛ Nᴀᴍᴇ:</b> {user.first_name}\n"
        f"➲<b>Lᴀsᴛ Nᴀᴍᴇ:</b> {last_name}\n"
        f"➲<b>Tᴇʟᴇɢʀᴀᴍ ɪᴅ:</b> <code>{user.id}</code>\n\n"
        f"➲<b>Dᴀᴛᴀ Cᴇɴᴛʀᴇ:</b> {dc}\n\n"
        f"➲<b>Usᴇʀ Nᴀᴍᴇ:</b> {username}\n"
        f"➲<b>Usᴇʀ 𝖫𝗂𝗇𝗄:</b> {user_link}"
    )

    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos:
            await message.reply_photo(
                photo=photos[0].file_id,
                caption=caption,
                reply_to_message_id=message.id,
            )
            return
    except Exception:
        pass

    await message.reply_text(caption, reply_to_message_id=message.id)


# ─── CHECK SUB CALLBACK ──────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^check_sub$"))
async def check_sub_cb(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_force_sub(client, user_id):
        await callback_query.message.delete()
        # Re-trigger start
        greeting = get_greeting()
        image_url = await get_welcome_image()
        user = callback_query.from_user
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
            sticker_msg = await client.send_sticker(callback_query.message.chat.id, WELCOME_STICKER)
            await asyncio.sleep(2)
            await sticker_msg.delete()
        except Exception:
            pass
        await client.send_photo(
            callback_query.message.chat.id,
            photo=image_url,
            caption=script.START_TXT.format(user.mention, greeting),
            reply_markup=start_btn,
        )
    else:
        await callback_query.answer("⚠️ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ!", show_alert=True)


@Client.on_callback_query(filters.regex("^help_data$"))
async def help_cb(client, callback_query):
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_back")]])
    await callback_query.message.edit_text(script.HELP_TXT, reply_markup=btn)
    await callback_query.answer()


@Client.on_callback_query(filters.regex("^close_data$"))
async def close_data_cb(client, callback_query):
    await callback_query.message.delete()
    await callback_query.answer()
