"""Conexão PostgreSQL para o módulo de notificações (banco sigedam)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import psycopg
from psycopg import Connection

from domain.exceptions import DatabaseException
from settings import settings


@contextmanager
def get_connection() -> Generator[Connection[tuple], None, None]:
    """
    Context manager que abre uma conexão PostgreSQL usando DATABASE_URL.
    Conecta ao banco sigedam (usuários, preferências, envios).
    Fecha a conexão ao sair do bloco.
    """
    conn: Connection[tuple] | None = None
    try:
        conn = psycopg.connect(settings.DATABASE_URL)
        yield conn
        conn.commit()
    except psycopg.Error as e:
        if conn is not None:
            conn.rollback()
        raise DatabaseException(f"Erro PostgreSQL: {e}") from e
    finally:
        if conn is not None:
            conn.close()
