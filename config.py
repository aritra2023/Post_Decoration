import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Admin user ID
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# Default messages
DEFAULT_START_MESSAGE = """
🤖 **Welcome to Channel Manager Bot!**

I can help you manage multiple channels and format your posts automatically.

Available commands:
• /start - Show this menu
• /help - Get help information

*Admin only commands are hidden for security.*
"""

DEFAULT_FORMAT = """
📌 **{title}**
💰 Price: {price}
🔗 Link: {link}
"""

# Database collections
DB_NAME = "telegram_bot"
CHANNELS_COLLECTION = "channels"
FORMATS_COLLECTION = "formats"
SETTINGS_COLLECTION = "settings"
