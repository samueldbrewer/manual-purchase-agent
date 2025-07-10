import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the Flask application"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///instance/app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Encryption
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # Purchase settings
    ENABLE_REAL_PURCHASES = os.environ.get('ENABLE_REAL_PURCHASES', 'false').lower() == 'true'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Static file settings
    SEND_FILE_MAX_AGE_DEFAULT = 0