"""Entry point - consumer da fila de notificações."""

from __future__ import annotations

from application.consumer import NotificationConsumer
from application.dispatcher import DispatcherService
from application.filter import FilterService
from application.resolver import ResolverService
from application.templates.email_renderer import EmailRenderer
from application.templates.whatsapp_renderer import WhatsAppRenderer
from domain.constants import STATUS_FALHA, STATUS_SUCESSO
from infra.database.catalogo_repository import get_canais, get_status_by_canal
from infra.database.envio_repository import envio_exists, insert_envio
from infra.logger import get_logger
from infra.redis.queue_consumer import QueueConsumer
from infra.senders.email_sender import EmailSender
from infra.senders.whatsapp_sender import WhatsAppSender

logger = get_logger("notifications.main")


def _create_dispatcher():
    canais = get_canais()
    status_by_canal = get_status_by_canal()

    def get_canal_id(nome: str) -> str:
        return canais.get(nome.lower(), "")

    def get_status_id(id_canal: str, status_name: str) -> str | None:
        canal_statuses = status_by_canal.get(id_canal, {})
        sid = canal_statuses.get(status_name.lower())
        if sid:
            return sid
        if canal_statuses:
            return next(iter(canal_statuses.values()))
        return None

    return DispatcherService(
        logger=logger,
        email_renderer=EmailRenderer(),
        whatsapp_renderer=WhatsAppRenderer(),
        email_sender=EmailSender(),
        whatsapp_sender=WhatsAppSender(),
        insert_envio_fn=insert_envio,
        envio_exists_fn=envio_exists,
        get_canal_id_fn=get_canal_id,
        get_status_id_fn=get_status_id,
    )


def main() -> None:
    logger.info("Iniciando módulo de notificações")

    resolver = ResolverService(logger)
    filter_svc = FilterService(logger)
    dispatcher = _create_dispatcher()
    consumer = NotificationConsumer(
        logger=logger,
        resolver=resolver,
        filter_service=filter_svc,
        dispatcher=dispatcher,
    )

    queue = QueueConsumer()
    logger.info("Consumer iniciado, aguardando mensagens", queue="etl:notifications:ready")
    queue.consume(consumer.process)


if __name__ == "__main__":
    main()
