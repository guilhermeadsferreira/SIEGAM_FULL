"""Repositório para persistência de envios na tabela envios."""

from __future__ import annotations

from infra.database.postgres import get_connection


def envio_exists(id_canal: str, id_aviso: str, id_usuario: str) -> bool:
    """Verifica se já existe registro de envio para (canal, aviso, usuario)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM envios
                WHERE id_canal = %s::uuid AND id_aviso = %s::uuid AND id_usuario_destinatario = %s::uuid
                LIMIT 1
                """,
                (id_canal, id_aviso, id_usuario),
            )
            return cur.fetchone() is not None


def insert_envio(id_canal: str, id_aviso: str, id_usuario: str, id_status: str) -> None:
    """Insere registro de envio. Chamar envio_exists antes para idempotência."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO envios (id_canal, id_aviso, id_usuario_destinatario, id_status)
                VALUES (%s::uuid, %s::uuid, %s::uuid, %s::uuid)
                """,
                (id_canal, id_aviso, id_usuario, id_status),
            )
