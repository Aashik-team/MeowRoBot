import aiohttp
from urllib.parse import quote
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Shortener"
__module__ = "𝐒ʜᴏʀᴛ🔗"

__help__ = """
*URL Shortener & Expander🔗*

*Description:*  
Create short, shareable links or unshorten/expand suspicious short links safely.

*Commands:*  
❂ `/short <long_url>` — Shorten a long URL via TinyURL  
❂ `/unshort <short_url>` — Expand a shortened URL to see original destination  

*Examples:*  
`/short https://en.wikipedia.org/wiki/Artificial_intelligence`  
`/unshort https://tinyurl.com/2b3xyz`
"""

@bot.on_message(filters.command(["short", "shorten"]) & ~filters.forwarded)
async def shorten_url(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide a URL to shorten.\nExample: `/short https://example.com`"))

    long_url = m.command[1].strip()
    if not long_url.startswith("http://") and not long_url.startswith("https://"):
        long_url = f"https://{long_url}"

    loading = await m.reply_text(font("⏳ Shortening URL..."))

    try:
        api_url = f"https://tinyurl.com/api-create.php?url={quote(long_url)}"
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    short_link = (await resp.text()).strip()
                    await loading.edit_text(
                        f"🔗 **Shortened URL:**\n`{short_link}`\n\nOriginal: `{long_url}`",
                        disable_web_page_preview=True
                    )
                else:
                    await loading.edit_text(font("❌ Failed to shorten URL. Make sure it's valid."))
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")

@bot.on_message(filters.command(["unshort", "unshorten", "expand"]) & ~filters.forwarded)
async def unshorten_url(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide a short URL to expand.\nExample: `/unshort https://tinyurl.com/...`"))

    short_url = m.command[1].strip()
    if not short_url.startswith("http://") and not short_url.startswith("https://"):
        short_url = f"https://{short_url}"

    loading = await m.reply_text(font("⏳ Expanding URL..."))

    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(short_url, allow_redirects=True) as resp:
                final_url = str(resp.url)
                await loading.edit_text(
                    f"🔍 **Original Destination:**\n`{final_url}`\n\nShort URL: `{short_url}`",
                    disable_web_page_preview=True
                )
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")
