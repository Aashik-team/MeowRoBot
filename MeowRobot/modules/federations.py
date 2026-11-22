import uuid
import html
from pyrogram import filters, types, enums

from MeowRobot import pbot as bot, DRAGONS as DEV_LIST
from MeowRobot.utils.fonts import font
from MeowRobot.utils.mongo import db

__mod_name__ = "Federations"
__module__ = "𝐅ᴇᴅᴇʀᴀᴛɪᴏɴs🏛️"

__help__ = """
*Federations Module🏛️*

*Description:*  
Manage shared bans across multiple connected groups. When a spammer or scammer is federation-banned (`/fban`), they are banned across all connected chats!

*Commands:*  
❂ `/newfed <Fed Name>` — Create a new federation (Owner only)  
❂ `/delfed <Fed ID>` — Delete a federation  
❂ `/joinfed <Fed ID>` — Connect your group to a federation (Group Admin only)  
❂ `/leavefed` — Disconnect your group from the federation  
❂ `/chatfed` — View current federation connected to this group  
❂ `/fedinfo <Fed ID>` — View federation details, owner, and banned count  
❂ `/fban <user> <reason>` — Federation-ban a user across all connected groups  
❂ `/unfban <user>` — Remove federation ban for a user  
"""

fed_col = db["federations"]
fed_chats_col = db["fed_chats"]
fed_bans_col = db["fed_bans"]

async def is_group_admin(chat_id: int, user_id: int) -> bool:
    if user_id in DEV_LIST:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

