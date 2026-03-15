"""Logger estruturado JSON com suporte a correlation_id."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

_loggers: dict[str, "JsonLogger"] = {}


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str = "notifications"):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": self.service,
        }

        if hasattr(record, "context"):
            entry["context"] = record.context

        if hasattr(record, "correlation_id") and record.correlation_id:
            entry["correlation_id"] = record.correlation_id

        if record.exc_info:
            entry["error"] = self.formatException(record.exc_info)

        return json.dumps(entry, ensure_ascii=False, default=str)


class JsonLogger:
    def __init__(self, name: str, level: int = logging.INFO, service: str = "notifications"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.handlers.clear()
        self._logger.propagate = False

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(service))
        self._logger.addHandler(handler)

    def _log(self, level: int, msg: str, exc: bool = False, correlation_id: str | None = None, **ctx: Any) -> None:
        extra: dict[str, Any] = {"context": ctx} if ctx else {}
        if correlation_id:
            extra["correlation_id"] = correlation_id
        self._logger.log(level, msg, extra=extra, exc_info=exc)

    def debug(self, msg: str, correlation_id: str | None = None, **ctx: Any) -> None:
        self._log(logging.DEBUG, msg, correlation_id=correlation_id, **ctx)

    def info(self, msg: str, correlation_id: str | None = None, **ctx: Any) -> None:
        self._log(logging.INFO, msg, correlation_id=correlation_id, **ctx)

    def warning(self, msg: str, correlation_id: str | None = None, **ctx: Any) -> None:
        self._log(logging.WARNING, msg, correlation_id=correlation_id, **ctx)

    def error(self, msg: str, exc: bool = False, correlation_id: str | None = None, **ctx: Any) -> None:
        self._log(logging.ERROR, msg, exc, correlation_id=correlation_id, **ctx)

    def exception(self, msg: str, correlation_id: str | None = None, **ctx: Any) -> None:
        self._log(logging.ERROR, msg, True, correlation_id=correlation_id, **ctx)


def get_logger(
    name: str = "notifications",
    level: int = logging.INFO,
    service: str = "notifications",
) -> JsonLogger:
    if name not in _loggers:
        _loggers[name] = JsonLogger(name, level, service)
    return _loggers[name]
