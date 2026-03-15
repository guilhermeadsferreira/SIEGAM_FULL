"""Renderizador de template HTML para e-mail."""

from __future__ import annotations

import html
import math
from typing import Any

from application.templates.base import (
    format_alert_for_template,
    format_data_pt_br,
    get_manage_url,
)
from domain.value_objects import get_severity


class EmailRenderer:
    """Gera HTML para notificações por e-mail."""

    def render(self, cidades_alertas: list[dict[str, Any]]) -> str:
        city_blocks = ""
        for item in cidades_alertas:
            city_blocks += self._render_city_block(
                cidade=item["cidade"],
                uf=item.get("uf", "GO"),
                alertas=item["alertas"],
            )
        manage_url = html.escape(get_manage_url())
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resumo de Avisos Meteorológicos - CEMPA</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
    {self._header()}
    <div style="padding: 20px;">
        {city_blocks}
    </div>
    {self._footer(manage_url)}
</body>
</html>
"""

    def _header(self) -> str:
        return """
    <div style="background-color: #e74c3c; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0;">
        <h2>Resumo de Avisos Meteorológicos</h2>
    </div>
"""

    def _footer(self, manage_url: str) -> str:
        return f"""
    <hr style="border: 0; border-top: 1px solid #ddd; margin: 30px 0;">
    <p style="color: #777; font-size: 12px;">Este é um e-mail automático do CEMPA.</p>
    <p style="color: #777; font-size: 12px;">Por favor, não responda a este e-mail.</p>
    <div style="text-align: center; margin-top: 20px;">
        <a href="{manage_url}"
           style="background-color: #dc3545; color: white; padding: 10px 20px;
                  text-decoration: none; border-radius: 5px; display: inline-block;">
           Descadastrar ou atualizar preferências
        </a>
    </div>
"""

    def _render_city_block(self, cidade: str, uf: str, alertas: list[dict]) -> str:
        alert_html = ""
        for alerta in alertas:
            formatted = format_alert_for_template(alerta)
            alert_html += self._render_alert_block(formatted)
        cidade_safe = html.escape(cidade)
        uf_safe = html.escape(uf)
        return f"""
    <div style="margin-bottom: 30px; padding: 15px; border: 1px solid #eee; border-radius: 5px;">
        <h3 style="margin-bottom: 10px;">Município: {cidade_safe}/{uf_safe}</h3>
        {alert_html}
    </div>
"""

    def _render_alert_block(self, alerta: dict[str, Any]) -> str:
        tipo = alerta.get("eventoNome", "").lower()
        severity = alerta.get("severity")
        cor = severity.cor if severity else "#7f8c8d"
        valor = alerta.get("valor", 0)
        unidade_safe = html.escape(str(alerta.get("unidadeMedida", "")))
        data_safe = html.escape(format_data_pt_br(alerta.get("dataReferencia", "")))
        periodo_safe = html.escape(str(alerta.get("periodo", "")))

        if tipo == "temperatura baixa":
            return f"""
    <div style="margin-bottom: 20px;">
        <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
            <strong>Aviso - Previsão de temperatura mínima baixa</strong>
        </div>
        <div style="padding: 10px;">
            <p><strong>Data:</strong> {data_safe}</p>
            <p>Temperatura mínima prevista é de <strong>{math.floor(valor)} {unidade_safe}</strong>
            no período entre <strong>{periodo_safe}</strong>.</p>
        </div>
        <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
    </div>
"""
        if tipo == "temperatura alta":
            return f"""
    <div style="margin-bottom: 20px;">
        <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
            <strong>Aviso - Previsão de temperatura máxima elevada</strong>
        </div>
        <div style="padding: 10px;">
            <p><strong>Data:</strong> {data_safe}</p>
            <p>Temperatura máxima prevista é de <strong>{math.ceil(valor)} {unidade_safe}</strong>
            no período entre <strong>{periodo_safe}</strong>.</p>
        </div>
        <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
    </div>
"""
        if tipo == "umidade baixa":
            nivel_msg = severity.nivel_msg if severity else ""
            return f"""
    <div style="margin-bottom: 20px;">
        <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
            <strong>Aviso - Previsão de registros de baixa umidade relativa do ar em superfície</strong>
        </div>
        <div style="padding: 10px;">
            <p><strong>Data:</strong> {data_safe}</p>
            <p>Umidade relativa prevista é de <strong>{math.floor(valor)} {unidade_safe}</strong>
            no período entre <strong>{periodo_safe}</strong>.</p>
            <p style="margin-top: 10px;"><em>{nivel_msg}</em></p>
        </div>
        <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
    </div>
"""
        if tipo == "vento":
            titulo = severity.titulo if severity and severity.titulo else "Aviso - Ventania / Vento Forte"
            nivel_msg = severity.nivel_msg if severity else ""
            return f"""
    <div style="margin-bottom: 20px;">
        <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
            <strong>{titulo}</strong>
        </div>
        <div style="padding: 10px;">
            <p><strong>Data:</strong> {data_safe}</p>
            <p>Velocidade do vento prevista é de <strong>{math.ceil(valor)} {unidade_safe}</strong>
            no período entre <strong>{periodo_safe}</strong>.</p>
            <p style="margin-top: 10px;"><em>{nivel_msg}</em></p>
        </div>
        <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
    </div>
"""
        if tipo == "chuva":
            nivel_msg = severity.nivel_msg if severity else ""
            return f"""
    <div style="margin-bottom: 20px;">
        <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
            <strong>Aviso - Previsão de ocorrência de chuva intensa</strong>
        </div>
        <div style="padding: 10px;">
            <p><strong>Data:</strong> {data_safe}</p>
            <p>Precipitação estimada de <strong>{math.ceil(valor)} {unidade_safe}</strong>
            no período entre <strong>{periodo_safe}</strong>.</p>
            <p style="margin-top: 10px;"><em>{nivel_msg}</em></p>
        </div>
        <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
    </div>
"""

        tipo_safe = html.escape(tipo.replace("_", " ").capitalize())
        valor_safe = html.escape(str(valor))
        return f"""
    <div style="margin-bottom: 20px;">
        <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
            <strong>Aviso - {tipo_safe}</strong>
        </div>
        <div style="padding: 10px;">
            <p><strong>Valor:</strong> {valor_safe}{unidade_safe}</p>
            <p><strong>Data:</strong> {data_safe}</p>
        </div>
        <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
    </div>
"""
