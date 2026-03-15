"""Repositório para catálogos (canais, status)."""

from __future__ import annotations

from infra.database.postgres import get_connection


def get_canais() -> dict[str, str]:
    """Retorna mapeamento nome_canal (lower) -> id."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id::text, nome_canal FROM canais")
            rows = cur.fetchall()
    return {str(row[1]).lower(): row[0] for row in rows}


def get_status_by_canal() -> dict[str, dict[str, str]]:
    """Retorna dict[id_canal] -> dict[nome_status.lower -> id_status]."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_canal::text, nome_status, id::text FROM possiveis_status"
            )
            rows = cur.fetchall()

    result: dict[str, dict[str, str]] = {}
    for id_canal, nome_status, id_status in rows:
        if id_canal not in result:
            result[id_canal] = {}
        result[id_canal][str(nome_status).lower()] = id_status
    return result
