"""Repositório de inserção de avisos no banco ETL."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from uuid import UUID

from infra.database.postgres import get_connection


def insert_batch(avisos: list[dict]) -> int:
    """
    Insere um lote de avisos na tabela `avisos`.
    Retorna o número de registros inseridos.

    Cada item do lote deve ter:
        id_evento (str UUID), id_cidade (str UUID),
        valor (float), valor_limite (float | None),
        diferenca (float), unidade_medida (str),
        data_geracao (str YYYY-MM-DD), data_referencia (str YYYY-MM-DD),
        horario (str HH:MM | None), segundos (float | None)
    """
    if not avisos:
        return 0

    rows = [
        (
            UUID(a["id_evento"]),
            UUID(a["id_cidade"]),
            Decimal(str(a["valor"])),
            Decimal(str(a["valor_limite"])) if a.get("valor_limite") is not None else None,
            Decimal(str(a["diferenca"])),
            a["unidade_medida"],
            date.fromisoformat(a["data_geracao"]),
            date.fromisoformat(a["data_referencia"]),
            time.fromisoformat(a["horario"]) if a.get("horario") else None,
            Decimal(str(a["segundos"])) if a.get("segundos") is not None else None,
        )
        for a in avisos
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO avisos
                    (id_evento, id_cidade, valor, valor_limite, diferenca,
                     unidade_medida, data_geracao, data_referencia, horario, segundos)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
    return len(rows)
