import math
from pyrogram import filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from MeowRobot import pbot as app
from MeowRobot.utils.fonts import font

__mod_name__ = "Calculator"
__module__ = "𝐂ᴀʟᴄᴜʟᴀᴛᴏʀ🧮"

__help__ = """
**Calculator🧮**

**Description:**
Perform calculations directly using the bot with an interactive inline keypad.

**Commands:**
❂ `/calc` or `/calculator` – Open interactive calculator
"""

calc_states = {}

def calcExpression(text: str) -> str:
    try:
        if not text.strip():
            return ""
        text = text.replace("×", "*").replace("÷", "/").replace("^", "**")
        # Allowed math functions
        allowed_names = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "pi": math.pi, "e": math.e
        }
        res = eval(text, {"__builtins__": None}, allowed_names)
        return str(round(float(res), 6)).rstrip('0').rstrip('.') if isinstance(res, (int, float)) else str(res)
    except Exception:
        return "Error"

def calc_btn(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("7", callback_data=f"c|{uid}|7"),
            InlineKeyboardButton("8", callback_data=f"c|{uid}|8"),
            InlineKeyboardButton("9", callback_data=f"c|{uid}|9"),
            InlineKeyboardButton("÷", callback_data=f"c|{uid}|/"),
            InlineKeyboardButton(font("DEL"), callback_data=f"c|{uid}|D"),
        ],
        [
            InlineKeyboardButton("4", callback_data=f"c|{uid}|4"),
            InlineKeyboardButton("5", callback_data=f"c|{uid}|5"),
            InlineKeyboardButton("6", callback_data=f"c|{uid}|6"),
            InlineKeyboardButton("×", callback_data=f"c|{uid}|*"),
            InlineKeyboardButton(font("AC"), callback_data=f"c|{uid}|A"),
        ],
        [
            InlineKeyboardButton("1", callback_data=f"c|{uid}|1"),
            InlineKeyboardButton("2", callback_data=f"c|{uid}|2"),
            InlineKeyboardButton("3", callback_data=f"c|{uid}|3"),
            InlineKeyboardButton("-", callback_data=f"c|{uid}|-"),
            InlineKeyboardButton("(", callback_data=f"c|{uid}|("),
        ],
        [
            InlineKeyboardButton("0", callback_data=f"c|{uid}|0"),
            InlineKeyboardButton(".", callback_data=f"c|{uid}|."),
            InlineKeyboardButton("=", callback_data=f"c|{uid}|="),
            InlineKeyboardButton("+", callback_data=f"c|{uid}|+"),
            InlineKeyboardButton(")", callback_data=f"c|{uid}|)"),
        ],
        [
            InlineKeyboardButton(font("❌ Close"), callback_data=f"c|{uid}|C"),
        ],
    ])

@app.on_message(filters.command(["calc", "calculate", "calculator"]) & ~filters.forwarded, group=25)
async def calculate_handler(client, message: Message):
    if not message.from_user:
        return
    
    uid = message.from_user.id
    calc_states[uid] = {"text": ""}
    
    await message.reply_text(
        text="```\n0\n```",
        reply_markup=calc_btn(uid),
        disable_web_page_preview=True,
        quote=True
    )

@app.on_callback_query(filters.regex(r"^c\|"))
async def calc_cb(client, query: CallbackQuery):
    try:
        parts = query.data.split("|")
        uid = int(parts[1])
        data = parts[2]
        
        if query.from_user.id != uid:
            return await query.answer(font("⚠️ This is not your calculator!"), show_alert=True)
        
        if uid not in calc_states:
            calc_states[uid] = {"text": ""}
        
        state = calc_states[uid]
        text = state["text"]
        
        if data == "A":
            text = ""
        elif data == "D":
            text = text[:-1] if text else ""
        elif data == "=":
            text = calcExpression(text)
        elif data == "C":
            await query.message.delete()
            return await query.answer()
        else:
            text += data
        
        state["text"] = text
        
        try:
            display = f"```\n{text if text else '0'}\n```"
            await query.message.edit_text(
                text=display,
                reply_markup=calc_btn(uid),
                disable_web_page_preview=True
            )
        except errors.MessageNotModified:
            pass
        
        await query.answer()
    except Exception:
        await query.answer(font("Error!"), show_alert=False)
