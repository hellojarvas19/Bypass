# Bot Configuration
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8338936618:AAEx5U8Stn6IM2GVnaZ_q9Feno56wNlm9Kw")
ALLOWED_GROUP = int(os.getenv("ALLOWED_GROUP", "-1003681367566"))
OWNER_ID = int(os.getenv("OWNER_ID", "7520618222"))
ALLOWED_USERS = []  # Add user IDs here: [123456789, 987654321]
PREMIUM_USERS = {}  # {user_id: expiry_timestamp}
PROXY_FILE = "proxies.json"
