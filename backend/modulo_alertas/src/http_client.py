import os
import requests
import json
from datetime import date, time
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class HttpClient:
    def __init__(self,
                 base_url: str = None,
                 email: str = None,
                 senha: str = None):
        # Prioriza os argumentos, depois variáveis de ambiente e, por último, valores padrão.
        self.base_url_usuarios = (base_url or os.getenv("API_BASE_URL", "http://localhost:8002")).rstrip("/")
        self.base_url_envios = os.getenv("ENVIOS_API_BASE_URL", "http://localhost:8000").rstrip("/")
        self.email = email or os.getenv("API_EMAIL", "admin@admin.com")
        self.senha = senha or os.getenv("API_PASSWORD", "0_=QsY86jyAE")
        self.token = None

    def _headers(self) -> Dict[str, str]:
        if not self.token:
            raise RuntimeError("Token não encontrado. Execute login() primeiro.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def login(self) -> None:
        url = f"{self.base_url_usuarios}/usuarios/login"
        payload = {"email": self.email, "senha": self.senha}
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Falha no login: {response.status_code} - {response.text}")

        data = response.json()
        self.token = data.get("token")

        if not self.token:
            raise RuntimeError("Token não retornado pela API.")
        print("Login realizado com sucesso.")

    def obter_eventos(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url_usuarios}/eventos"
        response = requests.get(url, headers=self._headers())

        if response.status_code != 200:
            raise RuntimeError(f"Erro ao obter eventos: {response.status_code} - {response.text}")
        return response.json()

    def obter_cidades(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url_usuarios}/cidades"
        response = requests.get(url, headers=self._headers())

        if response.status_code != 200:
            raise RuntimeError(f"Erro ao obter cidades: {response.status_code} - {response.text}")
        return response.json()

    def importar_avisos(self, avisos: List[Dict[str, Any]]) -> str:
        """
        Envia uma lista de avisos para a API Java.
        Cada item deve seguir o formato do AvisoDTO.
        """
        url = f"{self.base_url_usuarios}/avisos/lote"
        payload = {"avisos": avisos}

        # conversão segura de datas e horários para string ISO-8601
        def default_serializer(o):
            if isinstance(o, (date, time)):
                return o.isoformat()
            raise TypeError(f"Objeto não serializável: {type(o)}")

        
        payloadJson = json.dumps(payload, default=default_serializer)

        response = requests.post(
            url,
            data=payloadJson,
            headers=self._headers()
        )

        if response.status_code != 200:
            raise RuntimeError(f"Erro ao importar avisos: {response.status_code} - {response.text}")

        return response.text

    def iniciar_processamento_alertas(self) -> None:
        """
        Inicia o processamento de alertas no módulo de envios.
        """
        url = f"{self.base_url_envios}/alerts/start"
        print(f"Iniciando processamento de alertas no módulo de envios em {url}...")
        response = requests.post(url)

        if response.status_code != 200:
            raise RuntimeError(f"Falha ao iniciar processamento de alertas: {response.status_code} - {response.text}")
        print("Processamento de alertas iniciado com sucesso.")