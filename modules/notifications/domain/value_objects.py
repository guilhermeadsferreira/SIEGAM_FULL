"""Value objects de domínio."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Literal


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"


@dataclass(frozen=True)
class PhoneNumber:
    """Normaliza telefone: remove não numéricos, adiciona 55 se ausente."""
    raw: str

    @property
    def normalized(self) -> str:
        digits = re.sub(r"\D", "", str(self.raw))
        if not digits:
            return ""
        if not digits.startswith("55"):
            digits = "55" + digits
        return digits


@dataclass(frozen=True)
class Period:
    """Calcula período a partir do horário (±1h). Ex: 14:00 -> '13:00 às 15:00'."""
    horario_str: str

    def to_display(self) -> str:
        try:
            if ":" in self.horario_str and len(self.horario_str) >= 5:
                parts = self.horario_str.split(":")
                h = int(parts[0]) if parts[0] else 0
                m = int(parts[1]) if len(parts) > 1 else 0
                hora = datetime(2000, 1, 1, h, m)
            else:
                hora = datetime.strptime(self.horario_str, "%H:%M:%S")
        except (ValueError, IndexError):
            try:
                hora = datetime.strptime(self.horario_str, "%H:%M")
            except ValueError:
                return self.horario_str
        inicio = (hora - timedelta(hours=1)).strftime("%H:%M")
        fim = (hora + timedelta(hours=1)).strftime("%H:%M")
        return f"{inicio} às {fim}"


EventType = Literal["temperatura alta", "temperatura baixa", "umidade baixa", "vento", "chuva"]


@dataclass
class SeverityInfo:
    """Informações de severidade para templates (cor, emoji, mensagem)."""
    cor: str
    emoji: str
    nivel_msg: str
    titulo: str | None = None


def get_severity(tipo: str, valor: float) -> SeverityInfo:
    """
    Calcula severidade com base no tipo de evento e valor.
    Encapsula toda a lógica de níveis (umidade, vento, chuva).
    """
    tipo_lower = tipo.lower() if tipo else ""

    if tipo_lower == "umidade baixa":
        if 30 <= valor <= 60:
            return SeverityInfo("#f39c12", "💧", "Crítico para a saúde humana (30% a 60%).")
        if 21 <= valor < 30:
            return SeverityInfo("#e74c3c", "💧", "Estado de Atenção (21% a 30%).")
        if 12 <= valor < 21:
            return SeverityInfo("#e74c3c", "💧", "Estado de Alerta (12% a 20%).")
        if valor < 12:
            return SeverityInfo("#e74c3c", "💧", "Estado de Emergência (abaixo de 12%).")
        return SeverityInfo("#7f8c8d", "💧", "Umidade dentro da normalidade.")

    if tipo_lower == "vento":
        titulo = "Aviso - Previsão de ventania ou vento forte" if valor >= 30 else "Aviso - Previsão de brisa fraca"
        if 12 <= valor < 20:
            return SeverityInfo("#f39c12", "💨", "Brisa fraca (12 km/h – 20 km/h).", titulo)
        if 20 <= valor < 30:
            return SeverityInfo("#f39c12", "💨", "Brisa moderada (20 km/h – 30 km/h).", titulo)
        if 30 <= valor < 40:
            return SeverityInfo("#e74c3c", "💨", "Ventania (30 km/h – 40 km/h).", titulo)
        if 40 <= valor <= 50:
            return SeverityInfo("#e74c3c", "💨", "Forte ventania (40 km/h – 50 km/h).", titulo)
        if valor > 50:
            return SeverityInfo("#e74c3c", "💨", "Vento forte (acima de 50 km/h).", titulo)
        return SeverityInfo("#7f8c8d", "💨", "Vento dentro da normalidade.", titulo)

    if tipo_lower == "chuva":
        if 15 <= valor <= 25:
            return SeverityInfo("#f39c12", "🌧️", "Chuva de intensidade moderada (15 mm/h – 25 mm/h).")
        if valor > 25:
            return SeverityInfo("#e74c3c", "🌧️", "Chuva de intensidade forte (acima de 25 mm/h).")
        return SeverityInfo("#7f8c8d", "🌧️", "Chuva fraca ou dentro da normalidade.")

    if tipo_lower in ("temperatura alta", "temperatura baixa"):
        emoji = "🔥" if tipo_lower == "temperatura alta" else "❄️"
        return SeverityInfo("#e74c3c", emoji, "")

    return SeverityInfo("#7f8c8d", "⚠️", "")


def is_alert_critical(tipo: str, valor: float) -> bool:
    """Determina se um alerta é crítico (vento ≥ 30, umidade ≤ 30, chuva sempre)."""
    tipo_lower = tipo.lower() if tipo else ""
    if tipo_lower in ("chuva", "temperatura alta", "temperatura baixa"):
        return True
    if tipo_lower == "vento":
        return valor >= 30
    if tipo_lower == "umidade baixa":
        return valor <= 30
    return True
