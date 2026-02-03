from __future__ import annotations

from typing import Any, Dict, Protocol

from domain.entities import Alert


class Analyzer(Protocol):
    def analyze(
        self, polygon_data: Dict[float, Dict[str, Any]], polygon_name: str
    ) -> Dict[str, Alert]: ...
