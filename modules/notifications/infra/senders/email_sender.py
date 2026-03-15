"""Envio de e-mail via SMTP com retry."""

from __future__ import annotations

import smtplib
import email.message
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from domain.exceptions import SmtpException
from settings import settings


class EmailSender:
    """Envia e-mails via SMTP Gmail com retry e backoff."""

    def __init__(self):
        self._host = settings.SMTP_HOST
        self._port = settings.SMTP_PORT
        self._email = settings.SMTP_EMAIL
        self._password = settings.SMTP_PASSWORD

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True,
    )
    def send(self, destinatarios: list[dict[str, Any]], conteudo: str) -> bool:
        """Envia e-mail para lista de destinatários. Assunto fixo: Alerta Meteorológico."""
        emails = [u.get("email") for u in destinatarios if u.get("email")]
        if not emails:
            return False

        msg = email.message.Message()
        msg["Subject"] = "Alerta Meteorológico"
        msg["From"] = self._email
        msg["To"] = ", ".join(emails)
        msg.add_header("Content-Type", "text/html; charset=utf-8")
        msg.set_payload(conteudo)

        try:
            with smtplib.SMTP(self._host, self._port) as s:
                s.starttls()
                s.login(self._email, self._password)
                s.sendmail(self._email, emails, msg.as_string().encode("utf-8"))
            return True
        except smtplib.SMTPException as e:
            raise SmtpException(f"Erro SMTP: {e}") from e
