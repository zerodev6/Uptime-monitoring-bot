import pytz
import datetime
import asyncio
import logging
from pyrogram import Client, filters, raw
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)

from config import Config
from database import db
from script import script
from utils import get_seconds

log = logging.getLogger(__name__)

ADMINS = Config.ADMINS
PREMIUM_LOGS = Config.PREMIUM_LOGS
STAR_PREMIUM_PLANS = Config.STAR_PREMIUM_PLANS
SUBSCRIPTION = "https://i.ibb.co/gMrpRQWP/photo-2025-07-09-05-21-32-7524948058832896004.jpg"


# ─── /remove_premium (admin) ─────────────────────────────────────────────────

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        if await db.remove_premium_access(user_id):
            await message.reply_text("ᴜꜱᴇʀ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !")
            await client.send_message(
                chat_id=user_id,
                text=script.PREMIUM_END_TEXT.format(user.mention)
            )
        else:
            await message.reply_text("ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜꜱᴇʀ!\nᴀʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ᴛʜᴇʏ ᴡᴇʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ?")
    else:
        await message.reply_text("ᴜꜱᴀɢᴇ : /remove_premium user_id")


# ─── /myplan ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("myplan"))
async def myplan(client, message):
    try:
        user = message.from_user.mention
        user_id = message.from_user.id
        data = await db.get_user(user_id)

        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time")
            if expiry.tzinfo is None:
                expiry = pytz.utc.localize(expiry)
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str = expiry_ist.strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")

            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, rem = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(rem, 60)
            time_left_str = f"{days} ᴅᴀʏꜱ, {hours} ʜᴏᴜʀꜱ, {minutes} ᴍɪɴᴜᴛᴇꜱ"

            caption = (
                f"⚜️ <b>ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴅᴀᴛᴀ :</b>\n\n"
                f"👤 <b>ᴜꜱᴇʀ :</b> {user}\n"
                f"⚡ <b>ᴜꜱᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n"
                f"⏰ <b>ᴛɪᴍᴇ ʟᴇꜰᴛ :</b> {time_left_str}\n"
                f"⌛️ <b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ :</b> {expiry_str}"
            )

            await message.reply_photo(
                photo=SUBSCRIPTION,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔥 ᴇxᴛᴇɴᴅ ᴘʟᴀɴ", callback_data="premium_info")]]
                )
            )
        else:
            await message.reply_photo(
                photo=SUBSCRIPTION,
                caption=(
                    f"<b>ʜᴇʏ {user},\n\n"
                    f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ.\n"
                    f"ʙᴜʏ ᴏᴜʀ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ᴛᴏ ᴇɴᴊᴏʏ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ.</b>"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("💎 ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ", callback_data="premium_info")]]
                )
            )
    except Exception as e:
        log.exception(e)


# ─── /get_premium (admin) ─────────────────────────────────────────────────────

@Client.on_message(filters.command("get_premium") & filters.user(ADMINS))
async def get_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        data = await db.get_user(user_id)
        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time")
            if expiry.tzinfo is None:
                expiry = pytz.utc.localize(expiry)
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str = expiry_ist.strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, rem = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(rem, 60)
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(
                f"⚜️ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴅᴀᴛᴀ :\n\n"
                f"👤 ᴜꜱᴇʀ : {user.mention}\n"
                f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ : {time_left_str}\n"
                f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str}"
            )
        else:
            await message.reply_text("ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴅᴀᴛᴀ ᴏꜰ ᴛʜɪꜱ ᴜꜱᴇʀ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ!")
    else:
        await message.reply_text("ᴜꜱᴀɢᴇ : /get_premium user_id")


