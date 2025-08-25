import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from config import ADMIN_USER_ID, WELCOME_IMAGES

# Simple state tracking - no conversation handler needed

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID

def format_movie_links(message_text, urls):
    """Format movie links with special template"""
    lines = message_text.split('\n')
    
    # Clean message - remove hashtags, non-terabox links, and existing format text
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Remove hashtags
        line = re.sub(r'#\w+', '', line).strip()
        # Skip existing format text
        if ('Wᴀᴛᴄʜ Oɴʟɪɴᴇ' in line or 'Dᴏᴡɴʟᴏᴀᴅ' in line or 
            'ᴅɪʀᴇᴄᴛ ꜰɪʟᴇ ᴄʜᴀɴɴᴇʟ' in line or '═══' in line or
            '╔' in line or '╚' in line or 'Cʜᴀɴɴᴇʟ' in line):
            continue
        # Keep only terabox links and clean text
        if line and ('terabox' in line.lower() or 'http' not in line):
            cleaned_lines.append(line)
    
    # Start building the formatted message
    formatted_parts = []
    
    # Extract title (first line if it doesn't contain links)
    title_line = cleaned_lines[0].strip() if cleaned_lines else ""
    if title_line and 'http' not in title_line:
        formatted_parts.append(f"<b>{title_line}</b>")
        formatted_parts.append("")
        start_index = 1
    else:
        start_index = 0
    
    # Add Watch/Download header
    formatted_parts.append("<b>📥Wᴀᴛᴄʜ Oɴʟɪɴᴇ / Dᴏᴡɴʟᴏᴀᴅ</b>")
    formatted_parts.append("")
    
    # Process links
    quality_links = {'480p': [], '720p': [], '1080p': []}
    terabox_links = []
    
    for line in cleaned_lines[start_index:]:
        line = line.strip()
        if line and 'terabox' in line.lower():
            # Extract terabox link
            url_pattern = r'https?://[^\s]+'
            link_match = re.search(url_pattern, line)
            if link_match:
                link = link_match.group()
                
                # Check for quality
                quality_found = None
                for quality in ['480p', '720p', '1080p']:
                    if quality in line.lower():
                        quality_found = quality
                        break
                
                if quality_found:
                    quality_links[quality_found].append(link)
                else:
                    terabox_links.append(link)
    
    # Add quality links
    has_quality = False
    for quality in ['480p', '720p', '1080p']:
        if quality_links[quality]:
            formatted_parts.append(f"<b>{quality.upper()} - <a href='{quality_links[quality][0]}'>Download {quality.upper()}</a></b>")
            formatted_parts.append("")
            has_quality = True
    
    # Add 1080p default if no 1080p found but other qualities exist
    if has_quality and not quality_links['1080p']:
        formatted_parts.append("<b>1080P - ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴅɪʀᴇᴄᴛ ꜰɪʟᴇ ᴄʜᴀɴɴᴇʟ</b>")
        formatted_parts.append("")
    
    # Add links without quality
    if not has_quality and terabox_links:
        if len(terabox_links) == 1:
            formatted_parts.append(f"<b>Lɪɴᴋ - <a href='{terabox_links[0]}'>Download Here</a></b>")
            formatted_parts.append("")
        else:
            for i, link in enumerate(terabox_links, 1):
                formatted_parts.append(f"<b>Pᴀʀᴛ {i} - <a href='{link}'>Download Part {i}</a></b>")
                formatted_parts.append("")
    
    # Add footer with fancy box
    formatted_parts.append("<b>╔.★. .═════════════════════╗</b>")
    formatted_parts.append("<b>      ᴅɪʀᴇᴄᴛ ꜰɪʟᴇ ᴄʜᴀɴɴᴇʟ ‒ 29ʀꜱ./ᴍᴏɴᴛʜ</b>")
    formatted_parts.append("<b>      𝐌ᴀɪɴ Cʜᴀɴɴᴇʟ - <a href='https://t.me/+uCTbb3GPc6AwNTk1'>𝐌ᴜꜱᴛ 𝐉ᴏɪɴ</a></b>")
    formatted_parts.append("<b>╚═════════════════════. .★.╝</b>")
    
    return '\n'.join(formatted_parts)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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
                [InlineKeyboardButton("📢 Manage Channels", callback_data="manage_channels"), InlineKeyboardButton("📊 Settings", callback_data="settings")]
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
• /addchannel <channel_id> - Add channel for posting
• /removechannel <channel_id> - Remove channel
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
    """Handle /addchannel command"""
    if not update.effective_user or not update.message:
        return
        
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
    if not update.effective_user or not update.message:
        return
        
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
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    channels = db.get_channels(active_only=False)
    
    if not channels:
        await update.message.reply_text("📭 No channels configured.")
        return
    
    channel_list = "📢 <b>Configured Channels:</b>\n\n"
    for i, channel in enumerate(channels, 1):
        channel_list += f"{i}. <code>{channel}</code>\n"
    
    await update.message.reply_text(channel_list, parse_mode='HTML')

