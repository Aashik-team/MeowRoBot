#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

from pyrate_limiter import BucketFullException, Duration, Limiter, Rate
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, BaseHandler

import MeowRobot.modules.sql.blacklistusers_sql as sql
from MeowRobot import ALLOW_EXCL, DEMONS, DEV_USERS, DRAGONS, TIGERS, WOLVES

if ALLOW_EXCL:
    CMD_STARTERS = ("/", "!")
else:
    CMD_STARTERS = ("/",)


class AntiSpam:
    def __init__(self):
        self.whitelist = (
            list(DEV_USERS or [])
            + list(DRAGONS or [])
            + list(WOLVES or [])
            + list(DEMONS or [])
            + list(TIGERS or [])
        )
        # Values are HIGHLY experimental, its recommended you pay attention to our commits as we will be adjusting the values over time with what suits best.
        self.sec_limit = Rate(6, 15)  # 6 / Per 15 Seconds
        self.min_limit = Rate(20, 60)  # 20 / Per minute
        self.hour_limit = Rate(100, 3600)  # 100 / Per hour
        self.daily_limit = Rate(1000, 86400)  # 1000 / Per day
        self.rates = [self.sec_limit, self.min_limit, self.hour_limit, self.daily_limit]
        self.limiter = Limiter(self.rates)

    def check_user(self, user):
        """
        Return True if user is to be ignored else False
        """
        if user in self.whitelist:
            return False
        try:
            self.limiter.try_acquire(user)
            return False
        except BucketFullException:
            return True


SpamChecker = AntiSpam()
MessageHandlerChecker = AntiSpam()


class CustomCommandHandler(CommandHandler):
    def __init__(self, command, callback, admin_ok=False, allow_edit=False, **kwargs):
        super().__init__(command, callback, **kwargs)
        self.allow_edit = allow_edit

    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if not self.allow_edit and (update.edited_message or update.edited_channel_post):
                return None

            try:
                user_id = update.effective_user.id
            except:
                user_id = None

            if user_id:
                if sql.is_user_blacklisted(user_id):
                    return None

            if message.text and len(message.text) > 1:
                fst_word = message.text.split(None, 1)[0]
                if len(fst_word) > 1 and any(
                    fst_word.startswith(start) for start in CMD_STARTERS
                ):
                    command_parts = fst_word[1:].split("@")

                    if user_id == 1087968824:
                        user_id = update.effective_chat.id

                    if command_parts[0].lower() not in [c.lower() for c in self.commands]:
                        return None

                    if len(command_parts) > 1 and command_parts[1].lower() != update.get_bot().username.lower():
                        return None

                    if SpamChecker.check_user(user_id):
                        return None

                    return super().check_update(update)


class CustomMessageHandler(MessageHandler):
    def __init__(self, filters, callback, friendly="", allow_edit=False, **kwargs):
        super().__init__(filters, callback, **kwargs)
        self.allow_edit = allow_edit

    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message:
            if not self.allow_edit and (update.edited_message or update.edited_channel_post):
                return None
            return super().check_update(update)
