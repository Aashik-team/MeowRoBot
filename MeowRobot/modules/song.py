#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import asyncio
import os
import re
import json
import logging
import urllib.parse
import time
from typing import Union, Optional

import httpx
import yt_dlp
from pyrogram import filters, types, enums

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

logger = logging.getLogger(__name__)

__mod_name__ = "Song"
__module__ = "𝐒ᴏɴɢ🎵"

__help__ = """
*Song & Video Downloader Module🎵*

*Commands:*  
❂ `/song [song name or link]` — Download high quality MP3 audio from YouTube  
❂ `/music [song name or link]` — Same as `/song`  
❂ `/vsong [video name or link]` — Download MP4 video from YouTube  
❂ `/video [video name or link]` — Same as `/vsong`  
"""

# Monkey patch httpx to remain compatible with older libraries (like youtube-search-python) in newer HTTPX versions
try:
    original_async_init = httpx.AsyncClient.__init__
    def patched_async_init(self, *args, **kwargs):
        if 'proxies' in kwargs:
            proxies = kwargs.pop('proxies')
            if proxies:
                kwargs['proxy'] = proxies
        return original_async_init(self, *args, **kwargs)
    httpx.AsyncClient.__init__ = patched_async_init

    original_client_init = httpx.Client.__init__
    def patched_client_init(self, *args, **kwargs):
        if 'proxies' in kwargs:
            proxies = kwargs.pop('proxies')
            if proxies:
                kwargs['proxy'] = proxies
        return original_client_init(self, *args, **kwargs)
    httpx.Client.__init__ = patched_client_init
except Exception:
    pass

try:
    from youtubesearchpython.__future__ import VideosSearch
except ImportError:
    try:
        from youtubesearchpython import VideosSearch
    except ImportError:
        VideosSearch = None

# Configuration
API_URL = os.getenv("API_URL", "http://web.riteshyt.in").rstrip("/")
API_KEY = os.getenv("API_KEY", "riteshpermanent_6e2e564b3b37175d82acfce7").strip()

def time_to_seconds(time_str: str) -> int:
    if not time_str:
        return 0
    try:
        parts = [int(x) for x in time_str.split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
    except Exception:
        pass
    return 0

def extract_vidid(query: str) -> Optional[str]:
    if not query:
        return None
    if re.match(r"^[a-zA-Z0-9_-]{11}$", query):
        return query
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|shorts\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, query)
    return match.group(1) if match else None

