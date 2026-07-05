"""
tools/email_tool.py
====================
SMTP email dispatch. This module NEVER sends an email on its own
initiative — `send_email` is only ever called after the human-in-the-loop
confirmation node has recorded an explicit "yes" from the user (see
agents/confirmation.py and agents/email_agent.py).
"""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from typing import Tuple

from config import settings
from utils.logger import get_logger, log_email

logger = get_logger()


def build_email(to_address: str, subject: str, body: str) -> MIMEText:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.email_from or settings.smtp_user or "researchcompass@localhost"
    msg["To"] = to_address
    return msg


def send_email(to_address: str, subject: str, body: str) -> Tuple[bool, str]:
    """
    Sends an email via SMTP. Returns (success, message).
    If SMTP is not configured, logs the email as "not sent" and returns
    a clear explanatory message rather than raising.
    """
    if not settings.has_smtp:
        log_email(to_address, subject, body, sent=False)
        return False, (
            "SMTP is not configured (SMTP_HOST/SMTP_USER/SMTP_PASSWORD missing in .env). "
            "The email was logged but not sent."
        )

    msg = build_email(to_address, subject, body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(msg["From"], [to_address], msg.as_string())
        log_email(to_address, subject, body, sent=True)
        return True, f"Email successfully sent to {to_address}."
    except Exception as exc:
        logger.error("SMTP send failed: %s", exc)
        log_email(to_address, subject, body, sent=False)
        return False, f"Failed to send email: {exc}"
