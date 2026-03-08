import logging
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)
router = Router()

from config import OWNER_ID, PREMIUM_USERS, BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

@router.message(Command("addp"))
async def addp_handler(msg: Message):
    if msg.from_user.id != OWNER_ID:
        await msg.answer(
            "<blockquote><code>𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗢𝗻𝗹𝘆 𝗢𝘄𝗻𝗲𝗿 𝗖𝗮𝗻 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀</blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    args = msg.text.split()
    if len(args) < 3 or not args[1].isdigit() or not args[2].isdigit():
        await msg.answer(
            "<blockquote><code>𝗔𝗱𝗱 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 ⚡</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗨𝘀𝗮𝗴𝗲 : <code>/addp [userid] [days]</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return
    
    user_id = int(args[1])
    days = int(args[2])
    
    expiry = datetime.now() + timedelta(days=days)
    PREMIUM_USERS[user_id] = expiry.timestamp()
    
    # Save to file
    try:
        import os
        os.makedirs('/root/3D', exist_ok=True)
        with open('/root/3D/premium_users.json', 'w') as f:
            json.dump(PREMIUM_USERS, f)
        
        expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")
        
        # Notify admin
        await msg.answer(
            "<blockquote><code>𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝗱𝗱𝗲𝗱 ✅</code></blockquote>\n\n"
            f"<blockquote>「❃」 𝗨𝘀𝗲𝗿 : <code>{user_id}</code>\n"
            f"「❃」 𝗗𝗮𝘆𝘀 : <code>{days}</code>\n"
            f"「❃」 𝗘𝘅𝗽𝗶𝗿𝘆 : <code>{expiry_str}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        
        # Notify user
        try:
            await bot.send_message(
                user_id,
                "<blockquote><code>𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗲𝗱 🎉</code></blockquote>\n\n"
                f"<blockquote>「❃」 𝗣𝗹𝗮𝗻 : <code>{days} Days Premium</code>\n"
                f"「❃」 𝗘𝘅𝗽𝗶𝗿𝘆 : <code>{expiry_str}</code>\n"
                f"「❃」 𝗦𝘁𝗮𝘁𝘂𝘀 : <code>Active ✅</code></blockquote>\n\n"
                "<blockquote>「❃」 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘂𝘀𝗶𝗻𝗴 𝗼𝘂𝗿 𝘀𝗲𝗿𝘃𝗶𝗰𝗲!</blockquote>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error notifying user {user_id}: {e}")
            
    except Exception as e:
        logger.error(f"Error saving premium users: {e}")
        await msg.answer(
            "<blockquote><code>𝗘𝗿𝗿𝗼𝗿 ❌</code></blockquote>\n\n"
            "<blockquote>「❃」 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝘀𝗮𝘃𝗲</blockquote>",
            parse_mode=ParseMode.HTML
        )

@router.message(Command("info"))
async def info_handler(msg: Message):
    user = msg.from_user
    user_id = user.id
    name = user.first_name
    username = f"@{user.username}" if user.username else "None"
    
    # Check premium status
    if user_id in PREMIUM_USERS:
        expiry_ts = PREMIUM_USERS[user_id]
        now_ts = datetime.now().timestamp()
        if now_ts < expiry_ts:
            days_left = int((expiry_ts - now_ts) / 86400)
            premium_status = f"<code>{days_left} days</code>"
        else:
            premium_status = "<code>Expired</code>"
    else:
        premium_status = "<code>Free</code>"
    
    await msg.answer(
        "<blockquote><code>𝗨𝘀𝗲𝗿 𝗜𝗻𝗳𝗼 ℹ️</code></blockquote>\n\n"
        f"<blockquote>「❃」 𝗡𝗮𝗺𝗲 : <code>{name}</code>\n"
        f"「❃」 𝗨𝘀𝗲𝗿 𝗜𝗗 : <code>{user_id}</code>\n"
        f"「❃」 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : <code>{username}</code>\n"
        f"「❃」 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 : {premium_status}</blockquote>",
        parse_mode=ParseMode.HTML
    )


