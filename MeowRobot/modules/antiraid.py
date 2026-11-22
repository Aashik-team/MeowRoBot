#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import time
from collections import defaultdict
from pyrogram import filters, types, enums

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "AntiRaid"
__module__ = "𝐒ᴇᴄᴜʀɪᴛʏ🛡️"

__help__ = """
*Anti-Raid Protection Module🛡️*

*Description:*  
Protects your group from bot raid attacks. When more than 5 users join within 10 seconds, anti-raid automatically kicks the raiders and alerts admins!

*Commands:*  
❂ `/antiraid [on/off]` — Enable or disable anti-raid protection  
❂ `/antiraid` — Check current anti-raid status  
"""

antiraid_col = db["antiraid_settings"]
# In-memory join tracking: chat_id -> list of timestamps
join_tracker = defaultdict(list)
RAID_THRESHOLD = 5  # joins
RAID_WINDOW = 10    # seconds

async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

@bot.on_message(filters.command("antiraid") & filters.group)
async def toggle_antiraid(_, m: types.Message):
    if not m.from_user:
        return

    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can change anti-raid settings."))

    if len(m.command) < 2:
        doc = await antiraid_col.find_one({"chat_id": m.chat.id})
        status = "ENABLED 🟢" if (doc and doc.get("enabled")) else "DISABLED 🔴"
        return await m.reply_text(font(f"🛡️ Anti-Raid protection is currently **{status}** in this chat.\n\nUse `/antiraid [on/off]` to change."))

    action = m.command[1].lower()
    if action in ["on", "enable", "yes"]:
        await antiraid_col.update_one(
            {"chat_id": m.chat.id},
            {"$set": {"chat_id": m.chat.id, "enabled": True}},
            upsert=True
        )
        return await m.reply_text(font("🛡️ **Anti-Raid Protection is now ENABLED!**\nMass bot joins will be automatically countered."))
    elif action in ["off", "disable", "no"]:
        await antiraid_col.update_one(
            {"chat_id": m.chat.id},
            {"$set": {"chat_id": m.chat.id, "enabled": False}},
            upsert=True
        )
        return await m.reply_text(font("🛡️ **Anti-Raid Protection is now DISABLED!**"))
    else:
        return await m.reply_text(font("❌ Invalid option. Use `/antiraid on` or `/antiraid off`."))

@bot.on_message(filters.new_chat_members & filters.group, group=106)
async def monitor_raid_joins(_, m: types.Message):
    doc = await antiraid_col.find_one({"chat_id": m.chat.id})
    if not (doc and doc.get("enabled")):
        return

    now = time.time()
    chat_joins = join_tracker[m.chat.id]
    # Keep only joins within window
    join_tracker[m.chat.id] = [t for t in chat_joins if now - t < RAID_WINDOW]
    join_tracker[m.chat.id].append(now)

    if len(join_tracker[m.chat.id]) >= RAID_THRESHOLD:
        # Trigger anti-raid
        try:
            for member in m.new_chat_members:
                if not member.is_bot:
                    await bot.ban_chat_member(m.chat.id, member.id)
                    await bot.unban_chat_member(m.chat.id, member.id)

            await m.reply_text(
                "🚨 **ANTI-RAID TRIGGERED!**\n\n"
                f"Detected mass member joins ({len(join_tracker[m.chat.id])} in {RAID_WINDOW}s). "
                "The suspicious accounts were automatically kicked to protect the group!"
            )
            # Reset after trigger
            join_tracker[m.chat.id].clear()
        except Exception:
            pass