async def format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /format command"""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    current_format = db.get_format()
    
    await update.message.reply_text(
        f"📝 <b>Current Format:</b>\n\n<pre>{current_format}</pre>\n\n"
        "<b>Available variables:</b>\n"
        "• {title} - Post title\n"
        "• {price} - Item price\n"
        "• {link} - Link URL\n"
        "• {description} - Description",
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages from admin for auto-posting"""
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
    
    if urls:
        # Auto-format with movie/content template
        logging.info("Applying movie format")
        formatted_message = format_movie_links(message_text, urls)
        logging.info(f"Formatted message: {formatted_message}")
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
    
    # Send to user first (as preview)
    try:
        if has_photo and photo_file_id:
            await update.message.reply_photo(
                photo=photo_file_id,
                caption=f"📋 <b>Formatted Preview:</b>\n\n{formatted_message}",
                parse_mode='HTML'
            )
        else:
            # For text messages, show preview with default image
            await update.message.reply_photo(
                photo=default_image_url,
                caption=f"📋 <b>Formatted Preview:</b>\n\n{formatted_message}",
                parse_mode='HTML'
            )
    except Exception as e:
        logging.error(f"Failed to send preview to user: {e}")
    
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    if not query or not query.from_user:
        return
        
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "help":
        await help_command(update, context)
    
    elif data == "settings" and is_admin(user_id):
        # Get current settings status
        auto_forward_status = "🟢 ON" if db.get_auto_forward_status() else "🔴 OFF"
        timer_settings = db.get_schedule_timer()
        timer_status = "🟢 ON" if timer_settings["enabled"] else "🔴 OFF"
        timer_time = f"{timer_settings['hours']:02d}:{timer_settings['minutes']:02d}"
        
        keyboard = [
            [InlineKeyboardButton("📝 Change Start Message", callback_data="change_start_msg")],
            [InlineKeyboardButton("📄 Change Format", callback_data="set_format")],
            [InlineKeyboardButton("📢 Toggle Channels", callback_data="toggle_channels")],
            [InlineKeyboardButton(f"🚀 Auto Forward: {auto_forward_status}", callback_data="toggle_auto_forward")],
            [InlineKeyboardButton(f"⏰ Schedule Timer: {timer_status} ({timer_time})", callback_data="schedule_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ <b>Settings Menu</b>\n\nChoose what you want to configure:",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "manage_channels" and is_admin(user_id):
        keyboard = [
            [InlineKeyboardButton("📋 All Channels", callback_data="show_all_channels")],
            [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"), InlineKeyboardButton("➖ Remove Channel", callback_data="remove_channel")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Edit the photo caption instead of creating new message
        try:
            await query.edit_message_caption(
                caption="📢 <b>Channel Management</b>\n\nChoose an option:",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception as e:
            # Fallback for text messages
            try:
                await query.edit_message_text(
                    "📢 <b>Channel Management</b>\n\nChoose an option:",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception:
                # If both edit methods fail, silently continue
                pass
    
    elif data == "show_all_channels" and is_admin(user_id):
        channels = db.get_channels(active_only=False)
        
        if not channels:
            try:
                await query.edit_message_caption(
                    caption="📭 <b>No channels configured</b>\n\nUse Add Channel option to add channels.",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]])
                )
            except Exception:
                await query.edit_message_text(
                    "📭 <b>No channels configured</b>\n\nUse Add Channel option to add channels.",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]])
                )
            return
        
        channel_text = "📢 <b>All Channels</b>\n\nConfigured channels:\n\n"
        for i, channel in enumerate(channels, 1):
            channel_text += f"{i}. <code>{channel}</code>\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_caption(
                caption=channel_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception:
            await query.edit_message_text(
                channel_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    elif data == "add_channel" and is_admin(user_id):
        try:
            await query.edit_message_caption(
                caption="➕ <b>Add Channel</b>\n\nUse the command: <code>/addchannel @channel_username</code> or <code>/addchannel -100xxxxxxxxx</code>\n\nExample:\n<code>/addchannel @mychannel</code>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]])
            )
        except Exception:
            await query.edit_message_text(
                "➕ <b>Add Channel</b>\n\nUse the command: <code>/addchannel @channel_username</code> or <code>/addchannel -100xxxxxxxxx</code>\n\nExample:\n<code>/addchannel @mychannel</code>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]])
            )
    
    elif data == "remove_channel" and is_admin(user_id):
        try:
            await query.edit_message_caption(
                caption="➖ <b>Remove Channel</b>\n\nUse the command: <code>/removechannel @channel_username</code> or <code>/removechannel -100xxxxxxxxx</code>\n\nExample:\n<code>/removechannel @mychannel</code>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]])
            )
        except Exception:
            await query.edit_message_text(
                "➖ <b>Remove Channel</b>\n\nUse the command: <code>/removechannel @channel_username</code> or <code>/removechannel -100xxxxxxxxx</code>\n\nExample:\n<code>/removechannel @mychannel</code>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]])
            )
    
    elif data and data.startswith("toggle_") and is_admin(user_id):
        channel_id = data.replace("toggle_", "")
        success, message = db.toggle_channel(channel_id)
        
        if success:
            await query.answer(f"✅ {message}")
            # Refresh the channel management view
            await button_callback(update, context)  # This will show updated channel list
        else:
            await query.answer(f"❌ {message}")
    
    elif data == "toggle_auto_forward" and is_admin(user_id):
        success, message = db.toggle_auto_forward()
        await query.answer(f"✅ {message}" if success else f"❌ {message}")
        # Refresh settings menu to show updated status
        # Simulate clicking settings again to refresh
        query.data = "settings"
        await button_callback(update, context)
    
    elif data == "schedule_menu" and is_admin(user_id):
        timer_settings = db.get_schedule_timer()
        timer_status = "🟢 ON" if timer_settings["enabled"] else "🔴 OFF"
        timer_time = f"{timer_settings['hours']:02d}:{timer_settings['minutes']:02d}"
        
        keyboard = [
            [InlineKeyboardButton(f"🔄 Toggle Timer: {timer_status}", callback_data="toggle_schedule_timer")],
            [InlineKeyboardButton("🕐 Set Hour +", callback_data="hour_plus"), InlineKeyboardButton("🕐 Set Hour -", callback_data="hour_minus")],
            [InlineKeyboardButton("🕕 Set Minute +", callback_data="minute_plus"), InlineKeyboardButton("🕕 Set Minute -", callback_data="minute_minus")],
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⏰ <b>Schedule Timer Settings</b>\n\nCurrent Time: <code>{timer_time}</code>\nStatus: {timer_status}\n\nThis timer controls when auto-posting is active.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif data == "toggle_schedule_timer" and is_admin(user_id):
        success, message = db.toggle_schedule_timer()
        await query.answer(f"✅ {message}" if success else f"❌ {message}")
        # Refresh schedule menu
        query.data = "schedule_menu"
        await button_callback(update, context)
    
    elif data in ["hour_plus", "hour_minus", "minute_plus", "minute_minus"] and is_admin(user_id):
        timer_settings = db.get_schedule_timer()
        hours = timer_settings["hours"]
        minutes = timer_settings["minutes"]
        
        if data == "hour_plus":
            hours = (hours + 1) % 24
        elif data == "hour_minus":
            hours = (hours - 1) % 24
        elif data == "minute_plus":
            minutes = (minutes + 15) % 60
        elif data == "minute_minus":
            minutes = (minutes - 15) % 60
            
        success, message = db.set_schedule_timer(hours, minutes)
        await query.answer(f"✅ {message}" if success else f"❌ {message}")
        # Refresh schedule menu
        query.data = "schedule_menu"
        await button_callback(update, context)
    
    elif data == "back_to_main":
        # Edit back to welcome message
        user_name = query.from_user.first_name or "User"
        start_message = db.get_start_message().format(user_name)
        
        keyboard = []
        if is_admin(query.from_user.id):
            keyboard = [
                [InlineKeyboardButton("📢 Manage Channels", callback_data="manage_channels"), InlineKeyboardButton("📊 Settings", callback_data="settings")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_caption(
                caption=start_message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception:
            await query.edit_message_text(
                start_message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    if update.message:
        await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END
