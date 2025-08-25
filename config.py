import os

# Bot configuration - Using environment variables for security
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Admin user ID
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "7342290214"))

# Default messages
DEFAULT_START_MESSAGE = "<b>𝐇ᴇʏ {}, 𝐈'ᴍ ʏᴏᴜʀ sᴍᴀʀᴛ ᴅᴇᴄᴏʀᴀᴛɪɴɢ + ᴀᴜᴛᴏ-ᴘᴏsᴛɪɴɢ ʙᴏᴛ! 🎉 𝐈 ᴄᴀɴ sᴛʏʟᴇ ᴀɴᴅ ғᴏʀᴍᴀᴛ ʏᴏᴜʀ ᴘᴏsᴛs ʙᴇᴀᴜᴛɪғᴜʟʟʏ, ɢɪᴠɪɴɢ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴀ sᴜᴘᴇʀ sᴀᴛɪsғʏɪɴɢ ᴀɴᴅ ᴘʀᴏғᴇssɪᴏɴᴀʟ ʟᴏᴏᴋ. 🚀✨</b>"

# Welcome images
WELCOME_IMAGES = [
    "https://i.postimg.cc/W3NpydGC/Whats-App-Image-2025-08-25-at.jpg",
    "https://i.postimg.cc/CxpgtZY7/Whats-App-Image-2025-08-25-at-22-44-03-41c55cf3.jpg"
]

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
