import os
from urllib.parse import quote
import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from MeowRobot import pbot as bot
from MeowRobot.utils.fonts import font

__mod_name__ = "QR-Code"
__module__ = "𝐐ʀ📱"

__help__ = """
*Commands*:
/createqr, /readqr

*Description:*  
Generate or read QR codes directly in Telegram.

*Usage:*  
❂ `/createqr` — Reply to a text message or provide text to generate a QR code  
❂ `/readqr` — Scan and decode a QR code from an image

*Example:*  
`/createqr Hello World`  
`/readqr` (reply to a QR code image)
"""

@bot.on_message(filters.command("readqr") & ~filters.forwarded, group=-555)
async def readqr(c, m: Message):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply(font("Please reply with a photo that contains a valid QR Code."))
    
    foto = await m.reply_to_message.download()
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "http://api.qrserver.com/v1/read-qr-code/"
            data = aiohttp.FormData()
            data.add_field(
                'file', 
                open(foto, 'rb'), 
                filename=os.path.basename(foto)
            )
            
            async with session.post(url, data=data) as r:
                response = await r.json()
                qr_data = response[0]["symbol"][0]["data"]
                
                if qr_data is None:
                    return await m.reply_text(font("Could not read the QR code."))
                
                bot_user = c.me.username if c.me else "MeowRoBot"
                await m.reply_text(
                    f"<b>QR Code Reader by @{bot_user}:</b> <code>{qr_data}</code>",
                    quote=True,
                )
    except Exception as e:
        await m.reply_text(f"An error occurred: {str(e)}")
    finally:
        if os.path.exists(foto):
            os.remove(foto)


@bot.on_message(filters.command("createqr") & ~filters.forwarded, group=-444)
async def makeqr(c, m: Message):
    if m.reply_to_message and m.reply_to_message.text:
        teks = m.reply_to_message.text
    elif len(m.command) > 1:
        teks = m.text.split(None, 1)[1]
    else:
        return await m.reply(
            "Please add text after command or reply to text to convert text -> QR Code."
        )
    
    encoded_text = quote(teks)
    url = f"https://api.qrserver.com/v1/create-qr-code/?data={encoded_text}&size=300x300"
    
    bot_user = c.me.username if c.me else "MeowRoBot"
    await m.reply_photo(
        url, caption=f"<b>QR Code Maker by @{bot_user}</b>", quote=True
    )
