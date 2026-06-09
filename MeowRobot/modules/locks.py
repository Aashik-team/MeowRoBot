#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

import html
import unicodedata as ud

from telegram import ChatPermissions, MessageEntity, Update
from telegram.constants import ParseMode, ChatType, ChatMemberStatus
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler, filters, MessageHandler
from telegram.helpers import mention_html

import MeowRobot.modules.sql.locks_sql as sql
from MeowRobot import DRAGONS, LOGGER, application
from MeowRobot.modules.connection import connected
from MeowRobot.modules.disable import DisableAbleCommandHandler
from MeowRobot.modules.helper_funcs.alternate import send_message, typing_action
from MeowRobot.modules.helper_funcs.chat_status import (
    can_delete,
    is_bot_admin,
    is_user_admin,
    user_admin,
    user_not_admin,
)
from MeowRobot.modules.log_channel import loggable
from MeowRobot.modules.sql.approve_sql import is_approved


def al_detect(unistr):
    return set(ud.name(char).split(" ")[0] for char in unistr if char.isalpha())


LOCK_TYPES = {
    "audio": filters.AUDIO,
    "voice": filters.VOICE,
    "document": filters.Document.ALL,
    "video": filters.VIDEO,
    "contact": filters.CONTACT,
    "photo": filters.PHOTO,
    "url": filters.Entity(MessageEntity.URL)
    | filters.CaptionEntity(MessageEntity.URL),
    "bots": filters.StatusUpdate.NEW_CHAT_MEMBERS,
    "forward": filters.FORWARDED,
    "game": filters.GAME,
    "location": filters.LOCATION,
    "egame": filters.Dice.ALL,
    "rtl": "rtl",
    "button": "button",
    "inline": "inline",
}

LOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": False,
        "can_send_polls": False,
        "can_send_other_messages": False,
        "can_add_web_page_previews": False,
        "can_change_info": False,
        "can_invite_users": False,
        "can_pin_messages": False,
        "can_send_audios": False,
        "can_send_documents": False,
        "can_send_photos": False,
        "can_send_videos": False,
        "can_send_video_notes": False,
        "can_send_voice_notes": False,
    },
    "messages": {"can_send_messages": False},
    "media": {
        "can_send_audios": False,
        "can_send_documents": False,
        "can_send_photos": False,
        "can_send_videos": False,
        "can_send_video_notes": False,
        "can_send_voice_notes": False,
    },
    "sticker": {"can_send_other_messages": False},
    "gif": {"can_send_other_messages": False},
    "poll": {"can_send_polls": False},
    "other": {"can_send_other_messages": False},
    "previews": {"can_add_web_page_previews": False},
    "info": {"can_change_info": False},
    "invite": {"can_invite_users": False},
    "pin": {"can_pin_messages": False},
}

UNLOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": True,
        "can_send_polls": True,
        "can_send_other_messages": True,
        "can_add_web_page_previews": True,
        "can_invite_users": True,
        "can_send_audios": True,
        "can_send_documents": True,
        "can_send_photos": True,
        "can_send_videos": True,
        "can_send_video_notes": True,
        "can_send_voice_notes": True,
    },
    "messages": {"can_send_messages": True},
    "media": {
        "can_send_audios": True,
        "can_send_documents": True,
        "can_send_photos": True,
        "can_send_videos": True,
        "can_send_video_notes": True,
        "can_send_voice_notes": True,
    },
    "sticker": {"can_send_other_messages": True},
    "gif": {"can_send_other_messages": True},
    "poll": {"can_send_polls": True},
    "other": {"can_send_other_messages": True},
    "previews": {"can_add_web_page_previews": True},
    "info": {"can_change_info": True},
    "invite": {"can_invite_users": True},
    "pin": {"can_pin_messages": True},
}

PERM_GROUP = 1
REST_GROUP = 2


async def locktypes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "\n • ".join(
            ["Locks available: "]
            + sorted(list(LOCK_TYPES) + list(LOCK_CHAT_RESTRICTION))
        )
    )


