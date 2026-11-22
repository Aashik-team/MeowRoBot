import aiohttp
import asyncio
from pyrogram import filters

from MeowRobot import pbot as app
from MeowRobot.utils.fonts import font

__mod_name__ = "IP"
__module__ = "𝐈ᴘ✨"

__help__ = """
*Commands*:
❂ `/ip <address>` — Fetch information and geolocation for an IP address.

*Example*:
`/ip 162.243.19.47`
"""

async def lookup(ip: str):
    url = f"http://ip-api.com/json/{ip}"
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error: HTTP {response.status}"
                
                ip_info = await response.json()
                
                if ip_info.get('status') == 'fail':
                    return f"Error: {ip_info.get('message', 'Failed to lookup IP')}"
                
                bot_user = app.me.username if app.me else "MeowRoBot"
                info = (
                    f"\n**ℹ️ IP Information Lookup Result**:\n\n"
                    f"**IP Address**: `{ip_info.get('query', 'N/A')}`\n"
                    f"**Country**: {ip_info.get('country', 'N/A')} ({ip_info.get('countryCode', 'N/A')})\n"
                    f"**Region**: {ip_info.get('regionName', 'N/A')} ({ip_info.get('region', 'N/A')})\n"
                    f"**City**: {ip_info.get('city', 'N/A')}\n"
                    f"**ZIP Code**: {ip_info.get('zip', 'N/A')}\n"
                    f"**Latitude**: `{ip_info.get('lat', 'N/A')}`\n"
                    f"**Longitude**: `{ip_info.get('lon', 'N/A')}`\n"
                    f"**ISP**: {ip_info.get('isp', 'N/A')}\n"
                    f"**Organization**: {ip_info.get('org', 'N/A')}\n"
                    f"**AS**: {ip_info.get('as', 'N/A')}\n\n"
                    f"**By @{bot_user}**"
                )
                return info
    except aiohttp.ClientError as e:
        return f"An error occurred: {e}"
    except asyncio.TimeoutError:
        return "Error: The request timed out. Please try again later."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@app.on_message(filters.command('ip') & ~filters.forwarded)
async def ip_lookup(_, message):
    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not query:
        return await message.reply_text(font('**Please provide an IP address!**\nExample: `/ip 8.8.8.8`'))
    
    result = await lookup(query)
    await message.reply_text(result)
