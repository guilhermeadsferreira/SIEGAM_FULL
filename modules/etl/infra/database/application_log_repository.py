"""Repositório para persistência de application logs no PostgreSQL."""

from __future__ import annotations

from uuid import UUID

from psycopg.types.json import Jsonb

from infra.database.postgres import get_connection


def insert(
    *,
    task: str,
    execution_id: UUID | str,
    message: str,
    status: str | None = None,
    extra: dict | None = None,
) -> None:
    """
    Insere um registro na tabela application_logs.

    Status sugeridos: STARTED, IN_PROGRESS, SUCCESS, ERROR.
    """
    execution_id_uuid = execution_id if isinstance(execution_id, UUID) else UUID(str(execution_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO application_logs (task, execution_id, message, status, extra)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    task[:100],
                    execution_id_uuid,
                    message[:255],
                    status[:20] if status else None,
                    Jsonb(extra) if extra is not None else None,
                ),
            )
