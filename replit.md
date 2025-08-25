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
- **MongoDB Atlas**: Cloud database service for data persistence (connection string in config)
- **Google Gemini API**: AI service integration (API key configured but usage not visible in current codebase)

## Python Libraries
- **python-telegram-bot**: Official Telegram bot framework
- **pymongo**: MongoDB driver for Python
- **flask**: Lightweight web framework for keep-alive server
- **threading**: Built-in library for concurrent keep-alive server

## Configuration Management
- **Hardcoded Credentials**: Bot token, MongoDB URI, and API keys stored directly in config.py
- **Environment Variables**: Structure ready for .env file usage (referenced in requirements but not implemented)

## Hosting Platform
- **Replit**: Target deployment platform with specific keep-alive requirements
- **Port Configuration**: Flask server configured for port 5000