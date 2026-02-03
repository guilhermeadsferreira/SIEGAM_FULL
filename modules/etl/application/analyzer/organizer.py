from __future__ import annotations

import json
from typing import Any, Dict, Optional

from domain.exceptions import ParseException, NonRetryableException, RetryableException
from infra.logger import JsonLogger


class DataOrganizer:

    def __init__(self, json_path: str, logger: JsonLogger):
        self.json_path = json_path
        self._logger = logger
        self._raw: Optional[Dict[str, Any]] = None
        self._organized: Optional[Dict[str, Dict[float, Dict[str, Any]]]] = None

    def load(self) -> Dict[str, Any]:
        self._logger.debug("Loading JSON file", file=self.json_path)

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self._raw = json.load(f)
        except FileNotFoundError as e:
            raise NonRetryableException(f"Arquivo JSON não encontrado: {e}") from e
        except json.JSONDecodeError as e:
            raise ParseException(f"Erro ao decodificar JSON: {e}") from e
        except (OSError, IOError) as e:
            raise RetryableException(f"Erro ao ler arquivo JSON: {e}") from e
        except Exception as e:
            raise ParseException(f"Erro inesperado ao carregar JSON: {e}") from e

        file_size_kb = round(len(json.dumps(self._raw or {})) / 1024, 2)
        self._logger.info(
            "JSON file loaded",
            file=self.json_path,
            file_size_kb=file_size_kb,
        )

        return self._raw or {}

    def organize_by_polygon(self) -> Dict[str, Dict[float, Dict[str, Any]]]:
        self._logger.debug("Organizing data by polygon")

        if not self._raw:
            self.load()

        raw = self._raw or {}
        time_headers = raw.get("time_headers", [])
        data_rows = raw.get("data", [])

        dt_to_seconds: Dict[str, float] = {
            th.get("datetime"): float(th.get("seconds"))
            for th in time_headers
            if "datetime" in th and "seconds" in th
        }

        organized: Dict[str, Dict[float, Dict[str, Any]]] = {}
        rows_processed = 0
        rows_valid = 0

        for row in data_rows:
            rows_processed += 1
            polygon_name = row.get("polygon_name")
            timestamp_str = row.get("timestamp")
            values: Dict[str, Any] = row.get("values", {})
            if not polygon_name or not timestamp_str:
                continue

            seconds = dt_to_seconds.get(timestamp_str)
            if seconds is None:
                continue

            rows_valid += 1
            if polygon_name not in organized:
                organized[polygon_name] = {}

            organized[polygon_name][seconds] = {
                **values,
                "seconds": seconds,
                "date": timestamp_str,
                "datetime": timestamp_str,
            }

        self._organized = organized

        self._logger.info(
            "Data organized by polygon",
            polygons_count=len(organized),
            time_headers_count=len(time_headers),
            rows_processed=rows_processed,
            rows_valid=rows_valid,
        )

        return organized
