#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import datetime
from typing import List
import asyncio

import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from MeowRobot import TIME_API_KEY, application
from MeowRobot.modules.disable import DisableAbleCommandHandler


async def generate_time(to_find: str, findtype: List[str]) -> str:
    loop = asyncio.get_event_loop()
    data = None
    if TIME_API_KEY:
        try:
            response = await loop.run_in_executor(None, requests.get,
                f"https://api.timezonedb.com/v2.1/list-time-zone"
                f"?key={TIME_API_KEY}"
                f"&format=json"
                f"&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst"
            )
            data = response.json()
        except Exception:
            data = None

    country_name = country_zone = country_code = daylight_saving = current_day = current_time = current_date = None

    if data and "zones" in data:
        for zone in data.get("zones", []):
            for eachtype in findtype:
                if to_find in zone[eachtype].lower():
                    country_name = zone["countryName"]
                    country_zone = zone["zoneName"]
                    country_code = zone["countryCode"]
                    daylight_saving = "Yes" if zone["dst"] == 1 else "No"
                    gmt_offset = zone["gmtOffset"]
                    timestamp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=gmt_offset)
                    current_date = timestamp.strftime(r"%d-%m-%Y")
                    current_time = timestamp.strftime(r"%H:%M:%S")
                    current_day = timestamp.strftime(r"%A")
                    break
            if country_name:
                break

    # Robust pytz fallback (no API key required)
    if not country_name:
        import pytz
        clean_q = to_find.lower().replace(" ", "_").strip()
        matched_tz = None

        # Check country code map
        if len(clean_q) == 2 and clean_q.upper() in pytz.country_timezones:
            matched_tz = pytz.country_timezones[clean_q.upper()][0]
        else:
            for tz_cand in pytz.all_timezones:
                if clean_q in tz_cand.lower():
                    matched_tz = tz_cand
                    break

        if matched_tz:
            tz = pytz.timezone(matched_tz)
            now_dt = datetime.datetime.now(tz)
            country_name = matched_tz.split("/")[0] if "/" in matched_tz else "World"
            country_zone = matched_tz
            country_code = matched_tz.split("/")[-1] if "/" in matched_tz else matched_tz
            daylight_saving = "Yes" if now_dt.dst() else "No"
            current_date = now_dt.strftime(r"%d-%m-%Y")
            current_time = now_dt.strftime(r"%H:%M:%S")
            current_day = now_dt.strftime(r"%A")

    if not country_name:
        return None

    return (
        f"<b>Zone:</b> <code>{country_zone}</code>\n"
        f"<b>Region:</b> <code>{country_name}</code>\n"
        f"<b>Day:</b> <code>{current_day}</code>\n"
        f"<b>Current Time:</b> <code>{current_time}</code>\n"
        f"<b>Current Date:</b> <code>{current_date}</code>\n"
        f"<b>Daylight Saving:</b> <code>{daylight_saving}</code>\n"
        '<b>Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>'
    )


async def gettime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message.text:
        return

    try:
        query = message.text.strip().split(" ", 1)[1]
    except IndexError:
        await message.reply_text("Provide a country name/abbreviation/timezone to find.")
        return

    sent_msg = await message.reply_text(
        f"Finding timezone info for <b>{query}</b>", parse_mode=ParseMode.HTML
    )

    query_timezone = query.lower()
    if len(query_timezone) == 2:
        result = await generate_time(query_timezone, ["countryCode"])
    else:
        result = await generate_time(query_timezone, ["zoneName", "countryName"])

    if not result:
        await sent_msg.edit_text(
            f"Timezone info not available for <b>{query}</b>\n"
            '<b>All Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    await sent_msg.edit_text(
        result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


__help__ = """
 ❍ /time <query>*:* Gives information about a timezone.
*Available queries:* Country Code/Country Name/Timezone Name

 ❍ ⏰ [ᴛɪᴍᴇᴢᴏɴᴇs ʟɪsᴛ](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

💡 Ex:- /time IN *:* It will shows Indian current time and date..
"""

TIME_HANDLER = DisableAbleCommandHandler("time", gettime)

application.add_handler(TIME_HANDLER)

__mod_name__ = "Tɪᴍᴇ"
__command_list__ = ["time"]
__handlers__ = [TIME_HANDLER]
