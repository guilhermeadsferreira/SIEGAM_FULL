from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from domain.exceptions import (
    RetryableException,
    NonRetryableException,
    ParseException,
)
from infra.logger import JsonLogger

from .humidity import HumidityAnalyzer
from .organizer import DataOrganizer
from .rain import RainAnalyzer
from .temperature import TemperatureAnalyzer
from .types import Analyzer
from .wind import WindAnalyzer


class MainAnalyzer:

    def __init__(
        self,
        json_path: str,
        logger: JsonLogger,
        *,
        humidity_threshold: float = 60.0,
        wind_threshold: float = 12.0,
        rain_threshold: float = 15.0,
    ):
        self._logger = logger
        self.organizer = DataOrganizer(json_path, logger)
        self.analyzers: List[Analyzer] = [
            TemperatureAnalyzer(logger),
            HumidityAnalyzer(logger, min_threshold=humidity_threshold),
            WindAnalyzer(logger, max_threshold=wind_threshold),
            RainAnalyzer(logger, max_threshold=rain_threshold),
        ]
        self._alerts: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def analyze_all(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        self._logger.info("Starting analysis of all polygons")

        try:
            organized = self.organizer.organize_by_polygon()
        except (ParseException, NonRetryableException) as e:
            raise NonRetryableException(f"Erro ao organizar dados: {e}") from e
        except RetryableException:
            raise
        except Exception as e:
            raise NonRetryableException(f"Erro ao organizar dados: {e}") from e

        polygons_analyzed = 0
        total_alerts = 0
        alerts_by_type: Dict[str, int] = {}

        try:
            for polygon_name, polygon_data in organized.items():
                polygons_analyzed += 1
                if polygon_name not in self._alerts:
                    self._alerts[polygon_name] = {}

                for analyzer in self.analyzers:
                    try:
                        results = analyzer.analyze(polygon_data, polygon_name)
                        for key, alert in results.items():
                            self._alerts[polygon_name][key] = asdict(alert)
                            total_alerts += 1
                            alerts_by_type[key] = alerts_by_type.get(key, 0) + 1
                    except Exception as e:
                        self._logger.warning(
                            "Error analyzing polygon",
                            polygon=polygon_name,
                            analyzer=analyzer.__class__.__name__,
                            error=str(e),
                        )
                        continue

            result = {city: alerts for city, alerts in self._alerts.items() if alerts}

            self._logger.info(
                "Analysis completed",
                operation="analyze_all",
                polygons_analyzed=polygons_analyzed,
                polygons_with_alerts=len(result),
                total_alerts=total_alerts,
                alerts_by_type=alerts_by_type,
            )

            return result
        except Exception as e:
            raise NonRetryableException(f"Erro durante análise: {e}") from e
