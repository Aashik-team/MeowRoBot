#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

import random
import httpx
from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "Waifu"
__module__ = "𝐖ᴀɪғᴜ💍"

__help__ = """
*Waifu & Harem Collector Module💍*

*Description:*  
Roll, marry, and build your ultimate anime harem with your friends!

*Commands:*  
❂ `/waifu` — Roll a random anime waifu to admire or marry  
❂ `/marry` — Reply to a rolled waifu to marry her and add to your harem!  
❂ `/mywaifu` (or `/harem`) — View your collection of married waifus  
❂ `/divorce [waifu name]` — Release a waifu from your harem  
"""

harem_col = db["waifu_harems"]
# In-memory tracking of recent rolled waifus per message_id
rolled_waifus = {}

# Popular anime character fallback database
FALLBACK_CHARACTERS = [
    {"name": "Rem", "anime": "Re:Zero", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐⭐"},
    {"name": "Mikasa Ackerman", "anime": "Attack on Titan", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐⭐"},
    {"name": "Nezuko Kamado", "anime": "Demon Slayer", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐"},
    {"name": "Zero Two", "anime": "Darling in the Franxx", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐⭐"},
    {"name": "Hinata Hyuga", "anime": "Naruto", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐"},
    {"name": "Marin Kitagawa", "anime": "My Dress-Up Darling", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐⭐"},
    {"name": "Yor Forger", "anime": "Spy x Family", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐⭐"},
    {"name": "Makima", "anime": "Chainsaw Man", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐⭐"},
    {"name": "Asuka Langley", "anime": "Neon Genesis Evangelion", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐"},
    {"name": "Megumin", "anime": "KonoSuba", "img": "https://files.catbox.moe/k31z1h.jpg", "rarity": "⭐⭐⭐⭐"}
]

@bot.on_message(filters.command(["waifu", "rollwaifu"]) & ~filters.forwarded)
async def roll_waifu(_, m: types.Message):
    # Try fetching from Jikan Top Characters API
    char_data = None
    try:
        page = random.randint(1, 20)
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(f"https://api.jikan.moe/v4/top/characters?page={page}&limit=25")
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                if data:
                    picked = random.choice(data)
                    img = picked.get("images", {}).get("jpg", {}).get("image_url")
                    name = picked.get("name", "Anime Waifu")
                    rarity = random.choice(["⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
                    char_data = {
                        "name": name,
                        "anime": picked.get("about", "")[:40] or "Anime Series",
                        "img": img,
                        "rarity": rarity
                    }
    except Exception:
        pass

    if not char_data or not char_data.get("img"):
        char_data = random.choice(FALLBACK_CHARACTERS)

    caption = (
        f"💖 **A wild Waifu appeared!**\n\n"
        f"🌸 **Name:** `{char_data['name']}`\n"
        f"✨ **Rarity:** {char_data['rarity']}\n\n"
        f"👉 *Reply with `/marry` to add her to your harem!*"
    )

    try:
        sent = await m.reply_photo(photo=char_data["img"], caption=caption)
        rolled_waifus[sent.id] = char_data
    except Exception:
        sent = await m.reply_text(caption)
        rolled_waifus[sent.id] = char_data


@bot.on_message(filters.command("marry") & ~filters.forwarded)
async def marry_waifu(_, m: types.Message):
    if not m.reply_to_message or m.reply_to_message.id not in rolled_waifus:
        return await m.reply_text(font("❌ Reply to a rolled `/waifu` message to marry her!"))

    waifu = rolled_waifus[m.reply_to_message.id]
    user = m.from_user
    user_name = f"{user.first_name} {user.last_name or ''}".strip()

    # Check if already married by someone
    existing = await harem_col.find_one({"waifu_name": waifu["name"]})
    if existing:
        return await m.reply_text(font(f"💔 **{waifu['name']}** is already happily married to [{existing['owner_name']}](tg://user?id={existing['owner_id']})!"))

    # Save to user's harem
    await harem_col.insert_one({
        "owner_id": user.id,
        "owner_name": user_name,
        "waifu_name": waifu["name"],
        "rarity": waifu["rarity"]
    })

    # Remove from roll cache
    del rolled_waifus[m.reply_to_message.id]

    await m.reply_text(
        f"💍 **CONGRATULATIONS!**\n\n"
        f"👰 You are now married to **{waifu['name']}** {waifu['rarity']}!\n"
        f"She has been permanently added to your harem collection."
    )


@bot.on_message(filters.command(["mywaifu", "harem"]) & ~filters.forwarded)
async def my_harem(_, m: types.Message):
    user = m.from_user
    user_name = f"{user.first_name} {user.last_name or ''}".strip()

    harems = await harem_col.find({"owner_id": user.id}).to_list(length=100)
    if not harems:
        return await m.reply_text(font("💔 You haven't married any waifus yet! Use `/waifu` and reply with `/marry` to start your harem."))

    text = f"🏰 **{user_name}'s Harem Collection ({len(harems)})**\n\n"
    for i, w in enumerate(harems, 1):
        text += f"{i}. 🌸 **{w['waifu_name']}** — {w.get('rarity', '⭐⭐⭐')}\n"

    text += f"\n*Use `/divorce [waifu name]` if you want to release any.*"
    await m.reply_text(text)


@bot.on_message(filters.command("divorce") & ~filters.forwarded)
async def divorce_waifu(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/divorce [waifu name]`"))

    waifu_name = m.text.split(None, 1)[1].strip()
    res = await harem_col.delete_one({"owner_id": m.from_user.id, "waifu_name": {"$regex": f"^{waifu_name}$", "$options": "i"}})
    if res.deleted_count > 0:
        await m.reply_text(font(f"💔 You have divorced **{waifu_name}**. She is now free for others to marry!"))
    else:
        await m.reply_text(font(f"❌ You are not married to **{waifu_name}**!"))
