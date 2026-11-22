import random
import string
from pyrogram import filters, types
from pyrogram.enums import ParseMode

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Passwords"
__module__ = "𝐏ᴀssᴡᴏʀᴅs🔑"

__help__ = """
❂ *Commands*:
❂ `/password` or `/passwords`

❂ *Description:*  
Generate secure, random, readable, or complex passwords instantly using interactive buttons.
"""

NOUNS = [
    "Shadow", "Tiger", "Dragon", "Phoenix", "Eagle", "Falcon", "Wolf", "Hunter",
    "Knight", "Storm", "Viper", "Ghost", "Wizard", "Ninja", "Warrior", "Legend",
    "Titan", "Panther", "Blaze", "Frost", "Thunder", "Rocket", "Cyber", "Matrix"
]

ADJECTIVES = [
    "Brave", "Swift", "Silent", "Fierce", "Golden", "Crimson", "Mighty", "Cosmic",
    "Infinite", "Dynamic", "Electric", "Dark", "Epic", "Savage", "Neon", "Atomic",
    "Stealth", "Hyper", "Prime", "Royal", "Lucky", "Clever", "Iron", "Sharp"
]

SYMBOLS = ['#', '$', '_', '@', '!', '%']

class PasswordGen:
    @staticmethod
    def easy_password(count: int = 5) -> list:
        passwords = []
        for _ in range(count):
            word = random.choice(NOUNS) + random.choice(ADJECTIVES)
            passwords.append(word + str(random.randint(100, 9999)))
        return passwords

    @staticmethod
    def normal_password(count: int = 5) -> list:
        passwords = []
        for _ in range(count):
            word = random.choice(ADJECTIVES) + random.choice(SYMBOLS) + random.choice(NOUNS)
            passwords.append(word + str(random.randint(100, 9999)))
        return passwords

    @staticmethod
    def random_password(count: int = 5, length: int = 12, digits_only: bool = False, chars_only: bool = False) -> list:
        chars = ""
        if digits_only:
            chars = string.digits
        elif chars_only:
            chars = string.ascii_letters
        else:
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
        
        return [''.join(random.choice(chars) for _ in range(length)) for _ in range(count)]

def get_buttons(user_id: int):
    return [
        [
            types.InlineKeyboardButton(font("🔢 Digits"), callback_data=f"pw_digits#{user_id}"),
            types.InlineKeyboardButton(font("🔤 Strings"), callback_data=f"pw_strings#{user_id}"),
            types.InlineKeyboardButton(font("🎲 Random"), callback_data=f"pw_random#{user_id}")
        ],
        [
            types.InlineKeyboardButton(font("📘 Normal Password"), callback_data=f"pw_normal#{user_id}"),
            types.InlineKeyboardButton(font("📙 Easy Password"), callback_data=f"pw_easy#{user_id}")
        ],
        [
            types.InlineKeyboardButton(font("❌ Close"), callback_data=f"pw_close#{user_id}")
        ]
    ]

@bot.on_message(filters.command(["password", "passwords"]) & ~filters.forwarded, group=-38)
async def GenPasswordCmd(_, message: types.Message):
    user = message.from_user
    bot_name = bot.me.username if bot.me else "MeowRoBot"
    text = (
        "🔐 **Password Generator**\n"
        "Click a button below to generate secure passwords.\n\n"
        f"_By @{bot_name}_"
    )

    buttons = get_buttons(user.id if user else 0)
    await message.reply_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

@bot.on_callback_query(filters.regex(r"^pw_"))
async def GenPasswordCq(_, query: types.CallbackQuery):
    cmd, user_id_str = query.data.split("#")
    user_id = int(user_id_str)

    if query.from_user.id != user_id:
        return await query.answer(font("This is not your request."), show_alert=True)

    if cmd == "pw_close":
        await query.message.delete()
        return await query.answer()

    password_list = []
    if cmd == "pw_random":
        password_list = PasswordGen.random_password(count=5, length=12)
    elif cmd == "pw_digits":
        password_list = PasswordGen.random_password(count=5, length=8, digits_only=True)
    elif cmd == "pw_strings":
        password_list = PasswordGen.random_password(count=5, length=10, chars_only=True)
    elif cmd == "pw_normal":
        password_list = PasswordGen.normal_password(count=5)
    elif cmd == "pw_easy":
        password_list = PasswordGen.easy_password(count=5)
    else:
        return await query.answer(font("Unknown command"), show_alert=True)

    bot_name = bot.me.username if bot.me else "MeowRoBot"
    text = "**🔐 Generated Passwords:**\n\n"
    text += "\n".join(f"`{p}`" for p in password_list)
    text += "\n\n⚙️ **Choose options below:**"
    text += f"\n_By @{bot_name}_"

    buttons = get_buttons(user_id)
    await query.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )
    await query.answer()
