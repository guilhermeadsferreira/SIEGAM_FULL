
from typing import Optional, List, Iterator, Dict, Any, Tuple

from domain.exceptions import (
    ParseException,
    NonRetryableException,
    RetryableException,
)
from infra.file_system import FileSystem
from infra.logger import JsonLogger
from domain.value_objects import TimeHeader, PolygonData


class MeteogramTransformer:

    def __init__(self, file_path: str, logger: JsonLogger):
        self.file_path = file_path
        self._logger = logger
        self.time_headers: List[TimeHeader] = []
        self.polygon_data: List[PolygonData] = []
        self.column_headers: List[str] = []
        self.city_count: Optional[int] = None

    def perform(
        self,
        output_json_path: Optional[str] = None,
        min_seconds: float = 39600.0,
        max_seconds: float = 126000.0,
        filter_state: str = "GO",
    ) -> str:
        self._logger.info(
            "Starting transformation",
            operation="transform",
            file=self.file_path,
            min_seconds=min_seconds,
            max_seconds=max_seconds,
            filter_state=filter_state,
        )

        self._extract_data(min_seconds, max_seconds, filter_state)
        result = self._build_result()

        if output_json_path:
            try:
                FileSystem.save_json(result, output_json_path)
            except (OSError, IOError) as e:
                raise RetryableException(f"Erro ao salvar arquivo JSON: {e}") from e
            except Exception as e:
                raise RetryableException(
                    f"Erro de infraestrutura ao salvar arquivo: {e}"
                ) from e

            self._logger.info(
                "Transformation completed",
                operation="transform",
                file=self.file_path,
                output_file=output_json_path,
                polygons_processed=len(self.polygon_data),
                time_headers_extracted=len(self.time_headers),
                city_count=self.city_count,
            )
            return output_json_path

        self._logger.info(
            "Transformation completed",
            operation="transform",
            file=self.file_path,
            polygons_processed=len(self.polygon_data),
            time_headers_extracted=len(self.time_headers),
            city_count=self.city_count,
        )

        return self.file_path

    def _extract_data(
        self, min_seconds: float, max_seconds: float, filter_state: str
    ) -> None:
        self._reset_state()

        current_timestamp: Optional[TimeHeader] = None
        skip_block = False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                file_iterator = iter(f)

                for line_num, line in enumerate(file_iterator, start=1):
                    try:
                        line = line.strip()
                        if not line:
                            continue

                        if self._is_metadata_line(line):
                            self._extract_city_count(line)
                            continue

                        time_header = self._parse_time_header(line)

                        if time_header:
                            current_timestamp, skip_block = self._handle_time_header(
                                time_header, min_seconds, max_seconds, file_iterator
                            )
                            continue

                        if not skip_block and current_timestamp and self.column_headers:
                            self._process_polygon_line(
                                line,
                                current_timestamp,
                                self.column_headers,
                                filter_state,
                            )
                    except Exception as e:
                        self._logger.warning(
                            "Error processing line",
                            line_number=line_num,
                            line_preview=line[:100] if line else "",
                            error=str(e),
                        )
                        continue
        except UnicodeDecodeError as e:
            raise ParseException(f"Erro de encoding ao ler arquivo: {e}") from e
        except FileNotFoundError as e:
            raise NonRetryableException(f"Arquivo não encontrado: {e}") from e
        except (ValueError, OSError, IOError) as e:
            raise RetryableException(f"Erro ao ler arquivo: {e}") from e
        except Exception as e:
            raise ParseException(f"Erro ao processar arquivo: {e}") from e

    def _handle_time_header(
        self,
        time_header: TimeHeader,
        min_seconds: float,
        max_seconds: float,
        file_iterator: Iterator[str],
    ) -> Tuple[Optional[TimeHeader], bool]:
        if time_header.is_in_range(min_seconds, max_seconds):
            self.time_headers.append(time_header)

            try:
                next_line = next(file_iterator)
                self.column_headers = next_line.strip().split()
                return time_header, False
            except StopIteration:
                return None, True

        return None, True

    def _process_polygon_line(
        self,
        line: str,
        timestamp: TimeHeader,
        headers: List[str],
        filter_state: str,
    ) -> None:
        polygon = self._parse_polygon_line(line, timestamp, headers, filter_state)
        if polygon:
            self.polygon_data.append(polygon)

    def _parse_time_header(self, line: str) -> Optional[TimeHeader]:
        if not line or not line[0].isdigit():
            return None

        parts = line.split()
        if len(parts) < 5:
            return None

        try:
            return TimeHeader(
                seconds=float(parts[0]),
                year=int(parts[1]),
                month=int(parts[2]),
                day=int(parts[3]),
                hour=int(parts[4]),
            )
        except (ValueError, IndexError):
            return None

    def _parse_polygon_line(
        self,
        line: str,
        timestamp: TimeHeader,
        column_headers: List[str],
        target_state: str,
    ) -> Optional[PolygonData]:
        if f" - {target_state} " not in line:
            return None

        parts = line.split()

        if len(parts) < 4 or parts[1] != "-" or parts[2] != target_state:
            return None

        polygon_name = parts[0]
        state = parts[2]

        data_start_index = self._find_first_float_index(parts)
        if data_start_index is None:
            return None

        numeric_parts = parts[data_start_index:]
        valid_headers = column_headers[data_start_index:]
        values = {}

        for i, header in enumerate(valid_headers):
            if i < len(numeric_parts):
                val_str = numeric_parts[i]
                try:
                    values[header] = float(val_str)
                except ValueError:
                    values[header] = val_str

        return PolygonData(
            polygon_name=polygon_name,
            state=state,
            timestamp=timestamp,
            values=values,
        )

    def _find_first_float_index(self, parts: List[str]) -> Optional[int]:
        for i, part in enumerate(parts):
            try:
                float(part)
                return i
            except ValueError:
                continue
        return None

    def _build_result(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "city_count": self.city_count,
                "total_polygons": len(self.polygon_data),
                "total_time_headers": len(self.time_headers),
            },
            "time_headers": [t.to_dict() for t in self.time_headers],
            "data": [p.to_dict() for p in self.polygon_data],
        }

    def _is_metadata_line(self, line: str) -> bool:
        return line.startswith("nCities:")

    def _reset_state(self):
        self.time_headers = []
        self.polygon_data = []
        self.column_headers = []
        self.city_count = None

    def _extract_city_count(self, line: str):
        parts = line.split()
        if len(parts) >= 2 and parts[1].isdigit():
            self.city_count = int(parts[1])
