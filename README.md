# Teams Meeting Audio to Notes

A comprehensive Python application that captures audio from Microsoft Teams meetings, transcribes it using Azure Cognitive Services, formats the transcription into professional meeting notes, and automatically distributes them to participants via email.

## Features

- 🎤 **Audio Capture**: Record audio from Teams meetings with configurable quality settings
- 🗣️ **Speech-to-Text**: Accurate transcription using Azure Cognitive Services
- 📄 **Professional Formatting**: Automatically formats notes with metadata, key points, and action items
- 📧 **Email Distribution**: Sends formatted notes to meeting participants with attachments
- 📝 **Structured Notes**: Generates Word documents (.docx) for easy sharing and archiving
- 🔧 **Configurable**: Environment-based configuration for easy deployment

## Prerequisites

- Python 3.8 or higher
- Microsoft Azure account with Cognitive Services (Speech API)
- Email account (Outlook/Office 365 recommended)
- Active microphone/audio input device

## Installation

1. **Clone or create the project directory**:
   ```bash
   cd d:\Project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your credentials:
     ```
     AZURE_SPEECH_KEY=your_azure_speech_key
     AZURE_SPEECH_REGION=eastus
     EMAIL_SENDER=your_email@outlook.com
     EMAIL_PASSWORD=your_app_password
     ```

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_SPEECH_KEY` | Azure Speech API key | `sk-xxx` |
| `AZURE_SPEECH_REGION` | Azure region | `eastus` |
| `EMAIL_SENDER` | Sender email address | `your_email@outlook.com` |
| `EMAIL_PASSWORD` | Email app password* | `your_password` |
| `EMAIL_SMTP_SERVER` | SMTP server | `smtp-mail.outlook.com` |
| `EMAIL_SMTP_PORT` | SMTP port | `587` |
| `OUTPUT_DIRECTORY` | Notes output directory | `./meeting_notes` |

**\*Important**: For Gmail/Outlook, use an [App Password](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-your-microsoft-account) instead of your regular password.

## Usage

### Basic Usage

```bash
python main.py --title "Team Standup" --participants john@example.com jane@example.com
```

### With Duration (for testing)

```bash
python main.py --title "Sprint Planning" --duration 60 --participants team@example.com
```

### With Action Items

```bash
python main.py --title "Project Kickoff" \
  --participants lead@example.com team@example.com \
  --action-items "Create project plan" "Set up repository" "Review requirements"
```

### With Custom Email Message

```bash
python main.py --title "Board Meeting" \
  --participants exec1@example.com exec2@example.com \
  --message "Please review the attached meeting notes and provide feedback by EOD."
```

### Validate Configuration

```bash
python main.py --validate-config
```

## API Reference

### MeetingPipeline

Main orchestrator for the entire workflow.

```python
from src.pipeline import MeetingPipeline

# Create pipeline
pipeline = MeetingPipeline(
    meeting_title="Team Meeting",
    participants=["john@example.com", "jane@example.com"]
)

# Capture audio
audio_file = pipeline.capture_audio(duration_seconds=60)

# Transcribe
transcription = pipeline.transcribe_audio()

# Format notes
notes_file = pipeline.format_notes(
    include_full_transcription=True,
    action_items=["Item 1", "Item 2"]
)

# Send to participants
pipeline.send_notes(custom_message="See attached notes")
```

### AudioCapture

Record audio from system microphone.

```python
from src.audio_capture import AudioCapture

capture = AudioCapture()
capture.start_capture()
# ... capture audio ...
capture.stop_capture()
audio_file = capture.save_audio("meeting.wav")
capture.cleanup()
```

### Transcriber

Convert audio to text using Azure Speech Services.

```python
from src.transcription import Transcriber

transcriber = Transcriber()
text = transcriber.transcribe_file("audio.wav")
```

### MeetingNoteFormatter

Create professional Word documents from transcriptions.

```python
from src.note_formatter import MeetingNoteFormatter

formatter = MeetingNoteFormatter(
    meeting_title="Team Meeting",
    participants=["john@example.com"]
)
formatter.add_key_points_from_transcription(text)
formatter.add_action_items(["Action 1", "Action 2"])
formatter.save("notes.docx")
```

### EmailSender

Distribute notes via email.

```python
from src.email_sender import EmailSender

sender = EmailSender()
sender.send_meeting_notes(
    recipient_emails=["john@example.com"],
    meeting_title="Team Meeting",
    notes_file_path="notes.docx"
)
```

## Project Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── audio_capture.py       # Audio recording
│   ├── transcription.py       # Speech-to-text
│   ├── note_formatter.py      # Document formatting
│   ├── email_sender.py        # Email distribution
│   ├── logger.py              # Logging setup
│   └── pipeline.py            # Main orchestration
├── tests/                     # Unit tests
├── meeting_notes/             # Output directory
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .env.example               # Configuration template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Logging

Logs are automatically saved to `meeting_notes/app.log`. Configure logging level in `.env`:

```
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### Azure Speech Services Error

- Verify `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` are correct
- Check that the Speech API is enabled in your Azure subscription
- Ensure your region is available for Speech Services

### Email Not Sending

- Verify SMTP credentials and server settings
- For Outlook/Office 365, use [App Passwords](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-your-microsoft-account)
- Check that "Less secure app access" is disabled (Outlook requirement)
- Verify firewall allows SMTP port 587

### Audio Capture Issues

- Ensure microphone is connected and working
- Check system volume levels
- Verify PyAudio installation: `pip install pyaudio`
- On Windows, install [VC++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) if PyAudio fails to install

### Transcription Cuts Off

- Use `transcriber.transcribe_continuous()` for longer meetings
- Consider splitting very long meetings into segments
- Check Azure Speech Services limits for your subscription tier

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests with coverage
pytest tests/ --cov=src
```

## Security Considerations

- Never commit `.env` file to version control
- Use environment variables for all credentials
- For production, consider using Azure Key Vault
- Restrict file permissions on output directories containing sensitive notes
- Use dedicated app passwords instead of account passwords

## Performance Tips

- Use `AZURE_SPEECH_REGION` closest to your location
- For very long meetings (1+ hour), process in segments
- Archive old meeting notes periodically to manage storage
- Use continuous recognition for better accuracy on long audio files

## Limitations

- Maximum file size depends on Azure Speech Services tier
- Real-time transcription requires separate implementation
- Some specialized terminology may not be recognized without custom models
- Email delivery depends on SMTP server availability

## Future Enhancements

- Real-time transcription during meetings
- Custom vocabulary and language models
- Meeting sentiment analysis
- Integration with Teams bot for direct capture
- Calendar integration for automatic scheduling
- Multi-language support
- Custom formatting templates

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Write tests for new features
2. Follow PEP 8 style guide
3. Update README with changes
4. Document complex functions
5. Test before submitting

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:

1. Check the Troubleshooting section
2. Review Azure Cognitive Services documentation
3. Check email provider SMTP requirements
4. Create an issue with detailed error logs

## Credits

Built with:
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio recording
- [Azure Speech Services](https://azure.microsoft.com/en-us/services/cognitive-services/speech-services/) - Transcription
- [python-docx](https://python-docx.readthedocs.io/) - Document generation
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Configuration management

---

**Last Updated**: February 2026
