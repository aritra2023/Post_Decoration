import logging
import json
import os
from config import DB_NAME, CHANNELS_COLLECTION, FORMATS_COLLECTION, SETTINGS_COLLECTION, DEFAULT_FORMAT, DEFAULT_START_MESSAGE, WELCOME_IMAGES

class Database:
    def __init__(self):
        try:
            # Use simple file-based storage for Replit compatibility
            self.data_dir = "bot_data"
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            
            self.channels_file = os.path.join(self.data_dir, "channels.json")
            self.formats_file = os.path.join(self.data_dir, "formats.json")
            self.settings_file = os.path.join(self.data_dir, "settings.json")
            
            # Initialize files if they don't exist
            self._init_file(self.channels_file, [])
            self._init_file(self.formats_file, {"current_format": DEFAULT_FORMAT})
            self._init_file(self.settings_file, {"start_message": DEFAULT_START_MESSAGE, "auto_forward": True})
            
            # Initialize default values
            self.initialize_defaults()
            logging.info("File-based database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            # Don't raise exception, continue with default values
    
    def _init_file(self, filepath, default_data):
        """Initialize a JSON file with default data if it doesn't exist"""
        try:
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(default_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error initializing file {filepath}: {e}")
    
    def _read_file(self, filepath, default_data):
        """Read data from a JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return default_data
        except Exception as e:
            logging.error(f"Error reading file {filepath}: {e}")
            return default_data
    
    def _write_file(self, filepath, data):
        """Write data to a JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error writing file {filepath}: {e}")
            return False

    def initialize_defaults(self):
        """Initialize default format and settings if they don't exist"""
        try:
            # Files are already initialized in __init__
            logging.info("Defaults initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing defaults: {e}")

    def add_channel(self, channel_id):
        """Add a channel to the database"""
        try:
            channels = self._read_file(self.channels_file, [])
            
            # Check if channel already exists
            for channel in channels:
                if channel.get("channel_id") == channel_id:
                    return False, "Channel already exists"
            
            channels.append({
                "channel_id": channel_id,
                "active": True
            })
            
            if self._write_file(self.channels_file, channels):
                return True, "Channel added successfully"
            else:
                return False, "Failed to save channel"
        except Exception as e:
            logging.error(f"Error adding channel: {e}")
            return False, f"Error: {e}"

    def add_channel_with_name(self, channel_id, channel_name):
        """Add a channel with custom name to the database"""
        try:
            channels = self._read_file(self.channels_file, [])
            
            # Check if channel already exists by ID or name
            for channel in channels:
                if (channel.get("channel_id") == channel_id or 
                    channel.get("channel_name") == channel_name):
                    return False, "Channel with this ID or name already exists"
            
            channels.append({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "active": True
            })
            
            if self._write_file(self.channels_file, channels):
                return True, f"Channel '{channel_name}' added successfully"
            else:
                return False, "Failed to save channel"
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
            channels = self._read_file(self.channels_file, [])
            filtered_channels = []
            for channel in channels:
                if not active_only or channel.get("active", True):
                    filtered_channels.append(channel["channel_id"])
            return filtered_channels
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
            formats_data = self._read_file(self.formats_file, {})
            formats_data["current_format"] = format_text
            if self._write_file(self.formats_file, formats_data):
                return True, "Format updated successfully"
            else:
                return False, "Failed to save format"
        except Exception as e:
            logging.error(f"Error setting format: {e}")
            return False, f"Error: {e}"

    def get_format(self):
        """Get the current format"""
        try:
            formats_data = self._read_file(self.formats_file, {"current_format": DEFAULT_FORMAT})
            return formats_data.get("current_format", DEFAULT_FORMAT)
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
