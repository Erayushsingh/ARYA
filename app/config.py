import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Environment Configuration
    GOOGLE_GEMINI_KEY = os.getenv('GOOGLE_GEMINI_KEY', 'your-api-key-here')
    SARVAM_API_KEY = os.getenv('SARVAM_API_KEY', 'your-sarvam-api-key-here')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8001))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # File Upload Settings
    MAX_FILE_SIZE = os.getenv('MAX_FILE_SIZE', '50MB')
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', '.jpg,.jpeg,.png,.bmp,.tiff,.webp,.docx').split(',')
    
    # Function Settings
    DEFAULT_IMAGE_QUALITY = int(os.getenv('DEFAULT_IMAGE_QUALITY', 85))
    DEFAULT_PAGE_SIZE = os.getenv('DEFAULT_PAGE_SIZE', 'A4')
    DEFAULT_ORIENTATION = os.getenv('DEFAULT_ORIENTATION', 'portrait')
      # Cleanup Settings
    CLEANUP_INTERVAL_HOURS = int(os.getenv('CLEANUP_INTERVAL_HOURS', 24))
      # File paths - using absolute paths for reliability
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.path.join(BASE_DIR, "app", "file_handler", "uploads")
    OUTPUT_DIR = os.path.join(BASE_DIR, "app", "file_handler", "outputs")