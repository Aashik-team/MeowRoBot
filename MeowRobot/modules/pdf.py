import os
from img2pdf import get_fixed_dpi_layout_fun, convert
from pyrogram import filters, types, enums

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

user_temp = {}

__mod_name__ = "PDF"
__module__ = "𝐏ᴅғ〽️"

__help__ = """
**Commands**:
/img2pdf, /getimg2pdf

❂ `/img2pdf` — Add images to the conversion queue (reply to photo)
❂ `/getimg2pdf` — Convert queued images to a PDF file

**Usage:**
1. Send or reply to an image with `/img2pdf`
2. Repeat for all images you want to include
3. Use `/getimg2pdf` to receive your generated PDF

*Note:* After generating the PDF, your image queue will be cleared automatically.
"""

@bot.on_message(filters.command("img2pdf") & ~filters.forwarded)
async def add_img_to_pdf(_, m: types.Message):
    reply = m.reply_to_message
    user = m.from_user
    if not user:
        return

    if not reply or not reply.photo:
        return await m.reply_text(font("Reply to a photo to convert to pdf."))

    try:
        loading = await m.reply_text(font("⏳ Downloading image..."))
        file_path = await reply.download()

        if user.id not in user_temp:
            user_temp[user.id] = {'images': []}

        user_temp[user.id]['images'].append(file_path)
        images = user_temp[user.id]['images']

        await loading.edit_text(
            f"⚡ Successfully image {len(images)} added to convert!\n"
            f"If you want to add multiple images, continue using `/img2pdf`.\n"
            f"When done, use `/getimg2pdf` to receive the PDF."
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: {str(e)}")


@bot.on_message(filters.command("getimg2pdf") & ~filters.forwarded)
async def generate_pdf(_, m: types.Message):
    user = m.from_user
    if not user:
        return

    if user.id not in user_temp or not user_temp[user.id].get('images'):
        return await m.reply_text(
            "🙋 It seems you haven't added any images to convert to PDF. Please use `/img2pdf` first."
        )

    images = user_temp[user.id].get('images', [])
    loading = await m.reply_text(font("⏳ Generating PDF..."))

    dpix = dpiy = 300
    layout_fun = get_fixed_dpi_layout_fun((dpix, dpiy))
    file_path = f"user_{user.id}_{int(m.date.timestamp() if m.date else 0)}.pdf"

    try:
        with open(file_path, "wb") as f:
            f.write(convert(images, layout_fun=layout_fun))

        bot_name = bot.me.username if bot.me else "MeowRoBot"
        await m.reply_document(
            file_path,
            caption=f"**By @{bot_name} ⚡**",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await loading.delete()

        # Clean up downloaded images
        for img_path in images:
            if os.path.exists(img_path):
                os.remove(img_path)
        user_temp[user.id]['images'].clear()

    except Exception as e:
        await m.reply_text(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
