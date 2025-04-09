"""
Configuration settings for the LocalFlix backend.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # LocalFlix specific settings
    VIDEO_DIRECTORY = os.environ.get('VIDEO_DIRECTORY', '/home/pi/videos')
    ALLOWED_EXTENSIONS = {'mp4', 'mkv'}
    THUMBNAIL_DIRECTORY = os.environ.get('THUMBNAIL_DIRECTORY', '/home/pi/localflix/thumbnails')
    GENERATE_THUMBNAILS = os.environ.get('GENERATE_THUMBNAILS', 'True').lower() in ('true', '1', 't')
    THUMBNAIL_WIDTH = int(os.environ.get('THUMBNAIL_WIDTH', 320))
    
    # API settings
    API_VERSION = '1.0'
    
    # Caching settings
    SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', 3600))  # Default: rescan every hour
