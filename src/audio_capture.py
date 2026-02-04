"""Audio capture module for Teams meeting audio

Supports dual backends:
- PyAudio (preferred when available)
- sounddevice (fallback when PyAudio is not installed)
"""

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
    CHANNELS = 2
    RATE = 16000

    def __init__(self, output_dir=None):
        """Initialize audio capture.

        Args:
            output_dir (str): Directory to save audio files. Defaults to Config.OUTPUT_DIRECTORY
        """
        self.output_dir = output_dir or Config.OUTPUT_DIRECTORY
        self.stream = None
        self.frames = []  # list of bytes
        self.backend = None

        # Try PyAudio first, then fallback to sounddevice
        try:
            import pyaudio  # type: ignore
            self.pyaudio = pyaudio
            self.audio = pyaudio.PyAudio()
            self.FORMAT = pyaudio.paFloat32
            self.backend = 'pyaudio'
            logger.info("Audio backend: PyAudio")
        except Exception:
            self.pyaudio = None
            self.audio = None
            self.FORMAT = None
            try:
                import sounddevice as sd  # type: ignore
                import numpy as np  # type: ignore
                self.sd = sd
                self.np = np
                self.backend = 'sounddevice'
                logger.info("Audio backend: sounddevice (fallback)")
            except Exception as e:
                logger.error(f"No audio backend available: {e}")
                self.sd = None
                self.np = None

    def start_capture(self):
        """Start capturing audio from the microphone"""
        try:
            self.frames = []
            if self.backend == 'pyaudio':
                self.stream = self.audio.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK,
                )
            elif self.backend == 'sounddevice':
                self.stream = self.sd.InputStream(
                    samplerate=self.RATE,
                    channels=self.CHANNELS,
                    dtype='float32',
                    blocksize=self.CHUNK,
                )
                self.stream.start()
            else:
                raise RuntimeError("No audio backend available")

            logger.info("Audio capture started")
            return True
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            return False

    def capture_chunk(self):
        """Capture a chunk of audio data"""
        if not self.stream:
            return False

        try:
            if self.backend == 'pyaudio':
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
            elif self.backend == 'sounddevice':
                data, _ = self.stream.read(self.CHUNK)
                # data is numpy array float32 (frames, channels)
                self.frames.append(data.tobytes())
            else:
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to capture audio chunk: {e}")
            return False

    def stop_capture(self):
        """Stop audio capture"""
        if self.stream:
            try:
                if self.backend == 'pyaudio':
                    self.stream.stop_stream()
                    self.stream.close()
                elif self.backend == 'sounddevice':
                    self.stream.stop()
                    self.stream.close()
            finally:
                logger.info("Audio capture stopped")

    def save_audio(self, filename=None):
        """Save captured audio to a WAV file"""
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
                # sample width in bytes: PyAudio gives size, sounddevice uses float32 (4 bytes)
                if self.backend == 'pyaudio' and self.audio and self.FORMAT is not None:
                    sampwidth = self.audio.get_sample_size(self.FORMAT)
                else:
                    sampwidth = 4
                wf.setsampwidth(sampwidth)
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))

            logger.info(f"Audio saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None

    def cleanup(self):
        """Clean up audio resources"""
        try:
            if self.stream:
                try:
                    if self.backend == 'pyaudio':
                        self.stream.close()
                    elif self.backend == 'sounddevice':
                        self.stream.close()
                except Exception:
                    pass
            if self.backend == 'pyaudio' and self.audio:
                try:
                    self.audio.terminate()
                except Exception:
                    pass
        finally:
            logger.info("Audio resources cleaned up")
