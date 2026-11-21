import os
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MeowRobot import pbot as bot  # <-- apne repo ke hisaab se change karna


def upload_yuki(file_path: str):
    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                "https://yukiapi.site/upload",
                files={"file": f},
                timeout=120,
            )
        if not r.text.strip():
            return False, "YukiAPI: empty response"

        data = r.json()

        if r.status_code != 200:
            return False, f"YukiAPI: {r.status_code} - {str(data)[:100]}"

        if isinstance(data, dict):
            link = data.get("url", "")
            if link and link.startswith("http"):
                return True, link
            return False, f"YukiAPI: {str(data)[:100]}"

        return False, f"YukiAPI: unexpected response - {str(data)[:100]}"
    except Exception as e:
        return False, f"YukiAPI error: {e}"


@bot.on_message(filters.command(["tgm", "tm", "meow"]))
async def telegraph_upload(_, message):
    reply = message.reply_to_message

    if not reply or not reply.media:
        return await message.reply("❌ Reply to a media file")

    # file size check
    file_size = 0
    if reply.photo:
        file_size = reply.photo.file_size
    elif reply.video:
        file_size = reply.video.file_size
    elif reply.document:
        file_size = reply.document.file_size
    elif reply.animation:
        file_size = reply.animation.file_size
    elif reply.sticker:
        file_size = reply.sticker.file_size

    if file_size > 200 * 1024 * 1024:
        return await message.reply("❌ File must be under 200MB")

    msg = await message.reply("📥 Downloading...")

    try:
        path = await reply.download()
        await msg.edit("📤 Uploading to YukiAPI...")

        import asyncio
        success, result = await asyncio.to_thread(upload_yuki, path)

        if success:
            await msg.edit(
                f"✅ Uploaded Successfully\n\n🔗 {result}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🌐 Open Link", url=result)]]
                ),
                disable_web_page_preview=False
            )
        else:
            await msg.edit(f"❌ Upload failed: {result}")

    except Exception as e:
        await msg.edit(f"❌ Error:\n{e}")

    finally:
        if 'path' in locals() and os.path.exists(path):
            os.remove(path)


__mod_name__ = "Tɢ-M"

__help__ = """
❍ /tgm : Reply to media to get direct link

Supports:
• Video
• Photo
• Document
• Animation
• Sticker

Max Size: 200MB
"""
