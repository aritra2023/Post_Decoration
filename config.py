import os

# Bot configuration
BOT_TOKEN = "8334858851:AAFxltESLhq8qu2Qx1WnMiIVrhsOywCJziw"
MONGO_URI = "mongodb+srv://404movie:404moviepass@cluster0.fca76c9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
GEMINI_API_KEY = "AIzaSyAYBwHPiMIVte903r5OGLX_C2g-TStJ5Tk"

# Admin user ID (replace with actual admin user ID)
ADMIN_USER_ID = 123456789  # Replace with actual admin user ID

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
