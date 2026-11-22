#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "CAS"
__module__ = "𝐒ᴇᴄᴜʀɪᴛʏ🛡️"

__help__ = """
*Combot Anti-Spam (CAS) Checker Module🛡️*

*Description:*  
Check whether a Telegram user is flagged in the global Combot Anti-Spam (CAS) database as a known scammer or spammer.

*Commands:*  
❂ `/cas [user_id or username]` — Check user ban status in CAS  
❂ `/scamcheck [user_id or username]` — Same as `/cas`  
❂ Reply to any user with `/cas`  
"""

@bot.on_message(filters.command(["cas", "scamcheck"]) & ~filters.forwarded)
async def check_cas_status(_, m: types.Message):
    target_user = None

    if m.reply_to_message and m.reply_to_message.from_user:
        target_user = m.reply_to_message.from_user
    elif len(m.command) > 1:
        user_input = m.command[1].strip()
        try:
            if user_input.isdigit():
                target_user = await bot.get_users(int(user_input))
            else:
                target_user = await bot.get_users(user_input)
        except Exception:
            return await m.reply_text(font("❌ User not found."))
    else:
        target_user = m.from_user

    if not target_user:
        return await m.reply_text(font("❌ Usage: `/cas [user_id or username]` or reply to a user."))

    status_msg = await m.reply_text(font(f"🔍 Checking CAS database for {target_user.first_name}..."))

    url = f"https://api.cas.chat/check?user_id={target_user.id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                is_banned = data.get("ok", False)

                mention = f"[{target_user.first_name}](tg://user?id={target_user.id})"

                if is_banned:
                    result = data.get("result", {})
                    offenses = result.get("offenses", 1)
                    time_added = result.get("time_added", "N/A")
                    reply_text = (
                        f"🚨 **CAS BANNED USER DETECTED!** 🚨\n\n"
                        f"👤 **User:** {mention} (`{target_user.id}`)\n"
                        f"🚫 **Status:** Banned in CAS Database\n"
                        f"⚠️ **Total Offenses:** `{offenses}`\n"
                        f"📅 **Added on:** `{time_added}`\n\n"
                        f"⚠️ *This user has a history of spamming or scamming across Telegram groups.*"
                    )
                else:
                    reply_text = (
                        f"🛡️ **CAS Anti-Spam Check**\n\n"
                        f"👤 **User:** {mention} (`{target_user.id}`)\n"
                        f"✅ **Status:** Clean (Not banned in CAS)\n"
                        f"✨ *No global spam infractions found.*"
                    )

                return await status_msg.edit_text(reply_text)

        await status_msg.edit_text(font("❌ Failed to query CAS API. Please try again later."))
    except Exception as e:
        await status_msg.edit_text(font(f"❌ Error checking CAS status: {e}"))
