#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

from math import ceil
from typing import Dict, List
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from MeowRobot import NO_LOAD, OWNER_ID


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def split_message(msg: str) -> List[str]:
    # PTB v20+ doesn't have MAX_MESSAGE_LENGTH constant in telegram, it's 4096
    MAX_MESSAGE_LENGTH = 4096
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MAX_MESSAGE_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    else:
        # Else statement at the end of the for loop, so append the leftover string.
        result.append(small_msg)

    return result


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i * 3 : (i + 1) * 3] for i in range((len(modules) + 3 - 1) // 3)]

    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc in [1, 2]:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 4)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 3:
        pairs = pairs[modulo_page * 4 : 4 * (modulo_page + 1)] + [
            [
                EqInlineKeyboardButton(
                    "◁", callback_data="{}_prev({})".format(prefix, modulo_page)
                ),
                EqInlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="MeowRoBot_back"),
                EqInlineKeyboardButton(
                    "▷", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            ]
        ]

    else:
        pairs += [[EqInlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="MeowRoBot_back")]]

    return pairs


def article(
    title: str = "",
    description: str = "",
    message_text: str = "",
    thumb_url: str = None,
    reply_markup: InlineKeyboardMarkup = None,
    disable_web_page_preview: bool = False,
) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        id=str(uuid4()),
        title=title,
        description=description,
        thumb_url=thumb_url,
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            disable_web_page_preview=disable_web_page_preview,
        ),
        reply_markup=reply_markup,
    )


async def send_to_list(
    bot, send_to: list, message: str, markdown=False, html=False
) -> None:
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        try:
            if markdown:
                await bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                await bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        url = btn.url
        if url.startswith("@"):
            url = "https://t.me/{}".format(url[1:])
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=url)])

    return keyb


def revert_buttons(buttons):
    res = ""
    for btn in buttons:
        if btn.same_line:
            res += "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        else:
            res += "\n[{}](buttonurl://{})".format(btn.name, btn.url)

    return res


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        url = btn.url
        if url == "{rules}":
            url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if url.startswith("@"):
            url = "https://t.me/{}".format(url[1:])
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=url)])

    return keyb


def build_keyboard_alternate(buttons):
    keyb = []
    for btn in buttons:
        url = btn[1]
        if url.startswith("@"):
            url = "https://t.me/{}".format(url[1:])
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=url))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=url)])

    return keyb


def is_module_loaded(name):
    return name not in NO_LOAD
