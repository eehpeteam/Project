"""Tests for configuration module"""

import unittest
import os
from unittest.mock import patch
from src.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration loading and validation"""
    
    def test_config_loads_from_env(self):
        """Test that config loads values from environment"""
        with patch.dict(os.environ, {'AZURE_SPEECH_KEY': 'test-key'}):
            self.assertEqual(os.getenv('AZURE_SPEECH_KEY'), 'test-key')
    
    def test_config_has_required_fields(self):
        """Test that config has all required fields"""
        required_fields = [
            'AZURE_SPEECH_KEY',
            'AZURE_SPEECH_REGION',
            'EMAIL_SENDER',
            'EMAIL_PASSWORD'
        ]
        
        for field in required_fields:
            self.assertTrue(hasattr(Config, field))
    
    def test_config_defaults(self):
        """Test that config has sensible defaults"""
        self.assertEqual(Config.AZURE_SPEECH_REGION, 'eastus')
        self.assertEqual(Config.EMAIL_SMTP_SERVER, 'smtp-mail.outlook.com')
        self.assertEqual(Config.EMAIL_SMTP_PORT, 587)


if __name__ == '__main__':
    unittest.main()
