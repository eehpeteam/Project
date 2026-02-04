"""Simple GUI for Teams Meeting Audio to Notes

Provides Start/Stop controls to capture audio while a Microsoft Teams
meeting is in progress, then transcribes, formats notes, and emails them
to participants.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

from src.config import Config
from src.logger import setup_logger
from src.audio_capture import AudioCapture
from src.transcription import get_transcriber
from src.note_formatter import MeetingNoteFormatter
from src.email_sender import EmailSender


logger = setup_logger('teams_notes.gui')


class TeamsNotesGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Teams Meeting Notes")
        self.root.geometry("640x480")

        # State
        self.stop_event = threading.Event()
        self.worker_thread = None

        # Form variables
        self.var_title = tk.StringVar(value="Team Meeting")
        self.var_participants = tk.StringVar(value="")
        self.var_message = tk.StringVar(value="")
        self.var_status = tk.StringVar(value="Idle")

        # Layout
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        # Meeting title
        ttk.Label(frm, text="Meeting Title").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.var_title, width=40).grid(row=0, column=1, sticky=tk.EW)

        # Participants
        ttk.Label(frm, text="Participants (comma-separated)").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.var_participants, width=40).grid(row=1, column=1, sticky=tk.EW)

        # Custom message
        ttk.Label(frm, text="Email Message (optional)").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.var_message, width=40).grid(row=2, column=1, sticky=tk.EW)

        # Action items
        ttk.Label(frm, text="Action Items (one per line, optional)").grid(row=3, column=0, sticky=tk.W)
        self.txt_actions = tk.Text(frm, height=5, width=40)
        self.txt_actions.grid(row=3, column=1, sticky=tk.EW)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=12)
        self.btn_start = ttk.Button(btns, text="Start", command=self.on_start)
        self.btn_stop = ttk.Button(btns, text="Stop", command=self.on_stop, state=tk.DISABLED)
        self.btn_start.grid(row=0, column=0, padx=6)
        self.btn_stop.grid(row=0, column=1, padx=6)

        # Status
        ttk.Label(frm, text="Status").grid(row=5, column=0, sticky=tk.W)
        ttk.Label(frm, textvariable=self.var_status).grid(row=5, column=1, sticky=tk.W)

        # Log/Progress area
        ttk.Label(frm, text="Progress Log").grid(row=6, column=0, sticky=tk.W)
        self.txt_log = tk.Text(frm, height=10)
        self.txt_log.grid(row=6, column=1, sticky=tk.NSEW)

        # Configure grid weights
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

    def log(self, msg: str):
        logger.info(msg)
        self.var_status.set(msg)
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)

    def on_start(self):
        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            messagebox.showerror("Configuration Error", f"{e}\nPlease update your .env file.")
            return

        participants = [p.strip() for p in self.var_participants.get().split(',') if p.strip()]
        if not participants:
            if not messagebox.askyesno("No Participants", "No participants specified. Continue without emailing notes?"):
                return

        self.stop_event.clear()
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.log("Starting audio capture…")

        # Launch worker thread
        self.worker_thread = threading.Thread(target=self._run_workflow, args=(participants,), daemon=True)
        self.worker_thread.start()

    def on_stop(self):
        self.log("Stopping… finishing capture and processing")
        self.stop_event.set()
        self.btn_stop.config(state=tk.DISABLED)

    def _run_workflow(self, participants):
        # Step 1: Capture audio until stop
        audio_capture = AudioCapture()
        if not audio_capture.start_capture():
            self.log("Failed to start audio capture")
            self._reset_buttons()
            return

        # Capture loop
        while not self.stop_event.is_set():
            audio_capture.capture_chunk()
            time.sleep(0.1)

        # Stop and save
        audio_capture.stop_capture()
        audio_file = audio_capture.save_audio()
        audio_capture.cleanup()
        if not audio_file:
            self.log("No audio captured; aborting.")
            self._reset_buttons()
            return
        self.log(f"Audio saved: {audio_file}")

        # Step 2: Transcribe
        try:
            self.log("Transcribing audio…")
            transcriber = get_transcriber()
            transcription = transcriber.transcribe_file(audio_file)
        except Exception as e:
            self.log(f"Transcription error: {e}")
            self._reset_buttons()
            return

        if not transcription:
            self.log("Transcription failed or empty.")
            self._reset_buttons()
            return
        self.log("Transcription completed.")

        # Step 3: Format notes
        formatter = MeetingNoteFormatter(meeting_title=self.var_title.get(), participants=participants)
        formatter.add_key_points_from_transcription(transcription)
        # Optional action items
        action_items = [line.strip() for line in self.txt_actions.get("1.0", tk.END).splitlines() if line.strip()]
        if action_items:
            formatter.add_action_items(action_items)
        formatter.add_full_transcription(transcription)
        notes_file = formatter.save()
        if not notes_file:
            self.log("Failed to save notes document.")
            self._reset_buttons()
            return
        self.log(f"Notes saved: {notes_file}")

        # Step 4: Email notes (if participants provided)
        if participants:
            self.log("Sending notes via email…")
            sender = EmailSender()
            ok = sender.send_meeting_notes(
                recipient_emails=participants,
                meeting_title=self.var_title.get(),
                notes_file_path=notes_file,
                message_body=self.var_message.get() or None,
            )
            if ok:
                self.log("Email sent successfully.")
            else:
                self.log("Failed to send email.")

        self.log("Workflow completed.")
        self._reset_buttons()

    def _reset_buttons(self):
        # Return controls to initial state
        def _reset():
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
        self.root.after(0, _reset)


def main():
    root = tk.Tk()
    app = TeamsNotesGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
