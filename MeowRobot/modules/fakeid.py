#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "FakeID"
__module__ = "𝐔ᴛɪʟɪᴛʏ🛠️"

__help__ = """
*Fake Identity Generator Module👤*

*Description:*  
Generates random realistic identity profiles for testing signups, form filling, and development.

*Commands:*  
❂ `/fakeid` — Generate a realistic random user profile with avatar  
❂ `/fakeinfo` — Same as `/fakeid`  
"""

@bot.on_message(filters.command(["fakeid", "fakeinfo"]) & ~filters.forwarded)
async def generate_fake_id(_, m: types.Message):
    status_msg = await m.reply_text(font("👤 Generating realistic profile..."))

    url = "https://randomuser.me/api/"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json().get("results", [{}])[0]
                name_info = data.get("name", {})
                full_name = f"{name_info.get('title', '')} {name_info.get('first', '')} {name_info.get('last', '')}".strip()

                gender = data.get("gender", "Unknown").capitalize()
                email = data.get("email", "N/A")
                phone = data.get("phone", "N/A")
                cell = data.get("cell", "N/A")

                loc = data.get("location", {})
                street = f"{loc.get('street', {}).get('number', '')} {loc.get('street', {}).get('name', '')}".strip()
                city = loc.get("city", "N/A")
                state = loc.get("state", "N/A")
                country = loc.get("country", "N/A")
                postcode = loc.get("postcode", "N/A")

                dob_info = data.get("dob", {})
                dob = (dob_info.get("date") or "").split("T")[0]
                age = dob_info.get("age", "N/A")

                username = data.get("login", {}).get("username", "N/A")
                password = data.get("login", {}).get("password", "N/A")

                picture = data.get("picture", {}).get("large")

                caption = (
                    f"👤 **Fake Identity Profile**\n\n"
                    f"📛 **Name:** `{full_name}`\n"
                    f"⚧️ **Gender:** `{gender}` | **Age:** `{age}`\n"
                    f"🎂 **DOB:** `{dob}`\n"
                    f"📧 **Email:** `{email}`\n"
                    f"📞 **Phone:** `{phone}`\n"
                    f"📱 **Cell:** `{cell}`\n\n"
                    f"📍 **Address:**\n"
                    f"🏠 **Street:** `{street}`\n"
                    f"🏙️ **City:** `{city}`\n"
                    f"🗺️ **State:** `{state}`\n"
                    f"🌍 **Country:** `{country}`\n"
                    f"📮 **Postal Code:** `{postcode}`\n\n"
                    f"🔑 **Credentials:**\n"
                    f"👤 **Username:** `{username}`\n"
                    f"🔒 **Password:** `{password}`"
                )

                if picture:
                    await m.reply_photo(photo=picture, caption=caption)
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(caption)
                return

        await status_msg.edit_text(font("❌ Failed to generate fake profile. Please try again!"))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error: {e}"))
