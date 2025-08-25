from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, CHANNELS_COLLECTION, FORMATS_COLLECTION, SETTINGS_COLLECTION, DEFAULT_FORMAT, DEFAULT_START_MESSAGE
import logging

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.channels = self.db[CHANNELS_COLLECTION]
            self.formats = self.db[FORMATS_COLLECTION]
            self.settings = self.db[SETTINGS_COLLECTION]
            
            # Initialize default values if they don't exist
            self.initialize_defaults()
            logging.info("Database connected successfully")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def initialize_defaults(self):
        """Initialize default format and settings if they don't exist"""
        try:
            # Initialize default format
            if not self.formats.find_one({"type": "current_format"}):
                self.formats.insert_one({
                    "type": "current_format",
                    "format": DEFAULT_FORMAT
                })
            
            # Initialize default start message
            if not self.settings.find_one({"type": "start_message"}):
                self.settings.insert_one({
                    "type": "start_message",
                    "message": DEFAULT_START_MESSAGE
                })
        except Exception as e:
            logging.error(f"Error initializing defaults: {e}")

    def add_channel(self, channel_id):
        """Add a channel to the database"""
        try:
            # Check if channel already exists
            if self.channels.find_one({"channel_id": channel_id}):
                return False, "Channel already exists"
            
            self.channels.insert_one({
                "channel_id": channel_id,
                "active": True
            })
            return True, "Channel added successfully"
        except Exception as e:
            logging.error(f"Error adding channel: {e}")
            return False, f"Error: {e}"

    def remove_channel(self, channel_id):
        """Remove a channel from the database"""
        try:
            result = self.channels.delete_one({"channel_id": channel_id})
            if result.deleted_count > 0:
                return True, "Channel removed successfully"
            else:
                return False, "Channel not found"
        except Exception as e:
            logging.error(f"Error removing channel: {e}")
            return False, f"Error: {e}"

    def get_channels(self, active_only=True):
        """Get all channels from the database"""
        try:
            query = {"active": True} if active_only else {}
            channels = list(self.channels.find(query))
            return [channel["channel_id"] for channel in channels]
        except Exception as e:
            logging.error(f"Error getting channels: {e}")
            return []

    def toggle_channel(self, channel_id):
        """Toggle channel active status"""
        try:
            channel = self.channels.find_one({"channel_id": channel_id})
            if not channel:
                return False, "Channel not found"
            
            new_status = not channel.get("active", True)
            self.channels.update_one(
                {"channel_id": channel_id},
                {"$set": {"active": new_status}}
            )
            status_text = "activated" if new_status else "deactivated"
            return True, f"Channel {status_text} successfully"
        except Exception as e:
            logging.error(f"Error toggling channel: {e}")
            return False, f"Error: {e}"

    def set_format(self, format_text):
        """Set the current format"""
        try:
            self.formats.update_one(
                {"type": "current_format"},
                {"$set": {"format": format_text}},
                upsert=True
            )
            return True, "Format updated successfully"
        except Exception as e:
            logging.error(f"Error setting format: {e}")
            return False, f"Error: {e}"

    def get_format(self):
        """Get the current format"""
        try:
            format_doc = self.formats.find_one({"type": "current_format"})
            if format_doc:
                return format_doc["format"]
            return DEFAULT_FORMAT
        except Exception as e:
            logging.error(f"Error getting format: {e}")
            return DEFAULT_FORMAT

    def set_start_message(self, message):
        """Set the start message"""
        try:
            self.settings.update_one(
                {"type": "start_message"},
                {"$set": {"message": message}},
                upsert=True
            )
            return True, "Start message updated successfully"
        except Exception as e:
            logging.error(f"Error setting start message: {e}")
            return False, f"Error: {e}"

    def get_start_message(self):
        """Get the start message"""
        try:
            setting_doc = self.settings.find_one({"type": "start_message"})
            if setting_doc:
                return setting_doc["message"]
            return DEFAULT_START_MESSAGE
        except Exception as e:
            logging.error(f"Error getting start message: {e}")
            return DEFAULT_START_MESSAGE

# Global database instance
db = Database()
