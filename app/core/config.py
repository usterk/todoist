"""
Application configuration settings.

This module contains configuration settings for the application,
including database settings, security settings, and other constants.
"""

import os
from typing import Dict, Any

# Database settings
DB_SETTINGS = {
    # Default admin credentials
    "default_admin_username": "admin",
    "default_admin_email": "admin@example.com",
    "default_admin_password": "admin"  # Move from hardcoded value to configuration
}

# Security settings
SECURITY_SETTINGS = {
    "jwt_secret_key": os.environ.get("JWT_SECRET_KEY", "temporarysecretkey"),
    "jwt_algorithm": "HS256",
    "access_token_expire_minutes": 30,
}

# API settings
API_SETTINGS = {
    "title": "Todoist API",
    "description": "Task Management API",
    "version": "1.0.0",
}

# Get all settings as a single dictionary
def get_settings() -> Dict[str, Any]:
    """
    Get all application settings as a dictionary.
    
    Returns:
        Dict[str, Any]: Dictionary containing all settings
    """
    return {
        "db": DB_SETTINGS,
        "security": SECURITY_SETTINGS,
        "api": API_SETTINGS,
    }