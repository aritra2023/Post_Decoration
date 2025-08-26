import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from config import ADMIN_USER_ID, WELCOME_IMAGES

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with error handling"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"
        start_message = db.get_start_message().format(user_name)
        
        # Create keyboard
        keyboard = []
        
        if is_admin(user_id):
            keyboard = [
                [InlineKeyboardButton("📢 Manage Channels", callback_data="manage_channels")],
                [InlineKeyboardButton("📝 Set Format", callback_data="set_format")],
                [InlineKeyboardButton("📊 Settings", callback_data="settings")]
            ]
        else:
            keyboard = []
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            # Alternate between the two welcome images
            import time
            image_index = int(time.time()) % len(WELCOME_IMAGES)
            selected_image = WELCOME_IMAGES[image_index]
            
            # Send welcome image with message as caption
            try:
                await update.message.reply_photo(
                    photo=selected_image,
                    caption=start_message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logging.error(f"Failed to send welcome image with caption: {e}")
                # Fallback to text message if image fails
                await update.message.reply_text(
                    start_message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
    except Exception as e:
        logging.error(f"Error in start command: {e}")
        if update.message:
            await update.message.reply_text("An error occurred. Please try again.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not update.message:
        return
        
    help_text = """
🤖 <b>Bot Help</b>

<b>Public Commands:</b>
• /start - Show main menu
• /help - Show this help message

<b>Admin Commands:</b>
• /addchannel @channel_id [Name] - Add channel for posting
• /removechannel Channel Name/ID - Remove channel
• /listchannels - List all channels
• /format - Set post format
• /settings - Bot settings

<b>Format Variables:</b>
You can use these variables in your format:
• {title} - Post title
• {price} - Item price
• {link} - Link URL
• {description} - Description
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addchannel command with error handling"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide channel ID and name.\nUsage: /addchannel @channel_id [Channel Name]")
            return
        
        # Join all arguments to get the full text
        full_text = " ".join(context.args)
        
        # Check if there's a bracket format
        if '[' in full_text and ']' in full_text:
            # Extract channel ID (before bracket) and name (inside bracket)
            parts = full_text.split('[', 1)
            channel_id = parts[0].strip()
            channel_name = parts[1].split(']')[0].strip()
            
            # Validate channel ID format
            if not (channel_id.startswith('@') or channel_id.startswith('-100') or channel_id.lstrip('-').isdigit()):
                await update.message.reply_text("❌ Invalid channel ID format. Use @channel_username or -100xxxxxxxxx")
                return
                
            success, message = db.add_channel_with_name(channel_id, channel_name)
        else:
            await update.message.reply_text("❌ Please use format: /addchannel @channel_id [Channel Name]")
            return
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")
    except Exception as e:
        logging.error(f"Error in add_channel_command: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred while adding the channel.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with comprehensive error handling"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        logging.info(f"Message received from user: {user_id}")
        
        if not is_admin(user_id):
            logging.info(f"User {user_id} is not admin. Admin ID: {ADMIN_USER_ID}")
            return
        
        # Check if auto forward is enabled
        if not db.get_auto_forward_status():
            await update.message.reply_text("🚀 Auto forward is currently disabled. Enable it in Settings to auto-post messages.")
            return
        
        # Get message content (text or caption)
        message_text = update.message.text or update.message.caption or ""
        
        # Check if message has photo
        has_photo = update.message.photo is not None
        photo_file_id = update.message.photo[-1].file_id if has_photo and update.message.photo else None
        
        # Default image URL for text-only messages
        default_image_url = "https://files.catbox.moe/9i18yn.jpg"
        
        logging.info(f"Message text: {message_text}")
        logging.info(f"Has photo: {has_photo}")
        
        if not message_text:
            logging.info("No message text found")
            return
        
        # Check if it's a format bypass (contains links)
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message_text)
        
        logging.info(f"URLs found: {urls}")
        
        # Just apply basic formatting for now
        formatted_message = message_text
        
        # Get active channels and post to them
        channels = db.get_channels(active_only=True)
        
        if not channels:
            # No channels configured - just send formatted message as reply
            logging.info("No channels configured, sending as reply")
            if has_photo and photo_file_id:
                await update.message.reply_photo(
                    photo=photo_file_id,
                    caption=formatted_message,
                    parse_mode='HTML'
                )
            else:
                # For text messages, send with default image
                await update.message.reply_photo(
                    photo=default_image_url,
                    caption=formatted_message,
                    parse_mode='HTML'
                )
            return
        
        success_count = 0
        failed_channels = []
        
        # Post to all active channels
        for channel_id in channels:
            try:
                if has_photo and photo_file_id:
                    await context.bot.send_photo(
                        chat_id=channel_id,
                        photo=photo_file_id,
                        caption=formatted_message,
                        parse_mode='HTML'
                    )
                else:
                    # For text messages, send with default image
                    await context.bot.send_photo(
                        chat_id=channel_id,
                        photo=default_image_url,
                        caption=formatted_message,
                        parse_mode='HTML'
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
            
    except Exception as e:
        logging.error(f"Error in handle_message: {e}")
        if update and update.message:
            try:
                await update.message.reply_text("❌ An error occurred while processing your message.")
            except Exception:
                pass

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    try:
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        logging.info(f"Button clicked - User: {user_id}, Data: {data}, Is Admin: {is_admin(user_id)}")
        
        if data == "help":
            await help_command(update, context)
        
        elif data == "settings" and is_admin(user_id):
            keyboard = [
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    "⚙️ <b>Settings</b>\n\nThis is a dummy settings menu. All main features are available directly from the main menu!",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception:
                # If editing fails, try caption edit
                try:
                    await query.edit_message_caption(
                        caption="⚙️ <b>Settings</b>\n\nThis is a dummy settings menu. All main features are available directly from the main menu!",
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                except Exception:
                    pass
        
        elif data == "back_to_main" and is_admin(user_id):
            await start_command(update, context)
            
    except Exception as e:
        logging.error(f"Error in button_callback: {e}")

async def autoforward_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /autoforward command"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please specify 'on' or 'off'.\nUsage: /autoforward on/off")
            return
        
        command = context.args[0].lower()
        
        if command in ['on', 'off']:
            # Toggle auto forward based on command
            current_status = db.get_auto_forward_status()
            new_status = (command == 'on')
            
            if current_status != new_status:
                success, message = db.toggle_auto_forward()
                if success:
                    await update.message.reply_text(f"✅ Auto forward {message}")
                else:
                    await update.message.reply_text(f"❌ {message}")
            else:
                status_text = "enabled" if new_status else "disabled"
                await update.message.reply_text(f"✅ Auto forward is already {status_text}")
        else:
            await update.message.reply_text("❌ Please specify 'on' or 'off'.\nUsage: /autoforward on/off")
            
    except Exception as e:
        logging.error(f"Error in autoforward_command: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred.")

async def forwardstatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /forwardstatus command"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        # Get current status
        auto_forward_enabled = db.get_auto_forward_status()
        status_text = "🟢 Enabled" if auto_forward_enabled else "🔴 Disabled"
        
        # Get channel information
        channels = db.get_all_channels_with_status()
        active_count = sum(1 for ch in channels if ch['active'])
        total_count = len(channels)
        
        status_message = f"""📊 <b>Forward Status</b>

🚀 <b>Auto Forward:</b> {status_text}
📢 <b>Active Channels:</b> {active_count}/{total_count}
💬 <b>Total Channels:</b> {total_count}

<b>Channel Details:</b>"""
        
        for ch in channels:
            status_icon = "🟢" if ch['active'] else "🔴"
            status_message += f"\n{status_icon} {ch['channel_name']}"
        
        await update.message.reply_text(status_message, parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Error in forwardstatus_command: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred.")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    if update.message:
        await update.message.reply_text("❌ Operation cancelled.")

async def remove_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removechannel command"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide channel name or ID.\nUsage: /removechannel Channel Name or /removechannel @channel_id")
            return
        
        # Join all arguments to get the input
        input_text = " ".join(context.args)
        
        # Check if input looks like a channel ID
        if input_text.startswith('@') or input_text.startswith('-100') or input_text.lstrip('-').isdigit():
            # It's a channel ID
            success, message = db.remove_channel(input_text)
        else:
            # It's a channel name
            success, message = db.remove_channel_by_name(input_text)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")
            
    except Exception as e:
        logging.error(f"Error in remove_channel_command: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred.")

async def list_channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listchannels command"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        channels = db.get_channels_display(active_only=False)
        
        if not channels:
            await update.message.reply_text("📭 No channels configured.")
            return
        
        channel_list = "\n".join([f"• {channel}" for channel in channels])
        await update.message.reply_text(f"📢 <b>Configured Channels:</b>\n\n{channel_list}", parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Error in list_channels_command: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred.")

async def format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /format command"""
    try:
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        current_format = db.get_format()
        await update.message.reply_text(f"📝 <b>Current Format:</b>\n\n<code>{current_format}</code>", parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Error in format_command: {e}")
        if update and update.message:
            await update.message.reply_text("❌ An error occurred.")