@user_admin
@loggable
@typing_action
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if (
        await can_delete(chat, context.bot.id)
        or update.effective_message.chat.type == ChatType.PRIVATE
    ):
        if len(args) >= 1:
            ltype = args[0].lower()
            if ltype in LOCK_TYPES:
                # Connection check
                conn = await connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat_obj = await context.bot.get_chat(conn)
                    chat_id = conn
                    chat_name = chat_obj.title
                    text = "Locked {} for non-admins in {}!".format(ltype, chat_name)
                else:
                    if update.effective_message.chat.type == ChatType.PRIVATE:
                        await send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = "Locked {} for non-admins!".format(ltype)
                sql.update_lock(chat_id, ltype, locked=True)
                await send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)

                return (
                    "<b>{}:</b>"
                    "\n#LOCK"
                    "\n<b>Admin:</b> {}"
                    "\nLocked <code>{}</code>.".format(
                        html.escape(chat_name),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )

            elif ltype in LOCK_CHAT_RESTRICTION:
                # Connection check
                conn = await connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat_obj = await context.bot.get_chat(conn)
                    chat_id = conn
                    chat_name = chat_obj.title
                    text = "Locked {} for all non-admins in {}!".format(
                        ltype, chat_name
                    )
                else:
                    if update.effective_message.chat.type == ChatType.PRIVATE:
                        await send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = "Locked {} for all non-admins!".format(ltype)

                current_chat = await context.bot.get_chat(chat_id)
                current_permission = current_chat.permissions

                await context.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=get_permission_list(
                        current_permission.to_dict(),
                        LOCK_CHAT_RESTRICTION[ltype.lower()],
                    ),
                )

                await send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
                return (
                    "<b>{}:</b>"
                    "\n#Permission_LOCK"
                    "\n<b>Admin:</b> {}"
                    "\nLocked <code>{}</code>.".format(
                        html.escape(chat_name),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )

            else:
                await send_message(
                    update.effective_message,
                    "What are you trying to lock...? Try /locktypes for the list of lockables",
                )
        else:
            await send_message(update.effective_message, "What are you trying to lock...?")

    else:
        await send_message(
            update.effective_message,
            "I am not administrator or haven't got enough rights.",
        )

    return ""


@user_admin
@loggable
@typing_action
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    if await is_user_admin(chat, message.from_user.id):
        if len(args) >= 1:
            ltype = args[0].lower()
            if ltype in LOCK_TYPES:
                # Connection check
                conn = await connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat_obj = await context.bot.get_chat(conn)
                    chat_id = conn
                    chat_name = chat_obj.title
                    text = "Unlocked {} for everyone in {}!".format(ltype, chat_name)
                else:
                    if update.effective_message.chat.type == ChatType.PRIVATE:
                        await send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = "Unlocked {} for everyone!".format(ltype)
                sql.update_lock(chat_id, ltype, locked=False)
                await send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
                return (
                    "<b>{}:</b>"
                    "\n#UNLOCK"
                    "\n<b>Admin:</b> {}"
                    "\nUnlocked <code>{}</code>.".format(
                        html.escape(chat_name),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )

            elif ltype in UNLOCK_CHAT_RESTRICTION:
                # Connection check
                conn = await connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat_obj = await context.bot.get_chat(conn)
                    chat_id = conn
                    chat_name = chat_obj.title
                    text = "Unlocked {} for everyone in {}!".format(ltype, chat_name)
                else:
                    if update.effective_message.chat.type == ChatType.PRIVATE:
                        await send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = "Unlocked {} for everyone!".format(ltype)

                member = await chat.get_member(context.bot.id)
                if not getattr(member, 'can_change_info', False):
                    await send_message(
                        update.effective_message,
                        "I don't have permission to change group info.",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    return ""

                current_chat = await context.bot.get_chat(chat_id)
                current_permission = current_chat.permissions

                await context.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=get_permission_list(
                        current_permission.to_dict(),
                        UNLOCK_CHAT_RESTRICTION[ltype.lower()],
                    ),
                )

                await send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)

                return (
                    "<b>{}:</b>"
                    "\n#UNLOCK"
                    "\n<b>Admin:</b> {}"
                    "\nUnlocked <code>{}</code>.".format(
                        html.escape(chat_name),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )
            else:
                await send_message(
                    update.effective_message,
                    "What are you trying to unlock...? Try /locktypes for the list of lockables.",
                )

        else:
            await send_message(update.effective_message, "What are you trying to unlock...?")

    return ""


@user_not_admin
async def del_lockables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    if is_approved(chat.id, user.id):
        return
    for lockable, filter in LOCK_TYPES.items():
        if lockable == "rtl":
            if sql.is_locked(chat.id, lockable) and await can_delete(chat, context.bot.id):
                if message.caption:
                    check = al_detect("{}".format(message.caption))
                    if "ARABIC" in check:
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "Message to delete not found":
                                pass
                            else:
                                LOGGER.exception("ERROR in lockables")
                        break
                if message.text:
                    check = al_detect("{}".format(message.text))
                    if "ARABIC" in check:
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "Message to delete not found":
                                pass
                            else:
                                LOGGER.exception("ERROR in lockables")
                        break
            continue
        if lockable == "button":
            if sql.is_locked(chat.id, lockable) and await can_delete(chat, context.bot.id):
                if message.reply_markup and message.reply_markup.inline_keyboard:
                    try:
                        await message.delete()
                    except BadRequest as excp:
                        if excp.message == "Message to delete not found":
                            pass
                        else:
                            LOGGER.exception("ERROR in lockables")
                    break
            continue
        if lockable == "inline":
            if sql.is_locked(chat.id, lockable) and await can_delete(chat, context.bot.id):
                if message and message.via_bot:
                    try:
                        await message.delete()
                    except BadRequest as excp:
                        if excp.message == "Message to delete not found":
                            pass
                        else:
                            LOGGER.exception("ERROR in lockables")
                    break
            continue

        if isinstance(filter, filters.BaseFilter):
            res = filter.check_update(update)
        else:
            res = False

        if (
            res
            and sql.is_locked(chat.id, lockable)
            and await can_delete(chat, context.bot.id)
        ):
            if lockable == "bots":
                new_members = update.effective_message.new_chat_members
                for new_mem in new_members:
                    if new_mem.is_bot:
                        if not await is_bot_admin(chat, context.bot.id):
                            await send_message(
                                update.effective_message,
                                "I see a bot and I've been told to stop them from joining..."
                                "but I'm not admin!",
                            )
                            return

                        await chat.ban_member(new_mem.id)
                        await send_message(
                            update.effective_message,
                            "Only admins are allowed to add bots in this chat! Get outta here.",
                        )
                        break
            else:
                try:
                    await message.delete()
                except BadRequest as excp:
                    if excp.message == "Message to delete not found":
                        pass
                    else:
                        LOGGER.exception("ERROR in lockables")

                break


async def build_lock_message(chat_id):
    locks = sql.get_locks(chat_id)
    res = ""
    locklist = []
    permslist = []
    if locks:
        res += "*" + "These are the current locks in this Chat:" + "*"
        locklist.append("sticker = `{}`".format(locks.sticker))
        locklist.append("audio = `{}`".format(locks.audio))
        locklist.append("voice = `{}`".format(locks.voice))
        locklist.append("document = `{}`".format(locks.document))
        locklist.append("video = `{}`".format(locks.video))
        locklist.append("contact = `{}`".format(locks.contact))
        locklist.append("photo = `{}`".format(locks.photo))
        locklist.append("gif = `{}`".format(locks.gif))
        locklist.append("url = `{}`".format(locks.url))
        locklist.append("bots = `{}`".format(locks.bots))
        locklist.append("forward = `{}`".format(locks.forward))
        locklist.append("game = `{}`".format(locks.game))
        locklist.append("location = `{}`".format(locks.location))
        locklist.append("rtl = `{}`".format(locks.rtl))
        locklist.append("button = `{}`".format(locks.button))
        locklist.append("egame = `{}`".format(locks.egame))
        locklist.append("inline = `{}`".format(locks.inline))

    chat = await context.bot.get_chat(chat_id)
    permissions = chat.permissions
    permslist.append("messages = `{}`".format(permissions.can_send_messages))
    permslist.append("audios = `{}`".format(permissions.can_send_audios))
    permslist.append("documents = `{}`".format(permissions.can_send_documents))
    permslist.append("photos = `{}`".format(permissions.can_send_photos))
    permslist.append("videos = `{}`".format(permissions.can_send_videos))
    permslist.append("video_notes = `{}`".format(permissions.can_send_video_notes))
    permslist.append("voice_notes = `{}`".format(permissions.can_send_voice_notes))
    permslist.append("poll = `{}`".format(permissions.can_send_polls))
    permslist.append("other = `{}`".format(permissions.can_send_other_messages))
    permslist.append("previews = `{}`".format(permissions.can_add_web_page_previews))
    permslist.append("info = `{}`".format(permissions.can_change_info))
    permslist.append("invite = `{}`".format(permissions.can_invite_users))
    permslist.append("pin = `{}`".format(permissions.can_pin_messages))

    if locklist:
        # Ordering lock list
        locklist.sort()
        # Building lock list string
        for x in locklist:
            res += "\n • {}".format(x)
    res += "\n\n*" + "These are the current chat permissions:" + "*"
    for x in permslist:
        res += "\n • {}".format(x)
    return res


@user_admin
@typing_action
async def list_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # Connection check
    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_obj = await context.bot.get_chat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == ChatType.PRIVATE:
            await send_message(
                update.effective_message,
                "This command is meant to use in group not in PM",
            )
            return
        chat_name = update.effective_message.chat.title

    res = await build_lock_message(chat.id)
    if conn:
        res = res.replace("Locks in", "*{}*".format(chat_name))

    await send_message(update.effective_message, res, parse_mode=ParseMode.MARKDOWN)


def get_permission_list(current, new):
    permissions = {
        "can_send_messages": None,
        "can_send_audios": None,
        "can_send_documents": None,
        "can_send_photos": None,
        "can_send_videos": None,
        "can_send_video_notes": None,
        "can_send_voice_notes": None,
        "can_send_polls": None,
        "can_send_other_messages": None,
        "can_add_web_page_previews": None,
        "can_change_info": None,
        "can_invite_users": None,
        "can_pin_messages": None,
    }
    permissions.update(current)
    permissions.update(new)

    # Filter out obsolete keys
    allowed_keys = {
        "can_send_messages", "can_send_audios", "can_send_documents", "can_send_photos",
        "can_send_videos", "can_send_video_notes", "can_send_voice_notes", "can_send_polls",
        "can_send_other_messages", "can_add_web_page_previews", "can_change_info",
        "can_invite_users", "can_pin_messages", "can_manage_topics"
    }
    filtered_permissions = {k: v for k, v in permissions.items() if k in allowed_keys}

    new_permissions = ChatPermissions(**filtered_permissions)
    return new_permissions


def __import_data__(chat_id, data):
    # set chat locks
    locks = data.get("locks", {})
    for itemlock in locks:
        if itemlock in LOCK_TYPES:
            sql.update_lock(chat_id, itemlock, locked=True)
        elif itemlock in LOCK_CHAT_RESTRICTION:
            sql.update_restriction(chat_id, itemlock, locked=True)
        else:
            pass


async def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


async def __chat_settings__(chat_id, user_id):
    return await build_lock_message(chat_id)


__help__ = """
Do stickers annoy you? or want to avoid people sharing links? or pictures? \
You're in the right place!
The locks module allows you to lock away some common items in the \
telegram world; the bot will automatically delete them!

 ❍ /locktypes*:* Lists all possible locktypes
 
*Admins only:*
 ❍ /lock <type>*:* Lock items of a certain type (not available in private)
 ❍ /unlock <type>*:* Unlock items of a certain type (not available in private)
 ❍ /locks*:* The current list of locks in this chat.
 
Locks can be used to restrict a group's users.
eg:
Locking urls will auto-delete all messages with urls, locking stickers will restrict all \
non-admin users from sending stickers, etc.
Locking bots will stop non-admins from adding bots to the chat.

*Note:*
 • Unlocking permission *info* will allow members (non-admins) to change the group information, such as the description or the group name
 • Unlocking permission *pin* will allow members (non-admins) to pin a message in a group
"""

__mod_name__ = "Lᴏᴄᴋs"

LOCKTYPES_HANDLER = DisableAbleCommandHandler("locktypes", locktypes)
LOCK_HANDLER = CommandHandler(
    "lock", lock
)
UNLOCK_HANDLER = CommandHandler(
    "unlock", unlock
)
LOCKED_HANDLER = CommandHandler(
    "locks", list_locks
)

application.add_handler(LOCK_HANDLER)
application.add_handler(UNLOCK_HANDLER)
application.add_handler(LOCKTYPES_HANDLER)
application.add_handler(LOCKED_HANDLER)

DEL_LOCKABLES_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, del_lockables
)
application.add_handler(DEL_LOCKABLES_HANDLER, PERM_GROUP)

__handlers__ = [
    LOCK_HANDLER,
    UNLOCK_HANDLER,
    LOCKTYPES_HANDLER,
    LOCKED_HANDLER,
    (DEL_LOCKABLES_HANDLER, PERM_GROUP),
]
