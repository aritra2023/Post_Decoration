import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DEFAULT_FORMAT, DEFAULT_START_MESSAGE

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable is required")

# Simple direct PostgreSQL implementation

class Database:
    def __init__(self):
        self.connection = None
        try:
            self.connection = psycopg2.connect(DATABASE_URL)
            self.create_tables()
            self.initialize_defaults()
            logging.info("PostgreSQL database connected and initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(DATABASE_URL)
        return self.connection
    
    def create_tables(self):
        """Create database tables"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Create channels table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    channel_id VARCHAR(255) UNIQUE NOT NULL,
                    channel_name VARCHAR(255),
                    active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create formats table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS formats (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(100) UNIQUE NOT NULL,
                    format TEXT NOT NULL
                )
            """)
            
            # Create settings table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(100) UNIQUE NOT NULL,
                    message TEXT,
                    enabled BOOLEAN,
                    hours INTEGER,
                    minutes INTEGER
                )
            """)
            
            conn.commit()
        except Exception as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def initialize_defaults(self):
        """Initialize default format and settings if they don't exist"""
        try:
            # Initialize default format
            if not Format.query.filter_by(type="current_format").first():
                default_format = Format(type="current_format", format=DEFAULT_FORMAT)
                self.db.session.add(default_format)
            
            # Initialize default start message
            if not Setting.query.filter_by(type="start_message").first():
                start_setting = Setting(type="start_message", message=DEFAULT_START_MESSAGE)
                self.db.session.add(start_setting)
            
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error initializing defaults: {e}")

    def add_channel(self, channel_id):
        """Add a channel to the database"""
        try:
            # Check if channel already exists
            if Channel.query.filter_by(channel_id=channel_id).first():
                return False, "Channel already exists"
            
            channel = Channel(channel_id=channel_id, active=True)
            self.db.session.add(channel)
            self.db.session.commit()
            return True, "Channel added successfully"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error adding channel: {e}")
            return False, f"Error: {e}"

    def add_channel_with_name(self, channel_id, channel_name):
        """Add a channel with custom name to the database"""
        try:
            # Check if channel already exists by ID or name
            existing = Channel.query.filter(
                (Channel.channel_id == channel_id) | 
                (Channel.channel_name == channel_name)
            ).first()
            
            if existing:
                return False, "Channel with this ID or name already exists"
            
            channel = Channel(channel_id=channel_id, channel_name=channel_name, active=True)
            self.db.session.add(channel)
            self.db.session.commit()
            return True, f"Channel '{channel_name}' added successfully"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error adding channel with name: {e}")
            return False, f"Error: {e}"

    def remove_channel(self, channel_id):
        """Remove a channel from the database"""
        try:
            channel = Channel.query.filter_by(channel_id=channel_id).first()
            if channel:
                self.db.session.delete(channel)
                self.db.session.commit()
                return True, "Channel removed successfully"
            else:
                return False, "Channel not found"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error removing channel: {e}")
            return False, f"Error: {e}"

    def remove_channel_by_name(self, channel_name):
        """Remove a channel by its display name"""
        try:
            channel = Channel.query.filter_by(channel_name=channel_name).first()
            if channel:
                self.db.session.delete(channel)
                self.db.session.commit()
                return True, f"Channel '{channel_name}' removed successfully"
            else:
                return False, f"Channel '{channel_name}' not found"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error removing channel by name: {e}")
            return False, f"Error: {e}"

    def get_channels(self, active_only=True):
        """Get all channels from the database"""
        try:
            query = Channel.query
            if active_only:
                query = query.filter_by(active=True)
            channels = query.all()
            return [channel.channel_id for channel in channels]
        except Exception as e:
            logging.error(f"Error getting channels: {e}")
            return []
    
    def get_channels_display(self, active_only=True):
        """Get channels with display names for UI"""
        try:
            query = Channel.query
            if active_only:
                query = query.filter_by(active=True)
            channels = query.all()
            return [channel.channel_name or channel.channel_id for channel in channels]
        except Exception as e:
            logging.error(f"Error getting channels display: {e}")
            return []

    def get_all_channels_with_status(self):
        """Get all channels with their active status"""
        try:
            channels = Channel.query.all()
            result = []
            for channel in channels:
                result.append({
                    "channel_id": channel.channel_id,
                    "channel_name": channel.channel_name or channel.channel_id,
                    "active": channel.active
                })
            return result
        except Exception as e:
            logging.error(f"Error getting channels with status: {e}")
            return []

    def toggle_channel(self, channel_id):
        """Toggle channel active status"""
        try:
            channel = Channel.query.filter_by(channel_id=channel_id).first()
            if not channel:
                return False, "Channel not found"
            
            channel.active = not channel.active
            self.db.session.commit()
            
            display_name = channel.channel_name or channel.channel_id
            status_text = "activated" if channel.active else "deactivated"
            return True, f"'{display_name}' {status_text} successfully"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error toggling channel: {e}")
            return False, f"Error: {e}"

    def set_format(self, format_text):
        """Set the current format"""
        try:
            format_obj = Format.query.filter_by(type="current_format").first()
            if format_obj:
                format_obj.format = format_text
            else:
                format_obj = Format(type="current_format", format=format_text)
                self.db.session.add(format_obj)
            
            self.db.session.commit()
            return True, "Format updated successfully"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error setting format: {e}")
            return False, f"Error: {e}"

    def get_format(self):
        """Get the current format"""
        try:
            format_obj = Format.query.filter_by(type="current_format").first()
            return format_obj.format if format_obj else DEFAULT_FORMAT
        except Exception as e:
            logging.error(f"Error getting format: {e}")
            return DEFAULT_FORMAT

    def set_start_message(self, message):
        """Set the start message"""
        try:
            setting = Setting.query.filter_by(type="start_message").first()
            if setting:
                setting.message = message
            else:
                setting = Setting(type="start_message", message=message)
                self.db.session.add(setting)
            
            self.db.session.commit()
            return True, "Start message updated successfully"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error setting start message: {e}")
            return False, f"Error: {e}"

    def get_start_message(self):
        """Get the start message"""
        try:
            setting = Setting.query.filter_by(type="start_message").first()
            return setting.message if setting else DEFAULT_START_MESSAGE
        except Exception as e:
            logging.error(f"Error getting start message: {e}")
            return DEFAULT_START_MESSAGE

    def toggle_auto_forward(self):
        """Toggle auto forward setting"""
        try:
            setting = Setting.query.filter_by(type="auto_forward").first()
            current_status = setting.enabled if setting else True
            new_status = not current_status
            
            if setting:
                setting.enabled = new_status
            else:
                setting = Setting(type="auto_forward", enabled=new_status)
                self.db.session.add(setting)
            
            self.db.session.commit()
            status_text = "enabled" if new_status else "disabled"
            return True, f"Auto forward {status_text}"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error toggling auto forward: {e}")
            return False, f"Error: {e}"

    def get_auto_forward_status(self):
        """Get auto forward status"""
        try:
            setting = Setting.query.filter_by(type="auto_forward").first()
            return setting.enabled if setting else True
        except Exception as e:
            logging.error(f"Error getting auto forward status: {e}")
            return True

    def set_schedule_timer(self, hours, minutes):
        """Set schedule timer"""
        try:
            setting = Setting.query.filter_by(type="schedule_timer").first()
            if setting:
                setting.hours = hours
                setting.minutes = minutes
                setting.enabled = True
            else:
                setting = Setting(type="schedule_timer", hours=hours, minutes=minutes, enabled=True)
                self.db.session.add(setting)
            
            self.db.session.commit()
            return True, f"Schedule timer set for {hours:02d}:{minutes:02d}"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error setting schedule timer: {e}")
            return False, f"Error: {e}"

    def get_schedule_timer(self):
        """Get schedule timer settings"""
        try:
            setting = Setting.query.filter_by(type="schedule_timer").first()
            if setting:
                return {
                    "hours": setting.hours or 0,
                    "minutes": setting.minutes or 0,
                    "enabled": setting.enabled or False
                }
            return {"hours": 0, "minutes": 0, "enabled": False}
        except Exception as e:
            logging.error(f"Error getting schedule timer: {e}")
            return {"hours": 0, "minutes": 0, "enabled": False}

    def toggle_schedule_timer(self):
        """Toggle schedule timer enabled/disabled"""
        try:
            setting = Setting.query.filter_by(type="schedule_timer").first()
            current_status = setting.enabled if setting else False
            new_status = not current_status
            
            if setting:
                setting.enabled = new_status
            else:
                setting = Setting(type="schedule_timer", enabled=new_status)
                self.db.session.add(setting)
            
            self.db.session.commit()
            status_text = "enabled" if new_status else "disabled"
            return True, f"Schedule timer {status_text}"
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error toggling schedule timer: {e}")
            return False, f"Error: {e}"

# Global database instance
db = Database()