async def download_assistant(query: str, dl_type: str) -> str:
    """Helper to get stream URL from the API"""
    safe_query = urllib.parse.quote(query)
    ext = "mp3" if dl_type == "audio" else "mp4"
    if API_KEY:
        url = f"{API_URL}/downloads/{API_KEY}/{safe_query}.{ext}"
    else:
        url = f"{API_URL}/downloads/stream?query={safe_query}&dl_type={dl_type}"
    return url

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self._client = None

    async def get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=10.0), follow_redirects=True)
        return self._client

    def _clean_link(self, link: str):
        if not link:
            return ""
        link = str(link)
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
        return link

    async def _fetch_details(self, link: str):
        link = self._clean_link(link)
        client = await self.get_client()
        params = {"link": link}
        if API_KEY:
            params["api_key"] = API_KEY
        try:
            response = await client.get(f"{API_URL}/details", params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Error fetching details from API: {e}")
        return None

    async def details(self, link: str):
        link = self._clean_link(link)

        # API first
        if API_URL:
            data = await self._fetch_details(link)
            if data:
                return (
                    data.get("title") or "Unknown Title",
                    data.get("duration_min") or "00:00",
                    int(data.get("duration_sec") or 0),
                    data.get("thumbnail"),
                    data.get("vidid") or extract_vidid(link)
                )

        # Fallback to local VideosSearch
        if VideosSearch:
            try:
                results = VideosSearch(link, limit=1)
                if hasattr(results, 'next') and asyncio.iscoroutinefunction(results.next):
                    res = await results.next()
                else:
                    res = results.next()
                if res and res.get("result"):
                    result = res["result"][0]
                    title = result["title"]
                    duration_min = result["duration"]
                    thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                    vidid = result["id"]
                    duration_sec = int(time_to_seconds(duration_min)) if duration_min and duration_min != "None" else 0
                    return title, duration_min, duration_sec, thumbnail, vidid
            except Exception as e:
                logger.warning(f"Local VideosSearch fallback failed in details: {e}")

        # Fallback using search_youtube_seed
        vid, title = await search_youtube_seed(link)
        if vid:
            return title or "Unknown", "00:00", 0, f"https://img.youtube.com/vi/{vid}/hqdefault.jpg", vid

        return None, None, 0, None, None

    async def download(
        self,
        link: str,
        dl_type: str = "audio",
        vidid: Optional[str] = None,
        title: Optional[str] = None
    ) -> Optional[str]:
        vidid_extracted = vidid or extract_vidid(link) or link
        ext = "mp4" if dl_type == "video" else "mp3"
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title or vidid_extracted)[:50].strip() or vidid_extracted
        filepath = os.path.join("downloads", f"{safe_title}.{ext}")
        os.makedirs("downloads", exist_ok=True)

        # Helper to download from API
        async def download_from_api() -> bool:
            if not API_URL:
                return False

            # Try 1: URL via API key path
            url1 = await download_assistant(vidid_extracted, dl_type)
            try:
                async with httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client:
                    async with client.stream("GET", url1) as resp:
                        if resp.status_code == 200:
                            with open(filepath, "wb") as f:
                                async for chunk in resp.aiter_bytes(131072):
                                    f.write(chunk)
                            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                                return True
            except Exception as e:
                logger.warning(f"API download try 1 failed: {e}")

            # Try 2: Stream endpoint
            safe_query = urllib.parse.quote(vidid_extracted)
            if API_KEY:
                url2 = f"{API_URL}/downloads/stream?query={safe_query}&dl_type={dl_type}&api_key={API_KEY}"
            else:
                url2 = f"{API_URL}/downloads/stream?query={safe_query}&dl_type={dl_type}"
            try:
                async with httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client:
                    async with client.stream("GET", url2) as resp:
                        if resp.status_code == 200:
                            with open(filepath, "wb") as f:
                                async for chunk in resp.aiter_bytes(131072):
                                    f.write(chunk)
                            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                                return True
            except Exception as e:
                logger.warning(f"API download try 2 failed: {e}")

            # Try 3: /download endpoint
            try:
                params = {"query": vidid_extracted, "dl_type": dl_type}
                if API_KEY:
                    params["api_key"] = API_KEY
                async with httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client:
                    async with client.stream("GET", f"{API_URL}/download", params=params) as resp:
                        if resp.status_code == 200:
                            with open(filepath, "wb") as f:
                                async for chunk in resp.aiter_bytes(131072):
                                    f.write(chunk)
                            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                                return True
            except Exception as e:
                logger.warning(f"API download try 3 failed: {e}")

            if os.path.exists(filepath):
                try: os.remove(filepath)
                except Exception: pass
            return False

        # Try API first
        if await download_from_api():
            return filepath

        # Fallback to local yt-dlp
        loop = asyncio.get_running_loop()
        def _ytdl_download():
            target_link = f"https://www.youtube.com/watch?v={vidid_extracted}"
            if dl_type == "video":
                opts = {
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "outtmpl": filepath,
                    "quiet": True,
                    "no_warnings": True,
                    "geo_bypass": True,
                }
            else:
                opts = {
                    "format": "bestaudio/best",
                    "outtmpl": filepath.replace(".mp3", "") + ".%(ext)s",
                    "quiet": True,
                    "no_warnings": True,
                    "geo_bypass": True,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([target_link])
            return filepath

        try:
            res_path = await loop.run_in_executor(None, _ytdl_download)
            if os.path.exists(res_path) and os.path.getsize(res_path) > 0:
                return res_path
        except Exception as e:
            logger.error(f"Local yt-dlp download failed: {e}")

        return None


YouTube = YouTubeAPI()


async def search_youtube_seed(query: str):
    """Search YouTube for a seed video"""
    if not query:
        return None, None
    try:
        loop = asyncio.get_running_loop()
        def _search():
            url = "https://www.youtube.com/youtubei/v1/search"
            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20240101.00.00",
                        "hl": "en",
                        "gl": "US"
                    }
                },
                "query": query
            }
            import urllib.request
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            sections = data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", [])
            for sec in sections:
                items = sec.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    v = item.get("videoRenderer", {})
                    vid = v.get("videoId")
                    if vid:
                        title = v.get("title", {}).get("runs", [{}])[0].get("text")
                        return vid, title
            return None, None

        return await loop.run_in_executor(None, _search)
    except Exception as e:
        logger.debug(f"search_youtube_seed error: {e}")
        return None, None


