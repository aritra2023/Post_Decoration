import logging
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from bot_handlers import (
    start_command, help_command, add_channel_command, remove_channel_command,
    list_channels_command, format_command, handle_message,
    button_callback, cancel_command, autoforward_command, forwardstatus_command
)
from config import BOT_TOKEN
from keep_alive import keep_alive
import asyncio

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot"""
    try:
        # Start keep alive server
        keep_alive()
        
        # Validate bot token
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN environment variable is required. Please set it in your environment.")
            sys.exit(1)
            
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers - Commands first
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("addchannel", add_channel_command))
        application.add_handler(CommandHandler("removechannel", remove_channel_command))
        application.add_handler(CommandHandler("listchannels", list_channels_command))
        application.add_handler(CommandHandler("format", format_command))
        application.add_handler(CommandHandler("forward", autoforward_command))
        application.add_handler(CommandHandler("forwardstatus", forwardstatus_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Message handler for auto-posting (should be last) - handles both text and photos
        application.add_handler(MessageHandler(
            (filters.TEXT | filters.PHOTO) & ~filters.COMMAND, 
            handle_message
        ))
        
        logger.info("Bot started successfully!")
        logger.info("Bot username: @YourBotUsername")  # Replace with actual bot username
        
        # Run the bot
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
