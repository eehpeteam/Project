"""Configuration management for the application"""

import os
import sys
from pathlib import Path

# Optional dependency: python-dotenv with robust .env discovery
def _load_env_robust():
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        # dotenv not available; rely on existing environment variables
        return False

    # Candidate locations for .env
    candidates = []
    try:
        if getattr(sys, 'frozen', False) and hasattr(sys, 'executable'):
            # Executable directory (PyInstaller)
            candidates.append(Path(sys.executable).parent / '.env')
    except Exception:
        pass

    # Current working directory
    candidates.append(Path.cwd() / '.env')
    # Project root relative to this file (src/ -> project root)
    try:
        candidates.append(Path(__file__).resolve().parent.parent / '.env')
    except Exception:
        pass

    for env_path in candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path))
            return True

    # Fallback to default behavior (searching up the tree)
    load_dotenv()
    return True

_load_env_robust()


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
        """Validate that required configuration is present.

        Rules:
        - Azure provider requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.
        - OpenAI provider requires OPENAI_API_KEY.
        - Email credentials are not strictly required at startup; sending will be skipped/fail gracefully if missing.
        """
        provider = cls.TRANSCRIBER_PROVIDER.lower() if cls.TRANSCRIBER_PROVIDER else 'azure'
        if provider == 'azure':
            if not cls.AZURE_SPEECH_KEY or not cls.AZURE_SPEECH_REGION:
                raise ValueError("TRANSCRIBER_PROVIDER=azure requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
        elif provider == 'openai':
            if not cls.OPENAI_API_KEY:
                raise ValueError("TRANSCRIBER_PROVIDER=openai requires OPENAI_API_KEY")
        # whisper_local and mock do not require cloud API keys

        # Email credentials are optional at validation time; sending will check later.
        return True


# Create output directory if it doesn't exist
os.makedirs(Config.OUTPUT_DIRECTORY, exist_ok=True)
