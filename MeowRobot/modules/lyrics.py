#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import urllib.parse
import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Lyrics"
__module__ = "𝐋ʏʀɪᴄs📜"

__help__ = """
*Song Lyrics Module📜*

*Commands:*  
❂ `/lyrics [song name]` — Search and get complete lyrics for any song  
"""

@bot.on_message(filters.command(["lyrics", "lyric"]) & ~filters.forwarded)
async def search_lyrics(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/lyrics [song name]`"))

    query = m.text.split(None, 1)[1].strip()
    status_msg = await m.reply_text(font("🔍 Searching lyrics for you..."))

    url = f"https://lrclib.net/api/search?q={urllib.parse.quote(query)}"

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                results = resp.json()
                if results and isinstance(results, list):
                    # Find first result with lyrics
                    for track in results:
                        lyrics_text = track.get("plainLyrics") or track.get("syncedLyrics")
                        if lyrics_text:
                            track_name = track.get("trackName") or query
                            artist_name = track.get("artistName") or "Unknown Artist"
                            album_name = track.get("albumName") or ""

                            # Clean up synced lyrics timestamps if present
                            if track.get("syncedLyrics") and not track.get("plainLyrics"):
                                import re
                                lyrics_text = re.sub(r"\[\d+:\d+\.\d+\]", "", lyrics_text).strip()

                            header = (
                                f"🎵 **{track_name}**\n"
                                f"🎤 **Artist:** `{artist_name}`\n"
                            )
                            if album_name:
                                header += f"💿 **Album:** `{album_name}`\n"
                            header += f"\n━━━━━━━━━━━━━━━━━━━━\n\n"

                            full_text = header + lyrics_text

                            if len(full_text) > 4000:
                                full_text = full_text[:3950] + "\n\n...[Lyrics truncated due to length]"

                            await status_msg.edit_text(full_text)
                            return

        await status_msg.edit_text(font("❌ No lyrics found for this song. Please check the spelling!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error fetching lyrics: {e}"))
