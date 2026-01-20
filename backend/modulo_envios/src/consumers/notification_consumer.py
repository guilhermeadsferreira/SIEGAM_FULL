import time
import json
import asyncio
from typing import Any, Dict, List
from redis import Redis
from src.utils.redis_client import redis_client
from src.services.email_service import EmailService
from src.services.whatsapp_service import WhatsAppService
from src.services.external_integration_service import ExternalIntegrationService

class NotificationConsumer:
    def __init__(self):
        self.queue_name = "notification_queue"
        self.redis: Redis = redis_client
        self.email_service = EmailService()
        self.whatsapp_service = WhatsAppService()
        self.external_integration_service = ExternalIntegrationService()
        self.status_list: List[Dict[str, Any]] = []
        # Mapeamento de idCanal -> { nomeStatus.lower() -> id }
        self.status_map: Dict[str, Dict[str, str]] = {}
        # caso futuramente adicione SMS ou outros canais, criar services correspondentes

    async def load_all_status(self):
        """Busca todos os status disponíveis da API externa e armazena em cache."""
        print("[NotificationConsumer] Carregando todos os status disponíveis...")
        try:
            self.status_list = await self.external_integration_service.get_all_status()
            # Agrupar status por canal (idCanal) => { nomeStatus.lower(): id }
            for status in self.status_list:
                status_id = status.get("id")
                nome_status = status.get("nomeStatus")
                id_canal = status.get("idCanal")
                key = str(id_canal) if id_canal is not None else "unknown"
                if not status_id or not nome_status:
                    continue
                if key not in self.status_map:
                    self.status_map[key] = {}
                self.status_map[key][nome_status.lower()] = status_id

            print(f"[NotificationConsumer] {len(self.status_list)} status carregados com sucesso.")
            # Mostrar sumário por canal
            for canal_key, statuses in self.status_map.items():
                print(f"[NotificationConsumer] Canal {canal_key}: {list(statuses.keys())}")
        except Exception as e:
            print(f"[NotificationConsumer] Erro ao carregar status: {e}")
            raise

    def get_status_id(self, idCanal: str, status_name: str = "Sucesso") -> str:
        """Obtém o ID de um status pelo nome dentro do canal indicado por `idCanal`.
        Padrão de `status_name` é 'Sucesso'. Se não encontrar, tenta fallback local ao canal,
        depois usa o primeiro status global disponível.
        """
        key = str(idCanal) if idCanal is not None else "unknown"
        canal_statuses = self.status_map.get(key, {})
        status_id = canal_statuses.get(status_name.lower()) if canal_statuses else None

        if status_id:
            return status_id

        # Fallback 1: usar qualquer status disponível no mesmo canal
        if canal_statuses:
            first = next(iter(canal_statuses.values()), None)
            print(f"[NotificationConsumer] Status '{status_name}' não encontrado para canal {key}. Usando fallback local: {first}")
            return first

        # Fallback 2: usar o primeiro status global carregado
        if self.status_list:
            fallback_global = self.status_list[0].get("id")
            print(f"[NotificationConsumer] Status '{status_name}' não encontrado. Usando fallback global: {fallback_global}")
            return fallback_global

        print(f"[NotificationConsumer] Nenhum status disponível para obter ID do status '{status_name}'.")
        return None

    def start(self):
        """Inicia o consumer com carregamento inicial de status."""
        print("[NotificationConsumer] Iniciando consumo da fila de envios...")
        # Carregar status antes de começar
        try:
            asyncio.run(self.load_all_status())
        except Exception as e:
            print(f"[NotificationConsumer] Falha crítica ao carregar status: {e}")
            raise

        while True:
            _, message = self.redis.blpop(self.queue_name)
            payload = json.loads(message)
            asyncio.run(self.process_notification(payload))
            time.sleep(0.2)

    async def process_notification(self, payload: Dict[str, Any]):
        print(f"[NotificationConsumer] Processando notificação payload: {payload}.")
        canal = payload.get("canal")
        usuarios = payload.get("usuarios", [])
        conteudo = payload.get("conteudo", "")
        alertas = payload.get("alertas", [])

        if not usuarios:
            print(f"[NotificationConsumer] Nenhum usuário para enviar no canal {canal.get('nomeCanal', 'desconhecido')}.")
            return

        if conteudo == "":
            print(f"[NotificationConsumer] Conteúdo vazio para o canal {canal.get('nomeCanal', 'desconhecido')}.")
            return

        nomeCanal = canal.get("nomeCanal")
        idCanal = canal.get("id")
        # Extrair IDs de alerta de forma robusta (suporta vários formatos)
        alert_ids: List[str] = []
        print(f"[NotificationConsumer] alertas recebidos: {alertas}")
        for a in alertas:
            if not isinstance(a, dict):
                continue
            id_val = None
            # novo formato: {'alerta': {'id': '...'}, ...}
            alerta_obj = a.get("alerta")
            if isinstance(alerta_obj, dict):
                id_val = alerta_obj.get("id") or alerta_obj.get("idAviso")

            # formatos alternativos: {'id': '...'} ou {'idAviso': '...'}
            if not id_val:
                id_val = a.get("id") or a.get("idAviso") or a.get("alertaId")

            if id_val:
                alert_ids.append(str(id_val))

        # Remover duplicados mantendo ordem
        seen = set()
        unique_alert_ids = []
        for x in alert_ids:
            if x not in seen:
                seen.add(x)
                unique_alert_ids.append(x)
        alert_ids = unique_alert_ids
        print(f"[NotificationConsumer] Alert IDs encontrados: {alert_ids}")

        try:
            if nomeCanal.lower() == "email":
                self.email_service.send_bulk(usuarios, conteudo)
            elif nomeCanal.lower() == "whatsapp":
                self.whatsapp_service.send_bulk(usuarios, conteudo)
            else:
                print(f"[NotificationConsumer] Canal {nomeCanal} não suportado.")
                return

            # Após envio bem-sucedido, registrar envios na API externa para cada alerta
            if not alert_ids:
                print(f"[NotificationConsumer] Nenhum alerta encontrado para registro de envios.")
            else:
                for aid in alert_ids:
                    await self.register_envios(
                        idCanal=idCanal,
                        idAviso=aid,
                        usuarios=usuarios,
                        status_name="Sucesso"
                    )
        except Exception as e:
            print(f"[NotificationConsumer] Erro ao processar notificação: {e}")
            # Registrar com status de erro (se existir)
            try:
                if not alert_ids:
                    print(f"[NotificationConsumer] Nenhum alerta encontrado para registro de falha de envio.")
                else:
                    for aid in alert_ids:
                        await self.register_envios(
                            idCanal=idCanal,
                            idAviso=aid,
                            usuarios=usuarios,
                            status_name="Falha"
                        )
            except Exception as register_error:
                print(f"[NotificationConsumer] Erro ao registrar falha de envio: {register_error}")

    async def register_envios(
        self,
        idCanal: str,
        idAviso: str,
        usuarios: List[Dict[str, Any]],
        status_name: str = "Sucesso"
    ):
        """Registra os envios realizados na API externa."""
        idStatus = self.get_status_id(idCanal=idCanal, status_name=status_name)
        if not idStatus:
            print(f"[NotificationConsumer] Não foi possível obter ID do status '{status_name}'. Abortando registro.")
            return

        print(f"[NotificationConsumer] Registrando {len(usuarios)} envio(s) na API externa...")
        for usuario in usuarios:
            idUsuarioDestinatario = usuario.get("id")
            if not idUsuarioDestinatario:
                print(f"[NotificationConsumer] Usuário sem ID: {usuario}. Pulando...")
                continue

            try:
                resultado = await self.external_integration_service.create_envio(
                    idCanal=idCanal,
                    idAviso=idAviso,
                    idUsuarioDestinatario=idUsuarioDestinatario,
                    idStatus=idStatus
                )
                print(f"[NotificationConsumer] Envio registrado com sucesso para usuário {idUsuarioDestinatario}. ID: {resultado.get('id')}")
            except Exception as e:
                print(f"[NotificationConsumer] Erro ao registrar envio para usuário {idUsuarioDestinatario}: {e}")

if __name__ == "__main__":
    consumer = NotificationConsumer()
    consumer.start()
