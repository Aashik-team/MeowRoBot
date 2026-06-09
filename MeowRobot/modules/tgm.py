

import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MeowRobot import pbot as bot  # <-- apne repo ke hisaab se change karna
from meowbox import upload_async
from meowbox.exceptions import UploadError, RateLimitError


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
        await msg.edit("📤 Uploading to Meowbox...")

        urls = await upload_async(path)
        url = urls[0] if urls else None

        if url:
            await msg.edit(
                f"✅ Uploaded Successfully\n\n🔗 {url}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🌐 Open Link", url=url)]]
                ),
                disable_web_page_preview=False
            )
        else:
            await msg.edit("❌ Upload failed: No URL returned")

    except RateLimitError as e:
        await msg.edit(f"❌ Rate limit hit! Retry after {e.retry_after}s")

    except UploadError as e:
        await msg.edit(f"❌ Meowbox error:\n{e}")

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
