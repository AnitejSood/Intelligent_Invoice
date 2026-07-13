"""IMAP Email Ingestion Service."""

import os
import imaplib
import email
from email.header import decode_header
import uuid
from typing import List

from backend.services.settings_service import SettingsService
from backend.services.pipeline_service import PipelineService
from backend.database.session import SessionLocal
from backend.core.logging_config import get_logger

logger = get_logger("services.imap")


class ImapService:
    """Service for polling IMAP inboxes and extracting invoice attachments."""

    @staticmethod
    def _decode_string(value) -> str:
        """Decode email header strings safely."""
        if not value:
            return ""
        if isinstance(value, str):
            return value
        try:
            decoded_parts = decode_header(value)
            res = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    res += part.decode(encoding or "utf-8", errors="ignore")
                else:
                    res += str(part)
            return res
        except Exception:
            return str(value)

    @staticmethod
    def poll_inbox() -> int:
        """
        Poll the configured IMAP inbox for UNSEEN emails with PDF attachments.
        Process them via PipelineService and mark as SEEN.
        Returns the number of invoices processed.
        """
        settings = SettingsService.get_all()
        if not settings.get("EMAIL_INGESTION_ENABLED"):
            return 0

        server = settings.get("EMAIL_SERVER")
        username = settings.get("EMAIL_ADDRESS")
        password = settings.get("EMAIL_PASSWORD")

        if not all([server, username, password]):
            logger.warning("Email ingestion is enabled but IMAP credentials are not fully configured.")
            return 0

        processed_count = 0
        mail = None

        try:
            logger.info(f"Connecting to IMAP server: {server}")
            mail = imaplib.IMAP4_SSL(server)
            mail.login(username, password)
            mail.select("inbox")

            status, messages = mail.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                return 0

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails.")

            from backend.core.config import settings
            os.makedirs(settings.upload_path, exist_ok=True)

            for e_id in email_ids:
                status, msg_data = mail.fetch(e_id, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = ImapService._decode_string(msg.get("Subject"))
                        sender = ImapService._decode_string(msg.get("From"))
                        
                        logger.info(f"Processing email from {sender}: {subject}")

                        has_attachment = False
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_maintype() == "multipart":
                                    continue
                                if part.get("Content-Disposition") is None:
                                    continue
                                
                                filename = part.get_filename()
                                if filename:
                                    filename = ImapService._decode_string(filename)
                                    # Only process PDFs
                                    if filename.lower().endswith(".pdf"):
                                        has_attachment = True
                                        
                                        # Save attachment
                                        safe_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
                                        file_path = str(settings.upload_path / safe_filename)
                                        
                                        with open(file_path, "wb") as f:
                                            f.write(part.get_payload(decode=True))
                                            
                                        logger.info(f"Downloaded attachment: {safe_filename}. Sending to pipeline.")
                                        
                                        # Process via pipeline
                                        db = SessionLocal()
                                        try:
                                            PipelineService.process_invoice_file(
                                                db=db,
                                                file_path=file_path,
                                                original_filename=filename,
                                                source=f"EMAIL ({sender})"
                                            )
                                            processed_count += 1
                                        except Exception as e:
                                            logger.error(f"Pipeline failed for {filename}: {e}")
                                        finally:
                                            db.close()
                        
                        # Optionally mark as seen only if it was successfully processed
                        # Note: IMAP search UNSEEN automatically marks as seen during fetch usually,
                        # but we can explicitly set flags if needed.

            return processed_count
        
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP Authentication or connection error: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error during IMAP polling: {e}")
            return 0
        finally:
            if mail:
                try:
                    mail.logout()
                except:
                    pass
