#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import os
import edge_tts
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Speak"
__module__ = "𝐀𝐈 𝐕ᴏɪᴄᴇ🎙️"

__help__ = """
*Multi-Voice Text-To-Speech Module🎙️*

*Description:*  
Generate ultra-realistic human AI voices in Hindi, Indian English, US English, and Urdu!

*Commands:*  
❂ `/speak [text]` — Convert text to speech in cute female Hindi/English voice  
❂ `/voice [text]` — Same as `/speak`  
❂ `/boyvoice [text]` — Male voice in Hindi/English  
❂ `/girlvoice [text]` — Female voice  
❂ Reply to any text message with `/speak`  
"""

VOICE_MAP = {
    "girl": "hi-IN-SwaraNeural",
    "female": "hi-IN-SwaraNeural",
    "boy": "hi-IN-MadhurNeural",
    "male": "hi-IN-MadhurNeural",
    "us_female": "en-US-AriaNeural",
    "us_male": "en-US-GuyNeural",
}

@bot.on_message(filters.command(["speak", "voice", "girlvoice", "boyvoice"]) & ~filters.forwarded)
async def tts_speak_cmd(_, m: types.Message):
    text_to_speak = ""
    voice_name = "hi-IN-SwaraNeural"

    cmd = m.command[0].lower()
    if cmd == "boyvoice":
        voice_name = "hi-IN-MadhurNeural"
    elif cmd == "girlvoice":
        voice_name = "hi-IN-SwaraNeural"

    reply = m.reply_to_message
    if reply and (reply.text or reply.caption):
        text_to_speak = reply.text or reply.caption
    elif len(m.command) > 1:
        text_to_speak = m.text.split(None, 1)[1]

    if not text_to_speak or not text_to_speak.strip():
        return await m.reply_text(font("❌ Usage: `/speak [text]` or reply to any message!"))

    if len(text_to_speak) > 1000:
        text_to_speak = text_to_speak[:1000]

    status_msg = await m.reply_text(font("🎙️ Generating speech audio..."))

    audio_file = f"downloads/speak_{m.id}.ogg"
    os.makedirs("downloads", exist_ok=True)

    try:
        communicate = edge_tts.Communicate(text_to_speak, voice=voice_name)
        await communicate.save(audio_file)

        if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            await m.reply_voice(
                voice=audio_file,
                caption=f"🎙️ *\"{text_to_speak[:100]}...\"*",
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text(font("❌ Failed to generate audio voice."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error generating voice: {e}"))
    finally:
        if os.path.exists(audio_file):
            try: os.remove(audio_file)
            except Exception: pass
