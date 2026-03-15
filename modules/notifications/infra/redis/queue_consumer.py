"""Consumer da fila Redis com graceful shutdown e dead-letter."""

from __future__ import annotations

import json
import signal
from typing import Callable

from redis import Redis

from domain.constants import REDIS_DEAD_LETTER_QUEUE, REDIS_NOTIFICATIONS_QUEUE
from domain.entities import AlertPayload, ExecutionPayload
from settings import settings


class QueueConsumer:
    """Consome mensagens da fila etl:notifications:ready com BLPOP."""

    def __init__(self, max_failures_before_dlq: int = 3):
        self._redis = Redis.from_url(settings.REDIS_URL)
        self._queue = REDIS_NOTIFICATIONS_QUEUE
        self._dlq = REDIS_DEAD_LETTER_QUEUE
        self._max_failures = max_failures_before_dlq
        self._shutdown_requested = False

    def consume(self, callback: Callable[[ExecutionPayload], None]) -> None:
        """Loop de consumo com graceful shutdown (SIGTERM/SIGINT)."""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        failure_count = 0
        last_message: bytes | None = None
        while not self._shutdown_requested:
            try:
                result = self._redis.blpop(self._queue, timeout=5)
                if result is None:
                    continue

                _, last_message = result
                payload = self._parse_payload(last_message)
                if payload:
                    callback(payload)
                    failure_count = 0
            except Exception:
                failure_count += 1
                if failure_count >= self._max_failures and last_message:
                    self._move_to_dlq(last_message)
                    failure_count = 0
                raise

    def _handle_shutdown(self, signum: int, frame) -> None:
        self._shutdown_requested = True

    def _parse_payload(self, message: bytes) -> ExecutionPayload | None:
        try:
            data = json.loads(message.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

        alerts_raw = data.get("alerts", [])
        alerts = []
        for a in alerts_raw:
            if isinstance(a, dict):
                alerts.append(AlertPayload(
                    aviso_id=a.get("aviso_id", ""),
                    id_cidade=a.get("id_cidade", ""),
                    id_evento=a.get("id_evento", ""),
                    nome_cidade=a.get("nome_cidade", ""),
                    nome_evento=a.get("nome_evento", ""),
                    valor=float(a.get("valor", 0)),
                    unidade_medida=a.get("unidade_medida", ""),
                    horario=a.get("horario"),
                    data_referencia=str(a.get("data_referencia", "")),
                ))

        return ExecutionPayload(
            execution_id=str(data.get("execution_id", "")),
            date=str(data.get("date", "")),
            avisos_count=int(data.get("avisos_count", 0)),
            alerts=alerts,
        )

    def _move_to_dlq(self, message: bytes) -> None:
        try:
            self._redis.rpush(self._dlq, message)
        except Exception:
            pass
