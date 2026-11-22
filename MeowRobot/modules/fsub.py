import uuid
import asyncio
from pyrogram import types, errors, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "F-Sub"
__module__ = "𝐅-𝐒ᴜʙ🚡"

__help__ = """
❂ *Force Subscribe Module* — Ensure members join your updates channel before participating in the group.

❂ *Commands*:
❂ `/fsub <@channel_username>` — Set required channel for this group (Bot must be admin in channel)
❂ `/fsub off` or `/rmfsub` — Disable force subscription in this group
❂ `/fsub` — Check current force subscription settings
"""

fsub_db = db['fsub']
refresh_cache = {}

async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

async def check_membership(channel_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in [
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER
        ]
    except Exception:
        return False

@bot.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_fsub(_, message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(font("❌ Only admins can manage Force Subscribe."))

    if len(message.command) < 2:
        doc = await fsub_db.find_one({"chat_id": message.chat.id})
        if doc and doc.get("enabled"):
            return await message.reply_text(
                f"🛡️ **Force Subscribe is active in this group.**\nRequired Channel: `{doc.get('channel')}`"
            )
        return await message.reply_text(
            "ℹ️ **Usage:**\n`/fsub @channel_username` — Enable\n`/fsub off` — Disable"
        )

    arg = message.command[1].strip()
    if arg.lower() in ["off", "disable", "no"]:
        await fsub_db.delete_one({"chat_id": message.chat.id})
        return await message.reply_text(font("✅ Force Subscribe has been disabled for this chat."))

    channel_name = arg
    if not channel_name.startswith("@") and not channel_name.startswith("-100"):
        channel_name = f"@{channel_name}"

    try:
        chat_obj = await bot.get_chat(channel_name)
    except Exception as e:
        return await message.reply_text(
            f"❌ **Error:** Could not find channel `{channel_name}`.\nMake sure the username is correct and the bot is an admin in the channel!\n`{e}`"
        )

    await fsub_db.update_one(
        {"chat_id": message.chat.id},
        {"$set": {
            "chat_id": message.chat.id,
            "channel_id": chat_obj.id,
            "channel": channel_name,
            "enabled": True
        }},
        upsert=True
    )

    await message.reply_text(
        f"✅ **Force Subscribe Enabled!**\nUsers must now join **{chat_obj.title}** (`{channel_name}`) before chatting here."
    )

@bot.on_message(filters.command("rmfsub") & filters.group)
async def remove_fsub(_, message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(font("❌ Only admins can manage Force Subscribe."))

    await fsub_db.delete_one({"chat_id": message.chat.id})
    await message.reply_text(font("✅ Force Subscribe has been removed for this chat."))

@bot.on_callback_query(filters.regex(r"^fsub_refresh#"))
async def fsub_refresh_callback(_, query: types.CallbackQuery):
    _, user_id_str, channel_id_str = query.data.split("#")
    user_id = int(user_id_str)
    channel_id = int(channel_id_str)

    if query.from_user.id != user_id:
        return await query.answer("❌ This button is not for you!", show_alert=True)

    is_member = await check_membership(channel_id, user_id)
    if not is_member:
        return await query.answer("⚠️ You haven't joined the channel yet! Please join first.", show_alert=True)

    try:
        # Restore permissions
        chat_perms = (await bot.get_chat(query.message.chat.id)).permissions
        await bot.restrict_chat_member(query.message.chat.id, user_id, chat_perms)
    except Exception:
        pass

    await query.message.delete()
    await query.answer("✅ Verified! You can now send messages here.", show_alert=True)

@bot.on_message(filters.group & ~filters.bot & ~filters.service, group=-100)
async def fsub_enforce_handler(_, message: types.Message):
    if not message.from_user:
        return

    doc = await fsub_db.find_one({"chat_id": message.chat.id})
    if not doc or not doc.get("enabled"):
        return

    user_id = message.from_user.id
    if await is_admin(message.chat.id, user_id):
        return

    channel_id = doc.get("channel_id")
    is_member = await check_membership(channel_id, user_id)
    if is_member:
        return

    # Delete non-member message
    try:
        await message.delete()
    except Exception:
        pass

    # Restrict user until they join
    try:
        await bot.restrict_chat_member(message.chat.id, user_id, types.ChatPermissions())
    except Exception:
        pass

    channel_name = doc.get("channel")
    try:
        invite_link = (await bot.get_chat(channel_id)).invite_link or f"https://t.me/{channel_name.lstrip('@')}"
    except Exception:
        invite_link = f"https://t.me/{channel_name.lstrip('@')}"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=invite_link)],
        [InlineKeyboardButton("🔄 I have joined", callback_data=f"fsub_refresh#{user_id}#{channel_id}")]
    ])

    await message.reply_text(
        f"👋 Hello {message.from_user.mention}!\n\n"
        f"To send messages in **{message.chat.title}**, you must join our updates channel first.",
        reply_markup=buttons
    )
