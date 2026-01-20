from typing import List, Dict, Any
import requests
import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

class WhatsAppService:
    def __init__(self):
        load_dotenv()

        self.whatsapp_instance = os.getenv("WHATSAPP_INSTANCE")
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN")
        self.whatsapp_client_token = os.getenv("WHATSAPP_CLIENT_TOKEN")

        if not self.whatsapp_instance or not self.whatsapp_token or not self.whatsapp_client_token:
            msg = "Variáveis WHATSAPP_INSTANCE, WHATSAPP_TOKEN e WHATSAPP_CLIENT_TOKEN ausentes."
            print(f"[WhatsAppService] ERRO: {msg}", file=sys.stderr)
            raise ValueError(msg)

        self.url = (
            f"https://api.z-api.io/instances/"
            f"{self.whatsapp_instance}/token/{self.whatsapp_token}/send-text"
        )
        self.headers = {
            "Client-Token": self.whatsapp_client_token
        }

    def _normalize_phone(self, phone: str) -> str:
        """
        Normaliza telefone: remove caracteres não numéricos e
        adiciona o código de país '55' caso não exista.
        Retorna string vazia se não for possível extrair dígitos.
        """
        if not phone:
            return ""
        digits = re.sub(r"\D", "", str(phone))
        if not digits:
            return ""
        if not digits.startswith("55"):
            digits = "55" + digits
        return digits

    def send_bulk(self, usuarios: List[Dict[str, Any]], conteudo: str):
        for user in usuarios:
            telefone = user.get("whatsapp") or user.get("telefone")

            if not telefone:
                print(f"[WhatsAppService] Usuário sem telefone: {user}")
                continue
            
            telefone_formatado = self._normalize_phone(telefone)
            payload = {
                "phone": telefone_formatado,
                "message": conteudo
            }

            try:
                response = requests.post(self.url, json=payload, headers=self.headers)

                if response.status_code == 200:
                    print(f"[WhatsAppService] Enviado para {telefone}")
                else:
                    print(
                        f"[WhatsAppService] Falha ao enviar para {telefone}: "
                        f"{response.status_code} - {response.text}"
                    )

            except Exception as e:
                print(f"[WhatsAppService] Erro ao enviar para {telefone}: {e}")
