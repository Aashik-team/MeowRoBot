# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import os
import asyncio
import re
import aiohttp
from io import BytesIO
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatAction

from MeowRobot import pbot as app, DRAGONS, DEV_USERS, LOGGER
from MeowRobot.utils.mongo import chatbot_db as DB

API_URL = "https://chatgp-nine.vercel.app/api/chat"
# API key is fetched via environment variable for security, with a fallback
API_KEY = os.environ.get("CHATBOT_API_KEY", "ritesh-8179b3a5da99f300be2d50e1e9789729")
TRIGGERS = ["hi", "hello", "hey", "baby", "Meow"]

# A global aiohttp session for connection pooling
AIOHTTP_SESSION = None

async def get_session():
    global AIOHTTP_SESSION
    if AIOHTTP_SESSION is None or AIOHTTP_SESSION.closed:
        AIOHTTP_SESSION = aiohttp.ClientSession()
    return AIOHTTP_SESSION

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

    # Send typing action to give immediate visual feedback
    try:
        await app.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        pass

    prompt = SYSTEM_PROMPT.replace("{user_name}", message.from_user.first_name or "Friend")
    
    formatted_prompt = f"System: {prompt}\nUser: {message.text}\nAssistant:"
    
    # Project's custom API endpoint explicitly requires "prompt" string format instead of OpenAI "messages" array
    payload = {
        "prompt": formatted_prompt
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        session = await get_session()
        # Using aiohttp for non-blocking async IO, making it much faster
        async with session.post(API_URL, json=payload, headers=headers, timeout=15) as response:
            if response.status == 200:
                data = await response.json()
                reply = data.get("response")
                
                if reply:
                    # Feature requested by user ("tum apna vale code pr bnao"): extract markdown code blocks > 5 lines as files
                    code_blocks = re.findall(r'```([a-zA-Z]*)\n(.*?)```', reply, re.DOTALL)

                    files_to_send = []
                    for lang, code in code_blocks:
                        lines = code.strip().split('\n')
                        if len(lines) > 5:
                            ext = f".{lang}" if lang else ".txt"
                            if lang == "python": ext = ".py"
                            elif lang in ("javascript", "js"): ext = ".js"
                            elif lang == "html": ext = ".html"
                            elif lang == "css": ext = ".css"
                            elif lang == "json": ext = ".json"
                            elif lang in ("cpp", "c++"): ext = ".cpp"

                            filename = f"code_snippet{ext}"
                            file_obj = BytesIO(code.strip().encode('utf-8'))
                            file_obj.name = filename
                            files_to_send.append(file_obj)

                            original_block = f"```{lang}\n{code}```"
                            reply = reply.replace(original_block, f"**[Long code block sent as file: {filename}]**")

                    if reply.strip():
                        await message.reply_text(reply)
                    
                    for f in files_to_send:
                        await message.reply_document(document=f)
            else:
                LOGGER.error(f"Chatbot API error: {response.status}")
    except asyncio.TimeoutError:
        LOGGER.error("Chatbot request timed out")
    except Exception as e:
        LOGGER.error(f"Chatbot error: {e}")

__mod_name__ = "Cʜᴀᴛʙᴏᴛ"
__help__ = """
AI Chatbot for your group.

 ❍ /chatbot <on/off>*:* Toggle AI chatbot in group.
 ❍ Bot responds to triggers (hi, hello, etc.) or when replied to.
"""
