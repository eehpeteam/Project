"""Email sending module for distributing meeting notes"""

import smtplib
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from src.config import Config

logger = logging.getLogger(__name__)


class EmailSender:
    """Handle sending meeting notes via email"""
    
    def __init__(self, sender_email=None, sender_password=None, smtp_server=None, smtp_port=None):
        """
        Initialize email sender with credentials
        
        Args:
            sender_email (str): Email address to send from
            sender_password (str): Email password or app password
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
        """
        self.sender_email = sender_email or Config.EMAIL_SENDER
        self.sender_password = sender_password or Config.EMAIL_PASSWORD
        self.smtp_server = smtp_server or Config.EMAIL_SMTP_SERVER
        self.smtp_port = smtp_port or Config.EMAIL_SMTP_PORT
    
    def send_email(self, recipient_emails, subject, body, attachments=None):
        """
        Send email with optional attachments
        
        Args:
            recipient_emails (list or str): Email address(es) to send to
            subject (str): Email subject
            body (str): Email body text
            attachments (list): List of file paths to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if isinstance(recipient_emails, str):
            recipient_emails = [recipient_emails]
        
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = ", ".join(recipient_emails)
            message['Date'] = formatdate(localtime=True)
            message['Subject'] = subject
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if Path(attachment_path).exists():
                        self._attach_file(message, attachment_path)
                    else:
                        logger.warning(f"Attachment not found: {attachment_path}")
            
            # Send email
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {', '.join(recipient_emails)}")
            return True
        
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_meeting_notes(self, recipient_emails, meeting_title, notes_file_path, message_body=None):
        """
        Send meeting notes as email
        
        Args:
            recipient_emails (list or str): Email address(es) to send to
            meeting_title (str): Title of the meeting
            notes_file_path (str): Path to the notes document
            message_body (str): Optional custom message body
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if message_body is None:
            message_body = f"Please find attached the notes from the {meeting_title} meeting."
        
        subject = f"Meeting Notes: {meeting_title}"
        
        return self.send_email(
            recipient_emails=recipient_emails,
            subject=subject,
            body=message_body,
            attachments=[notes_file_path]
        )
    
    @staticmethod
    def _attach_file(message, file_path):
        """
        Attach a file to the email message
        
        Args:
            message: Email message object
            file_path (str): Path to file to attach
        """
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = Path(file_path).name
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            message.attach(part)
            logger.info(f"File attached: {filename}")
        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {e}")
