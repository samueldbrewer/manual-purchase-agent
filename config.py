import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'development-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API keys - must be set via environment variables
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Encryption key for sensitive data
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # File storage settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB