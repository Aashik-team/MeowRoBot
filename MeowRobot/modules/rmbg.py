#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import os
import asyncio
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Rmbg"
__module__ = "𝐈ᴍᴀɢᴇ🖼️"

__help__ = """
*AI Background Remover Module🖼️*

*Commands:*  
❂ `/rmbg` — Reply to a photo or sticker to automatically remove background and send transparent PNG  
❂ `/removebg` — Same as `/rmbg`  
"""

@bot.on_message(filters.command(["rmbg", "removebg"]) & ~filters.forwarded)
async def remove_background_cmd(_, m: types.Message):
    reply = m.reply_to_message
    if not reply or not (reply.photo or reply.sticker or (reply.document and reply.document.mime_type and "image" in reply.document.mime_type)):
        return await m.reply_text(font("❌ Reply to a photo, sticker, or image document with `/rmbg`!"))

    status_msg = await m.reply_text(font("✂️ Removing background with AI..."))

    temp_input = None
    output_path = None
    try:
        from rembg import remove
        from PIL import Image

        temp_input = await reply.download()
        output_path = f"downloads/rmbg_{m.id}.png"
        os.makedirs("downloads", exist_ok=True)

        def _process():
            inp_img = Image.open(temp_input)
            out_img = remove(inp_img)
            out_img.save(output_path, format="PNG")

        await asyncio.to_thread(_process)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            await m.reply_document(
                document=output_path,
                caption="✨ **Background Removed Successfully!**\n\n♨️ **Powered by:** @TheAloneTeam"
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text(font("❌ Failed to remove background."))
    except ImportError:
        await status_msg.edit_text(font("❌ rembg is initializing, please try again in a few moments!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))
    finally:
        if temp_input and os.path.exists(temp_input):
            try: os.remove(temp_input)
            except Exception: pass
        if output_path and os.path.exists(output_path):
            try: os.remove(output_path)
            except Exception: pass
