import os
import random
import aiohttp
from io import BytesIO
from PIL import Image
from pyrogram import filters, types
from pyrogram.enums import ParseMode

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Upscale"
__module__ = "𝐔ᴘsᴄᴀʟᴇʀ🖼️"

__help__ = """
*Upscaler*

*Description:*  
Upscale low resolution images up to 4× HD resolution using AI.

*Commands:*  
❂ `/upscale` — Reply to a photo to upscale it ×4  
❂ `/upscale anime` — Use anime-optimized upscaling mode  

*Example:*  
`/upscale` (reply to a photo)
"""

upscaling_users = {}

async def upscale_image(buffer: bytes, anime: bool = False) -> str:
    try:
        random_num = random.randint(1_000_000, 999_999_999)
        with Image.open(BytesIO(buffer)) as img:
            width, height = img.size

        form_data = aiohttp.FormData()
        form_data.add_field("image_file", buffer, filename="image.jpg", content_type="image/jpeg")
        form_data.add_field("name", str(random_num))
        form_data.add_field("desiredHeight", str(height * 4))
        form_data.add_field("desiredWidth", str(width * 4))
        form_data.add_field("outputFormat", "png")
        form_data.add_field("anime", str(anime).lower())

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://upscalepics.com",
            "Referer": "https://upscalepics.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post("https://api.upscalepics.com/upscale-to-size", data=form_data, headers=headers) as resp:
                if resp.status == 200:
                    json_res = await resp.json()
                    return json_res.get("bgRemoved", "").strip()
    except Exception:
        pass
    return None

@bot.on_message(filters.command("upscale") & ~filters.forwarded)
async def upscale_cmd(_, m: types.Message):
    user = m.from_user
    if not user:
        return

    if upscaling_users.get(user.id, False):
        return await m.reply(font("⚠️ You already have an ongoing upscale process."))

    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply(font("📷 Reply to a photo to upscale it."))

    upscaling_users[user.id] = True
    loading = await m.reply(font("🔄 Upscaling your image with AI..."))

    local_file = None
    output_file = None

    try:
        anime = "anime" in m.text.lower()
        local_file = await m.reply_to_message.download()
        with open(local_file, "rb") as f:
            buffer = f.read()

        image_url = await upscale_image(buffer, anime=anime)
        if not image_url or not image_url.startswith("http"):
            return await loading.edit_text(font("❌ Upscaling failed. Please try again later."))

        timeout = aiohttp.ClientTimeout(total=45)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(image_url) as r:
                if r.status == 200:
                    output_file = f"upscaled_{m.id}.png"
                    with open(output_file, "wb") as f:
                        f.write(await r.read())

                    bot_name = bot.me.username if bot.me else "MeowRoBot"
                    await m.reply_document(
                        output_file,
                        caption=f"✨ **Upscaled by @{bot_name}**"
                    )
                    await loading.delete()
                else:
                    await loading.edit_text(font("❌ Failed to download upscaled image."))
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** `{e}`")
    finally:
        if local_file and os.path.exists(local_file):
            os.remove(local_file)
        if output_file and os.path.exists(output_file):
            os.remove(output_file)
        upscaling_users.pop(user.id, None)