# ─── /add_premium (admin) ─────────────────────────────────────────────────────

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def give_premium_cmd_handler(client, message):
    if len(message.command) >= 4:
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : %I:%M:%S %p")
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        time_str = message.command[2] + " " + message.command[3]
        seconds = await get_seconds(time_str)
        if seconds > 0:
            expiry_time = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time}
            await db.update_user(user_data)
            data = await db.get_user(user_id)
            expiry = data.get("expiry_time")
            if expiry.tzinfo is None:
                expiry = pytz.utc.localize(expiry)
            expiry_str = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : %I:%M:%S %p")
            await message.reply_text(
                f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅\n\n"
                f"👤 ᴜꜱᴇʀ : {user.mention}\n"
                f"⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_str}</code>\n\n"
                f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str}",
                disable_web_page_preview=True
            )
            await client.send_message(
                chat_id=user_id,
                text=f"👋 ʜᴇʏ {user.mention},\nᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴘᴜʀᴄʜᴀꜱɪɴɢ ᴘʀᴇᴍɪᴜᴍ.\nᴇɴᴊᴏʏ !! ✨🎉\n\n"
                     f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_str}</code>\n"
                     f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                     f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str}",
                disable_web_page_preview=True
            )
            if PREMIUM_LOGS:
                await client.send_message(
                    PREMIUM_LOGS,
                    text=f"#Added_Premium\n\n👤 ᴜꜱᴇʀ : {user.mention}\n⚡ ᴜꜱᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                         f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : <code>{time_str}</code>\n\n"
                         f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {current_time}\n\n"
                         f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {expiry_str}",
                    disable_web_page_preview=True
                )
        else:
            await message.reply_text(
                "❌ ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ ❗\n"
                "🕒 ᴜsᴇ: <code>1 day</code>, <code>1 hour</code>, <code>1 min</code>, <code>1 month</code>, or <code>1 year</code>"
            )
    else:
        await message.reply_text(
            "📌 ᴜsᴀɢᴇ: <code>/add_premium user_id time</code>\n"
            "📅 ᴇxᴀᴍᴘʟᴇ: <code>/add_premium 123456 1 month</code>"
        )


# ─── /premium_users (admin) ───────────────────────────────────────────────────

@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_user(client, message):
    aa = await message.reply_text("<i>ꜰᴇᴛᴄʜɪɴɢ...</i>")
    new = "ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ʟɪꜱᴛ :\n\n"
    user_count = 1
    users = db.get_all_users()
    async for user in await users:
        data = await db.get_user(user["id"])
        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time")
            if expiry.tzinfo is None:
                expiry = pytz.utc.localize(expiry)
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            if expiry_ist > datetime.datetime.now(pytz.timezone("Asia/Kolkata")):
                expiry_str = expiry_ist.strftime("%d-%m-%Y %I:%M %p")
                time_left = expiry_ist - datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
                days = time_left.days
                hours, rem = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(rem, 60)
                time_left_str = f"{days}d {hours}h {minutes}m"
                try:
                    u = await client.get_users(user["id"])
                    new += f"{user_count}. {u.mention}\n👤 ɪᴅ: {user['id']}\n⏳ ᴇxᴘɪʀʏ: {expiry_str}\n⏰ ᴛɪᴍᴇ ʟᴇꜰᴛ: {time_left_str}\n\n"
                    user_count += 1
                except Exception:
                    pass
    try:
        await aa.edit_text(new if user_count > 1 else "ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ.")
    except MessageTooLong:
        with open("usersplan.txt", "w+") as f:
            f.write(new)
        await message.reply_document("usersplan.txt", caption="ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ:")
        import os; os.remove("usersplan.txt")


