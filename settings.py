import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'service_account.json')
    FIREBASE_STORAGE_BUCKET: str = os.getenv('FIREBASE_STORAGE_BUCKET', '')
    
    # API Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    
    # CORS Configuration
    FRONTEND_URL: str = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_EXTENSIONS: list = ['.mp3', '.wav', '.m4a', '.flac']
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required environment variables"""
        required_vars = [
            'OPENAI_API_KEY',
            'FIREBASE_STORAGE_BUCKET',
            'FIREBASE_SERVICE_ACCOUNT_PATH'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True

settings = Settings() 