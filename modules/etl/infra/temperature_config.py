"""Carregador de limiares mensais de temperatura por polígono (config.csv)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

MONTH_COLUMNS = {
    1: ("temp_max_jan", "temp_min_jan"),
    2: ("temp_max_feb", "temp_min_feb"),
    3: ("temp_max_mar", "temp_min_mar"),
    4: ("temp_max_apr", "temp_min_apr"),
    5: ("temp_max_may", "temp_min_may"),
    6: ("temp_max_jun", "temp_min_jun"),
    7: ("temp_max_jul", "temp_min_jul"),
    8: ("temp_max_aug", "temp_min_aug"),
    9: ("temp_max_sep", "temp_min_sep"),
    10: ("temp_max_oct", "temp_min_oct"),
    11: ("temp_max_nov", "temp_min_nov"),
    12: ("temp_max_dec", "temp_min_dec"),
}

MIN_DIFF_TEMPERATURE = 5.0  # Diferença mínima em °C para considerar temperatura crítica


def _default_config_path() -> Path:
    return Path(__file__).parent.parent / "data" / "config.csv"


class TemperatureConfig:
    """
    Carrega limiares mensais de temperatura do config.csv.
    Usa polygon_name_meteogram como chave (ex: 0247-Abadia_de_Goias).
    """

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path or _default_config_path()
        self._thresholds: dict[str, dict[str, float]] = {}  # polygon -> {col: value}
        self._polygon_to_display_name: dict[str, str] = {}  # polygon -> display_name
        self._load()

    def _load(self) -> None:
        self._polygon_to_display_name: dict[str, str] = {}
        if not self._config_path.exists():
            return
        with open(self._config_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                polygon = row.get("polygon_name_meteogram", "").strip()
                display_name = row.get("display_name", "").strip()
                if not polygon:
                    continue
                self._polygon_to_display_name[polygon] = display_name
                self._thresholds[polygon] = {}
                for col, val in row.items():
                    if col.startswith("temp_") and val:
                        try:
                            self._thresholds[polygon][col] = float(val)
                        except ValueError:
                            pass

    def get_display_name(self, polygon_name: str) -> Optional[str]:
        """Retorna o nome de exibição (cidade) para o polígono. Usado no Load para mapear polígono -> cidade."""
        return self._polygon_to_display_name.get(polygon_name)

    def get_max_threshold(self, polygon_name: str, month: int) -> Optional[float]:
        """Retorna o limiar de temperatura máxima para o polígono no mês (1-12)."""
        if month not in MONTH_COLUMNS:
            return None
        col, _ = MONTH_COLUMNS[month]
        return self._thresholds.get(polygon_name, {}).get(col)

    def get_min_threshold(self, polygon_name: str, month: int) -> Optional[float]:
        """Retorna o limiar de temperatura mínima para o polígono no mês (1-12)."""
        if month not in MONTH_COLUMNS:
            return None
        _, col = MONTH_COLUMNS[month]
        return self._thresholds.get(polygon_name, {}).get(col)

    def should_emit_max_alert(self, polygon_name: str, month: int, value: float) -> bool:
        """
        Temperatura alta: emite alerta se valor > limiar E diferença >= 5°C.
        """
        threshold = self.get_max_threshold(polygon_name, month)
        if threshold is None:
            return False
        diff = value - threshold
        return value > threshold and diff >= MIN_DIFF_TEMPERATURE

    def should_emit_min_alert(self, polygon_name: str, month: int, value: float) -> bool:
        """
        Temperatura baixa: emite alerta se valor < limiar E diferença <= -5°C.
        """
        threshold = self.get_min_threshold(polygon_name, month)
        if threshold is None:
            return False
        diff = value - threshold
        return value < threshold and diff <= -MIN_DIFF_TEMPERATURE
