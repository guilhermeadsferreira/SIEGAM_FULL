"""Repositório de inserção de avisos no banco ETL."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from uuid import UUID

from infra.database.postgres import get_connection


def insert_batch(avisos: list[dict]) -> list[str]:
    """
    Insere um lote de avisos na tabela `avisos`.
    Retorna a lista de UUIDs dos avisos inseridos (mesma ordem do input).

    Cada item do lote deve ter:
        id_evento (str UUID), id_cidade (str UUID),
        valor (float), valor_limite (float | None),
        diferenca (float), unidade_medida (str),
        data_geracao (str YYYY-MM-DD), data_referencia (str YYYY-MM-DD),
        horario (str HH:MM | None), segundos (float | None)
    """
    if not avisos:
        return []

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

    placeholders = ", ".join(
        ["(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"] * len(rows)
    )
    flat_values = [v for row in rows for v in row]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO avisos
                    (id_evento, id_cidade, valor, valor_limite, diferenca,
                     unidade_medida, data_geracao, data_referencia, horario, segundos)
                VALUES {placeholders}
                RETURNING id
                """,
                flat_values,
            )
            inserted_ids = [str(row[0]) for row in cur.fetchall()]
    return inserted_ids
