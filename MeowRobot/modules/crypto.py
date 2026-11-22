import aiohttp
import time
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from MeowRobot import pbot
from MeowRobot.utils.fonts import font

__mod_name__ = "Crypto"
__module__ = "𝐂ʀʏᴘᴛᴏ🪙"

__help__ = """
❂ `/price <coin>` — Check coin price in USD/INR (e.g. `/price btc`)  
❂ `/price <amount> <from> <to>` — Convert currencies or coins (e.g. `/price 10 usd inr` or `/price 1 btc usd`)  
❂ `/listcoins` — List supported fiat currencies  
"""

CACHE = {"data": {}, "last": 0}
FIAT = {
    "usd", "inr", "eur", "gbp", "jpy", "aud", "cad", "rub", "cny", "brl", "idr",
    "mxn", "sar", "aed", "chf", "hkd", "sgd", "thb", "ngn", "zar"
}

async def get_id(q: str):
    q = q.lower().strip()
    if q in FIAT:
        return q, "fiat"
    if q in CACHE["data"] and time.time() - CACHE["last"] < 600:
        return CACHE["data"][q], "coin"
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            async with s.get(f"https://api.coingecko.com/api/v3/search?query={q}") as r:
                if r.status != 200:
                    return None, None
                res = await r.json()
    except Exception:
        return None, None

    for c in res.get("coins", []):
        if q in [c["symbol"].lower(), c["name"].lower()]:
            CACHE["data"][q] = c["id"]
            CACHE["last"] = time.time()
            return c["id"], "coin"
    return None, None

async def convert_amount(amount: float, from_curr: str, to_curr: str):
    fid, ft = await get_id(from_curr)
    tid, tt = await get_id(to_curr)
    if not fid or not tid:
        return None
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            if ft == "coin" and tt == "fiat":
                async with s.get(f"https://api.coingecko.com/api/v3/simple/price?ids={fid}&vs_currencies={tid}") as r:
                    rate = (await r.json()).get(fid, {}).get(tid)
            elif ft == "fiat" and tt == "coin":
                async with s.get(f"https://api.coingecko.com/api/v3/simple/price?ids={tid}&vs_currencies={fid}") as r:
                    val = (await r.json()).get(tid, {}).get(fid)
                    rate = 1 / val if val else None
            elif ft == "coin" and tt == "coin":
                async with s.get(f"https://api.coingecko.com/api/v3/simple/price?ids={fid},{tid}&vs_currencies=usd") as r:
                    data = await r.json()
                    fu, tu = data.get(fid, {}).get("usd"), data.get(tid, {}).get("usd")
                    rate = fu / tu if fu and tu else None
            else:  # fiat → fiat
                async with s.get("https://api.coingecko.com/api/v3/exchange_rates") as r:
                    data = await r.json()
                    rates = data.get("rates", {})
                    rate = rates.get(tid, {}).get("value") / rates.get(fid, {}).get("value")
    except Exception:
        return None
    return rate * amount if rate else None

@pbot.on_message(filters.command("price") & ~filters.forwarded, group=29)
async def price_handler(_, m: Message):
    if len(m.command) < 2:
        return await m.reply(
            "❌ **Usage:**\n`/price btc`\n`/price 10 usd inr`\n`/price 1 btc usd`",
            parse_mode=ParseMode.MARKDOWN
        )
    args = m.command[1:]

    # Conversion mode (amount from to)
    if args[0].replace(".", "", 1).isdigit() and len(args) >= 3:
        amt = float(args[0])
        f_curr, t_curr = args[1].lower(), args[2].lower()
        res = await convert_amount(amt, f_curr, t_curr)
        if res is None:
            return await m.reply(f"❌ Conversion failed for `{amt} {f_curr.upper()} → {t_curr.upper()}`")
        
        txt = (
            f"🔄 **Currency Conversion**\n\n"
            f"`{amt}` **{f_curr.upper()}** = `{res:.6f}` **{t_curr.upper()}**\n"
            f"🔁 _Live rate from CoinGecko_"
        )
        return await m.reply(txt, parse_mode=ParseMode.MARKDOWN)

    # Single coin price mode
    cid, typ = await get_id(args[0])
    if not cid or typ == "fiat":
        return await m.reply(f"❌ Coin not found: `{args[0]}`", parse_mode=ParseMode.MARKDOWN)

    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd,inr&include_24hr_change=true"
            async with s.get(url) as r:
                data = await r.json()
                coin = data.get(cid, {})
                usd = coin.get("usd", "N/A")
                inr = coin.get("inr", "N/A")
                ch = coin.get("usd_24h_change", 0.0)
                arrow = "🟢" if ch >= 0 else "🔴"
                
                txt = (
                    f"🪙 **{cid.title()} ({args[0].upper()})**\n\n"
                    f"💵 **USD:** `${usd}`\n"
                    f"🇮🇳 **INR:** `₹{inr}`\n"
                    f"📈 **24h Change:** {arrow} `{ch:.2f}%`"
                )
                await m.reply(txt, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await m.reply(f"❌ Failed to fetch coin price: {e}")

@pbot.on_message(filters.command("listcoins") & ~filters.forwarded)
async def list_fiat(_, m: Message):
    fiats = ", ".join(f.upper() for f in sorted(FIAT))
    await m.reply(f"📋 **Supported Fiat Currencies:**\n\n`{fiats}`")
