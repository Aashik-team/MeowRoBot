#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/MeowRobot/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MeowRobot import pbot
from MeowRobot.utils.fonts import Fonts


@pbot.on_message(filters.command(["font", "fonts"]))
async def style_buttons(c, m, cb=False):
    buttons = [
        [
            InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="style+typewriter"),
            InlineKeyboardButton("𝕆𝕦𝕥𝕝𝕚𝕟𝕖", callback_data="style+outline"),
            InlineKeyboardButton("𝐒𝐞𝐫𝐢𝐟", callback_data="style+serif"),
        ],
        [
            InlineKeyboardButton("𝑺𝒆𝒓𝒊𝒇", callback_data="style+bold_cool"),
            InlineKeyboardButton("𝑆𝑒𝑟𝑖𝑓", callback_data="style+cool"),
            InlineKeyboardButton("Sᴍᴀʟʟ Cᴀᴘs", callback_data="style+small_cap"),
        ],
        [
            InlineKeyboardButton("𝓈𝒸𝓇𝒾𝓅𝓉", callback_data="style+script"),
            InlineKeyboardButton("𝓼𝓬𝓻𝓲𝓹𝓽", callback_data="style+script_bolt"),
            InlineKeyboardButton("ᵗⁱⁿʸ", callback_data="style+tiny"),
        ],
        [
            InlineKeyboardButton("ᑕOᗰIᑕ", callback_data="style+comic"),
            InlineKeyboardButton("𝗦𝗮𝗻𝘀", callback_data="style+sans"),
            InlineKeyboardButton("𝙎𝙖𝙣𝙨", callback_data="style+slant_sans"),
        ],
        [
            InlineKeyboardButton("𝘚𝘢𝘯𝘴", callback_data="style+slant"),
            InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="style+sim"),
            InlineKeyboardButton("Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎", callback_data="style+circles"),
        ],
        [
            InlineKeyboardButton("🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎", callback_data="style+circle_dark"),
            InlineKeyboardButton("𝔊𝔬𝔱𝔥𝔦𝔠", callback_data="style+gothic"),
            InlineKeyboardButton("𝕲𝖔𝖙𝖍𝖎𝖈", callback_data="style+gothic_bolt"),
        ],
        [
            InlineKeyboardButton("C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡", callback_data="style+cloud"),
            InlineKeyboardButton("H̆̈ă̈p̆̈p̆̈y̆̈", callback_data="style+happy"),
            InlineKeyboardButton("S̑̈ȃ̈d̑̈", callback_data="style+sad"),
        ],
        [InlineKeyboardButton("ɴᴇxᴛ ➻", callback_data="nxt")],
    ]
    if not cb:
        if len(m.text.split()) < 2:
            await m.reply_text("Provide some text to style!")
            return
        await m.reply_text(
            text=m.text.split(None, 1)[1],
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
        )
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


@pbot.on_callback_query(filters.regex("^nxt"))
async def nxt(c, m):
    if m.data == "nxt":
        buttons = [
            [
                InlineKeyboardButton("🇸 🇵 🇪 🇨 🇮 🇦 🇱 ", callback_data="style+special"),
                InlineKeyboardButton("🅂🅀🅄🄰🅁🄴🅂", callback_data="style+squares"),
                InlineKeyboardButton("🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎", callback_data="style+squares_bold"),
            ],
            [
                InlineKeyboardButton("ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ", callback_data="style+andalucia"),
                InlineKeyboardButton("爪卂几ᘜ卂", callback_data="style+manga"),
                InlineKeyboardButton("S̾t̾i̾n̾k̾y̾", callback_data="style+stinky"),
            ],
            [
                InlineKeyboardButton("B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ", callback_data="style+bubbles"),
                InlineKeyboardButton("U͟n͟d͟e͟r͟l͟i͟n͟e͟", callback_data="style+underline"),
                InlineKeyboardButton("꒒ꍏꀷꌩꌃꀎꁅ", callback_data="style+ladybug"),
            ],
            [
                InlineKeyboardButton("R҉a҉y҉s҉", callback_data="style+rays"),
                InlineKeyboardButton("B҈i҈r҈d҈s҈", callback_data="style+birds"),
                InlineKeyboardButton("S̸l̸a̸s̸h̸", callback_data="style+slash"),
            ],
            [
                InlineKeyboardButton("s⃠t⃠o⃠p⃠", callback_data="style+stop"),
                InlineKeyboardButton("S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆", callback_data="style+skyline"),
                InlineKeyboardButton("A͎r͎r͎o͎w͎s͎", callback_data="style+arrows"),
            ],
            [
                InlineKeyboardButton("ዪሀክቿነ", callback_data="style+qvnes"),
                InlineKeyboardButton("S̶t̶r̶i̶k̶e̶", callback_data="style+strike"),
                InlineKeyboardButton("F༙r༙o༙z༙e༙n༙", callback_data="style+frozen"),
            ],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="nxt+0")],
        ]
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await style_buttons(c, m, cb=True)


