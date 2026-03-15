"""Orquestrador principal do pipeline de notificações."""

from __future__ import annotations

from domain.entities import ExecutionPayload
from infra.logger import JsonLogger


class NotificationConsumer:
    """Consume payload da fila, resolve, filtra e despacha."""

    def __init__(
        self,
        logger: JsonLogger,
        resolver,
        filter_service,
        dispatcher,
    ):
        self._logger = logger
        self._resolver = resolver
        self._filter = filter_service
        self._dispatcher = dispatcher

    def process(self, payload: ExecutionPayload) -> None:
        """Pipeline: Resolve -> Filtra -> Despacha."""
        if not payload.alerts:
            self._logger.info("Payload sem alertas", execution_id=payload.execution_id)
            return

        users_alerts = self._resolver.resolve(payload.alerts)

        for uid, data in list(users_alerts.items()):
            data["alertas"] = self._filter.apply(data["alertas"], data["usuario"])

        users_alerts = {k: v for k, v in users_alerts.items() if v["alertas"]}

        for uid, data in users_alerts.items():
            try:
                self._dispatcher.dispatch(data["usuario"], data["alertas"])
            except Exception as e:
                self._logger.exception(
                    "Erro ao despachar para usuário",
                    user_id=uid,
                    error=str(e),
                )

        self._logger.info(
            "Processamento concluído",
            execution_id=payload.execution_id,
            usuarios_notificados=len(users_alerts),
        )