# ─── /plan ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("plan"))
async def plan(client, message):
    btn = [[
        InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_info"),
    ], [
        InlineKeyboardButton("🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data")
    ]]
    msg = await message.reply_photo(
        photo="https://graph.org/file/86da2027469565b5873d6.jpg",
        caption=script.BPREMIUM_TXT,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await asyncio.sleep(300)
    try:
        await msg.delete()
        await message.delete()
    except Exception:
        pass


# ─── premium_info callback ────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^premium_info$"))
async def premium_info_cb(client, callback_query):
    buttons = []
    for stars, duration in STAR_PREMIUM_PLANS.items():
        buttons.append([InlineKeyboardButton(f"⭐ {stars} Stars — {duration}", callback_data=f"buy_{stars}")])
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="close_data")])
    try:
        await callback_query.message.edit_caption(
            caption=script.BPREMIUM_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception:
        await callback_query.message.reply_text(
            script.BPREMIUM_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    await callback_query.answer()


# ─── Telegram Stars payment via raw API (LabeledPrice not in pyrogram.types) ─

@Client.on_callback_query(filters.regex(r"^buy_\d+$"))
async def premium_button(client, callback_query):
    try:
        amount = int(callback_query.data.split("_")[1])
        if amount not in STAR_PREMIUM_PLANS:
            await callback_query.answer("⚠️ Invalid Premium Package.", show_alert=True)
            return

        peer = await client.resolve_peer(callback_query.message.chat.id)
        cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄᴀɴᴄᴇʟ 🚫", callback_data="close_data")]])

        await client.invoke(
            raw.functions.messages.SendMedia(
                peer=peer,
                media=raw.types.InputMediaInvoice(
                    title="Premium Subscription",
                    description=f"Pay {amount} Stars & Get Premium For {STAR_PREMIUM_PLANS[amount]}",
                    invoice=raw.types.Invoice(
                        currency="XTR",
                        prices=[raw.types.LabeledPrice(label="Premium Subscription", amount=amount)],
                    ),
                    payload=f"renamepremium_{amount}".encode(),
                    provider="",
                    provider_data=raw.types.DataJSON(data="{}"),
                ),
                message="",
                random_id=client.rnd_id(),
                reply_markup=await cancel_btn.write(client),
            )
        )
        await callback_query.answer()
    except Exception as e:
        log.exception(e)
        await callback_query.answer("🚫 Error Processing Payment. Try again.", show_alert=True)


# ─── Successful payment handler ───────────────────────────────────────────────

def successful_payment_filter(_, __, message):
    try:
        return hasattr(message, "successful_payment") and message.successful_payment is not None
    except AttributeError:
        return False


from pyrogram import filters as pfilters
successful_payment = pfilters.create(successful_payment_filter)


@Client.on_message(successful_payment & filters.private)
async def successful_premium_payment(client, message):
    try:
        payload = message.successful_payment.invoice_payload
        user_id = message.from_user.id
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y | %I:%M:%S %p")

        amount = None
        if payload.startswith("renamepremium_"):
            amount = int(payload.split("_")[1])

        if amount and amount in STAR_PREMIUM_PLANS:
            time_str = STAR_PREMIUM_PLANS[amount]
            seconds = await get_seconds(time_str)
            if seconds > 0:
                expiry_time = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=seconds)
                await db.update_user({"id": user_id, "expiry_time": expiry_time})
                data = await db.get_user(user_id)
                expiry = data.get("expiry_time")
                if expiry.tzinfo is None:
                    expiry = pytz.utc.localize(expiry)
                expiry_str = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y | %I:%M:%S %p")
                await message.reply(
                    f"✅ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴘᴜʀᴄʜᴀꜱɪɴɢ ᴘʀᴇᴍɪᴜᴍ!\n\n"
                    f"⏰ Subscription: {time_str}\n"
                    f"⌛️ Expires: {expiry_str}",
                    disable_web_page_preview=True
                )
                if PREMIUM_LOGS:
                    await client.send_message(
                        PREMIUM_LOGS,
                        text=f"#Purchase_Premium_With_Star\n\n"
                             f"👤 ᴜꜱᴇʀ: {message.from_user.mention}\n"
                             f"⚡ ɪᴅ: <code>{user_id}</code>\n"
                             f"⭐ Stars: {amount}\n"
                             f"⏰ Access: {time_str}\n"
                             f"⏳ Joined: {current_time}\n"
                             f"⌛️ Expiry: {expiry_str}",
                        disable_web_page_preview=True
                    )
    except Exception as e:
        log.exception(e)
        await message.reply("✅ Payment received! (Error logging details)")
