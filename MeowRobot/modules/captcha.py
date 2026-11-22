import asyncio
from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "Captcha"
__module__ = "𝐂ᴀᴘᴛᴄʜᴀ🛡️"

__help__ = """
*Captcha Verification🛡️*

*Description:*  
Prevent automated userbots and spammers from joining and spamming your group. When enabled, new members are muted until they click the verification button.

*Commands:*  
❂ `/captcha on` — Enable captcha verification in this group  
❂ `/captcha off` — Disable captcha verification  
❂ `/captcha` — Check current captcha status in this group  

*Note:* Bot must have Admin rights to restrict and unrestrict members!
"""

captcha_db = db["captcha"]

async def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

@bot.on_message(filters.command("captcha") & filters.group)
async def captcha_toggle(_, message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(font("❌ Only admins can manage Captcha."))

    if len(message.command) < 2:
        doc = await captcha_db.find_one({"chat_id": message.chat.id})
        status = "ENABLED" if doc and doc.get("enabled") else "DISABLED"
        return await message.reply_text(
            f"🛡️ **Captcha Status:** `{status}`\n\nUsage: `/captcha on` or `/captcha off`"
        )

    arg = message.command[1].strip().lower()
    if arg in ["on", "enable", "yes"]:
        await captcha_db.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"chat_id": message.chat.id, "enabled": True}},
            upsert=True
        )
        await message.reply_text(font("✅ Captcha verification is now ENABLED in this group."))
    elif arg in ["off", "disable", "no"]:
        await captcha_db.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"chat_id": message.chat.id, "enabled": False}},
            upsert=True
        )
        await message.reply_text(font("❌ Captcha verification is now DISABLED in this group."))
    else:
        await message.reply_text("Usage:\n`/captcha on` or `/captcha off`")

@bot.on_message(filters.new_chat_members & filters.group, group=99)
async def on_user_join(_, message: types.Message):
    doc = await captcha_db.find_one({"chat_id": message.chat.id})
    if not doc or not doc.get("enabled"):
        return

    for new_user in message.new_chat_members:
        if new_user.is_bot:
            continue

        try:
            # Mute new user immediately
            await bot.restrict_chat_member(
                message.chat.id,
                new_user.id,
                types.ChatPermissions()
            )
        except Exception:
            continue

        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I am Human / Verify", callback_data=f"cptch_ver#{new_user.id}")]
        ])

        try:
            await message.reply_text(
                f"👋 Welcome {new_user.mention} to **{message.chat.title}**!\n\n"
                f"🛡️ Please click the button below to verify yourself and unmute.",
                reply_markup=button
            )
        except Exception:
            pass

@bot.on_callback_query(filters.regex(r"^cptch_ver#"))
async def on_captcha_verify(_, query: types.CallbackQuery):
    target_id = int(query.data.split("#")[1])
    clicker_id = query.from_user.id

    if clicker_id != target_id:
        return await query.answer("⚠️ This captcha is not for you!", show_alert=True)

    try:
        # Restore chat permissions
        chat_perms = (await bot.get_chat(query.message.chat.id)).permissions
        await bot.restrict_chat_member(query.message.chat.id, target_id, chat_perms)
    except Exception:
        pass

    try:
        await query.message.delete()
    except Exception:
        pass

    await query.answer("✅ Verification successful! You can now chat.", show_alert=True)
