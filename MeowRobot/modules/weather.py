#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import urllib.parse
import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Weather"
__module__ = "𝐖ᴇᴀᴛʜᴇʀ⛅"

__help__ = """
*Weather Forecast Module⛅*

*Commands:*  
❂ `/weather [city name]` — Get live weather conditions, temperature, and forecast  
"""

@bot.on_message(filters.command(["weather", "temp"]) & ~filters.forwarded)
async def get_weather(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/weather [city name]` (e.g. `/weather Delhi`)"))

    city = m.text.split(None, 1)[1].strip()
    status_msg = await m.reply_text(font(f"🔍 Checking weather for {city}..."))

    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_condition", [{}])[0]
                area_info = data.get("nearest_area", [{}])[0]

                area_name = area_info.get("areaName", [{}])[0].get("value", city.capitalize())
                country = area_info.get("country", [{}])[0].get("value", "")

                temp_c = current.get("temp_C", "N/A")
                temp_f = current.get("temp_F", "N/A")
                feels_c = current.get("FeelsLikeC", "N/A")
                feels_f = current.get("FeelsLikeF", "N/A")
                desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
                humidity = current.get("humidity", "N/A")
                wind_kph = current.get("windspeedKmph", "N/A")
                uv = current.get("uvIndex", "N/A")
                cloudcover = current.get("cloudcover", "N/A")

                weather_text = (
                    f"⛅ **Weather for {area_name}, {country}**\n\n"
                    f"🌡️ **Temperature:** `{temp_c}°C` ({temp_f}°F)\n"
                    f"🤔 **Feels Like:** `{feels_c}°C` ({feels_f}°F)\n"
                    f"🌤️ **Condition:** `{desc}`\n"
                    f"💧 **Humidity:** `{humidity}%`\n"
                    f"💨 **Wind Speed:** `{wind_kph} km/h`\n"
                    f"☁️ **Cloud Cover:** `{cloudcover}%`\n"
                    f"☀️ **UV Index:** `{uv}`"
                )

                await status_msg.edit_text(weather_text)
                return

        await status_msg.edit_text(font("❌ City not found! Please check the spelling."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error getting weather: {e}"))