async def download_thumbnail(thumb_url: str, vidid: str) -> Optional[str]:
    if not thumb_url:
        return None
    thumb_path = os.path.join("downloads", f"{vidid}_thumb.jpg")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(thumb_url)
            if resp.status_code == 200:
                with open(thumb_path, "wb") as f:
                    f.write(resp.content)
                return thumb_path
    except Exception:
        pass
    return None


@bot.on_message(filters.command(["song", "music"]) & ~filters.forwarded)
async def song_download_cmd(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/song [song name or YouTube link]`"))

    query = m.text.split(None, 1)[1].strip()
    status_msg = await m.reply_text(font("🔎 Searching YouTube for your song..."))

    title, duration_min, duration_sec, thumb_url, vidid = await YouTube.details(query)
    if not vidid:
        return await status_msg.edit_text(font("❌ Could not find the requested song on YouTube."))

    await status_msg.edit_text(font(f"📥 Downloading: **{title}**..."))

    file_path = await YouTube.download(link=query, dl_type="audio", vidid=vidid, title=title)
    if not file_path or not os.path.exists(file_path):
        return await status_msg.edit_text(font("❌ Failed to download audio. Please try again later."))

    thumb_path = await download_thumbnail(thumb_url, vidid)

    caption = (
        f"🎵 **{title}**\n\n"
        f"⏳ **Duration:** `{duration_min}`\n"
        f"🔗 **YouTube:** [Watch on YouTube](https://www.youtube.com/watch?v={vidid})\n"
        f"👤 **Requested by:** {m.from_user.mention if m.from_user else 'User'}\n\n"
        f"♨️ **Powered by:** @TheAloneTeam"
    )

    await status_msg.edit_text(font("📤 Uploading audio to Telegram..."))

    try:
        await m.reply_audio(
            audio=file_path,
            caption=caption,
            duration=duration_sec,
            title=title,
            performer="MeowRoBot",
            thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Error sending audio: {e}")
        await status_msg.edit_text(font(f"❌ Failed to send audio: {e}"))
    finally:
        # Cleanup temporary files
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except Exception: pass
        if thumb_path and os.path.exists(thumb_path):
            try: os.remove(thumb_path)
            except Exception: pass


@bot.on_message(filters.command(["vsong", "video"]) & ~filters.forwarded)
async def video_download_cmd(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/video [video name or YouTube link]`"))

    query = m.text.split(None, 1)[1].strip()
    status_msg = await m.reply_text(font("🔎 Searching YouTube for your video..."))

    title, duration_min, duration_sec, thumb_url, vidid = await YouTube.details(query)
    if not vidid:
        return await status_msg.edit_text(font("❌ Could not find the requested video on YouTube."))

    await status_msg.edit_text(font(f"📥 Downloading: **{title}**..."))

    file_path = await YouTube.download(link=query, dl_type="video", vidid=vidid, title=title)
    if not file_path or not os.path.exists(file_path):
        return await status_msg.edit_text(font("❌ Failed to download video. Please try again later."))

    thumb_path = await download_thumbnail(thumb_url, vidid)

    caption = (
        f"🎬 **{title}**\n\n"
        f"⏳ **Duration:** `{duration_min}`\n"
        f"🔗 **YouTube:** [Watch on YouTube](https://www.youtube.com/watch?v={vidid})\n"
        f"👤 **Requested by:** {m.from_user.mention if m.from_user else 'User'}\n\n"
        f"♨️ **Powered by:** @TheAloneTeam"
    )

    await status_msg.edit_text(font("📤 Uploading video to Telegram..."))

    try:
        await m.reply_video(
            video=file_path,
            caption=caption,
            duration=duration_sec,
            thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Error sending video: {e}")
        await status_msg.edit_text(font(f"❌ Failed to send video: {e}"))
    finally:
        # Cleanup temporary files
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except Exception: pass
        if thumb_path and os.path.exists(thumb_path):
            try: os.remove(thumb_path)
            except Exception: pass
