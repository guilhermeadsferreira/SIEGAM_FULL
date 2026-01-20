import os
from typing import List, Dict, Any
import httpx
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

BASE_URL = os.getenv("EXTERNAL_API_URL", "http://modulo_usuarios:8002")
API_EMAIL = os.getenv("API_EMAIL", "admin@admin.com")
API_PASSWORD = os.getenv("API_PASSWORD", "0_=QsY86jyAE")

class ExternalIntegrationService:

    def __init__(self):
        limits = httpx.Limits(
            max_connections=10,
            max_keepalive_connections=5
        )
        # Sessão HTTP reutilizável
        self.base_url = BASE_URL
        self.email = API_EMAIL
        self.senha = API_PASSWORD
        self.token = None
        self.token_created_at = None
        # Usar AsyncClient para chamadas assíncronas
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=15.0, limits=limits)
        # Tempo de expiração do token em segundos (55 minutos)
        self.TOKEN_EXPIRY_TIME = 55 * 60

    async def login(self) -> None:
        """Realiza o login na API para obter o token de autenticação."""
        url = "/usuarios/login"
        payload = {"email": self.email, "senha": self.senha}
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")
            if not self.token:
                raise RuntimeError("Token não foi retornado pela API após o login.")
            
            # Registra o momento da autenticação
            self.token_created_at = datetime.now()
            
            # Adiciona o token aos headers do cliente para todas as requisições futuras
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            print("[ExternalIntegrationService] Login realizado com sucesso.")
        except httpx.HTTPStatusError as e:
            error_message = f"Falha no login: {e.response.status_code} - {e.response.text}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise RuntimeError(error_message) from e
        except httpx.RequestError as e:
            error_message = f"Erro de conexão durante o login para {e.request.url}: {e}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise RuntimeError(error_message) from e

    def _token_expired(self) -> bool:
        """Verifica se o token expirou (passaram 55 minutos)."""
        if not self.token or not self.token_created_at:
            return True
        
        elapsed_time = (datetime.now() - self.token_created_at).total_seconds()
        return elapsed_time >= self.TOKEN_EXPIRY_TIME

    async def get_alerts_for_today(self) -> List[Dict[str, Any]]:
        """
        GET /avisos/today
        """
        if self._token_expired():
            await self.login()

        url = "/avisos/today"
        print(f"[ExternalIntegrationService] Buscando alertas do dia: GET {url}")
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            alerts = response.json()
            print(f"[ExternalIntegrationService] {len(alerts) if alerts else 0} alertas encontrados para hoje.")
            return alerts
        except httpx.HTTPStatusError as e:
            error_message = f"Erro ao buscar alertas: {e.response.status_code} - {e.response.text}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise
        except httpx.RequestError as e:
            error_message = f"Erro de conexão ao buscar alertas em {e.request.url}: {e}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise

    async def get_users_by_city_and_alert(self, idCidade: str, idEvento: str):
        """
        GET /usuarios/preferencia/evento/{idEvento}/cidade/{idCidade}/Detalhado
        """
        if self._token_expired():
            await self.login()

        url = f"/usuarios/preferencia/evento/{idEvento}/cidade/{idCidade}/Detalhado"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            users = response.json()
            return users
        except httpx.HTTPStatusError as e:
            error_message = f"Erro ao buscar usuários: {e.response.status_code} - {e.response.text}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise
        except httpx.TimeoutException as e:
            error_message = f"TIMEOUT ao buscar usuários em {e.request.url}. A requisição demorou mais de {self.client.timeout.read} segundos."
            print(f"[ExternalIntegrationService] {error_message}")
            raise RuntimeError(error_message) from e
        except httpx.RequestError as e:
            error_message = f"Erro de conexão ao buscar usuários em {e.request.url}: {e}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise

    async def get_all_status(self) -> List[Dict[str, Any]]:
        """
        GET /status
        Retorna lista de status disponíveis com id, nomeStatus e idCanal
        """
        if self._token_expired():
            await self.login()

        url = "/status"
        print(f"[ExternalIntegrationService] Buscando todos os status: GET {url}")
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            status_list = response.json()
            print(f"[ExternalIntegrationService] {len(status_list) if status_list else 0} status encontrados.")
            return status_list
        except httpx.HTTPStatusError as e:
            error_message = f"Erro ao buscar status: {e.response.status_code} - {e.response.text}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise
        except httpx.TimeoutException as e:
            error_message = f"TIMEOUT ao buscar status em {e.request.url}. A requisição demorou mais de {self.client.timeout.read} segundos."
            print(f"[ExternalIntegrationService] {error_message}")
            raise RuntimeError(error_message) from e
        except httpx.RequestError as e:
            error_message = f"Erro de conexão ao buscar status em {e.request.url}: {e}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise

    async def create_envio(
        self,
        idCanal: str,
        idAviso: str,
        idUsuarioDestinatario: str,
        idStatus: str
    ) -> Dict[str, Any]:
        """
        POST /envios
        Cria um novo registro de envio de notificação
        
        Args:
            idCanal: ID do canal de comunicação (WhatsApp, Email, etc)
            idAviso: ID do aviso/alerta
            idUsuarioDestinatario: ID do usuário destinatário
            idStatus: ID do status do envio
            
        Returns:
            Resposta da API com os dados do envio criado
        """
        if self._token_expired():
            await self.login()

        url = "/envios"
        payload = {
            "idCanal": idCanal,
            "idAviso": idAviso,
            "idUsuarioDestinatario": idUsuarioDestinatario,
            "idStatus": idStatus
        }
        
        print(f"[ExternalIntegrationService] Criando envio: POST {url}")
        print(f"[ExternalIntegrationService] Payload: {payload}")
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            envio_data = response.json()
            print(f"[ExternalIntegrationService] Envio criado com sucesso. ID: {envio_data.get('id', 'N/A')}")
            return envio_data
        except httpx.HTTPStatusError as e:
            error_message = f"Erro ao criar envio: {e.response.status_code} - {e.response.text}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise
        except httpx.TimeoutException as e:
            error_message = f"TIMEOUT ao criar envio em {e.request.url}. A requisição demorou mais de {self.client.timeout.read} segundos."
            print(f"[ExternalIntegrationService] {error_message}")
            raise RuntimeError(error_message) from e
        except httpx.RequestError as e:
            error_message = f"Erro de conexão ao criar envio em {e.request.url}: {e}"
            print(f"[ExternalIntegrationService] {error_message}")
            raise
