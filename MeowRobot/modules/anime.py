import aiohttp
from urllib.parse import quote
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Anime"
__module__ = "𝐀ɴɪᴍᴇ🎌"

__help__ = """
*Anime & Character Info🎌*

*Description:*  
Search anime information, character bios, and details directly from MyAnimeList.

*Commands:*  
❂ `/anime <anime_name>` — Search details about an anime series  
❂ `/character <character_name>` — Search details about an anime character  

*Examples:*  
`/anime Naruto`  
`/character Levi Ackerman`
"""

JIKAN_URL = "https://api.jikan.moe/v4"

@bot.on_message(filters.command("anime") & ~filters.forwarded)
async def anime_search(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide an anime name.\nExample: `/anime Attack on Titan`"))

    query = m.text.split(maxsplit=1)[1].strip()
    loading = await m.reply_text(font("⏳ Searching MyAnimeList..."))

    try:
        url = f"{JIKAN_URL}/anime?q={quote(query)}&limit=1"
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await loading.edit_text(font("❌ Could not connect to Anime API."))
                data = await resp.json()
                results = data.get("data", [])
                if not results:
                    return await loading.edit_text(font("❌ No anime found matching that query."))

                anime = results[0]
                title = anime.get("title", "N/A")
                title_japanese = anime.get("title_japanese", "N/A")
                score = anime.get("score", "N/A")
                episodes = anime.get("episodes", "Unknown")
                status = anime.get("status", "N/A")
                synopsis = anime.get("synopsis", "No synopsis available.")[:500] + "..."
                image_url = anime.get("images", {}).get("jpg", {}).get("large_image_url")
                mal_url = anime.get("url", "")

                caption = (
                    f"🎬 **{title}** ({title_japanese})\n\n"
                    f"⭐ **Score:** `{score}`\n"
                    f"📺 **Episodes:** `{episodes}`\n"
                    f"📡 **Status:** `{status}`\n\n"
                    f"📖 **Synopsis:**\n{synopsis}\n\n"
                    f"🔗 [View on MyAnimeList]({mal_url})"
                )

                if image_url:
                    await m.reply_photo(image_url, caption=caption)
                    await loading.delete()
                else:
                    await loading.edit_text(caption, disable_web_page_preview=True)
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")

@bot.on_message(filters.command("character") & ~filters.forwarded)
async def character_search(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Please provide a character name.\nExample: `/character Gojo Satoru`"))

    query = m.text.split(maxsplit=1)[1].strip()
    loading = await m.reply_text(font("⏳ Searching character details..."))

    try:
        url = f"{JIKAN_URL}/characters?q={quote(query)}&limit=1"
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await loading.edit_text(font("❌ Could not connect to Anime API."))
                data = await resp.json()
                results = data.get("data", [])
                if not results:
                    return await loading.edit_text(font("❌ No character found matching that name."))

                char = results[0]
                name = char.get("name", "N/A")
                name_kanji = char.get("name_kanji", "N/A")
                nicknames = ", ".join(char.get("nicknames", [])) or "None"
                about = (char.get("about", "No description available.") or "")[:500] + "..."
                image_url = char.get("images", {}).get("jpg", {}).get("image_url")
                mal_url = char.get("url", "")

                caption = (
                    f"👤 **{name}** ({name_kanji})\n"
                    f"🏷️ **Nicknames:** {nicknames}\n\n"
                    f"📝 **About:**\n{about}\n\n"
                    f"🔗 [View on MyAnimeList]({mal_url})"
                )

                if image_url:
                    await m.reply_photo(image_url, caption=caption)
                    await loading.delete()
                else:
                    await loading.edit_text(caption, disable_web_page_preview=True)
    except Exception as e:
        await loading.edit_text(f"❌ **Error:** {e}")
