from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


AlertType = Literal["temperatura alta", "temperatura baixa", "umidade baixa", "vento", "chuva"]


@dataclass(slots=True)
class Alert:
    type: AlertType
    value: float
    unit: str
    threshold: Optional[float]
    difference: Optional[float]
    seconds: float
    date: str
    polygon_name: str
