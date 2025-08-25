# Telegram Bot - Quick Setup Guide

## Next Time Setup (New Replit Account) - बिल्कुल Smooth!

### Step 1: Create New Bot Token
1. Telegram पर @BotFather को message करें
2. `/newbot` command use करें
3. Bot name और username set करें  
4. **IMPORTANT**: नया token generate करें, पुराना use न करें

### Step 2: Set Environment Variables (Replit Secrets)
```
BOT_TOKEN=your_new_bot_token_here
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

### Step 3: One-Click Start
```bash
# Just click "Run" button or execute:
python main.py
```

## क्यों था problem इस बार:
- Bot token conflict (same token multiple places use हो रहा था)
- Security hardcoded credentials थे
- Package dependencies missing थीं

## अब होगा smooth:
- ✅ Clean environment variables setup
- ✅ No hardcoded secrets
- ✅ All dependencies properly configured
- ✅ Single workflow for bot running

## Bot Features:
- Channel management (add/remove)
- Auto-posting with formatting
- Admin controls
- MongoDB data storage
- Keep-alive server for 24/7 running

Just make sure bot token fresh हो और बाकी सब automatic handle हो जाएगा!