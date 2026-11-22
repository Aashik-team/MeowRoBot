#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import urllib.parse
import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Summarize"
__module__ = "𝐀𝐈 𝐓ᴏᴏʟ𝐬📝"

__help__ = """
*AI Text Summarizer Module📝*

*Commands:*  
❂ `/summarize [long text]` — Get a concise, high-level summary of any article or text  
❂ `/tldr [long text]` — Same as `/summarize`  
❂ Reply to any long message with `/summarize`  
"""

@bot.on_message(filters.command(["summarize", "tldr"]) & ~filters.forwarded)
async def summarize_text_cmd(_, m: types.Message):
    text_to_summarize = ""
    reply = m.reply_to_message

    if reply and (reply.text or reply.caption):
        text_to_summarize = reply.text or reply.caption
    elif len(m.command) > 1:
        text_to_summarize = m.text.split(None, 1)[1]

    if not text_to_summarize or len(text_to_summarize.strip()) < 50:
        return await m.reply_text(font("❌ Please provide or reply to a text of at least 50 characters to summarize!"))

    if len(text_to_summarize) > 5000:
        text_to_summarize = text_to_summarize[:5000]

    status_msg = await m.reply_text(font("🧠 AI is analyzing and summarizing the text..."))

    prompt = f"Summarize the following text clearly in 3-5 concise bullet points:\n\n{text_to_summarize}"
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200 and resp.text:
                summary = resp.text.strip()
                card = (
                    f"📝 **AI Summary (TL;DR):**\n\n"
                    f"{summary}\n\n"
                    f"♨️ **Powered by:** @TheAloneTeam"
                )
                return await status_msg.edit_text(card)

        await status_msg.edit_text(font("❌ Could not generate summary. Please try again later."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error summarizing text: {e}"))
