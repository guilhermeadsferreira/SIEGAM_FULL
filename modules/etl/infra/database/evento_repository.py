"""Repositório de leitura de eventos do banco ETL."""

from __future__ import annotations

from infra.database.postgres import get_connection


def find_all() -> list[dict]:
    """
    Retorna todos os eventos cadastrados.
    Resultado: [{"id": "uuid-str", "nome_evento": "temperatura alta"}, ...]
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome_evento FROM eventos ORDER BY nome_evento")
            rows = cur.fetchall()
    return [{"id": str(row[0]), "nome_evento": row[1]} for row in rows]
