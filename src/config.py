"""Configuration management for the application"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Teams Integration
    TEAMS_MEETING_ID = os.getenv('TEAMS_MEETING_ID', '')
    
    # Azure Speech Services
    AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY', '')
    AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION', 'eastus')
    
    # Email Configuration
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp-mail.outlook.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    
    # Application Settings
    OUTPUT_DIRECTORY = os.getenv('OUTPUT_DIRECTORY', './meeting_notes')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    # Transcription provider selection: 'azure', 'whisper_local', 'openai', 'mock'
    TRANSCRIBER_PROVIDER = os.getenv('TRANSCRIBER_PROVIDER', 'azure')

    # Provider-specific keys (optional depending on provider)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    # Additional provider keys can be added as needed
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_fields = [
            'AZURE_SPEECH_KEY',
            'AZURE_SPEECH_REGION',
            'EMAIL_SENDER',
            'EMAIL_PASSWORD'
        ]
        
        # Basic required fields
        missing = [field for field in required_fields if not getattr(cls, field)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        # Provider-specific validation
        provider = cls.TRANSCRIBER_PROVIDER.lower() if cls.TRANSCRIBER_PROVIDER else 'azure'
        if provider == 'azure':
            if not cls.AZURE_SPEECH_KEY or not cls.AZURE_SPEECH_REGION:
                raise ValueError("TRANSCRIBER_PROVIDER=azure requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
        elif provider == 'openai':
            if not cls.OPENAI_API_KEY:
                raise ValueError("TRANSCRIBER_PROVIDER=openai requires OPENAI_API_KEY")
        # whisper_local and mock do not require cloud API keys
        
        return True


# Create output directory if it doesn't exist
os.makedirs(Config.OUTPUT_DIRECTORY, exist_ok=True)
