import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

_loggers: dict[str, "JsonLogger"] = {}


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str = "etl"):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if hasattr(record, "context"):
            entry["context"] = record.context

        if record.exc_info:
            entry["error"] = self.formatException(record.exc_info)

        return json.dumps(entry, ensure_ascii=False, default=str)


class JsonLogger:
    def __init__(self, name: str, level: int, service: str):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.handlers.clear()
        self._logger.propagate = False

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(service))
        self._logger.addHandler(handler)

    def _log(self, level: int, msg: str, exc: bool = False, **ctx: Any) -> None:
        extra = {"context": ctx} if ctx else {}
        self._logger.log(level, msg, extra=extra, exc_info=exc)

    def debug(self, msg: str, **ctx: Any) -> None:
        self._log(logging.DEBUG, msg, **ctx)

    def info(self, msg: str, **ctx: Any) -> None:
        self._log(logging.INFO, msg, **ctx)

    def warning(self, msg: str, **ctx: Any) -> None:
        self._log(logging.WARNING, msg, **ctx)

    def error(self, msg: str, exc: bool = False, **ctx: Any) -> None:
        self._log(logging.ERROR, msg, exc, **ctx)

    def exception(self, msg: str, **ctx: Any) -> None:
        self._log(logging.ERROR, msg, True, **ctx)


def get_logger(
    name: str = "etl",
    level: int = logging.INFO,
    service: str = "etl",
) -> JsonLogger:
    if name not in _loggers:
        _loggers[name] = JsonLogger(name, level, service)
    return _loggers[name]
