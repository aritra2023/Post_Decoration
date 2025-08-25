import logging
import sys
import asyncio
import time
from datetime import datetime
from threading import Thread
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from bot_handlers import (
    start_command, help_command, add_channel_command, remove_channel_command,
    list_channels_command, format_command, handle_message,
    button_callback, cancel_command
)
from config import BOT_TOKEN
from keep_alive import keep_alive
from database import db

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

def check_schedule():
    """Check if it's time to enable auto-forward based on schedule"""
    try:
        timer_settings = db.get_schedule_timer()
        if not timer_settings["enabled"]:
            return
            
        current_time = datetime.now()
        scheduled_hour = timer_settings["hours"]
        scheduled_minute = timer_settings["minutes"]
        
        # Check if current time matches scheduled time (within 1 minute)
        if (current_time.hour == scheduled_hour and 
            abs(current_time.minute - scheduled_minute) <= 1):
            
            # Enable auto forward if it's not already enabled
            if not db.get_auto_forward_status():
                db.toggle_auto_forward()
                logger.info(f"Auto-forward enabled by schedule at {scheduled_hour:02d}:{scheduled_minute:02d}")
                
    except Exception as e:
        logger.error(f"Error in schedule check: {e}")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    while True:
        try:
            check_schedule()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)

def main():
    """Main function to run the bot"""
    try:
        # Start keep alive server
        keep_alive()
        
        # Start scheduler thread
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Schedule checker started")
        
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
