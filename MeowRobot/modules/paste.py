#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import httpx
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Paste"
__module__ = "𝐔ᴛɪʟɪᴛʏ🛠️"

__help__ = """
*Code & Text Pastebin Module📋*

*Commands:*  
❂ `/paste [text]` — Upload text to pastebin and get a shareable link  
❂ Reply to a text message or a text file (`.txt`, `.py`, etc.) with `/paste`  
"""

@bot.on_message(filters.command(["paste", "bin"]) & ~filters.forwarded)
async def paste_text_cmd(_, m: types.Message):
    content = ""
    reply = m.reply_to_message

    if reply and reply.document and reply.document.file_size < 1024 * 1024:
        # Download document
        doc_path = await reply.download()
        try:
            with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            pass
        finally:
            import os
            if os.path.exists(doc_path):
                os.remove(doc_path)
    elif reply and (reply.text or reply.caption):
        content = reply.text or reply.caption
    elif len(m.command) > 1:
        content = m.text.split(None, 1)[1]

    if not content or not content.strip():
        return await m.reply_text(font("❌ Reply to a text message, text document, or provide text to `/paste`!"))

    status_msg = await m.reply_text(font("📋 Pasting content to bin..."))

    # Try Spacebin API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://spaceb.in/api/v1/documents", json={"content": content, "extension": "txt"})
            if resp.status_code in [200, 201]:
                doc_id = resp.json().get("payload", {}).get("id")
                if doc_id:
                    paste_url = f"https://spaceb.in/{doc_id}"
                    raw_url = f"https://spaceb.in/api/v1/documents/{doc_id}/raw"
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📋 View Paste", url=paste_url), InlineKeyboardButton("📥 Raw Text", url=raw_url)]
                    ])
                    return await status_msg.edit_text(
                        f"✅ **Pasted to Spacebin!**\n\n🔗 `{paste_url}`",
                        reply_markup=buttons,
                        disable_web_page_preview=True
                    )
    except Exception:
        pass

    # Fallback to Nekobin API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://nekobin.com/api/documents", json={"content": content})
            if resp.status_code in [200, 201]:
                key = resp.json().get("result", {}).get("key")
                if key:
                    paste_url = f"https://nekobin.com/{key}"
                    raw_url = f"https://nekobin.com/raw/{key}"
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📋 View Paste", url=paste_url), InlineKeyboardButton("📥 Raw Text", url=raw_url)]
                    ])
                    return await status_msg.edit_text(
                        f"✅ **Pasted to Nekobin!**\n\n🔗 `{paste_url}`",
                        reply_markup=buttons,
                        disable_web_page_preview=True
                    )
    except Exception:
        pass

    await status_msg.edit_text(font("❌ Failed to upload text to pastebin. Please try again later!"))
