"""Audio capture module for Teams meeting audio"""

import pyaudio
import wave
import logging
from datetime import datetime
from pathlib import Path
from src.config import Config

logger = logging.getLogger(__name__)


class AudioCapture:
    """Handle audio capture from Teams meetings"""
    
    # Audio configuration
    CHUNK = 1024
    FORMAT = pyaudio.paFloat32
    CHANNELS = 2
    RATE = 16000
    
    def __init__(self, output_dir=None):
        """
        Initialize audio capture
        
        Args:
            output_dir (str): Directory to save audio files. Defaults to Config.OUTPUT_DIRECTORY
        """
        self.output_dir = output_dir or Config.OUTPUT_DIRECTORY
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        
    def start_capture(self):
        """Start capturing audio from the microphone"""
        try:
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            self.frames = []
            logger.info("Audio capture started")
            return True
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            return False
    
    def capture_chunk(self):
        """Capture a chunk of audio data"""
        if self.stream:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.frames.append(data)
            return True
        return False
    
    def stop_capture(self):
        """Stop audio capture"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Audio capture stopped")
    
    def save_audio(self, filename=None):
        """
        Save captured audio to a WAV file
        
        Args:
            filename (str): Name of the file. If None, generates timestamp-based name
            
        Returns:
            str: Path to saved audio file or None if save failed
        """
        if not self.frames:
            logger.warning("No audio frames to save")
            return None
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"meeting_{timestamp}.wav"
            
            filepath = Path(self.output_dir) / filename
            
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))
            
            logger.info(f"Audio saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()
        logger.info("Audio resources cleaned up")
