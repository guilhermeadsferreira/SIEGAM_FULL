"""Testes dos templates."""

import pytest
from application.templates.base import format_data_pt_br, calcular_periodo, format_alert_for_template
from application.templates.email_renderer import EmailRenderer
from application.templates.whatsapp_renderer import WhatsAppRenderer


class TestBaseTemplates:
    def test_format_data_pt_br(self):
        assert format_data_pt_br("2026-03-14") == "14/03/2026"

    def test_calcular_periodo(self):
        assert "13:00" in calcular_periodo("14:00")
        assert "15:00" in calcular_periodo("14:00")


class TestEmailRenderer:
    def test_render_retorna_html(self):
        renderer = EmailRenderer()
        result = renderer.render([
            {"cidade": "Goiânia", "uf": "GO", "alertas": [
                {"nome_evento": "vento", "valor": 35, "unidade_medida": "km/h",
                 "horario": "14:00", "data_referencia": "2026-03-14"}
            ]}
        ])
        assert "<!DOCTYPE html>" in result
        assert "Goiânia" in result
        assert "35" in result


class TestWhatsAppRenderer:
    def test_render_retorna_texto(self):
        renderer = WhatsAppRenderer()
        result = renderer.render([
            {"cidade": "Goiânia", "uf": "GO", "alertas": [
                {"nome_evento": "vento", "valor": 35, "unidade_medida": "km/h",
                 "horario": "14:00", "data_referencia": "2026-03-14"}
            ]}
        ])
        assert "Goiânia" in result
        assert "*" in result
        assert "35" in result
