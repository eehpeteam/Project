# Project Documentation: Teams Meeting Audio to Notes

## Overview

This project captures audio from Microsoft Teams meetings, transcribes speech to text using Azure Cognitive Services, formats the transcription into professional meeting notes (Word documents), and distributes the notes to participants via email.

## Goals

- Reliable, repeatable pipeline from audio capture → transcription → formatted notes → email delivery
- Clear configuration via environment variables
- Maintainable modular codebase for extension (real-time transcription, calendar integration)
- Safe handling of credentials and output files

## Architecture

- Audio Capture: Records audio from system microphone using PyAudio
- Transcription: Uses Azure Speech Services SDK to convert audio to text
- Note Formatting: Generates .docx documents using python-docx with metadata, summary, action items, and full transcription
- Email Distribution: Sends documents via SMTP (configurable server and port)
- Orchestration: `MeetingPipeline` coordinates the full workflow

## Components (files)

- **Entry point:** [main.py](main.py)
- **Configuration:** [src/config.py](src/config.py)
- **Audio capture:** [src/audio_capture.py](src/audio_capture.py)
- **Transcription:** [src/transcription.py](src/transcription.py)
- **Note formatting:** [src/note_formatter.py](src/note_formatter.py)
- **Email sending:** [src/email_sender.py](src/email_sender.py)
- **Pipeline orchestration:** [src/pipeline.py](src/pipeline.py)
- **Logging setup:** [src/logger.py](src/logger.py)
- **Tests:** [tests/](tests/)
- **Requirements:** [requirements.txt](requirements.txt)
- **Example env:** [.env.example](.env.example)

## Setup & Installation

**Prerequisites**

- Python 3.8+
- Microsoft Azure subscription with Speech service (Speech key + region)
- SMTP-capable email account (Outlook/Gmail with app password recommended)
- Microphone/audio input

**Create virtual environment (Windows PowerShell)**

```powershell
cd d:\Project
python -m venv venv
venv\Scripts\Activate.ps1    # or venv\Scripts\activate for cmd.exe
```

**Install dependencies**

```powershell
pip install -r requirements.txt
```

**Configure environment**

1. Copy `.env.example` to `.env`.
2. Edit `.env` to set at minimum:
   - `AZURE_SPEECH_KEY`
   - `AZURE_SPEECH_REGION`
   - `EMAIL_SENDER`
   - `EMAIL_PASSWORD` (use an app password)

## Environment Variables

- **AZURE_SPEECH_KEY:** Azure Cognitive Services Speech subscription key
- **AZURE_SPEECH_REGION:** Azure region (e.g., eastus)
- **EMAIL_SENDER:** Sender email address
- **EMAIL_PASSWORD:** Sender email password or app password
- **EMAIL_SMTP_SERVER:** SMTP server (default: smtp-mail.outlook.com)
- **EMAIL_SMTP_PORT:** SMTP port (default: 587)
- **OUTPUT_DIRECTORY:** Directory to save audio and notes (default: ./meeting_notes)
- **LOG_LEVEL:** Logging level (DEBUG, INFO, etc.)

## Usage Examples

- Validate configuration only:

```powershell
python main.py --validate-config
```

- Record for 60 seconds, create notes, and email to participants:

```powershell
python main.py --title "Team Sync" --duration 60 --participants alice@example.com bob@example.com
```

- Run pipeline and provide action items and custom message:

```powershell
python main.py --title "Project Kickoff" \
  --participants lead@example.com team@example.com \
  --action-items "Draft plan" "Assign owners" \
  --message "Please review attached notes"
```

## API Reference (high level)

- `MeetingPipeline` ([src/pipeline.py](src/pipeline.py))
  - `capture_audio(duration_seconds=None)` — Capture and save audio file
  - `transcribe_audio()` — Transcribe captured audio
  - `format_notes(include_full_transcription=True, action_items=None)` — Produce .docx
  - `send_notes(custom_message=None)` — Email notes to participants
  - `run_full_pipeline(duration_seconds=None, action_items=None, custom_message=None)` — Run all steps

- `AudioCapture` ([src/audio_capture.py](src/audio_capture.py))
  - `start_capture()`, `capture_chunk()`, `stop_capture()`, `save_audio(filename=None)`, `cleanup()`

- `Transcriber` ([src/transcription.py](src/transcription.py))
  - `transcribe_file(audio_file_path)`, `transcribe_continuous(audio_file_path)`

- `MeetingNoteFormatter` ([src/note_formatter.py](src/note_formatter.py))
  - `add_key_points_from_transcription(text)`, `add_full_transcription(text)`, `add_action_items(items)`, `save(filename=None)`

- `EmailSender` ([src/email_sender.py](src/email_sender.py))
  - `send_email(recipient_emails, subject, body, attachments=None)`, `send_meeting_notes(recipient_emails, meeting_title, notes_file_path)`

## Testing

- Unit tests are located in the `tests/` directory.
- Run tests with:

```powershell
pip install pytest
pytest tests/ -v
```

Note: Some tests (e.g., audio capture) may be environment-dependent and require hardware or mocked inputs.

## Logging

- Logs are configured in `src/logger.py` and will be saved under the output directory (default: `meeting_notes/app.log`).
- Set `LOG_LEVEL` in `.env` to `DEBUG` to get more detail.

## Troubleshooting

- PyAudio installation on Windows may require Visual C++ Build Tools if wheel isn't available.
- If `python -m venv` fails, ensure Python is installed and available in PATH.
- Azure transcription failures: verify key/region and that the Speech resource is provisioned.
- Emails failing: check SMTP server settings and that the `EMAIL_PASSWORD` is an app password.

## Security and Privacy

- **Do not commit `.env`**; secrets must remain local or be provided via secure store (Key Vault).
- Use app passwords and least-privilege accounts for email sending.
- Restrict access to `meeting_notes/` and logs containing transcriptions.

## Deployment Considerations

- For automated runs, place the application on a server with a persistent audio capture source or integrate with a Teams recording webhook/bot.
- Consider moving secrets to Azure Key Vault or environment-specific secret management.
- Use segmentation for long meetings to respect Azure Speech Service limits.

## Limitations & Future Work

- Current capture is local (microphone). Integrate with Teams APIs or a bot for direct meeting audio capture.
- Add real-time streaming transcription for live notes.
- Add custom vocabulary and multi-language support.
- Integrate calendar APIs to automatically fetch participants and meeting titles.

## Contributing

- Fork the repo, implement features, add tests, and open a pull request.
- Follow PEP 8 and include unit tests for new code.

## License

- Intended to be MIT licensed (update `LICENSE` file as needed).

## Contact

- For questions or help, reply here or add issues to the repository.

---

*Generated project documentation created on 2026-02-03.*