@pbot.on_callback_query(filters.regex("^style"))
async def style(c, m):
    await m.answer()
    cmd, style_name = m.data.split("+")

    if style_name == "typewriter":
        cls = Fonts.typewriter
    elif style_name == "outline":
        cls = Fonts.outline
    elif style_name == "serif":
        cls = Fonts.serief
    elif style_name == "bold_cool":
        cls = Fonts.bold_cool
    elif style_name == "cool":
        cls = Fonts.cool
    elif style_name == "small_cap":
        cls = Fonts.smallcap
    elif style_name == "script":
        cls = Fonts.script
    elif style_name == "script_bolt":
        cls = Fonts.bold_script
    elif style_name == "tiny":
        cls = Fonts.tiny
    elif style_name == "comic":
        cls = Fonts.comic
    elif style_name == "sans":
        cls = Fonts.san
    elif style_name == "slant_sans":
        cls = Fonts.slant_san
    elif style_name == "slant":
        cls = Fonts.slant
    elif style_name == "sim":
        cls = Fonts.sim
    elif style_name == "circles":
        cls = Fonts.circles
    elif style_name == "circle_dark":
        cls = Fonts.dark_circle
    elif style_name == "gothic":
        cls = Fonts.gothic
    elif style_name == "gothic_bolt":
        cls = Fonts.bold_gothic
    elif style_name == "cloud":
        cls = Fonts.cloud
    elif style_name == "happy":
        cls = Fonts.happy
    elif style_name == "sad":
        cls = Fonts.sad
    elif style_name == "special":
        cls = Fonts.special
    elif style_name == "squares":
        cls = Fonts.square
    elif style_name == "squares_bold":
        cls = Fonts.dark_square
    elif style_name == "andalucia":
        cls = Fonts.andalucia
    elif style_name == "manga":
        cls = Fonts.manga
    elif style_name == "stinky":
        cls = Fonts.stinky
    elif style_name == "bubbles":
        cls = Fonts.bubbles
    elif style_name == "underline":
        cls = Fonts.underline
    elif style_name == "ladybug":
        cls = Fonts.ladybug
    elif style_name == "rays":
        cls = Fonts.rays
    elif style_name == "birds":
        cls = Fonts.birds
    elif style_name == "slash":
        cls = Fonts.slash
    elif style_name == "stop":
        cls = Fonts.stop
    elif style_name == "skyline":
        cls = Fonts.skyline
    elif style_name == "arrows":
        cls = Fonts.arrows
    elif style_name == "qvnes":
        cls = Fonts.rvnes
    elif style_name == "strike":
        cls = Fonts.strike
    elif style_name == "frozen":
        cls = Fonts.frozen
    else:
        return

    new_text = cls(m.message.reply_to_message.text.split(None, 1)[1])
    try:
        await m.message.edit_text(new_text, reply_markup=m.message.reply_markup)
    except:
        pass


__help__ = """
 ❍ /font <text> *:* ᴄᴏɴᴠᴇʀᴛs sɪᴍᴩʟᴇ ᴛᴇxᴛ ᴛᴏ ʙᴇᴀᴜᴛɪғᴜʟ ᴛᴇxᴛ ʙʏ ᴄʜᴀɴɢɪɴɢ ɪᴛ's ғᴏɴᴛ.
 """

__mod_name__ = "Fᴏɴᴛs"
