# DesiFriend AI - Configuration Management
"""
Environment configuration management for DesiFriend AI.
Validates and provides access to environment variables.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Google Cloud Configuration (optional, for alternative TTS/STT)
    GOOGLE_CLOUD_API_KEY: Optional[str] = os.getenv('GOOGLE_CLOUD_API_KEY')
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Server Configuration
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv('MAX_CONVERSATION_HISTORY', 10))
    
    # Audio Configuration
    AUDIO_OUTPUT_DIR: str = os.getenv('AUDIO_OUTPUT_DIR', 'audio_files')
    AUDIO_FORMAT: str = os.getenv('AUDIO_FORMAT', 'mp3')
    AUDIO_COMPRESSION_QUALITY: int = int(os.getenv('AUDIO_COMPRESSION_QUALITY', 128))
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = os.getenv('ALLOWED_ORIGINS', '*')
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate required environment variables.
        
        Returns:
            True if all required variables are set
        """
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these variables in your .env file or environment.")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)."""
        print("=" * 50)
        print("DesiFriend AI Configuration")
        print("=" * 50)
        print(f"Environment: {cls.ENVIRONMENT}")
        print(f"Host: {cls.HOST}")
        print(f"Port: {cls.PORT}")
        print(f"Session Timeout: {cls.SESSION_TIMEOUT_MINUTES} minutes")
        print(f"Max Conversation History: {cls.MAX_CONVERSATION_HISTORY} messages")
        print(f"Audio Output Directory: {cls.AUDIO_OUTPUT_DIR}")
        print(f"Audio Format: {cls.AUDIO_FORMAT}")
        print(f"OpenAI API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Not Set'}")
        print("=" * 50)


# Validate configuration on import
if __name__ != '__main__':
    if not Config.validate():
        print("\nWARNING: Configuration validation failed!")
        print("The application may not work correctly without required environment variables.")