@bot.on_message(filters.command("newfed") & ~filters.forwarded)
async def new_fed(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/newfed <Federation Name>`"))

    fed_name = m.text.split(maxsplit=1)[1].strip()
    fed_id = str(uuid.uuid4())
    user_id = m.from_user.id

    await fed_col.insert_one({
        "fed_id": fed_id,
        "fed_name": fed_name,
        "owner_id": user_id,
        "owner_name": f"{m.from_user.first_name} {m.from_user.last_name or ''}".strip(),
        "admins": [user_id]
    })

    await m.reply_text(
        f"🏛️ **Federation Created Successfully!**\n\n"
        f"📛 **Name:** `{fed_name}`\n"
        f"🆔 **Fed ID:** `{fed_id}`\n\n"
        f"Use `/joinfed {fed_id}` in your groups to connect them to this federation."
    )

@bot.on_message(filters.command("delfed") & ~filters.forwarded)
async def del_fed(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/delfed <Fed ID>`"))

    fed_id = m.command[1].strip()
    fed = await fed_col.find_one({"fed_id": fed_id})

    if not fed:
        return await m.reply_text(font("❌ Federation not found."))

    if fed["owner_id"] != m.from_user.id and m.from_user.id not in DEV_LIST:
        return await m.reply_text(font("❌ Only the federation owner can delete this federation."))

    await fed_col.delete_one({"fed_id": fed_id})
    await fed_chats_col.delete_many({"fed_id": fed_id})
    await fed_bans_col.delete_many({"fed_id": fed_id})

    await m.reply_text(font(f"✅ Federation `{fed.get('fed_name')}` has been deleted."))

@bot.on_message(filters.command("joinfed") & filters.group)
async def join_fed(_, m: types.Message):
    if not await is_group_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can connect to a federation."))

    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/joinfed <Fed ID>`"))

    fed_id = m.command[1].strip()
    fed = await fed_col.find_one({"fed_id": fed_id})

    if not fed:
        return await m.reply_text(font("❌ Federation with that ID does not exist."))

    await fed_chats_col.update_one(
        {"chat_id": m.chat.id},
        {"$set": {"chat_id": m.chat.id, "fed_id": fed_id, "chat_title": m.chat.title}},
        upsert=True
    )

    await m.reply_text(
        f"✅ **Connected to Federation!**\n\n"
        f"🏛️ **Fed Name:** `{fed['fed_name']}`\n"
        f"🆔 **Fed ID:** `{fed_id}`"
    )

@bot.on_message(filters.command("leavefed") & filters.group)
async def leave_fed(_, m: types.Message):
    if not await is_group_admin(m.chat.id, m.from_user.id):
        return await m.reply_text(font("❌ Only group admins can disconnect from a federation."))

    res = await fed_chats_col.delete_one({"chat_id": m.chat.id})
    if res.deleted_count > 0:
        await m.reply_text(font("✅ Group disconnected from federation."))
    else:
        await m.reply_text(font("ℹ️ This group is not connected to any federation."))

@bot.on_message(filters.command("chatfed") & filters.group)
async def chat_fed(_, m: types.Message):
    doc = await fed_chats_col.find_one({"chat_id": m.chat.id})
    if not doc:
        return await m.reply_text(font("ℹ️ This group is not connected to any federation."))

    fed = await fed_col.find_one({"fed_id": doc["fed_id"]})
    fed_name = fed["fed_name"] if fed else "Unknown"

    await m.reply_text(
        f"🏛️ **Connected Federation Info:**\n\n"
        f"📛 **Name:** `{fed_name}`\n"
        f"🆔 **Fed ID:** `{doc['fed_id']}`"
    )

@bot.on_message(filters.command("fedinfo") & ~filters.forwarded)
async def fed_info(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(font("❌ Usage: `/fedinfo <Fed ID>`"))

    fed_id = m.command[1].strip()
    fed = await fed_col.find_one({"fed_id": fed_id})
    if not fed:
        return await m.reply_text(font("❌ Federation not found."))

    chat_count = await fed_chats_col.count_documents({"fed_id": fed_id})
    ban_count = await fed_bans_col.count_documents({"fed_id": fed_id})

    await m.reply_text(
        f"🏛️ **Federation Information:**\n\n"
        f"📛 **Name:** `{fed['fed_name']}`\n"
        f"🆔 **ID:** `{fed_id}`\n"
        f"👑 **Owner:** `{fed.get('owner_name', 'Unknown')}` (`{fed['owner_id']}`)\n"
        f"👥 **Connected Chats:** `{chat_count}`\n"
        f"🚫 **Total FBans:** `{ban_count}`"
    )

@bot.on_message(filters.command("fban") & ~filters.forwarded)
async def fban_user(_, m: types.Message):
    fed_id = None
    if m.chat.type != enums.ChatType.PRIVATE:
        chat_doc = await fed_chats_col.find_one({"chat_id": m.chat.id})
        if chat_doc:
            fed_id = chat_doc["fed_id"]

    if not fed_id:
        # Check if user owns a fed
        owned = await fed_col.find_one({"owner_id": m.from_user.id})
        if owned:
            fed_id = owned["fed_id"]

    if not fed_id:
        return await m.reply_text(font("❌ No federation connected or specified."))

    fed = await fed_col.find_one({"fed_id": fed_id})
    if not fed or (m.from_user.id not in fed.get("admins", []) and m.from_user.id not in DEV_LIST):
        return await m.reply_text(font("❌ Only federation admins can FBan."))

    target_user = None
    reason = "No reason provided"

    if m.reply_to_message and m.reply_to_message.from_user:
        target_user = m.reply_to_message.from_user
        if len(m.command) > 1:
            reason = m.text.split(maxsplit=1)[1]
    elif len(m.command) > 1:
        target_input = m.command[1]
        try:
            target_user = await bot.get_users(target_input)
        except Exception:
            return await m.reply_text(font("❌ User not found."))
        if len(m.command) > 2:
            reason = m.text.split(maxsplit=2)[2]
    else:
        return await m.reply_text(font("❌ Usage: `/fban <user> [reason]` (or reply)"))

    if target_user.id in DEV_LIST:
        return await m.reply_text(font("❌ You cannot FBan a bot developer!"))

    await fed_bans_col.update_one(
        {"fed_id": fed_id, "user_id": target_user.id},
        {"$set": {
            "fed_id": fed_id,
            "user_id": target_user.id,
            "user_name": f"{target_user.first_name} {target_user.last_name or ''}".strip(),
            "reason": reason,
            "banned_by": m.from_user.id
        }},
        upsert=True
    )

    # Ban in current chat immediately if in a group
    if m.chat.type != enums.ChatType.PRIVATE:
        try:
            await bot.ban_chat_member(m.chat.id, target_user.id)
        except Exception:
            pass

    await m.reply_text(
        f"🚫 **Federation Ban Applied!**\n\n"
        f"🏛️ **Fed:** `{fed['fed_name']}`\n"
        f"👤 **User:** {target_user.mention} (`{target_user.id}`)\n"
        f"📝 **Reason:** `{reason}`\n"
        f"👮 **By:** {m.from_user.mention}"
    )

@bot.on_message(filters.command(["unfban", "funban"]) & ~filters.forwarded)
async def unfban_user(_, m: types.Message):
    fed_id = None
    if m.chat.type != enums.ChatType.PRIVATE:
        chat_doc = await fed_chats_col.find_one({"chat_id": m.chat.id})
        if chat_doc:
            fed_id = chat_doc["fed_id"]

    if not fed_id:
        owned = await fed_col.find_one({"owner_id": m.from_user.id})
        if owned:
            fed_id = owned["fed_id"]

    if not fed_id:
        return await m.reply_text(font("❌ No federation connected or specified."))

    fed = await fed_col.find_one({"fed_id": fed_id})
    if not fed or (m.from_user.id not in fed.get("admins", []) and m.from_user.id not in DEV_LIST):
        return await m.reply_text(font("❌ Only federation admins can un-FBan."))

    target_user = None
    if m.reply_to_message and m.reply_to_message.from_user:
        target_user = m.reply_to_message.from_user
    elif len(m.command) > 1:
        try:
            target_user = await bot.get_users(m.command[1])
        except Exception:
            return await m.reply_text(font("❌ User not found."))
    else:
        return await m.reply_text(font("❌ Usage: `/unfban <user>` (or reply)"))

    await fed_bans_col.delete_one({"fed_id": fed_id, "user_id": target_user.id})

    if m.chat.type != enums.ChatType.PRIVATE:
        try:
            await bot.unban_chat_member(m.chat.id, target_user.id)
        except Exception:
            pass

    await m.reply_text(
        f"✅ **Federation Ban Removed!**\n\n"
        f"🏛️ **Fed:** `{fed['fed_name']}`\n"
        f"👤 **User:** {target_user.mention} (`{target_user.id}`)"
    )

@bot.on_message(filters.group & ~filters.bot & ~filters.service, group=98)
async def check_fed_ban_on_message(_, m: types.Message):
    if not m.from_user:
        return

    chat_doc = await fed_chats_col.find_one({"chat_id": m.chat.id})
    if not chat_doc:
        return

    banned = await fed_bans_col.find_one({"fed_id": chat_doc["fed_id"], "user_id": m.from_user.id})
    if banned:
        try:
            await m.delete()
            await bot.ban_chat_member(m.chat.id, m.from_user.id)
            await m.reply_text(
                f"🚫 {m.from_user.mention} is banned in federation **{chat_doc.get('chat_title', '')}**.\nReason: `{banned.get('reason', 'N/A')}`"
            )
        except Exception:
            pass
