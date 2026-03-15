from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from domain.entities import Alert
from domain.value_objects import Kelvin
from infra.logger import JsonLogger
from infra.temperature_config import TemperatureConfig


class TemperatureAnalyzer:
    def __init__(self, logger: JsonLogger, temperature_config: Optional[TemperatureConfig] = None):
        self._logger = logger
        self._config = temperature_config or TemperatureConfig()

    def analyze(
        self, polygon_data: Dict[float, Dict[str, Any]], polygon_name: str
    ) -> Dict[str, Alert]:
        self._logger.debug("Starting temperature analysis", polygon=polygon_name)

        max_temp_c = float("-inf")
        min_temp_c = float("inf")
        max_payload: Optional[Tuple[float, Dict[str, Any]]] = None
        min_payload: Optional[Tuple[float, Dict[str, Any]]] = None

        records_processed = 0
        records_valid = 0

        for seconds, values in polygon_data.items():
            records_processed += 1
            tmax_k = values.get("Tmax")
            tmin_k = values.get("Tmin")
            if tmax_k is None or tmin_k is None:
                continue
            if any(v < 200 or v > 350 for v in (tmax_k, tmin_k)):
                continue

            records_valid += 1
            tmax_c = Kelvin(float(tmax_k)).to_celsius().value
            tmin_c = Kelvin(float(tmin_k)).to_celsius().value

            if tmax_c > max_temp_c:
                max_temp_c = tmax_c
                max_payload = (seconds, values)
            if tmin_c < min_temp_c:
                min_temp_c = tmin_c
                min_payload = (seconds, values)

        month = datetime.now().month
        alerts: Dict[str, Alert] = {}

        if max_payload and self._config.should_emit_max_alert(polygon_name, month, max_temp_c):
            sec, vals = max_payload
            max_threshold = self._config.get_max_threshold(polygon_name, month)
            diff = max_temp_c - max_threshold if max_threshold else None
            alerts["temperatura alta"] = Alert(
                type="temperatura alta",
                value=max_temp_c,
                unit="°C",
                threshold=max_threshold,
                difference=diff,
                seconds=float(sec),
                date=str(vals.get("date", "")),
                polygon_name=polygon_name,
            )

        if min_payload and self._config.should_emit_min_alert(polygon_name, month, min_temp_c):
            sec, vals = min_payload
            min_threshold = self._config.get_min_threshold(polygon_name, month)
            diff = min_temp_c - min_threshold if min_threshold else None
            alerts["temperatura baixa"] = Alert(
                type="temperatura baixa",
                value=min_temp_c,
                unit="°C",
                threshold=min_threshold,
                difference=diff,
                seconds=float(sec),
                date=str(vals.get("date", "")),
                polygon_name=polygon_name,
            )

        return alerts
