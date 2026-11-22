#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# All rights reserved.

from pyrogram import filters, types

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "Style"
__module__ = "𝐅ᴏɴᴛs✒️"

__help__ = """
*Fancy Font Styler Module✒️*

*Commands:*  
❂ `/style [text]` — Convert your text into 15+ stylish aesthetic fonts!  
❂ Reply to any message with `/style`  
"""

NORMAL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

STYLES = {
    "𝔉𝔯𝔞𝔨𝔱𝔲𝔯 / 𝕲𝖔𝖙𝖍𝖎𝖈": {
        "chars": "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ0123456789"
    },
    "𝕭𝖔𝖑𝖉 𝕲𝖔𝖙𝖍𝖎𝖈": {
        "chars": "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅0123456789"
    },
    "𝓢𝓬𝓻𝓲𝓹𝓽 / 𝓒𝓾𝓻𝓼𝓲𝓿𝓮": {
        "chars": "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩0123456789"
    },
    "𝔻𝕠𝕦𝕓𝕝𝕖 𝕊𝕥𝕣𝕦𝕔𝕜": {
        "chars": "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
    },
    "🅂🅀🅄🄰🅁🄴🄳": {
        "chars": "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉0123456789"
    },
    "🅒🅘🅡🅒🅛🅔🅓": {
        "chars": "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ⓪①②③④⑤⑥⑦⑧⑨"
    },
    "𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎": {
        "chars": "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    },
    "ꜱᴍᴀʟʟ ᴄᴀᴘꜱ": {
        "chars": "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ0123456789"
    },
    "𝑩𝒐𝒍𝒅 𝑰𝒕𝒂𝒍𝒊𝒄": {
        "chars": "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁0123456789"
    },
    "Ｓａｎｓ Ｓｅｒｉｆ": {
        "chars": "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖵𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"
    },
    "Ｆｕｌｌｗｉｄｔｈ": {
        "chars": "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ０１２３４５６７８９"
    }
}

def transform(text: str, target_chars: str) -> str:
    res = []
    for ch in text:
        if ch in NORMAL:
            idx = NORMAL.index(ch)
            if idx < len(target_chars):
                res.append(target_chars[idx])
            else:
                res.append(ch)
        else:
            res.append(ch)
    return "".join(res)

@bot.on_message(filters.command(["style", "fontstyle"]) & ~filters.forwarded)
async def style_text_cmd(_, m: types.Message):
    input_text = ""
    reply = m.reply_to_message

    if reply and (reply.text or reply.caption):
        input_text = reply.text or reply.caption
    elif len(m.command) > 1:
        input_text = m.text.split(None, 1)[1]

    if not input_text or not input_text.strip():
        return await m.reply_text(font("❌ Usage: `/style [text to style]` or reply to a message!"))

    if len(input_text) > 150:
        input_text = input_text[:150]

    out_lines = [f"✒️ **Styled Fonts for:** `{input_text}`\n"]
    for name, data in STYLES.items():
        styled = transform(input_text, data["chars"])
        out_lines.append(f"**{name}:**\n`{styled}`\n")

    out_lines.append("💡 *Tap any text above to copy it!*")
    await m.reply_text("\n".join(out_lines))
