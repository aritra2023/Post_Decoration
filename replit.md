# Overview

This is a Telegram Channel Manager Bot built with Python that allows administrators to manage multiple channels and automatically format posts across all registered channels. The bot provides a menu-driven interface for channel management, post formatting, and automated message distribution. It uses MongoDB for persistent data storage and includes a keep-alive server for continuous deployment on Replit.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Technology**: python-telegram-bot library for Telegram API integration
- **Architecture Pattern**: Handler-based event-driven architecture with conversation states
- **Rationale**: Provides robust async support and comprehensive Telegram API coverage

## Database Design
- **Technology**: MongoDB with PyMongo driver
- **Collections Structure**:
  - `channels`: Stores channel IDs and their active status
  - `formats`: Stores the current message format template
  - `settings`: Stores bot configuration like start messages
- **Rationale**: NoSQL flexibility for simple document storage without complex relationships

## Authentication & Authorization
- **Approach**: Hardcoded admin user ID with role-based access control
- **Implementation**: Simple boolean check function `is_admin()` before sensitive operations
- **Rationale**: Single admin model sufficient for this use case, avoiding complex user management

## Message Processing
- **Pattern**: Template-based formatting with placeholder substitution
- **Flow**: Admin input → Format application → Multi-channel broadcast
- **Features**: Supports both text and image+caption posts

## Conversation Management
- **Technology**: ConversationHandler from python-telegram-bot
- **States**: Dedicated states for format setting, channel management, and message handling
- **Rationale**: Provides structured multi-step user interactions with proper state management

## Deployment Architecture
- **Keep-Alive Service**: Flask server running on separate thread
- **Health Monitoring**: Basic health check endpoints
- **Rationale**: Ensures continuous uptime on free hosting platforms like Replit

# External Dependencies

## Core Services
- **Telegram Bot API**: Primary interface for bot functionality
- **MongoDB Atlas**: Cloud database service for data persistence
- **Google Gemini API**: AI service integration for enhanced features

## Python Libraries
- **python-telegram-bot**: Official Telegram bot framework
- **pymongo**: MongoDB driver for Python
- **flask**: Lightweight web framework for keep-alive server
- **gunicorn**: WSGI server for production deployment

## Configuration Management
- **Environment Variables**: All sensitive data stored in Replit Secrets
  - BOT_TOKEN: Telegram bot authentication token
  - MONGO_URI: MongoDB connection string
  - GEMINI_API_KEY: Google AI API key
- **Security**: Hardcoded credentials removed for production safety

## Hosting Platform
- **Replit**: Target deployment platform with specific keep-alive requirements
- **Port Configuration**: Flask server configured for port 5000
- **Workflows**: "Telegram Bot" workflow for main bot, "Start application" for web server

# Migration Complete
- ✅ Secure environment variable configuration
- ✅ All dependencies installed and working
- ✅ Bot server running on port 5000
- ✅ Code compatibility issues resolved
- ✅ Settings button made dummy, main features moved to main menu
- ✅ Channel management with custom names (/addchannel @id [Name])
- ✅ Toggle buttons show friendly names instead of technical IDs
- ✅ Auto forward button removed, replaced with reliable command-based controls
- ✅ Commands implemented: /autoforward on/off, /forwardstatus