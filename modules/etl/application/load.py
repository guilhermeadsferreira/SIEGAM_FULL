"""Serviço de carga de avisos no banco ETL."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any

from domain.exceptions import NonRetryableException
from domain.value_objects import Date
from infra.database import find_all_cidades, find_all_eventos, insert_avisos
from infra.logger import JsonLogger
from infra.temperature_config import TemperatureConfig


def _normalize(name: str) -> str:
    """
    Normaliza nome para comparação: remove acentos, lowercase, strip.
    Ex: 'Goiânia' → 'goiania', 'GOIÂNIA ' → 'goiania'
    """
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = nfkd.encode("ASCII", "ignore").decode("ASCII")
    return ascii_str.lower().strip()


@dataclass
class LoadResult:
    avisos_built: int
    avisos_inserted: int
    unmatched_polygons: list[str]
    unmatched_events: list[str]
    dispatch_alerts: list[dict]  # Lista de alertas com aviso_id para o módulo de notificações


class LoadService:

    def __init__(self, logger: JsonLogger, temperature_config: TemperatureConfig | None = None):
        self._logger = logger
        self._temperature_config = temperature_config or TemperatureConfig()
        self._evento_map: dict[str, str] = {}  # nome_evento → UUID str
        self._cidade_map: dict[str, str] = {}  # nome_normalizado → UUID str
        self._cidade_id_to_nome: dict[str, str] = {}  # id → nome (para dispatch)
        self._evento_id_to_nome: dict[str, str] = {}  # id → nome_evento (para dispatch)

    def _build_catalogs(self) -> None:
        """
        Carrega eventos e cidades do banco ETL e constrói
        os dicionários de lookup usados no mapeamento.
        """
        eventos = find_all_eventos()
        if not eventos:
            raise NonRetryableException(
                "Tabela 'eventos' está vazia — execute o seed antes de rodar o ETL."
            )
        self._evento_map = {e["nome_evento"]: e["id"] for e in eventos}
        self._evento_id_to_nome = {e["id"]: e["nome_evento"] for e in eventos}

        cidades = find_all_cidades()
        if not cidades:
            raise NonRetryableException(
                "Tabela 'cidades' está vazia — execute o seed antes de rodar o ETL."
            )
        self._cidade_map = {_normalize(c["nome"]): c["id"] for c in cidades}
        self._cidade_id_to_nome = {c["id"]: c["nome"] for c in cidades}

        self._logger.info(
            "Catálogos carregados",
            eventos=len(self._evento_map),
            cidades=len(self._cidade_map),
        )

    def _resolve_cidade(self, polygon_name: str) -> str | None:
        """
        Resolve polygon_name do CEMPA para o UUID da cidade no banco ETL.
        Tenta match direto primeiro; se falhar, usa config.csv para mapear
        polygon_name_meteogram -> display_name e busca por display_name.
        """
        key = _normalize(polygon_name)
        if key in self._cidade_map:
            return self._cidade_map[key]
        display_name = self._temperature_config.get_display_name(polygon_name)
        if display_name:
            return self._cidade_map.get(_normalize(display_name))
        return None

    def _resolve_evento(self, alert_type: str) -> str | None:
        """
        Resolve o tipo de alerta do ETL para o UUID do evento no banco ETL.
        Os tipos do ETL e os nomes do banco devem ser idênticos (snake_case + espaços).
        """
        return self._evento_map.get(alert_type)

    def _build_aviso(
        self,
        alert: dict[str, Any],
        id_evento: str,
        id_cidade: str,
        today: str,
    ) -> dict:
        return {
            "id_evento": id_evento,
            "id_cidade": id_cidade,
            "valor": alert["value"],
            "valor_limite": alert.get("threshold"),
            "diferenca": alert.get("difference") or 0.0,
            "unidade_medida": alert["unit"],
            "data_geracao": today,
            "data_referencia": alert.get("date", today),
            "horario": _seconds_to_time(alert.get("seconds")),
            "segundos": alert.get("seconds"),
        }

    def process(self, analyze_results: dict[str, dict[str, Any]]) -> LoadResult:
        """
        Recebe o resultado da task 'analyze' e persiste os avisos no banco.

        analyze_results formato:
            { "Goiania": { "temperatura alta": {Alert dataclass fields}, ... }, ... }
        """
        self._build_catalogs()

        today = Date.get_current_date()
        avisos_to_insert: list[dict] = []
        unmatched_polygons: list[str] = []
        unmatched_events: list[str] = []

        avisos_meta: list[tuple[str, str]] = []  # (polygon_name, alert_type) por aviso

        for polygon_name, alerts_by_type in analyze_results.items():
            id_cidade = self._resolve_cidade(polygon_name)
            if not id_cidade:
                unmatched_polygons.append(polygon_name)
                self._logger.warning(
                    "Polígono sem correspondência de cidade",
                    polygon=polygon_name,
                )
                continue

            for alert_type, alert in alerts_by_type.items():
                id_evento = self._resolve_evento(alert_type)
                if not id_evento:
                    unmatched_events.append(alert_type)
                    self._logger.warning(
                        "Tipo de alerta sem correspondência de evento",
                        alert_type=alert_type,
                        polygon=polygon_name,
                    )
                    continue

                aviso = self._build_aviso(alert, id_evento, id_cidade, today)
                avisos_to_insert.append(aviso)
                avisos_meta.append((polygon_name, alert_type))

        inserted_ids = insert_avisos(avisos_to_insert)
        inserted = len(inserted_ids)

        # Monta payload para o módulo de notificações (com aviso_id, id_cidade, id_evento, etc.)
        dispatch_alerts: list[dict] = []
        for i, aviso in enumerate(avisos_to_insert):
            polygon_name, alert_type = avisos_meta[i]
            aviso_id = inserted_ids[i] if i < len(inserted_ids) else None
            if not aviso_id:
                continue
            nome_cidade = self._cidade_id_to_nome.get(aviso["id_cidade"], polygon_name)
            nome_evento = self._evento_id_to_nome.get(aviso["id_evento"], alert_type)
            horario = aviso.get("horario")
            # Formato HH:MM:00 para compatibilidade com o módulo de notificações
            horario_str = f"{horario}:00" if horario and len(str(horario)) == 5 else str(horario) if horario else None
            dispatch_alerts.append({
                "aviso_id": aviso_id,
                "id_cidade": aviso["id_cidade"],
                "id_evento": aviso["id_evento"],
                "nome_cidade": nome_cidade,
                "nome_evento": nome_evento,
                "valor": float(aviso["valor"]),
                "unidade_medida": aviso["unidade_medida"],
                "horario": horario_str,
                "data_referencia": str(aviso["data_referencia"]),
            })

        self._logger.info(
            "Avisos persistidos",
            total_built=len(avisos_to_insert),
            total_inserted=inserted,
            unmatched_polygons=unmatched_polygons,
            unmatched_events=list(set(unmatched_events)),
        )

        return LoadResult(
            avisos_built=len(avisos_to_insert),
            avisos_inserted=inserted,
            unmatched_polygons=unmatched_polygons,
            unmatched_events=list(set(unmatched_events)),
            dispatch_alerts=dispatch_alerts,
        )


def _seconds_to_time(seconds: float | None) -> str | None:
    """Converte segundos do dia (ex: 39600) para 'HH:MM'."""
    if seconds is None:
        return None
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    return f"{h:02d}:{m:02d}"
