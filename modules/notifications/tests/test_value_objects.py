"""Testes dos value objects."""

import pytest
from domain.value_objects import (
    PhoneNumber,
    Period,
    get_severity,
    is_alert_critical,
)


class TestPhoneNumber:
    def test_normaliza_com_prefixo_55(self):
        assert PhoneNumber("62999999999").normalized == "5562999999999"

    def test_nao_duplica_55(self):
        assert PhoneNumber("5562999999999").normalized == "5562999999999"

    def test_remove_nao_numericos(self):
        assert PhoneNumber("(62) 99999-9999").normalized == "5562999999999"

    def test_vazio_retorna_vazio(self):
        assert PhoneNumber("").normalized == ""


class TestPeriod:
    def test_periodo_mais_menos_1h(self):
        assert Period("14:00").to_display() == "13:00 às 15:00"

    def test_periodo_formato_hh_mm_ss(self):
        assert Period("14:00:00").to_display() == "13:00 às 15:00"


class TestGetSeverity:
    def test_umidade_baixa_niveis(self):
        s = get_severity("umidade baixa", 25)
        assert s.cor == "#e74c3c"
        assert "Atenção" in s.nivel_msg

    def test_vento_critico(self):
        s = get_severity("vento", 35)
        assert s.cor == "#e74c3c"
        assert "Ventania" in s.nivel_msg

    def test_chuva_moderada(self):
        s = get_severity("chuva", 20)
        assert s.cor == "#f39c12"


class TestIsAlertCritical:
    def test_chuva_sempre_critico(self):
        assert is_alert_critical("chuva", 10) is True

    def test_vento_30_critico(self):
        assert is_alert_critical("vento", 30) is True
        assert is_alert_critical("vento", 29) is False

    def test_umidade_30_critico(self):
        assert is_alert_critical("umidade baixa", 30) is True
        assert is_alert_critical("umidade baixa", 31) is False
