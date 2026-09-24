#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import os
import requests
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from MeowRobot import pbot as app, DRAGONS, DEV_USERS, LOGGER
from MeowRobot.utils.mongo import chatbot_db as DB

API = "https://aivya.thechiku.workers.dev/"
TRIGGERS = ["hi", "hello", "hey", "baby", "Meow"]

async def is_admin(message: Message, user_id: int):
    if user_id in DRAGONS or user_id in DEV_USERS:
        return True
    try:
        member = await app.get_chat_member(message.chat.id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False

def load_prompt():
    try:
        path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except:
        pass
    return "You are MeowRoBot AI. User is {user_name}. Reply friendly and helpful. You are a powerful group management bot."

SYSTEM_PROMPT = load_prompt()

@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(_, message: Message):
    if not await is_admin(message, message.from_user.id):
        return await message.reply_text("❗ Only admins can use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/chatbot on - Enable\n/chatbot off - Disable")

    arg = message.command[1].lower()
    if arg == "on":
        await DB.update_one({"chat_id": message.chat.id}, {"$set": {"enabled": True}}, upsert=True)
        await message.reply_text("✅ Chatbot is now ENABLED in this group.")
    elif arg == "off":
        await DB.update_one({"chat_id": message.chat.id}, {"$set": {"enabled": False}}, upsert=True)
        await message.reply_text("❌ Chatbot is now DISABLED in this group.")
    else:
        await message.reply_text("Invalid argument. Use `on` or `off`.")

@app.on_message(filters.text & ~filters.regex(r"^/") & ~filters.bot, group=10)
async def chatbot_handler(_, message: Message):
    if not message.text:
        return

    text = message.text.lower().strip()
    chat_id = message.chat.id

    if message.chat.type != message.chat.type.PRIVATE:
        settings = await DB.find_one({"chat_id": chat_id})
        if not settings or not settings.get("enabled", False):
            return

        is_trigger = any(t in text for t in TRIGGERS)
        is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user and
                           message.reply_to_message.from_user.is_self)

        if not is_trigger and not is_reply_to_bot:
            return

    prompt = SYSTEM_PROMPT.replace("{user_name}", message.from_user.first_name or "Friend")
    payload = {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message.text},
        ]
    }

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(API, json=payload, timeout=15))
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply") or data.get("message") or data.get("response")
            if reply:
                await message.reply_text(reply)
    except Exception as e:
        LOGGER.error(f"Chatbot error: {e}")

__mod_name__ = "Cʜᴀᴛʙᴏᴛ"
__help__ = """
AI Chatbot for your group.

 ❍ /chatbot <on/off>*:* Toggle AI chatbot in group.
 ❍ Bot responds to triggers (hi, hello, etc.) or when replied to.
"""
