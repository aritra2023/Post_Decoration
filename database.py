from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, CHANNELS_COLLECTION, FORMATS_COLLECTION, SETTINGS_COLLECTION, DEFAULT_FORMAT, DEFAULT_START_MESSAGE, WELCOME_IMAGES
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

    def add_channel_with_name(self, channel_id, channel_name):
        """Add a channel with custom name to the database"""
        try:
            # Check if channel already exists by ID or name
            if self.channels.find_one({"$or": [{"channel_id": channel_id}, {"channel_name": channel_name}]}):
                return False, "Channel with this ID or name already exists"
            
            self.channels.insert_one({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "active": True
            })
            return True, f"Channel '{channel_name}' added successfully"
        except Exception as e:
            logging.error(f"Error adding channel with name: {e}")
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

    def remove_channel_by_name(self, channel_name):
        """Remove a channel by its display name"""
        try:
            result = self.channels.delete_one({"channel_name": channel_name})
            if result.deleted_count > 0:
                return True, f"Channel '{channel_name}' removed successfully"
            else:
                return False, f"Channel '{channel_name}' not found"
        except Exception as e:
            logging.error(f"Error removing channel by name: {e}")
            return False, f"Error: {e}"

    def get_channels(self, active_only=True):
        """Get all channels from the database"""
        try:
            query = {"active": True} if active_only else {}
            channels = list(self.channels.find(query))
            # Return actual channel IDs for posting messages
            return [channel["channel_id"] for channel in channels]
        except Exception as e:
            logging.error(f"Error getting channels: {e}")
            return []
    
    def get_channels_display(self, active_only=True):
        """Get channels with display names for UI"""
        try:
            query = {"active": True} if active_only else {}
            channels = list(self.channels.find(query))
            # Return display names for UI
            return [channel.get("channel_name", channel["channel_id"]) for channel in channels]
        except Exception as e:
            logging.error(f"Error getting channels display: {e}")
            return []

    def get_all_channels_with_status(self):
        """Get all channels with their active status"""
        try:
            channels = list(self.channels.find({}))
            result = []
            for channel in channels:
                # Use channel_name if available, otherwise use channel_id
                display_name = channel.get("channel_name", channel["channel_id"])
                result.append({
                    "channel_id": channel["channel_id"],
                    "channel_name": display_name,
                    "active": channel.get("active", True)
                })
            return result
        except Exception as e:
            logging.error(f"Error getting channels with status: {e}")
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
            
            # Use display name if available
            display_name = channel.get("channel_name", channel_id)
            status_text = "activated" if new_status else "deactivated"
            return True, f"'{display_name}' {status_text} successfully"
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

    def toggle_auto_forward(self):
        """Toggle auto forward setting"""
        try:
            setting_doc = self.settings.find_one({"type": "auto_forward"})
            current_status = setting_doc["enabled"] if setting_doc else True
            new_status = not current_status
            
            self.settings.update_one(
                {"type": "auto_forward"},
                {"$set": {"enabled": new_status}},
                upsert=True
            )
            status_text = "enabled" if new_status else "disabled"
            return True, f"Auto forward {status_text}"
        except Exception as e:
            logging.error(f"Error toggling auto forward: {e}")
            return False, f"Error: {e}"

    def get_auto_forward_status(self):
        """Get auto forward status"""
        try:
            setting_doc = self.settings.find_one({"type": "auto_forward"})
            if setting_doc:
                return setting_doc.get("enabled", True)
            return True  # Default enabled
        except Exception as e:
            logging.error(f"Error getting auto forward status: {e}")
            return True

    def set_schedule_timer(self, hours, minutes):
        """Set schedule timer"""
        try:
            self.settings.update_one(
                {"type": "schedule_timer"},
                {"$set": {"hours": hours, "minutes": minutes, "enabled": True}},
                upsert=True
            )
            return True, f"Schedule timer set for {hours:02d}:{minutes:02d}"
        except Exception as e:
            logging.error(f"Error setting schedule timer: {e}")
            return False, f"Error: {e}"

    def get_schedule_timer(self):
        """Get schedule timer settings"""
        try:
            setting_doc = self.settings.find_one({"type": "schedule_timer"})
            if setting_doc:
                return {
                    "hours": setting_doc.get("hours", 0),
                    "minutes": setting_doc.get("minutes", 0),
                    "enabled": setting_doc.get("enabled", False)
                }
            return {"hours": 0, "minutes": 0, "enabled": False}
        except Exception as e:
            logging.error(f"Error getting schedule timer: {e}")
            return {"hours": 0, "minutes": 0, "enabled": False}

    def toggle_schedule_timer(self):
        """Toggle schedule timer enabled/disabled"""
        try:
            setting_doc = self.settings.find_one({"type": "schedule_timer"})
            current_status = setting_doc["enabled"] if setting_doc else False
            new_status = not current_status
            
            self.settings.update_one(
                {"type": "schedule_timer"},
                {"$set": {"enabled": new_status}},
                upsert=True
            )
            status_text = "enabled" if new_status else "disabled"
            return True, f"Schedule timer {status_text}"
        except Exception as e:
            logging.error(f"Error toggling schedule timer: {e}")
            return False, f"Error: {e}"

# Global database instance
db = Database()
