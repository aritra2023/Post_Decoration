import os

# Bot configuration - Direct credentials for reliable operation
BOT_TOKEN = "8334858851:AAFxltESLhq8qu2Qx1WnMiIVrhsOywCJziw"
MONGO_URI = "mongodb+srv://404movie:404moviepass@cluster0.fca76c9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
GEMINI_API_KEY = "AIzaSyAYBwHPiMIVte903r5OGLX_C2g-TStJ5Tk"

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
