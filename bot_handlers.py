import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from config import ADMIN_USER_ID

# Conversation states
WAITING_FORMAT, WAITING_START_MESSAGE, WAITING_CHANNEL_ADD, WAITING_CHANNEL_REMOVE = range(4)

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID

def format_movie_links(message_text, urls):
    """Format movie links with watch/download template"""
    lines = message_text.split('\n')
    
    # Extract title (first line usually)
    title = lines[0].strip() if lines else "Movie"
    
    # Start building the formatted message
    formatted_parts = []
    formatted_parts.append(f"🎬 **{title}**")
    formatted_parts.append("")
    
    # Add Watch and Download header
    formatted_parts.append("📺 **WATCH AND DOWNLOAD**")
    formatted_parts.append("")
    
    # Process each line to find quality and links
    for line in lines[1:]:  # Skip first line (title)
        line = line.strip()
        if line and ('http' in line or any(quality in line.lower() for quality in ['480p', '720p', '1080p', '4k', 'hd'])):
            # Find quality in the line
            quality_found = None
            for quality in ['480p', '720p', '1080p', '4k', 'hd']:
                if quality in line.lower():
                    quality_found = quality.upper()
                    break
            
            if quality_found:
                formatted_parts.append(f"🎭 **{quality_found}**")
            
            # Add the line with link
            formatted_parts.append(line)
            formatted_parts.append("")
    
    # Add backup channel footer
    formatted_parts.append("━━━━━━━━━━━━━━━━━")
    formatted_parts.append("📡 **Backup Channel**")
    formatted_parts.append("https://t.me/+uCTbb3GPc6AwNTk1")
    
    return '\n'.join(formatted_parts)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        user_id = update.effective_user.id
        start_message = db.get_start_message()
        
        # Create keyboard
        keyboard = []
        
        if is_admin(user_id):
            keyboard = [
                [InlineKeyboardButton("📊 Settings", callback_data="settings")],
                [InlineKeyboardButton("📝 Set Format", callback_data="set_format")],
                [InlineKeyboardButton("📢 Manage Channels", callback_data="manage_channels")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            start_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error in start command: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🤖 **Bot Help**

**Public Commands:**
• /start - Show main menu
• /help - Show this help message

**Admin Commands:**
• /addchannel <channel_id> - Add channel for posting
• /removechannel <channel_id> - Remove channel
• /listchannels - List all channels
• /format - Set post format
• /settings - Bot settings

**Format Variables:**
You can use these variables in your format:
• {title} - Post title
• {price} - Item price
• {link} - Link URL
• {description} - Description
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addchannel command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a channel ID.\nUsage: /addchannel @channel_username or -100xxxxxxxxx")
        return
    
    channel_id = context.args[0]
    
    # Validate channel ID format
    if not (channel_id.startswith('@') or channel_id.startswith('-100') or channel_id.lstrip('-').isdigit()):
        await update.message.reply_text("❌ Invalid channel ID format. Use @channel_username or -100xxxxxxxxx")
        return
    
    success, message = db.add_channel(channel_id)
    
    if success:
        await update.message.reply_text(f"✅ {message}")
    else:
        await update.message.reply_text(f"❌ {message}")

async def remove_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removechannel command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a channel ID.\nUsage: /removechannel @channel_username or -100xxxxxxxxx")
        return
    
    channel_id = context.args[0]
    success, message = db.remove_channel(channel_id)
    
    if success:
        await update.message.reply_text(f"✅ {message}")
    else:
        await update.message.reply_text(f"❌ {message}")

async def list_channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listchannels command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    channels = db.get_channels(active_only=False)
    
    if not channels:
        await update.message.reply_text("📭 No channels configured.")
        return
    
    channel_list = "📢 **Configured Channels:**\n\n"
    for i, channel in enumerate(channels, 1):
        channel_list += f"{i}. `{channel}`\n"
    
    await update.message.reply_text(channel_list, parse_mode='Markdown')

async def format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /format command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return ConversationHandler.END
    
    current_format = db.get_format()
    
    await update.message.reply_text(
        f"📝 **Current Format:**\n\n```\n{current_format}\n```\n\n"
        "Send me the new format you want to use.\n\n"
        "**Available variables:**\n"
        "• {title} - Post title\n"
        "• {price} - Item price\n"
        "• {link} - Link URL\n"
        "• {description} - Description\n\n"
        "Send /cancel to cancel.",
        parse_mode='Markdown'
    )
    
    return WAITING_FORMAT

async def handle_format_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle format input"""
    new_format = update.message.text
    
    success, message = db.set_format(new_format)
    
    if success:
        await update.message.reply_text(f"✅ {message}\n\n**New Format:**\n```\n{new_format}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {message}")
    
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages from admin for auto-posting"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    # Get message content
    message_text = update.message.text or update.message.caption or ""
    
    if not message_text:
        return
    
    # Check if it's a format bypass (contains links)
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, message_text)
    
    if urls:
        # Auto-format with movie/content template
        formatted_message = format_movie_links(message_text, urls)
    else:
        # Try to extract information from the message
        lines = message_text.split('\n')
        
        # Try to extract title, price, link, description
        extracted_data = {
            'title': '',
            'price': '',
            'link': '',
            'description': message_text
        }
        
        # Simple extraction logic
        for line in lines:
            line = line.strip()
            if line.startswith('Title:') or line.startswith('title:'):
                extracted_data['title'] = line.split(':', 1)[1].strip()
            elif line.startswith('Price:') or line.startswith('price:'):
                extracted_data['price'] = line.split(':', 1)[1].strip()
            elif 'http' in line:
                # Extract URL
                urls = re.findall(url_pattern, line)
                if urls:
                    extracted_data['link'] = urls[0]
        
        # If no specific data found, use the message as title
        if not extracted_data['title'] and not extracted_data['price'] and not extracted_data['link']:
            extracted_data['title'] = message_text[:100] + ('...' if len(message_text) > 100 else '')
        
        # Get current format and apply it
        current_format = db.get_format()
        
        try:
            formatted_message = current_format.format(**extracted_data)
        except KeyError as e:
            # If format contains variables not in extracted_data, use original message
            formatted_message = message_text
    
    # Get active channels and post to them
    channels = db.get_channels(active_only=True)
    
    if not channels:
        await update.message.reply_text("❌ No active channels configured for posting.")
        return
    
    success_count = 0
    failed_channels = []
    
    for channel_id in channels:
        try:
            await context.bot.send_message(
                chat_id=channel_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to send to channel {channel_id}: {e}")
            failed_channels.append(channel_id)
    
    # Send confirmation to admin
    if success_count > 0:
        result_message = f"✅ Message posted to {success_count} channel(s)"
        if failed_channels:
            result_message += f"\n❌ Failed to post to: {', '.join(failed_channels)}"
        await update.message.reply_text(result_message)
    else:
        await update.message.reply_text("❌ Failed to post to any channels. Please check channel permissions.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "help":
        await help_command(update, context)
    
    elif data == "settings" and is_admin(user_id):
        keyboard = [
            [InlineKeyboardButton("📝 Change Start Message", callback_data="change_start_msg")],
            [InlineKeyboardButton("📄 Change Format", callback_data="set_format")],
            [InlineKeyboardButton("📢 Toggle Channels", callback_data="toggle_channels")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ **Settings Menu**\n\nChoose what you want to configure:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == "manage_channels" and is_admin(user_id):
        channels = db.get_channels(active_only=False)
        
        if not channels:
            await query.edit_message_text("📭 No channels configured.\n\nUse /addchannel to add channels.")
            return
        
        channel_text = "📢 **Channel Management**\n\nConfigured channels:\n\n"
        keyboard = []
        
        for i, channel in enumerate(channels, 1):
            channel_text += f"{i}. `{channel}`\n"
            keyboard.append([InlineKeyboardButton(f"Toggle {channel}", callback_data=f"toggle_{channel}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            channel_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data.startswith("toggle_") and is_admin(user_id):
        channel_id = data.replace("toggle_", "")
        success, message = db.toggle_channel(channel_id)
        
        if success:
            await query.answer(f"✅ {message}")
            # Refresh the channel management view
            await button_callback(update, context)  # This will show updated channel list
        else:
            await query.answer(f"❌ {message}")
    
    elif data == "back_to_main":
        await start_command(update, context)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END
