# Teams Meeting Audio to Notes - Project Setup

## Project Overview

Python application that captures audio from Microsoft Teams meetings, transcribes it using Azure Cognitive Services, formats into professional meeting notes, and distributes via email.

## Setup Progress

- [x] Project structure created
- [x] Core modules implemented
- [x] Configuration management set up
- [x] Requirements file created
- [x] Tests scaffolded
- [ ] Virtual environment setup
- [ ] Dependencies installed
- [ ] Configuration validation
- [ ] Initial test run

## Key Files

- `main.py` - Entry point
- `src/pipeline.py` - Main orchestration
- `src/audio_capture.py` - Audio recording
- `src/transcription.py` - Speech-to-text
- `src/note_formatter.py` - Document generation
- `src/email_sender.py` - Email distribution

## Next Steps

1. Create virtual environment
2. Install dependencies from requirements.txt
3. Configure .env file with Azure and email credentials
4. Run validation test
5. Execute first meeting capture

## Environment Setup

Create .env file with:
- AZURE_SPEECH_KEY
- AZURE_SPEECH_REGION
- EMAIL_SENDER
- EMAIL_PASSWORD
