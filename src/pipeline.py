"""Main pipeline orchestration module"""

import logging
from src.audio_capture import AudioCapture
from src.transcription import get_transcriber
from src.note_formatter import MeetingNoteFormatter
from src.email_sender import EmailSender
from src.logger import setup_logger

logger = setup_logger('teams_notes.pipeline')


class MeetingPipeline:
    """Orchestrate the entire meeting capture and notes distribution pipeline"""
    
    def __init__(self, meeting_title="Team Meeting", participants=None):
        """
        Initialize the pipeline
        
        Args:
            meeting_title (str): Title of the meeting
            participants (list): List of participant emails
        """
        self.meeting_title = meeting_title
        self.participants = participants or []
        self.audio_file = None
        self.transcription = None
        self.notes_file = None
    
    def capture_audio(self, duration_seconds=None):
        """
        Capture audio from Teams meeting
        
        Args:
            duration_seconds (int): Duration to capture (for testing). 
                                   If None, manual stop is required.
            
        Returns:
            str: Path to saved audio file or None
        """
        logger.info(f"Starting audio capture for meeting: {self.meeting_title}")
        
        audio_capture = AudioCapture()
        
        if not audio_capture.start_capture():
            logger.error("Failed to start audio capture")
            return None
        
        try:
            if duration_seconds:
                import time
                logger.info(f"Capturing for {duration_seconds} seconds...")
                for _ in range(duration_seconds * 10):  # 100ms chunks
                    audio_capture.capture_chunk()
                    time.sleep(0.1)
            else:
                logger.info("Audio capture in progress. Press Ctrl+C to stop.")
                while True:
                    audio_capture.capture_chunk()
        except KeyboardInterrupt:
            logger.info("Audio capture stopped by user")
        finally:
            audio_capture.stop_capture()
            self.audio_file = audio_capture.save_audio()
            audio_capture.cleanup()
        
        return self.audio_file
    
    def transcribe_audio(self):
        """
        Transcribe captured audio
        
        Returns:
            str: Transcription text or None
        """
        if not self.audio_file:
            logger.error("No audio file to transcribe. Capture audio first.")
            return None
        
        logger.info("Starting transcription...")
        transcriber = get_transcriber()
        self.transcription = transcriber.transcribe_file(self.audio_file)
        
        if self.transcription:
            logger.info("Transcription completed successfully")
            logger.debug(f"Transcription preview: {self.transcription[:100]}...")
        else:
            logger.error("Transcription failed")
        
        return self.transcription
    
    def format_notes(self, include_full_transcription=True, action_items=None):
        """
        Format transcription into professional meeting notes
        
        Args:
            include_full_transcription (bool): Include full transcription in notes
            action_items (list): Optional list of action items to include
            
        Returns:
            str: Path to saved notes file or None
        """
        if not self.transcription:
            logger.error("No transcription available. Transcribe audio first.")
            return None
        
        logger.info("Formatting meeting notes...")
        
        formatter = MeetingNoteFormatter(
            meeting_title=self.meeting_title,
            participants=self.participants
        )
        
        formatter.add_key_points_from_transcription(self.transcription)
        
        if include_full_transcription:
            formatter.add_full_transcription(self.transcription)
        
        if action_items:
            formatter.add_action_items(action_items)
        
        self.notes_file = formatter.save()
        
        if self.notes_file:
            logger.info(f"Meeting notes saved: {self.notes_file}")
        else:
            logger.error("Failed to save meeting notes")
        
        return self.notes_file
    
    def send_notes(self, custom_message=None):
        """
        Send meeting notes to participants
        
        Args:
            custom_message (str): Optional custom message to include in email
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.notes_file:
            logger.error("No notes file to send. Format notes first.")
            return False
        
        if not self.participants:
            logger.warning("No participants specified. Skipping email distribution.")
            return False
        
        logger.info(f"Sending meeting notes to {len(self.participants)} participant(s)...")
        
        email_sender = EmailSender()
        success = email_sender.send_meeting_notes(
            recipient_emails=self.participants,
            meeting_title=self.meeting_title,
            notes_file_path=self.notes_file,
            message_body=custom_message
        )
        
        if success:
            logger.info("Meeting notes sent successfully")
        else:
            logger.error("Failed to send meeting notes")
        
        return success
    
    def run_full_pipeline(self, duration_seconds=None, action_items=None, custom_message=None):
        """
        Run the complete pipeline from capture to distribution
        
        Args:
            duration_seconds (int): Duration to capture (for testing)
            action_items (list): Optional action items to include
            custom_message (str): Optional custom email message
            
        Returns:
            bool: True if all steps completed successfully
        """
        logger.info("="*50)
        logger.info("Starting Teams Meeting Notes Pipeline")
        logger.info("="*50)
        
        # Step 1: Capture audio
        if not self.capture_audio(duration_seconds):
            return False
        
        # Step 2: Transcribe
        if not self.transcribe_audio():
            return False
        
        # Step 3: Format notes
        if not self.format_notes(action_items=action_items):
            return False
        
        # Step 4: Send notes
        if not self.send_notes(custom_message):
            return False
        
        logger.info("="*50)
        logger.info("Pipeline completed successfully!")
        logger.info("="*50)
        
        return True
