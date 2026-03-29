"""Lógica compartilhada entre templates de e-mail e WhatsApp."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from domain.value_objects import Period, get_severity
from settings import settings


def format_data_pt_br(data_str: str) -> str:
    """Converte YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS para DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS (pt-BR)."""
    try:
        if not data_str:
            return "N/A"
        s = str(data_str)
        if len(s) >= 19:
            data_obj = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
            return data_obj.strftime("%d/%m/%Y %H:%M:%S")
        if len(s) == 10:
            data_obj = datetime.strptime(s, "%Y-%m-%d")
            return data_obj.strftime("%d/%m/%Y")
        return s
    except (ValueError, AttributeError):
        return str(data_str)


def calcular_periodo(horario_str: str) -> str:
    """Calcula período ±1h. Ex: '14:00' -> '13:00 às 15:00'."""
    return Period(horario_str or "").to_display()


def format_alert_for_template(alerta: dict[str, Any]) -> dict[str, Any]:
    """Adiciona campos formatados ao alerta para o template."""
    import math
    tipo = alerta.get("nome_evento", alerta.get("eventoNome", "")).lower()
    valor = alerta.get("valor", 0)
    severity = get_severity(tipo, valor)

    if tipo in ("temperatura baixa", "umidade baixa"):
        valor_display = math.floor(valor)
    else:
        valor_display = math.ceil(valor)

    return {
        **alerta,
        "eventoNome": alerta.get("nome_evento", alerta.get("eventoNome", tipo)),
        "valor": valor_display,
        "periodo": calcular_periodo(alerta.get("horario", "") or ""),
        "dataReferencia": format_data_pt_br(alerta.get("data_referencia", "") or ""),
        "unidadeMedida": alerta.get("unidade_medida", ""),
        "severity": severity,
    }


def get_manage_url() -> str:
    """URL para gerenciamento de preferências."""
    frontend = (settings.FRONTEND_URL or "").rstrip("/")
    return f"{frontend}/manage-profile" if frontend else "/manage-profile"
