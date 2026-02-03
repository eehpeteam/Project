"""Tests for note formatter module"""

import unittest
from pathlib import Path
from src.note_formatter import MeetingNoteFormatter
from src.config import Config


class TestMeetingNoteFormatter(unittest.TestCase):
    """Test meeting note formatting"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = MeetingNoteFormatter(
            meeting_title="Test Meeting",
            participants=["test@example.com"]
        )
    
    def test_formatter_creation(self):
        """Test formatter can be created"""
        self.assertIsNotNone(self.formatter)
        self.assertEqual(self.formatter.meeting_title, "Test Meeting")
    
    def test_add_section(self):
        """Test adding sections"""
        self.formatter.add_section("Test Section")
        self.assertIsNotNone(self.formatter.doc)
    
    def test_add_text(self):
        """Test adding text"""
        self.formatter.add_text("This is test text")
        self.assertIsNotNone(self.formatter.doc)
    
    def test_add_bullet_point(self):
        """Test adding bullet points"""
        self.formatter.add_bullet_point("Test point")
        self.assertIsNotNone(self.formatter.doc)
    
    def test_save_document(self):
        """Test saving document"""
        self.formatter.add_text("Test content")
        output_file = self.formatter.save("test_notes.docx")
        
        # Check file was created
        if output_file:
            self.assertTrue(Path(output_file).exists())
            # Clean up
            Path(output_file).unlink()


if __name__ == '__main__':
    unittest.main()
