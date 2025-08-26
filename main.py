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
    """Main function to run the bot with comprehensive error handling"""
    try:
        # Start keep alive server with error handling
        try:
            keep_alive()
            logger.info("Keep alive server started successfully")
        except Exception as e:
            logger.warning(f"Keep alive server failed to start: {e}")
            # Continue without keep alive - bot can still work
        
        # Validate bot token
        if not BOT_TOKEN or BOT_TOKEN.strip() == "":
            logger.error("BOT_TOKEN is required. Please check your configuration.")
            sys.exit(1)
            
        logger.info("Initializing Telegram bot application...")
        
        # Create application with error handling
        try:
            application = Application.builder().token(BOT_TOKEN).build()
            logger.info("Telegram application created successfully")
        except Exception as e:
            logger.error(f"Failed to create Telegram application: {e}")
            sys.exit(1)
        
        # Test database connection
        try:
            from database import db
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.error("Bot will continue but database features may not work")
        
        # Add handlers with error handling
        try:
            # Commands first
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
            
            logger.info("All handlers registered successfully")
        except Exception as e:
            logger.error(f"Failed to register handlers: {e}")
            sys.exit(1)
        
        logger.info("Bot started successfully!")
        logger.info("Ready to receive messages...")
        
        # Run the bot with comprehensive error handling
        try:
            application.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            logger.info("Attempting to restart...")
            # Try to restart once
            try:
                application.run_polling(
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True
                )
            except Exception as restart_error:
                logger.error(f"Restart failed: {restart_error}")
                sys.exit(1)
        
    except Exception as e:
        logger.error(f"Critical error in main function: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main()
