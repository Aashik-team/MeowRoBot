#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

from pyrogram import filters, types, enums

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "AntiChannel"
__module__ = "𝐒ᴇᴄᴜʀɪᴛʏ🛡️"

__help__ = """
*Anti-Channel Protection Module🛡️*

*Description:*  
Prevents users from sending messages in your group acting as public/anonymous channels (a common spam tactic).

*Commands:*  
❂ `/antichannel [on/off]` — Enable or disable anti-channel message deletion in this chat  
❂ `/antichannel` — Check current anti-channel status  
"""

antichannel_col = db["antichannel_settings"]

async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

@bot.on_message(filters.command("antichannel") & filters.group)
async def toggle_antichannel(_, m: types.Message):
    if not m.from_user:
        return

    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can change anti-channel settings."))

    if len(m.command) < 2:
        doc = await antichannel_col.find_one({"chat_id": m.chat.id})
        status = "ENABLED 🟢" if (doc and doc.get("enabled")) else "DISABLED 🔴"
        return await m.reply_text(font(f"🛡️ Anti-Channel protection is currently **{status}** in this chat.\n\nUse `/antichannel [on/off]` to change."))

    action = m.command[1].lower()
    if action in ["on", "enable", "yes"]:
        await antichannel_col.update_one(
            {"chat_id": m.chat.id},
            {"$set": {"chat_id": m.chat.id, "enabled": True}},
            upsert=True
        )
        return await m.reply_text(font("🛡️ **Anti-Channel Protection is now ENABLED!**\nMessages sent as channels will be automatically deleted."))
    elif action in ["off", "disable", "no"]:
        await antichannel_col.update_one(
            {"chat_id": m.chat.id},
            {"$set": {"chat_id": m.chat.id, "enabled": False}},
            upsert=True
        )
        return await m.reply_text(font("🛡️ **Anti-Channel Protection is now DISABLED!**"))
    else:
        return await m.reply_text(font("❌ Invalid option. Use `/antichannel on` or `/antichannel off`."))

@bot.on_message(filters.group & ~filters.service, group=105)
async def check_channel_sender(_, m: types.Message):
    if not m.sender_chat:
        return

    # If the sender chat is the group itself, it's the anonymous group admin
    if m.sender_chat.id == m.chat.id:
        return

    # Check if anti-channel is enabled for this chat
    doc = await antichannel_col.find_one({"chat_id": m.chat.id})
    if doc and doc.get("enabled"):
        try:
            await m.delete()
            warning = await m.reply(font(f"⚠️ **Channel Message Deleted!**\nSending messages as channels is restricted in this group."))
            import asyncio
            await asyncio.sleep(5)
            await warning.delete()
        except Exception:
            pass
