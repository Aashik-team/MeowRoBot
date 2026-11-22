#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import uuid
from pyrogram import filters, types, enums

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "Confess"
__module__ = "𝐂ᴏɴғᴇss💌"

__help__ = """
*Anonymous Confession Module💌*

*Commands:*  
❂ `/setconfess` — (Group Admins only) Enable anonymous confessions in this group  
❂ `/confess [group_username or chat_id] [message]` — (In Bot PM) Send an anonymous confession to the group without revealing your identity!  
"""

confess_col = db["confessions_config"]
confess_count_col = db["confessions_count"]

async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

@bot.on_message(filters.command("setconfess") & filters.group)
async def set_confess_channel(_, m: types.Message):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only admins can enable confessions in this group."))

    await confess_col.update_one(
        {"chat_id": m.chat.id},
        {"$set": {"chat_id": m.chat.id, "chat_title": m.chat.title, "username": m.chat.username}},
        upsert=True
    )

    identifier = f"@{m.chat.username}" if m.chat.username else f"`{m.chat.id}`"
    bot_user = await bot.get_me()

    await m.reply_text(
        f"💌 **Anonymous Confessions Enabled for this group!**\n\n"
        f"Members can send confessions by messaging @{bot_user.username} in private:\n"
        f"👉 `/confess {identifier} Your secret message here...`\n\n"
        f"Their identity will be 100% hidden!"
    )

@bot.on_message(filters.command("confess") & filters.private)
async def send_confess_private(_, m: types.Message):
    if len(m.command) < 3:
        return await m.reply_text(font("❌ Usage: `/confess [group_username or chat_id] [your secret message]`"))

    target_input = m.command[1].strip()
    confess_text = m.text.split(None, 2)[2].strip()

    # Find group
    target_chat = None
    try:
        if target_input.startswith("@"):
            chat = await bot.get_chat(target_input)
            target_chat = chat.id
        elif target_input.startswith("-100") or target_input.lstrip("-").isdigit():
            target_chat = int(target_input)
        else:
            chat = await bot.get_chat(f"@{target_input}")
            target_chat = chat.id
    except Exception:
        return await m.reply_text(font("❌ Could not find that group. Make sure bot is an admin there!"))

    config = await confess_col.find_one({"chat_id": target_chat})
    if not config:
        return await m.reply_text(font("❌ Confessions are not enabled in that group yet! Ask an admin to send `/setconfess` there."))

    # Increment confession counter
    count_doc = await confess_count_col.find_one_and_update(
        {"chat_id": target_chat},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    c_num = count_doc.get("count", 1) if count_doc else 1

    post_card = (
        f"💌 **Anonymous Confession #{c_num}**\n\n"
        f"💬 *\"{confess_text}\"*\n\n"
        f"🔒 *Sender identity is protected and 100% anonymous.*"
    )

    try:
        await bot.send_message(target_chat, post_card)
        await m.reply_text(font(f"✅ Your anonymous confession #{c_num} has been successfully posted to the group!"))
    except Exception as e:
        await m.reply_text(font(f"❌ Failed to post confession: {e}"))
