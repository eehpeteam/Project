"""Transcription module with provider adapters (Azure, local Whisper, mock)"""

import logging
from pathlib import Path
from src.config import Config

logger = logging.getLogger(__name__)


class BaseTranscriber:
    """Interface for transcribers"""

    def transcribe_file(self, audio_file_path):
        raise NotImplementedError()


class AzureTranscriber(BaseTranscriber):
    """Azure Cognitive Services transcriber"""

    def __init__(self):
        try:
            import azure.cognitiveservices.speech as speechsdk
        except Exception as e:
            logger.error("Azure Speech SDK is not installed: %s", e)
            raise

        self.speechsdk = speechsdk
        self.speech_config = speechsdk.SpeechConfig(
            subscription=Config.AZURE_SPEECH_KEY,
            region=Config.AZURE_SPEECH_REGION
        )
        self.speech_config.speech_recognition_language = "en-US"

    def transcribe_file(self, audio_file_path):
        if not Path(audio_file_path).exists():
            logger.error("Audio file not found: %s", audio_file_path)
            return None

        try:
            audio_config = self.speechsdk.audio.AudioConfig(filename=audio_file_path)
            recognizer = self.speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )

            logger.info("Transcribing audio file with Azure: %s", audio_file_path)
            result = recognizer.recognize_once()

            if result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
                logger.info("Transcription completed successfully")
                return result.text
            elif result.reason == self.speechsdk.ResultReason.NoMatch:
                logger.warning("No speech could be recognized from the audio")
                return ""
            elif result.reason == self.speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error("Transcription canceled: %s", cancellation.reason)
                logger.error("Error details: %s", cancellation.error_details)
                return None
        except Exception as e:
            logger.error("Transcription error: %s", e)
            return None


class WhisperLocalTranscriber(BaseTranscriber):
    """Local Whisper-based transcriber (optional dependency)"""

    def __init__(self):
        try:
            import whisper
        except Exception as e:
            logger.error("Whisper package not available: %s", e)
            raise

        self.whisper = whisper
        # Load default model; for production consider model selection
        self.model = whisper.load_model("small")

    def transcribe_file(self, audio_file_path):
        if not Path(audio_file_path).exists():
            logger.error("Audio file not found: %s", audio_file_path)
            return None

        try:
            logger.info("Transcribing audio file with local Whisper: %s", audio_file_path)
            result = self.model.transcribe(str(audio_file_path))
            return result.get('text', '')
        except Exception as e:
            logger.error("Whisper transcription error: %s", e)
            return None


class MockTranscriber(BaseTranscriber):
    """Simple mock transcriber for testing without API keys"""

    def transcribe_file(self, audio_file_path):
        logger.info("Mock transcriber used. Returning placeholder transcription.")
        return "[Mock transcription] This is placeholder text for testing."


def get_transcriber():
    provider = (Config.TRANSCRIBER_PROVIDER or 'azure').lower()
    logger.info("Selecting transcriber provider: %s", provider)

    if provider == 'azure':
        return AzureTranscriber()
    elif provider in ('whisper_local', 'whisper'):
        return WhisperLocalTranscriber()
    elif provider in ('openai',):
        # Placeholder for OpenAI or other cloud providers implementation
        # For now attempt to use whisper_local if OPENAI_API_KEY is not implemented
        logger.warning("OpenAI provider selected but not implemented; falling back to mock transcriber")
        return MockTranscriber()
    elif provider == 'mock':
        return MockTranscriber()
    else:
        logger.warning("Unknown TRANSCRIBER_PROVIDER '%s', using mock transcriber", provider)
        return MockTranscriber()
