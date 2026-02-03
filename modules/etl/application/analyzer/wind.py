from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

from domain.entities import Alert
from domain.value_objects import WindSpeedKmh
from infra.logger import JsonLogger


class WindAnalyzer:
    def __init__(self, logger: JsonLogger, max_threshold: float = 12.0):
        self._logger = logger
        self.max_threshold = float(max_threshold)

    @staticmethod
    def _wind_kmh(u: float, v: float) -> WindSpeedKmh:
        speed_ms = math.sqrt(u * u + v * v)
        return WindSpeedKmh(speed_ms * 3.6)

    def analyze(
        self, polygon_data: Dict[float, Dict[str, Any]], polygon_name: str
    ) -> Dict[str, Alert]:
        self._logger.debug(
            "Starting wind analysis",
            polygon=polygon_name,
            threshold=self.max_threshold,
        )

        max_wind = float("-inf")
        max_payload: Optional[Tuple[float, Dict[str, Any], float]] = None

        records_processed = 0
        records_valid = 0

        for seconds, values in polygon_data.items():
            records_processed += 1
            umax = values.get("Umax")
            vmax = values.get("Vmax")
            if umax is None or vmax is None:
                continue
            if abs(umax) > 100 or abs(vmax) > 100:
                continue

            wind_kmh = self._wind_kmh(float(umax), float(vmax)).value
            if wind_kmh > 200:
                continue

            records_valid += 1
            if wind_kmh > max_wind:
                max_wind = wind_kmh
                max_payload = (seconds, values, wind_kmh)

        alerts: Dict[str, Alert] = {}
        if max_payload and max_wind > self.max_threshold:
            sec, vals, w_kmh = max_payload
            alerts["vento"] = Alert(
                type="vento",
                value=w_kmh,
                unit="km/h",
                threshold=self.max_threshold,
                difference=w_kmh - self.max_threshold,
                seconds=float(sec),
                date=str(vals.get("date", "")),
                polygon_name=polygon_name,
            )

        return alerts
