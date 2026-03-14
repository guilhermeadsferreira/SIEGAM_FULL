"""Repositório de leitura de cidades do banco ETL."""

from __future__ import annotations

from infra.database.postgres import get_connection


def find_all() -> list[dict]:
    """
    Retorna todas as cidades cadastradas.
    Resultado: [{"id": "uuid-str", "nome": "Goiânia"}, ...]
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome FROM cidades ORDER BY nome")
            rows = cur.fetchall()
    return [{"id": str(row[0]), "nome": row[1]} for row in rows]
