"""Envio de mensagens via Z-API (WhatsApp) com retry."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from domain.exceptions import WhatsAppApiException
from domain.value_objects import PhoneNumber
from settings import settings


class WhatsAppSender:
    """Envia mensagens via Z-API com retry e backoff."""

    def __init__(self):
        self._instance = settings.WHATSAPP_INSTANCE
        self._token = settings.WHATSAPP_TOKEN
        self._client_token = settings.WHATSAPP_CLIENT_TOKEN
        self._url = (
            f"https://api.z-api.io/instances/{self._instance}/token/{self._token}/send-text"
        )
        self._headers = {"Client-Token": self._client_token}

    def send(self, destinatarios: list[dict[str, Any]], conteudo: str) -> bool:
        """Envia mensagem para cada destinatário. Retorna True se todos enviados."""
        if not destinatarios:
            return False

        all_ok = True
        for user in destinatarios:
            phone = user.get("whatsapp") or user.get("telefone")
            if not phone:
                continue
            normalized = PhoneNumber(phone).normalized
            if not normalized:
                continue
            if not self._send_one(normalized, conteudo):
                all_ok = False
        return all_ok

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True,
    )
    def _send_one(self, phone: str, message: str) -> bool:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                self._url,
                json={"phone": phone, "message": message},
                headers=self._headers,
            )
            if resp.status_code != 200:
                raise WhatsAppApiException(
                    f"Z-API retornou {resp.status_code}: {resp.text}"
                )
        return True
