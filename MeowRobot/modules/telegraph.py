#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import os
import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Telegraph"
__module__ = "𝐓ᴇʟᴇɢʀᴀᴘʜ🌐"

__help__ = """
*Telegraph Uploader Module🌐*

*Commands:*  
❂ `/tgt` (or `/telegraph`) — Reply to a photo, sticker, or video (< 5MB) to upload and get a direct permanent link  
"""

@bot.on_message(filters.command(["tgt", "telegraph", "tgm"]) & ~filters.forwarded)
async def telegraph_upload(_, m: types.Message):
    reply = m.reply_to_message
    if not reply or not (reply.photo or reply.video or reply.animation or reply.sticker or reply.document):
        return await m.reply_text(font("❌ Reply to a photo, sticker, gif, or short video to upload to Telegraph!"))

    status_msg = await m.reply_text(font("📥 Downloading media..."))
    temp_path = None
    try:
        temp_path = await reply.download()
        if not temp_path or not os.path.exists(temp_path):
            return await status_msg.edit_text(font("❌ Failed to download media from Telegram."))

        await status_msg.edit_text(font("📤 Uploading to Telegraph..."))

        # Upload to Telegraph API (graph.org)
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(temp_path, "rb") as f:
                files = {"file": f}
                resp = await client.post("https://graph.org/upload", files=files)

            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0 and "src" in data[0]:
                    file_url = f"https://graph.org{data[0]['src']}"
                    await status_msg.edit_text(
                        f"🌐 **Telegraph Link Generated!**\n\n"
                        f"🔗 **URL:** `{file_url}`\n"
                        f"👀 [Open Link]({file_url})",
                        disable_web_page_preview=False
                    )
                    return

        # Fallback to catbox.moe
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(temp_path, "rb") as f:
                data = {"reqtype": "fileupload"}
                files = {"fileToUpload": f}
                resp = await client.post("https://catbox.moe/user/api.php", data=data, files=files)
                if resp.status_code == 200 and resp.text.startswith("http"):
                    file_url = resp.text.strip()
                    await status_msg.edit_text(
                        f"🌐 **Direct Link Generated!**\n\n"
                        f"🔗 **URL:** `{file_url}`\n"
                        f"👀 [Open Link]({file_url})",
                        disable_web_page_preview=False
                    )
                    return

        await status_msg.edit_text(font("❌ Failed to upload media. File might be too large!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error uploading media: {e}"))
    finally:
        if temp_path and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except Exception: pass
