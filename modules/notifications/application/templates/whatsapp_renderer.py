"""Renderizador de template texto para WhatsApp."""

from __future__ import annotations

import math
from typing import Any

from application.templates.base import format_alert_for_template, get_manage_url


class WhatsAppRenderer:
    """Gera texto formatado para notificações por WhatsApp."""

    def render(self, cidades_alertas: list[dict[str, Any]]) -> str:
        message = self._header()
        for item in cidades_alertas:
            message += self._render_city_block(
                item["cidade"],
                item.get("uf", "GO"),
                item["alertas"],
            )
        message += self._footer()
        return message

    def _header(self) -> str:
        return (
            "🌦️ *Resumo de Avisos Meteorológicos*\n"
            "_Centro de Excelência em Estudos, Monitoramento e Previsões Ambientais do Cerrado (CEMPA-Cerrado)_\n\n"
        )

    def _footer(self) -> str:
        manage_url = get_manage_url()
        return (
            "\n🤖 _Mensagem automática do CEMPA._\n"
            f"_Para gerenciar notificações, acesse: {manage_url}_"
        )

    def _render_city_block(self, cidade: str, uf: str, alertas: list[dict]) -> str:
        text = f"📍 *{cidade}/{uf}*\n"
        if not alertas:
            return text + "Nenhum alerta registrado.\n\n"
        for alerta in alertas:
            formatted = format_alert_for_template(alerta)
            text += self._render_alert(formatted)
        return text + "\n"

    def _render_alert(self, alerta: dict[str, Any]) -> str:
        tipo = alerta.get("eventoNome", "").lower()
        severity = alerta.get("severity")
        emoji = severity.emoji if severity else "⚠️"
        valor = alerta.get("valor", 0)

        if tipo == "temperatura baixa":
            return (
                f"{emoji} *Aviso - Previsão de temperatura mínima baixa*\n"
                f"• *Data:* {alerta.get('dataReferencia', '')}\n"
                f"• Temperatura mínima prevista: *{math.floor(valor)} {alerta.get('unidadeMedida', '')}*\n"
                f"• Período: {alerta.get('periodo', '')}\n"
                "----------------------\n"
            )
        if tipo == "temperatura alta":
            return (
                f"{emoji} *Aviso - Previsão de temperatura máxima elevada*\n"
                f"• *Data:* {alerta.get('dataReferencia', '')}\n"
                f"• Temperatura máxima prevista: *{math.ceil(valor)} {alerta.get('unidadeMedida', '')}*\n"
                f"• Período: {alerta.get('periodo', '')}\n"
                "----------------------\n"
            )
        if tipo == "umidade baixa":
            nivel_msg = severity.nivel_msg if severity else ""
            return (
                f"{emoji} *Aviso - Baixa Umidade Relativa do Ar*\n"
                f"• *Data:* {alerta.get('dataReferencia', '')}\n"
                f"• Umidade prevista: *{math.floor(valor)} {alerta.get('unidadeMedida', '')}*\n"
                f"• *Nível:* _{nivel_msg}_\n"
                f"• Período: {alerta.get('periodo', '')}\n"
                "----------------------\n"
            )
        if tipo == "vento":
            nivel_msg = severity.nivel_msg if severity else ""
            return (
                f"{emoji} *Aviso - Ventania / Vento Forte*\n"
                f"• *Data:* {alerta.get('dataReferencia', '')}\n"
                f"• Velocidade prevista: *{math.ceil(valor)} {alerta.get('unidadeMedida', '')}*\n"
                f"• *Nível:* _{nivel_msg}_\n"
                f"• Período: {alerta.get('periodo', '')}\n"
                "----------------------\n"
            )
        if tipo == "chuva":
            nivel_msg = severity.nivel_msg if severity else ""
            return (
                f"{emoji} *Aviso - Previsão de ocorrência de chuva intensa*\n"
                f"• *Data:* {alerta.get('dataReferencia', '')}\n"
                f"• Precipitação estimada: *{math.ceil(valor)} {alerta.get('unidadeMedida', '')}*\n"
                f"• *Nível:* _{nivel_msg}_\n"
                f"• Período: {alerta.get('periodo', '')}\n"
                "----------------------\n"
            )

        return (
            f"{emoji} *Aviso - {tipo.capitalize()}*\n"
            f"• Valor: {valor}{alerta.get('unidadeMedida', '')}\n"
            f"• Data: {alerta.get('dataReferencia', '')}\n"
            "----------------------\n"
        )
