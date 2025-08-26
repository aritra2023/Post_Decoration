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

async def error_handler(update, context):
    """Handle errors in the bot"""
    try:
        logger.error(f"Update {update} caused error {context.error}")
        
        # Handle specific error types
        if "terminated by other getUpdates request" in str(context.error):
            logger.warning("Bot instance conflict detected. Continuing...")
            return
        
        if "Connection refused" in str(context.error):
            logger.warning("Connection issue detected. Retrying...")
            return
            
        # For other errors, try to send error message to user
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, something went wrong. Please try again later."
                )
            except Exception:
                pass  # Ignore if we can't send error message
                
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def main():
    """Main function to run the bot"""
    try:
        # Start keep alive server
        keep_alive()
        
        # Validate bot token
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN is required.")
            sys.exit(1)
            
        # Create application with error handling
        application = (Application.builder()
                      .token(BOT_TOKEN)
                      .read_timeout(30)
                      .write_timeout(30)
                      .connect_timeout(30)
                      .pool_timeout(30)
                      .build())
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Add handlers - Commands first
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("addchannel", add_channel_command))
        application.add_handler(CommandHandler("removechannel", remove_channel_command))
        application.add_handler(CommandHandler("listchannels", list_channels_command))
        application.add_handler(CommandHandler("format", format_command))
        application.add_handler(CommandHandler("autoforward", autoforward_command))
        application.add_handler(CommandHandler("forwardstatus", forwardstatus_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Message handler for auto-posting (should be last) - handles both text and photos
        application.add_handler(MessageHandler(
            (filters.TEXT | filters.PHOTO) & ~filters.COMMAND, 
            handle_message
        ))
        
        logger.info("Bot started successfully!")
        logger.info("Bot is ready to receive messages")
        
        # Run the bot with error recovery
        while True:
            try:
                application.run_polling(
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True,
                    timeout=30
                )
                break  # Exit loop if polling stops gracefully
            except Exception as e:
                if "terminated by other getUpdates request" in str(e):
                    logger.warning("Bot conflict detected. Retrying in 5 seconds...")
                    import time
                    time.sleep(5)
                    continue
                else:
                    logger.error(f"Polling error: {e}")
                    import time
                    time.sleep(10)
                    continue
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import time
        time.sleep(5)  # Wait before exit

if __name__ == '__main__':
    main()
