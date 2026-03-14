from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True)
class Kelvin:
    value: float

    def to_celsius(self) -> "Celsius":
        return Celsius(self.value - 273.15)


@dataclass(frozen=True, slots=True)
class Celsius:
    value: float


@dataclass(frozen=True, slots=True)
class RelativeHumidity:
    value: float

    def clamp(self) -> "RelativeHumidity":
        v = max(0.0, min(100.0, self.value))
        return RelativeHumidity(v)

    def is_below(self, threshold: float) -> bool:
        return self.value < threshold


@dataclass(frozen=True, slots=True)
class WindSpeedKmh:
    value: float

    def is_above(self, threshold: float) -> bool:
        return self.value > threshold


@dataclass(frozen=True, slots=True)
class RainRateMmPerHour:
    value: float

    def is_above(self, threshold: float) -> bool:
        return self.value > threshold


class Date:
    @staticmethod
    def get_current_date() -> str:
        agora_sp = datetime.now(ZoneInfo("America/Sao_Paulo"))
        return agora_sp.strftime("%Y-%m-%d")


@dataclass(frozen=True, slots=True)
class TimeHeader:
    seconds: float
    year: int
    month: int
    day: int
    hour: int

    @property
    def as_datetime(self) -> datetime:
        return datetime(self.year, self.month, self.day) + timedelta(
            seconds=self.seconds
        )

    def to_datetime_string(self) -> str:
        return self.as_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def is_in_range(self, min_seconds: float, max_seconds: float) -> bool:
        return min_seconds <= self.seconds <= max_seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seconds": self.seconds,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "datetime": self.to_datetime_string(),
        }


@dataclass(frozen=True, slots=True)
class PolygonData:
    polygon_name: str
    state: str
    timestamp: TimeHeader
    values: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "polygon_name": self.polygon_name,
            "state": self.state,
            "timestamp": self.timestamp.to_datetime_string(),
            "values": self.values,
        }


@dataclass(frozen=True, slots=True)
class CityName:
    """
    Encapsula nome de cidade com normalização para comparação.
    Garante que 'Goiânia', 'GOIANIA' e 'goiania' sejam tratados como iguais.
    """

    raw: str

    @property
    def normalized(self) -> str:
        nfkd = unicodedata.normalize("NFKD", self.raw)
        return nfkd.encode("ASCII", "ignore").decode("ASCII").lower().strip()

    def matches(self, other: "CityName") -> bool:
        return self.normalized == other.normalized
