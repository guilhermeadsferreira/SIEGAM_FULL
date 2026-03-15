"""Testes do FilterService."""

import pytest
from domain.entities import AlertPayload, UserWithPreference
from application.filter import FilterService
from infra.logger import get_logger


logger = get_logger("test")


@pytest.fixture
def filter_service():
    return FilterService(logger)


def test_filtra_vento_nao_critico_personalizavel_false(filter_service):
    usuario = UserWithPreference(
        id="1", nome="Teste", email="a@b.com", whatsapp=None,
        personalizavel=False, valor=None, canais_preferidos=[],
    )
    alerta = AlertPayload(
        aviso_id="a1", id_cidade="c1", id_evento="e1",
        nome_cidade="Goiânia", nome_evento="vento",
        valor=20.0, unidade_medida="km/h", horario="14:00", data_referencia="2026-03-14",
    )
    result = filter_service.apply([alerta], usuario)
    assert len(result) == 0


def test_envia_vento_critico_personalizavel_false(filter_service):
    usuario = UserWithPreference(
        id="1", nome="Teste", email="a@b.com", whatsapp=None,
        personalizavel=False, valor=None, canais_preferidos=[],
    )
    alerta = AlertPayload(
        aviso_id="a1", id_cidade="c1", id_evento="e1",
        nome_cidade="Goiânia", nome_evento="vento",
        valor=35.0, unidade_medida="km/h", horario="14:00", data_referencia="2026-03-14",
    )
    result = filter_service.apply([alerta], usuario)
    assert len(result) == 1


def test_envia_chuva_sempre(filter_service):
    usuario = UserWithPreference(
        id="1", nome="Teste", email="a@b.com", whatsapp=None,
        personalizavel=False, valor=None, canais_preferidos=[],
    )
    alerta = AlertPayload(
        aviso_id="a1", id_cidade="c1", id_evento="e1",
        nome_cidade="Goiânia", nome_evento="chuva",
        valor=10.0, unidade_medida="mm/h", horario="14:00", data_referencia="2026-03-14",
    )
    result = filter_service.apply([alerta], usuario)
    assert len(result) == 1
