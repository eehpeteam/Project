#!/usr/bin/env python3
"""
Main entry point for Teams Meeting Audio to Notes application

This script orchestrates the capture of Microsoft Teams meeting audio,
transcription to text, formatting into professional meeting notes,
and distribution to participants via email.
"""

import argparse
import sys
from src.pipeline import MeetingPipeline
from src.config import Config
from src.logger import setup_logger

logger = setup_logger('teams_notes.main')


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Capture Teams meeting audio, transcribe it, and email notes to participants'
    )
    
    parser.add_argument(
        '--title',
        default='Team Meeting',
        help='Title of the meeting (default: Team Meeting)'
    )
    
    parser.add_argument(
        '--participants',
        nargs='+',
        help='Email addresses of participants (space-separated)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='Duration to capture in seconds (for testing). If not specified, capture manually'
    )
    
    parser.add_argument(
        '--action-items',
        nargs='+',
        help='Action items to include in notes (space-separated)'
    )
    
    parser.add_argument(
        '--message',
        help='Custom message to include in email'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        logger.error("Please set required environment variables in .env file")
        return 1
    
    if args.validate_config:
        print("✓ Configuration is valid")
        return 0
    
    # Create pipeline
    pipeline = MeetingPipeline(
        meeting_title=args.title,
        participants=args.participants
    )
    
    # Run pipeline
    try:
        success = pipeline.run_full_pipeline(
            duration_seconds=args.duration,
            action_items=args.action_items,
            custom_message=args.message
        )
        
        if success:
            logger.info("Application completed successfully")
            return 0
        else:
            logger.error("Application failed during execution")
            return 1
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
