from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from domain.entities import Alert
from domain.value_objects import RainRateMmPerHour
from infra.logger import JsonLogger


class RainAnalyzer:
    def __init__(self, logger: JsonLogger, max_threshold: float = 15.0):
        self._logger = logger
        self.max_threshold = float(max_threshold)

    def analyze(
        self, polygon_data: Dict[float, Dict[str, Any]], polygon_name: str
    ) -> Dict[str, Alert]:
        self._logger.debug(
            "Starting rain analysis",
            polygon=polygon_name,
            threshold=self.max_threshold,
        )

        max_rain = float("-inf")
        max_payload: Optional[Tuple[float, Dict[str, Any], float]] = None

        records_processed = 0
        records_valid = 0

        for seconds, values in polygon_data.items():
            records_processed += 1
            rain = values.get("PRECmax")
            if rain is None:
                continue

            records_valid += 1
            rain_val = RainRateMmPerHour(float(rain)).value
            if rain_val > max_rain:
                max_rain = rain_val
                max_payload = (seconds, values, rain_val)

        alerts: Dict[str, Alert] = {}
        if max_payload and max_rain > self.max_threshold:
            sec, vals, r = max_payload
            alerts["chuva"] = Alert(
                type="chuva",
                value=r,
                unit="mm/h",
                threshold=self.max_threshold,
                difference=r - self.max_threshold,
                seconds=float(sec),
                date=str(vals.get("date", "")),
                polygon_name=polygon_name,
            )

        return alerts
