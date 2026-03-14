from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from domain.entities import Alert
from domain.value_objects import Kelvin
from infra.logger import JsonLogger


class TemperatureAnalyzer:
    def __init__(self, logger: JsonLogger):
        self._logger = logger

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

        # TODO: aplicar threshold mensal por polígono antes de emitir os alertas de
        # temperatura — atualmente todo polígono gera alerta independentemente do valor.
        # HumidityAnalyzer e WindAnalyzer já fazem essa filtragem; temperatura precisa
        # do mesmo tratamento. Decisão pendente: config.csv local no ETL ou tabela no banco?
        # Ref: documentacao/tasks.md [CRÍTICO] — TemperatureAnalyzer não aplica threshold
        alerts: Dict[str, Alert] = {}
        if max_payload:
            sec, vals = max_payload
            alerts["temperatura alta"] = Alert(
                type="temperatura alta",
                value=max_temp_c,
                unit="°C",
                threshold=None,
                difference=None,
                seconds=float(sec),
                date=str(vals.get("date", "")),
                polygon_name=polygon_name,
            )
        if min_payload:
            sec, vals = min_payload
            alerts["temperatura baixa"] = Alert(
                type="temperatura baixa",
                value=min_temp_c,
                unit="°C",
                threshold=None,
                difference=None,
                seconds=float(sec),
                date=str(vals.get("date", "")),
                polygon_name=polygon_name,
            )

        return alerts
