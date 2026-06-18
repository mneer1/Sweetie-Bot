import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_CHANNEL_ID = 1516219570694652006

# تحديث 0.1: التحكم بالتاغات من هنا مباشرة
INCLUDE_TAGS = ["safe", "", ""]
EXCLUDE_TAGS = ["furry", ""] # التاغات المراد حجبها تلقائياً